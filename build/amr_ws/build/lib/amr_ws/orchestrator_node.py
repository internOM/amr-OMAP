#!/usr/bin/env python3

"""
orchestrator_node.py

Timer-driven state machine orchestrator for the AMR.

States:
    WAITING_FOR_LOCALIZATION  — startup default
    LOCALIZING                — running AMCL spin sequence
    IDLE                      — awaiting HMI command
    NAVIGATING                — executing waypoint sequence via Nav2
    RETURNING_HOME            — navigating back to home pose via Nav2
    FAULT                     — permanent halt, manual restart required
"""

import math
import os
import time

import rclpy
import yaml
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import SetInitialPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Bool, String


# ─── Constants ────────────────────────────────────────────────────────────────

# Home / initial pose
HOME_X   = -0.427
HOME_Y   =  0.025
HOME_YAW = -0.483

# Large initial covariance for AMCL seed
INITIAL_COVARIANCE = [
    0.5,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.5, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.5,
]

# Localization spin parameters
SPIN_ANGULAR_VEL    = 0.3           # rad/s
PAUSE_BETWEEN_SPINS = 1.5           # s
PHASE1_ANGLE        = math.pi / 2   # 90°
PHASE2_ANGLE        = math.pi       # 180°
PHASE1_REPS         = 4
PHASE2_REPS         = 2
CONVERGENCE_THRESHOLD = 0.1

# HMI debounce window (seconds)
DEBOUNCE_SEC = 2.0

# Heartbeat interval (seconds)
HEARTBEAT_SEC = 10.0

# State machine tick interval (seconds)
STATE_MACHINE_PERIOD = 0.1

# /set_initial_pose service timeout (seconds)
AMCL_SERVICE_TIMEOUT = 30.0

# ──────────────────────────────────────────────────────────────────────────────


class OrchestratorNode(Node):

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__('orchestrator_node')

        # ── State machine ──────────────────────────────────────────────────
        self._state = 'WAITING_FOR_LOCALIZATION'
        self._fault_message = ''
        self._fault_logged = False

        # ── Heartbeat trackers ─────────────────────────────────────────────
        self._last_heartbeat = self.get_clock().now()

        # ── HMI debounce timestamps ────────────────────────────────────────
        self._last_cmd_localize_time   = None
        self._last_cmd_navigate_time   = None
        self._last_cmd_return_home_time = None

        # ── AMCL covariance ────────────────────────────────────────────────
        self.latest_covariance_xx = float('inf')
        self.latest_covariance_yy = float('inf')

        # ── Localization flags ────────────────────────────────────────────
        self._localizing_started = False

        # ── Waypoint navigation state ─────────────────────────────────────
        self._waypoints = []
        self._waypoint_index = 0
        self._nav_state   = 'idle'   # idle | waiting | navigating | done
        self._nav_success = False
        self._nav_error_code = 0
        self._nav_goal_handle = None

        # ── Return-home navigation state ──────────────────────────────────
        self.home_x = HOME_X
        self.home_y = HOME_Y
        self.home_yaw = HOME_YAW
        self._home_nav_state   = 'idle'
        self._home_nav_success = False
        self._home_nav_error_code = 0
        self._home_nav_goal_handle = None

        # ── Feedback throttle ─────────────────────────────────────────────
        # Only log distance_remaining every 5th Nav2 feedback callback (~1 Hz)
        # to prevent /rosout flooding which causes Auto.html lag.
        self._feedback_log_counter = 0
        self._home_feedback_log_counter = 0

        # ── ROS interfaces ────────────────────────────────────────────────

        # AMCL service client
        self._set_pose_client = self.create_client(SetInitialPose, '/set_initial_pose')

        # Velocity publisher — routes to /cmd_vel_estop (priority 255 in twist_mux).
        # This channel is used for the FAULT E-stop halt. Publishing continuously while
        # in FAULT guarantees twist_mux always picks this over Nav2's /cmd_vel_nav.
        self._cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel_estop', 10)
        
        # Navigation Velocity Publisher - used to explicitly halt the robot on goal completion
        self._cmd_vel_nav_pub = self.create_publisher(Twist, '/cmd_vel_nav', 10)

        # State publisher — publishes the current state string at 10 Hz.
        # Auto.html subscribes here instead of parsing /rosout, giving real-time
        # state feedback with no log pipeline delay.
        self._state_pub = self.create_publisher(String, '/amr/state', 10)

        # AMCL pose subscriber
        self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._amcl_callback,
            10
        )

        # HMI subscribers
        self.create_subscription(Bool, '/amr/cmd_localize',    self._cmd_localize_cb,    10)
        self.create_subscription(Bool, '/amr/cmd_navigate',    self._cmd_navigate_cb,    10)
        self.create_subscription(Bool, '/amr/cmd_return_home', self._cmd_return_home_cb, 10)
        self.create_subscription(Bool, '/amr/cmd_estop',       self._cmd_estop_cb,       10)
        self.create_subscription(Bool, '/amr/cmd_recover',     self._cmd_recover_cb,     10)

        # Nav2 action client (shared for both waypoint and return-home navigation)
        self._nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # ── Load waypoints ────────────────────────────────────────────────
        self.declare_parameter('waypoints_file', '')
        waypoints_file = self.get_parameter('waypoints_file').get_parameter_value().string_value

        if not waypoints_file:
            try:
                from ament_index_python.packages import get_package_share_directory
                waypoints_file = os.path.join(
                    get_package_share_directory('amr_ws'),
                    'waypoints', 'waypoints.yaml'
                )
            except ImportError:
                self.get_logger().error("ament_index_python not found. Please provide 'waypoints_file' parameter.")

        self._load_waypoints(waypoints_file)

        # ── State machine timer ───────────────────────────────────────────
        self.create_timer(STATE_MACHINE_PERIOD, self._run_state_machine)

        self.get_logger().info('Orchestrator node started. State: WAITING_FOR_LOCALIZATION')

    # ── AMCL Callback ─────────────────────────────────────────────────────────

    def _amcl_callback(self, msg: PoseWithCovarianceStamped):
        self.latest_covariance_xx = msg.pose.covariance[0]
        self.latest_covariance_yy = msg.pose.covariance[7]

    # ── Waypoint Loading ──────────────────────────────────────────────────────

    def _load_waypoints(self, path: str):
        """Load and validate waypoints from YAML. Transition to FAULT on any error."""
        if not os.path.isfile(path):
            self._enter_fault(f'STARTUP — waypoints.yaml not found at: {path}')
            return

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self._enter_fault(f'STARTUP — failed to parse waypoints.yaml: {e}')
            return

        if not isinstance(data, dict) or 'waypoints' not in data:
            self._enter_fault("STARTUP — waypoints.yaml missing 'waypoints' key")
            return

        raw = data['waypoints']
        if not raw:
            self._enter_fault('STARTUP — waypoints list is empty')
            return

        waypoints = []
        for i, wp in enumerate(raw):
            for field in ('name', 'x', 'y', 'yaw'):
                if field not in wp:
                    self._enter_fault(
                        f"STARTUP — waypoint {i + 1} missing required field: '{field}'"
                    )
                    return
            waypoints.append(wp)

        self._waypoints = waypoints
        
        # Dynamically assign Point A to be the Home location mapping
        self.home_x = float(waypoints[0]['x'])
        self.home_y = float(waypoints[0]['y'])
        self.home_yaw = float(waypoints[0]['yaw'])
        
        self.get_logger().info(f'Loaded {len(self._waypoints)} waypoint(s) from {path}')
        self.get_logger().info(f'Point A (Home) mapped dynamically to: {waypoints[0]["name"]}')
        self.get_logger().info(f'Point B (Final Goal) mapped dynamically to: {waypoints[-1]["name"]}')

    # ── HMI Callbacks ─────────────────────────────────────────────────────────

    def _debounce_ok(self, last_time_attr: str) -> bool:
        """Return True if enough time has passed since the last command press."""
        now = self.get_clock().now()
        last = getattr(self, last_time_attr)
        if last is not None:
            elapsed = (now - last).nanoseconds * 1e-9
            if elapsed < DEBOUNCE_SEC:
                self.get_logger().warn(
                    f'Debounce: ignoring repeated command (elapsed {elapsed:.2f}s < {DEBOUNCE_SEC}s)'
                )
                return False
        setattr(self, last_time_attr, now)
        return True

    def _cmd_localize_cb(self, msg: Bool):
        if not msg.data:
            return
        if not self._debounce_ok('_last_cmd_localize_time'):
            return
        if self._state != 'WAITING_FOR_LOCALIZATION':
            self.get_logger().warn(
                f'cmd_localize ignored — current state is {self._state}, '
                'must be WAITING_FOR_LOCALIZATION'
            )
            return
        self.get_logger().info('cmd_localize received. Transitioning to LOCALIZING.')
        self._state = 'LOCALIZING'

    def _cmd_navigate_cb(self, msg: Bool):
        if not msg.data:
            return
        if not self._debounce_ok('_last_cmd_navigate_time'):
            return
        if self._state != 'IDLE':
            self.get_logger().warn(
                f'cmd_navigate ignored — current state is {self._state}, must be IDLE'
            )
            return
        self.get_logger().info('cmd_navigate received. Transitioning to NAVIGATING.')
        self._waypoint_index = 0
        self._nav_state = 'idle'
        self._state = 'NAVIGATING'

    def _cmd_return_home_cb(self, msg: Bool):
        if not msg.data:
            return
        if not self._debounce_ok('_last_cmd_return_home_time'):
            return
        if self._state != 'IDLE':
            self.get_logger().warn(
                f'cmd_return_home ignored — current state is {self._state}, must be IDLE'
            )
            return
        self.get_logger().info('cmd_return_home received. Transitioning to RETURNING_HOME.')
        self._home_nav_state = 'idle'
        self._state = 'RETURNING_HOME'

    def _cmd_estop_cb(self, msg: Bool):
        if not msg.data:
            return
            
        self.get_logger().error('E-STOP received from HMI! Halting robot immediately.')
        
        # Preemptively cancel any running Nav2 goals if we were moving
        if self._state == 'NAVIGATING' and self._nav_goal_handle:
            self.get_logger().warn('Cancelling active waypoint navigation goal.')
            self._nav_goal_handle.cancel_goal_async()
            
        if self._state == 'RETURNING_HOME' and self._home_nav_goal_handle:
            self.get_logger().warn('Cancelling active home navigation goal.')
            self._home_nav_goal_handle.cancel_goal_async()
            
        # Enter FAULT state (this internally publishes Twist() zero velocity to halt)
        self._enter_fault('E-STOP PRESSED ON DASHBOARD')

    def _cmd_recover_cb(self, msg: Bool):
        if not msg.data:
            return
        if self._state != 'FAULT':
            self.get_logger().warn(f'cmd_recover ignored — current state is {self._state}, must be FAULT')
            return

        self.get_logger().info('cmd_recover received! Transitioning out of FAULT to IDLE.')

        # Publish one definitive zero-velocity command before leaving FAULT.
        # This clears /cmd_vel_estop so twist_mux stops forwarding the E-stop
        # channel and any residual motion from ghost recovery actions is halted.
        self._cmd_vel_pub.publish(Twist())

        self._fault_message = ''
        self._fault_logged = False
        self._state = 'IDLE'
        self._last_heartbeat = self.get_clock().now()

    # ── State Machine Dispatcher ──────────────────────────────────────────────

    def _run_state_machine(self):
        state = self._state

        # Publish current state at 10 Hz so Auto.html can update without /rosout lag
        self._state_pub.publish(String(data=state))

        if state == 'WAITING_FOR_LOCALIZATION':
            self._handle_waiting_for_localization()
        elif state == 'LOCALIZING':
            self._handle_localizing()
        elif state == 'IDLE':
            self._handle_idle()
        elif state == 'NAVIGATING':
            self._handle_navigating()
        elif state == 'RETURNING_HOME':
            self._handle_returning_home()
        elif state == 'FAULT':
            self._handle_fault()

    # ── WAITING_FOR_LOCALIZATION ──────────────────────────────────────────────

    def _handle_waiting_for_localization(self):
        # Auto-detect if AMCL is already converged (e.g. if you ran localization_node manually)
        if self.latest_covariance_xx < CONVERGENCE_THRESHOLD and self.latest_covariance_yy < CONVERGENCE_THRESHOLD:
            self.get_logger().info('AMCL already converged. Bypassing localization.')
            self._state = 'IDLE'
            self._last_heartbeat = self.get_clock().now()
            return

        now = self.get_clock().now()
        elapsed = (now - self._last_heartbeat).nanoseconds * 1e-9
        if elapsed >= HEARTBEAT_SEC:
            self.get_logger().info('Orchestrator ready. Waiting for localization command.')
            self._last_heartbeat = now

    # ── IDLE ──────────────────────────────────────────────────────────────────

    def _handle_idle(self):
        now = self.get_clock().now()
        elapsed = (now - self._last_heartbeat).nanoseconds * 1e-9
        if elapsed >= HEARTBEAT_SEC:
            self.get_logger().info('Orchestrator idle. Awaiting command.')
            self._last_heartbeat = now

    # ── LOCALIZING ────────────────────────────────────────────────────────────

    def _handle_localizing(self):
        """
        Launches the external standalone localization_node.py which correctly
        handles its own execution thread, avoiding the timer callback RuntimeError.
        Once launched, we revert to WAITING_FOR_LOCALIZATION which will auto-detect
        when the external node successfully reduces the AMCL covariance.
        """
        import subprocess

        self.get_logger().info('Launching external localization node...')
        try:
            subprocess.Popen(['ros2', 'run', 'amr_ws', 'localization_node'])
        except Exception as e:
            self._enter_fault(f'LOCALIZING — Failed to launch localization_node: {e}')
            return

        # Revert back to waiting state so the auto-detect logic can 
        # seamlessly transition to IDLE once AMCL converges.
        self._state = 'WAITING_FOR_LOCALIZATION'

    # ── NAVIGATING ────────────────────────────────────────────────────────────

    def _handle_navigating(self):
        if self._nav_state == 'idle':
            wp = self._waypoints[self._waypoint_index]
            self.get_logger().info(
                f"Navigating to waypoint: {wp['name']} "
                f"(x={wp['x']}, y={wp['y']}, yaw={wp['yaw']})"
            )
            self._send_nav_goal(wp)
            self._nav_state = 'waiting'

        elif self._nav_state in ('waiting', 'navigating'):
            pass  # waiting for Nav2 callbacks

        elif self._nav_state == 'done':
            wp = self._waypoints[self._waypoint_index]
            if self._nav_success:
                self.get_logger().info(f"Reached waypoint: {wp['name']}")
                self._waypoint_index += 1

                if self._waypoint_index < len(self._waypoints):
                    # Intermediate waypoint — continue to the next one
                    self._nav_state = 'idle'
                else:
                    # Final waypoint reached — mission complete
                    self.get_logger().info('All waypoints complete. Mission success.')
                    self._handle_waypoint_arrival(wp)
                    self._waypoint_index = 0
                    self._nav_state = 'idle'
                    self._last_heartbeat = self.get_clock().now()
                    self._state = 'IDLE'
            else:
                self._enter_fault(
                    f"NAVIGATING — Navigation failed for waypoint: {wp['name']} "
                    f'(error code: {self._nav_error_code})'
                )

    # ── RETURNING_HOME ────────────────────────────────────────────────────────

    def _handle_returning_home(self):
        if self._home_nav_state == 'idle':
            self.get_logger().info(
                f'Returning home (Point A): x={self.home_x}, y={self.home_y}, yaw={self.home_yaw}'
            )
            self._send_home_nav_goal()
            self._home_nav_state = 'waiting'

        elif self._home_nav_state in ('waiting', 'navigating'):
            pass  # waiting for Nav2 callbacks

        elif self._home_nav_state == 'done':
            if self._home_nav_success:
                self.get_logger().info('✓ Robot has successfully returned home.')
                self._home_nav_state = 'idle'
                self._last_heartbeat = self.get_clock().now()
                self._state = 'IDLE'
            else:
                self._enter_fault(
                    f'RETURNING_HOME — Navigation failed (error code: {self._home_nav_error_code})'
                )

    # ── FAULT ─────────────────────────────────────────────────────────────────

    def _handle_fault(self):
        # Log the fault reason exactly once
        if not self._fault_logged:
            self.get_logger().error(f'FAULT — {self._fault_message}')
            self._fault_logged = True

        # Continuously publish zero velocity every state machine tick (0.1s).
        # This keeps /cmd_vel_estop active in twist_mux so it wins over Nav2's
        # /cmd_vel_nav for the entire duration of the E-stop, preventing any
        # residual Nav2 velocity from jerking the robot.
        self._cmd_vel_pub.publish(Twist())

    def _enter_fault(self, reason: str):
        self._fault_message = reason
        self._fault_logged = False
        self._state = 'FAULT'

    # ── Localization Helpers ──────────────────────────────────────────────────

    def _set_initial_pose(self):
        """Send the known starting pose to AMCL via the /set_initial_pose service."""
        request = SetInitialPose.Request()
        request.pose.header.frame_id = 'map'
        request.pose.header.stamp = self.get_clock().now().to_msg()

        request.pose.pose.pose.position.x = self.home_x
        request.pose.pose.pose.position.y = self.home_y
        request.pose.pose.pose.position.z = 0.0

        request.pose.pose.pose.orientation.x = 0.0
        request.pose.pose.pose.orientation.y = 0.0
        request.pose.pose.pose.orientation.z = math.sin(self.home_yaw / 2.0)
        request.pose.pose.pose.orientation.w = math.cos(self.home_yaw / 2.0)

        request.pose.pose.covariance = INITIAL_COVARIANCE

        future = self._set_pose_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(
                f'Initial pose set: x={self.home_x}, y={self.home_y}, yaw={self.home_yaw}'
            )
        else:
            self.get_logger().error('Failed to call /set_initial_pose service.')

    def _spin_robot(self, angle_rad: float, label: str):
        """Spin the robot by the given angle using time-based velocity control."""
        duration = abs(angle_rad) / SPIN_ANGULAR_VEL
        direction = 1.0 if angle_rad > 0 else -1.0

        twist = Twist()
        twist.angular.z = direction * SPIN_ANGULAR_VEL

        self.get_logger().info(
            f'Spinning {label} ({math.degrees(abs(angle_rad)):.0f}°)...'
        )

        start = time.time()
        while time.time() - start < duration:
            self._cmd_vel_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.05)

        # Stop
        self._cmd_vel_pub.publish(Twist())
        time.sleep(0.2)

    def _is_converged(self) -> bool:
        """Flush pending AMCL messages and check covariance convergence."""
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)

        xx = self.latest_covariance_xx
        yy = self.latest_covariance_yy
        self.get_logger().info(f'AMCL covariance — xx: {xx:.4f}, yy: {yy:.4f}')
        return xx < CONVERGENCE_THRESHOLD and yy < CONVERGENCE_THRESHOLD

    # ── Nav2 Goal Helpers ─────────────────────────────────────────────────────

    def _build_pose_stamped(self, x: float, y: float, yaw: float, tolerances: dict = None) -> NavigateToPose.Goal:
        """Build a NavigateToPose goal from x, y, yaw (and optional tolerances)."""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        # Apply per-waypoint tolerances if provided (behaviour_tree_filepath is
        # intentionally left blank to use default BT; goal checking tolerances
        # are not part of the NavigateToPose goal message in Jazzy — they are
        # configured via nav2_params; this block is reserved for future use)

        return goal_msg

    def _send_nav_goal(self, wp: dict):
        """Send a NavigateToPose goal for a waypoint. Uses waypoint-level callbacks."""
        tolerances = {
            k: wp[k] for k in ('xy_tolerance', 'yaw_tolerance') if k in wp
        }
        goal_msg = self._build_pose_stamped(wp['x'], wp['y'], wp['yaw'], tolerances)
        self._nav_action_client.wait_for_server()
        send_future = self._nav_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback
        )
        send_future.add_done_callback(self._goal_response_callback)

    def _send_home_nav_goal(self):
        """Send a NavigateToPose goal for the home pose (Point A). Uses home-level callbacks."""
        goal_msg = self._build_pose_stamped(self.home_x, self.home_y, self.home_yaw)
        self._nav_action_client.wait_for_server()
        send_future = self._nav_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._home_feedback_callback
        )
        send_future.add_done_callback(self._home_goal_response_callback)

    # ── Waypoint Nav2 Callbacks ───────────────────────────────────────────────

    def _goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            wp = self._waypoints[self._waypoint_index]
            self._enter_fault(
                f"NAVIGATING — Nav2 rejected goal for waypoint: {wp['name']}"
            )
            return
        self._nav_goal_handle = goal_handle
        self._nav_state = 'navigating'
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _feedback_callback(self, feedback_msg):
        self._feedback_log_counter += 1
        if self._feedback_log_counter % 20 != 0:
            return  # throttle: only log every 20th callback to reduce /rosout flood
        wp = self._waypoints[self._waypoint_index]
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f"Navigating to {wp['name']} — distance remaining: {distance:.2f} m"
        )

    def _result_callback(self, future):
        result = future.result()
        # GoalStatus.STATUS_SUCCEEDED == 4
        self._nav_success = (result.status == 4)
        self._nav_error_code = getattr(result.result, 'error_code', result.status)
        self._nav_state = 'done'
        
        # Explicit zero-velocity command to halt the robot immediately and prevent spinning
        self._cmd_vel_nav_pub.publish(Twist())

    # ── Return-Home Nav2 Callbacks ────────────────────────────────────────────

    def _home_goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self._enter_fault('RETURNING_HOME — Nav2 rejected home goal')
            return
        self._home_nav_goal_handle = goal_handle
        self._home_nav_state = 'navigating'
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._home_result_callback)

    def _home_feedback_callback(self, feedback_msg):
        self._home_feedback_log_counter += 1
        if self._home_feedback_log_counter % 20 != 0:
            return  # throttle: only log every 20th callback
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'Returning home — distance remaining: {distance:.2f} m')

    def _home_result_callback(self, future):
        result = future.result()
        self._home_nav_success = (result.status == 4)
        self._home_nav_error_code = getattr(result.result, 'error_code', result.status)
        self._home_nav_state = 'done'

        # Explicit zero-velocity command to halt the robot immediately and prevent spinning
        self._cmd_vel_nav_pub.publish(Twist())

    # ── Hooks (placeholders) ──────────────────────────────────────────────────

    def _should_return_home(self) -> bool:
        """
        Placeholder — always False for now.
        Future: check /battery_low topic or loop counter.
        """
        return False

    def _handle_waypoint_arrival(self, waypoint: dict):
        """
        Placeholder — loading/unloading logic goes here.
        e.g. publish to /amr/cmd_load or wait for /amr/load_complete.
        """
        pass


# ── Entry Point ────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = OrchestratorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
