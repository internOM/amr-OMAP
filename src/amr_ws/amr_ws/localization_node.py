#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav2_msgs.srv import SetInitialPose
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
import time
import math


# ─── Configuration ────────────────────────────────────────────────────────────

# Approximate starting position (from your AMCL pose reading)
INITIAL_X   = -0.427
INITIAL_Y   =  0.025
INITIAL_YAW = -0.483

# Large covariance — tells AMCL "I'm roughly here but not exact"
# Only the diagonal values matter:
#   index [0]  = x variance
#   index [7]  = y variance
#   index [35] = yaw variance
INITIAL_COVARIANCE = [
    0.5,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.5, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
    0.0,  0.0, 0.0, 0.0, 0.0, 0.5,
]

# Spin speeds and timing
SPIN_ANGULAR_VEL    = 0.3           # rad/s — slow spin for reliable scan matching
PAUSE_BETWEEN_SPINS = 1.5           # seconds pause between each rotation
PHASE1_ANGLE        = math.pi / 2   # 90 degrees in radians
PHASE2_ANGLE        = math.pi       # 180 degrees in radians
PHASE1_REPS         = 4
PHASE2_REPS         = 2

# AMCL convergence threshold
# When covariance xx AND yy drop below this, AMCL is considered converged
CONVERGENCE_THRESHOLD = 0.1

# ──────────────────────────────────────────────────────────────────────────────


class LocalizationNode(Node):

    def __init__(self):
        super().__init__('localization_node')

        # Service client for setting initial pose — bypasses QoS topic issues
        self.set_pose_client = self.create_client(
            SetInitialPose,
            '/set_initial_pose'
        )

        # Publisher for velocity commands (spinning)
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Subscriber to monitor AMCL covariance after pose is set
        self.amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        # Internal state
        self.latest_covariance_xx = float('inf')
        self.latest_covariance_yy = float('inf')

        self.get_logger().info('Localization node started.')

        # Run the full localization sequence
        self.run_localization()

    # ── AMCL Callback ─────────────────────────────────────────────────────────

    def amcl_callback(self, msg):
        """Store latest AMCL covariance values."""
        self.latest_covariance_xx = msg.pose.covariance[0]   # x variance
        self.latest_covariance_yy = msg.pose.covariance[7]   # y variance

    # ── Wait for AMCL Service ─────────────────────────────────────────────────

    def wait_for_amcl(self):
        """Wait until the /set_initial_pose service is available."""
        self.get_logger().info('Waiting for AMCL /set_initial_pose service...')
        while not self.set_pose_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not ready yet...')
        self.get_logger().info('AMCL service is ready.')

    # ── Set Initial Pose via Service ──────────────────────────────────────────

    def set_initial_pose(self):
        """Call /set_initial_pose service to initialize AMCL particles."""
        request = SetInitialPose.Request()

        request.pose.header.frame_id = 'map'
        request.pose.header.stamp = self.get_clock().now().to_msg()

        # Position
        request.pose.pose.pose.position.x = INITIAL_X
        request.pose.pose.pose.position.y = INITIAL_Y
        request.pose.pose.pose.position.z = 0.0

        # Orientation — convert yaw to quaternion
        request.pose.pose.pose.orientation.x = 0.0
        request.pose.pose.pose.orientation.y = 0.0
        request.pose.pose.pose.orientation.z = math.sin(INITIAL_YAW / 2.0)
        request.pose.pose.pose.orientation.w = math.cos(INITIAL_YAW / 2.0)

        # Large covariance
        request.pose.pose.covariance = INITIAL_COVARIANCE

        # Call the service synchronously
        future = self.set_pose_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(
                f'Initial pose set via service: x={INITIAL_X}, y={INITIAL_Y}, yaw={INITIAL_YAW}'
            )
        else:
            self.get_logger().error('Failed to call /set_initial_pose service.')

    # ── Spin Robot ────────────────────────────────────────────────────────────

    def spin_robot(self, angle_rad, label):
        """
        Spin the robot by a given angle in radians.
        Uses time-based control: duration = angle / angular_vel.
        """
        duration = abs(angle_rad) / SPIN_ANGULAR_VEL
        direction = 1.0 if angle_rad > 0 else -1.0

        twist = Twist()
        twist.angular.z = direction * SPIN_ANGULAR_VEL

        self.get_logger().info(f'Spinning {label} ({math.degrees(abs(angle_rad)):.0f} deg)...')

        start_time = time.time()
        while time.time() - start_time < duration:
            self.cmd_vel_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.05)

        # Stop the robot
        self.stop_robot()

    def stop_robot(self):
        """Publish zero velocity to stop the robot."""
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        time.sleep(0.2)

    # ── Check Convergence ─────────────────────────────────────────────────────

    def is_converged(self):
        """Check if AMCL covariance is below the convergence threshold."""
        # Flush latest AMCL messages into callback
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)

        xx = self.latest_covariance_xx
        yy = self.latest_covariance_yy
        self.get_logger().info(f'AMCL covariance — xx: {xx:.4f}, yy: {yy:.4f}')
        return xx < CONVERGENCE_THRESHOLD and yy < CONVERGENCE_THRESHOLD

    # ── Main Localization Sequence ────────────────────────────────────────────

    def run_localization(self):
        """Full localization sequence."""

        # Step 1: Wait for AMCL service to be available
        self.wait_for_amcl()

        # Step 2: Set initial pose via service — guaranteed delivery, no QoS issues
        self.set_initial_pose()

        # Step 3: Wait for AMCL to spread its particles
        self.get_logger().info('Waiting for AMCL to initialize particles...')
        time.sleep(2.0)

        # Step 4: Phase 1 — 4 x 90 degree spins
        self.get_logger().info('=== Phase 1: 4 x 90 degree spins ===')
        for i in range(PHASE1_REPS):
            self.spin_robot(PHASE1_ANGLE, f'90 deg spin {i+1}/{PHASE1_REPS}')
            time.sleep(PAUSE_BETWEEN_SPINS)

        # Step 5: Check convergence after Phase 1
        if self.is_converged():
            self.get_logger().info('✓ Localization converged after Phase 1. Robot is localized.')
            return

        self.get_logger().warn('Phase 1 did not converge. Starting Phase 2...')

        # Step 6: Phase 2 — 2 x 180 degree spins
        self.get_logger().info('=== Phase 2: 2 x 180 degree spins ===')
        for i in range(PHASE2_REPS):
            self.spin_robot(PHASE2_ANGLE, f'180 deg spin {i+1}/{PHASE2_REPS}')
            time.sleep(PAUSE_BETWEEN_SPINS)

        # Step 7: Final convergence check
        if self.is_converged():
            self.get_logger().info('✓ Localization converged after Phase 2. Robot is localized.')
        else:
            self.get_logger().error(
                '✗ Localization did not converge after both phases. '
                'Please manually set pose in RViz or move robot to a more distinctive area.'
            )


# ── Entry Point ───────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = LocalizationNode()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()