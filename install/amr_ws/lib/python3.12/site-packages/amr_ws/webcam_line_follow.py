#-----WARNING-----------------------------------------
#This code was first written by an Intern, which has been projected to be passed down to interns after interns

#When I first wrote this code, only God and me knew how this worked.
#Now, only God knows how this code works.

#This code works to a certain extent, and if you add features, be wary of the hours you will have to spend debugging.
#Always remember to push to GitHub to save your progress. 

#Hours spent debugging: 120
#First Intern: Tan Dong Xu
#Second Intern: Tang Wei Lun
#-----WARNING-----------------------------------------

#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

# ── LiDAR tiered safety zones ────────────────────────────────────────────────
# Each entry is (max_distance_m, half_cone_deg).
# A beam triggers an obstacle stop when BOTH conditions are met:
#   • its distance ≤ max_distance_m   AND
#   • its angle from forward is within ±half_cone_deg
# Zones are checked from the narrowest (closest) outward so the first
# matching zone wins — keeps the logic O(zones) not O(zones²).
#
#  Zone │ Distance band │ Cone (total)
#  ─────┼───────────────┼────────────
#    1  │   0 – 0.15 m  │   45°  (±22.5°)
#    2  │ 0.15 – 0.25 m │   60°  (±30°)
#    3  │ 0.25 – 0.50 m │   90°  (±45°)
#    4  │ 0.50 – 0.75 m │  120°  (±60°)
SAFETY_TIERS = [
    (0.225, 90.0),    # zone 1: very close  → narrow  90.0° cone
    (0.3182, 45.0),   # zone 2: close       → narrow  45.0° cone
    (0.45, 30.0),     # zone 3: medium      → medium  30.0° cone
]

# ── Obstacle debounce & slew-rate constants ────────────────────────────────────
# Number of consecutive obstacle-free scan frames required before the robot is
# allowed to resume.  Prevents jitter / false-clear transients.
OBSTACLE_CLEAR_DEBOUNCE = 20   # frames

# Slew-rate limiter: how much linear.x can increase per image frame once the
# robot resumes after an obstacle clear.  Target cruise speed = 0.25 m/s.
# At ~10 Hz image rate this gives ≈ 2.5 s to reach cruise speed.
LINEAR_SLEW_RATE = 0.01        # m/s per frame


class WebcamLineFollow(Node):
    def __init__(self):
        super().__init__('webcam_line_follow')

        self.bridge = CvBridge()

        # ── Subscriptions ──────────────────────────────────────────────
        self.create_subscription(Image, '/image_raw', self.image_callback, 1)

        # LiDAR safety sensor
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # UI control topics
        self.create_subscription(Bool,   '/agv/cmd_enable', self.enable_callback, 10)
        self.create_subscription(Bool,   '/agv/cmd_stop',   self.stop_callback,   10)
        self.create_subscription(String, '/agv/cmd_mode',   self.mode_callback,   10)

        # Rack sensor status — published by rack_websocket_server.py
        # Format: "rack_id:status:distance_cm"  (status 1=FULL, 0=EMPTY)
        self.create_subscription(String, '/rack_status', self.rack_status_callback, 10)

        # Ping Echo
        self.create_subscription(String, '/ui_heartbeat', self.heartbeat_callback, 10)

        # ── Publishers ─────────────────────────────────────────────────
        # twist_mux picks this up at priority 10 (same slot as Nav2)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel_agv', 10)

        # State feedback → UI
        self.state_pub = self.create_publisher(String, '/agv/state', 10)

        # Mode feedback → UI  (UI subscribes to keep its button in sync)
        self.mode_pub = self.create_publisher(String, '/agv/mode', 10)

        # Ping Echo pub
        self.heartbeat_pub = self.create_publisher(String, '/ui_heartbeat', 10)

        # ── Follow mode ────────────────────────────────────────────────
        # "green" → always follow green tape
        # "red"   → follow green, but at an intersection divert onto red if
        #           a qualifying red line is visible straight ahead in the
        #           bottom strip of the camera.
        self.follow_mode = "green"

        # Tracks whether we are currently homing onto (following) a red line
        self.following_red = False

        # ── Internal enable gate ───────────────────────────────────────
        # Node starts disabled; GO button on the UI enables it.
        self.enabled = False

        # ── Obstacle detection state ───────────────────────────────────
        # Set True when LiDAR detects something within OBSTACLE_DISTANCE_M
        # in the forward 180° safety cone.  The robot halts but audio keeps
        # playing.  Normal operation resumes once debounce frames pass.
        self.obstacle_detected = False

        # Debounce counter: incremented each scan frame that is obstacle-free.
        # The obstacle flag is only cleared once this reaches OBSTACLE_CLEAR_DEBOUNCE.
        self._clear_frame_count = 0

        # Wait timer for resuming after an obstacle is cleared
        self.resume_time = 0.0

        # Slew-rate limiter: current commanded linear speed.  Reset to 0.0
        # whenever an obstacle is detected so the robot ramps up smoothly
        # on resume instead of jumping straight to cruise speed.
        self._current_linear_x = 0.0

        # ── U-turn detection thresholds ────────────────────────────────
        self.EXPLOSION_THRESHOLD     = 1350000  # green strip sum → green U-turn
        self.RED_EXPLOSION_PX        = 900000  # red strip pixels → red U-turn
        self.u_turning               = False
        self.u_turn_start_time       = None
        self.U_TURN_MIN_TIME         = 2.0      # seconds before checking for line again

        # Debounce for "red line lost": number of consecutive frames with
        # red_strip_px < threshold before reverting to green.
        self._red_lost_frames = 0
        self.RED_LOST_DEBOUNCE = 5   # ~0.8 s at 10 Hz image rate

        # ── PD controller ──────────────────────────────────────────────
        self.Kp = 0.0032
        self.Kd = 0.00072
        self.last_err = 0
        self.last_time = None
        self.MAX_ANG_Z = 1.0
        self.MIN_ANG_Z_DEADZONE = 0.05

        # Issue 4: timestamp of the last per-frame info log (throttled to 1 Hz)
        self._last_log_time = 0.0

        # ── Docking Protocol State ─────────────────────────────────────
        self.docking_type = 0
        self.docking_phase = 0
        self.docking_timer = 0.0
        self.pending_docking_type = 0

        # ── Rack sensor state (12 ultrasonic slots) ───────────────────
        self.rack_states = {
            "Store-A1": 0, "Store-A2": 0, "Store-A3": 0,
            "Store-B1": 0, "Store-B2": 0, "Store-B3": 0,
            "CAPP-A1": 0, "CAPP-A2": 0, "CAPP-A3": 0,
            "CAPP-B1": 0, "CAPP-B2": 0, "CAPP-B3": 0,
        }
        self.waiting_operator_confirm = False
        self.waiting_capp_full_d1 = False    # True when aligned at D1 but CA-PP is all full
        self.waiting_store_empty_d2 = False  # True when aligned at D2 but Store is all empty

        # Cooldown after any docking completes — suppresses explosion re-trigger
        # while the AGV is still physically inside the docking zone.
        self.post_docking_cooldown_until = 0.0

        # Tracks which leg of the journey the AGV is on: "to_store" or "to_capp"
        # This determines which set of sensors controls the lane selection.
        self.agv_direction = "to_store"

        self.twist = Twist()

        self.get_logger().info("Webcam Line Follow node started — waiting for /agv/cmd_enable")

        # Broadcast state + mode at 1 Hz so UI always reflects node truth
        self.current_state = "WAITING"
        self.state_timer = self.create_timer(1.0, self.timer_state_callback)
        self._publish_state(self.current_state)
        self._publish_mode(self.follow_mode)

    # ── LiDAR safety callback ──────────────────────────────────────────────────

    def scan_callback(self, msg: LaserScan):
        # ── Override: Ignore obstacles during Docking and U-Turns ──────────────────────
        if self.docking_type in (1, 2) or self.u_turning:
            if self.obstacle_detected:
                self.obstacle_detected = False
                self._clear_frame_count = 0
                self.resume_time = 0.0
            return

       
        # Pre-compute half-cone radians for each tier once per callback
        tiers_rad = [(d, math.radians(h)) for d, h in SAFETY_TIERS]
        # Widest cone among all tiers — used as a fast early-reject gate
        max_half_rad = max(h for d, h in tiers_rad)

        ranges = msg.ranges
        n = len(ranges)
        if n == 0:
            return

        inc = msg.angle_increment
        angle_min = msg.angle_min
        range_min = msg.range_min
        range_max = msg.range_max

        obstacle_found = False
        for i, r in enumerate(ranges):
            # Skip invalid / out-of-range readings first (cheap)
            if not math.isfinite(r) or r < range_min or r > range_max:
                continue

            # Fast gate: skip beams outside the widest possible cone
            angle = angle_min + i * inc
            angle = math.atan2(math.sin(angle), math.cos(angle))  # → (-π, π]

            # Forward direction aligns with angle = ±π in our LiDAR frame
            fwd_dist = abs(abs(angle) - math.pi)   # 0 = dead ahead
            if fwd_dist > max_half_rad:
                continue

            # Find the innermost tier that covers this distance
            for max_dist, half_rad in tiers_rad:
                if r <= max_dist:
                    # Beam is within this tier's distance — check cone
                    if fwd_dist <= half_rad:
                        obstacle_found = True
                    break   # tier matched (cone may or may not have fired)

        # ── State transitions ──────────────────────────────────────────
        if obstacle_found:
            # ── Obstacle present ──────────────────────────────────────
            # Reset the clear-frame debounce counter every time we see an obstacle.
            self._clear_frame_count = 0

            if not self.obstacle_detected:
                self.obstacle_detected = True
                # Reset slew speed so resume is always a smooth ramp-up.
                self._current_linear_x = 0.0
                self.get_logger().warn(
                    "OBSTACLE DETECTED (tiered safety zone triggered) — halting robot. "
                    "Waiting for path to clear…"
                )
                # Immediately stop the robot (if we are running)
                if self.enabled:
                    zero = Twist()
                    self.cmd_vel_pub.publish(zero)
                    if self.current_state == "RUNNING":
                        self.current_state = "OBSTACLE_DETECTED"
                        self._publish_state(self.current_state)

        else:
            # ── No obstacle this frame ────────────────────────────────
            if self.obstacle_detected:
                self._clear_frame_count += 1
                if self._clear_frame_count >= OBSTACLE_CLEAR_DEBOUNCE:
                    # Debounce satisfied — path is genuinely clear.
                    self.obstacle_detected = False
                    self._clear_frame_count = 0
                    self.resume_time = time.time() + 3.0
                    self.get_logger().info(
                        f"Path clear ({OBSTACLE_CLEAR_DEBOUNCE} consecutive clear frames) "
                        "— waiting 3 seconds before resuming line following."
                    )
                else:
                    self.get_logger().debug(
                        f"Obstacle clear frame {self._clear_frame_count}/{OBSTACLE_CLEAR_DEBOUNCE} "
                        "— waiting for debounce."
                    )

    # ── Rack status callback ────────────────────────────────────────────────────

    def rack_status_callback(self, msg: String):
        """
        Receive rack occupancy data from the ESP32 ultrasonic sensor bridge.

        Message format (String): "rack_id:status:distance_cm"
          status == 1  → slot occupied
          status == 0  → slot empty

        Updates self.rack_states per slot, then recomputes lane selection
        based on column occupancy truth tables.
        """
        try:
            parts = msg.data.split(':')
            if len(parts) < 2:
                self.get_logger().warn(
                    f"rack_status_callback: unexpected format '{msg.data}' — ignoring."
                )
                return

            rack_id  = parts[0]
            status   = int(parts[1])
            distance = float(parts[2]) if len(parts) > 2 else 0.0

            if rack_id not in self.rack_states:
                self.get_logger().warn(
                    f"rack_status_callback: unknown rack_id '{rack_id}' — ignoring."
                )
                return

            self.rack_states[rack_id] = status
            status_text = "OCCUPIED" if status == 1 else "EMPTY"
            self.get_logger().info(
                f"[Rack {rack_id}] {status_text} (dist={distance:.1f} cm)"
            )

            # ── Recompute column occupancy ─────────────────────────────
            store_A = any(self.rack_states[k] == 1 for k in ["Store-A1", "Store-A2", "Store-A3"])
            store_B = any(self.rack_states[k] == 1 for k in ["Store-B1", "Store-B2", "Store-B3"])
            capp_A  = any(self.rack_states[k] == 1 for k in ["CAPP-A1",  "CAPP-A2",  "CAPP-A3"])
            capp_B  = any(self.rack_states[k] == 1 for k in ["CAPP-B1",  "CAPP-B2",  "CAPP-B3"])

            # ── Direction-based Lane Selection ─────────────────────────
            desired_mode = "green"  # default
            
            if self.agv_direction == "to_store":
                # Store determines the lane (Leg 1)
                if store_A:
                    desired_mode = "green"  # A takes priority
                elif store_B:
                    desired_mode = "red"    # only B has material
                # if both empty, stays green (Docking 1 gate handles the wait)
                
            elif self.agv_direction == "to_capp":
                # CA-PP determines the lane (Leg 2)
                if not capp_A:
                    desired_mode = "green"  # A has space
                elif not capp_B:
                    desired_mode = "red"    # A full, B has space
                # if both full, stays green (Docking 1 gate handles the wait)

            self.get_logger().info(
                f"[Lane logic] dir='{self.agv_direction}' | Store (A:{store_A} B:{store_B}) | "
                f"CAPP (A:{capp_A} B:{capp_B}) → mode='{desired_mode}'"
            )
            
            synthetic = String()
            synthetic.data = desired_mode
            self.mode_callback(synthetic)

        except (ValueError, IndexError) as e:
            self.get_logger().error(
                f"rack_status_callback: failed to parse '{msg.data}': {e}"
            )

    def _rack_stop(self, state: str, reason: str):
        """Stop the AGV due to a rack availability issue."""
        zero = Twist()
        self.cmd_vel_pub.publish(zero)
        self.enabled = False
        self.current_state = state
        self._publish_state(state)
        self.get_logger().warn(f"RACK STOP: {reason}")

    # ── Mode callback ──────────────────────────────────────────────────────────

    def mode_callback(self, msg: String):
        """
        Switch follow mode SEAMLESSLY — motion is never interrupted.

        green mode: follow green continuously, perform green U-turns.
        red   mode: follow green AND divert onto red at intersections;
                    perform red U-turns when on the red segment.

        Toggling can happen at any time while the robot is moving.
        """
        mode = msg.data.lower()
        if mode not in ("green", "red"):
            self.get_logger().warn(f"Unknown follow mode '{msg.data}' — ignoring.")
            return

        if mode == self.follow_mode:
            # Idempotent — same mode republished (e.g. on reconnect). No action needed.
            self._publish_mode(mode)
            return

        old_mode = self.follow_mode
        self.follow_mode = mode

        if mode == "green":
            # ── Red → Green transition ─────────────────────────────────
            # Stop tracking the red line; the robot will naturally fall
            # back onto the green line it was already moving alongside.
            if self.following_red:
                self.following_red = False
                self.get_logger().info(
                    "Mode → green: stopped red tracking — reverting to green follow."
                )
            # Docking 2 and its subsequent U-Turn are red-specific manoeuvres;
            # cancel them so the robot resumes green following without finishing
            # an irrelevant manoeuvre.
            if self.docking_type == 2:
                self.docking_type = 0
                self.docking_phase = 0
                self.current_state = "RUNNING"
                self._publish_state(self.current_state)
                self.get_logger().info("Mode → green: cancelled active Docking 2.")
            elif self.u_turning and self.pending_docking_type == 0:
                self.u_turning = False
                self.u_turn_start_time = None
                self.current_state = "RUNNING"
                self._publish_state(self.current_state)
                self.get_logger().info("Mode → green: cancelled active red U-turn.")
            # NOTE: green U-turn (u_turning with pending_docking_type=1) and PD state
            # are left intact — the robot keeps moving without any jolt.

        else:  # mode == "red"
            # ── Green → Red transition ─────────────────────────────────
            # No state changes needed. Robot continues following green;
            # image_callback will now also watch for red divert triggers.
            self.get_logger().info(
                "Mode → red: now watching for red tape at intersections "
                "(continuing green follow)."
            )

        self._publish_mode(mode)
        self.get_logger().info(f"Follow mode: '{old_mode}' → '{mode}' (motion uninterrupted)")

    # ── Enable / Stop & Ping callbacks ────────────────────────────────────────

    def heartbeat_callback(self, msg: String):
        # Bounce the ping straight back to the UI
        self.heartbeat_pub.publish(msg)

    def enable_callback(self, msg: Bool):
        # ── Operator confirmation for Docking 2 sensor gate ────────────
        if msg.data and self.waiting_operator_confirm:
            self.waiting_operator_confirm = False
            self.docking_phase = 3
            self.docking_timer = time.time()
            self.get_logger().info(
                "Operator confirmed — advancing Docking 2 to Phase 3."
            )
            return

        if msg.data and not self.enabled:
            self.enabled = True
            self.following_red = False
            # If an obstacle is already present, reflect that immediately
            if self.obstacle_detected or time.time() < self.resume_time:
                self.current_state = "OBSTACLE_DETECTED"
            else:
                self.current_state = "RUNNING"
            self.get_logger().info("AGV ENABLED — line following active")
            self._publish_state(self.current_state)

    def stop_callback(self, msg: Bool):
        if msg.data and self.enabled:
            self.enabled = False
            self.current_state = "STOPPED"
            # Publish a zero Twist immediately to halt the robot
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            self.get_logger().info("AGV STOPPED — cmd_vel_agv zeroed")
            self._publish_state(self.current_state)
            # Reset U-turn state so next GO starts clean
            self.u_turning = False
            self.u_turn_start_time = None
            self.last_err = 0
            self.last_time = None
            # Also clear obstacle flag and red-follow state
            self.obstacle_detected = False
            self.resume_time = 0.0
            self.following_red = False
            self._red_lost_frames = 0
            self.docking_type = 0
            self.docking_phase = 0
            self.pending_docking_type = 0
            self.waiting_operator_confirm = False
            self.waiting_capp_full_d1 = False
            self.waiting_store_empty_d2 = False
            self.post_docking_cooldown_until = 0.0
            self.agv_direction = "to_store"

    def _publish_state(self, state: str):
        msg = String()
        msg.data = state
        self.state_pub.publish(msg)

    def _publish_mode(self, mode: str):
        """Broadcast current follow_mode to /agv/mode so the UI stays in sync."""
        msg = String()
        msg.data = mode
        self.mode_pub.publish(msg)

    def timer_state_callback(self):
        """1 Hz heartbeat — keeps UI state and mode button always up to date."""
        self._publish_state(self.current_state)
        self._publish_mode(self.follow_mode)

    # ── Image callback ─────────────────────────────────────────────────────────

    def image_callback(self, msg):
        # Gate 1: do nothing if not enabled
        if not self.enabled:
            return

        # Gate 2: obstacle detected — hold still, let music keep playing
        if self.obstacle_detected:
            self._current_linear_x = 0.0   # ensure slew starts from 0 on resume
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            return

        # Gate 3: 3-second wait after obstacle cleared
        if time.time() < self.resume_time:
            self._current_linear_x = 0.0
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            return
        elif self.current_state == "OBSTACLE_DETECTED":
            # Wait is over, transition back to RUNNING
            self.current_state = "RUNNING"
            self._publish_state(self.current_state)
            self.get_logger().info("Resume wait complete — resuming line following.")

        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        h, w = frame.shape[:2]
        current_time = time.time()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # ── Tracking strip bounds ──────────────────────────────────────────
        search_top = (h // 4) * 3
        search_bot = search_top + 20
        # Issue 3: slice HSV to the 20-row strip BEFORE calling inRange — ~40× fewer
        # pixels to process compared to the full frame.
        hsv_strip = hsv[search_top:search_bot, :]

        # ── Green mask: computed only on the strip slice ───────────────────
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([120, 255, 255])
        mask_green  = cv2.inRange(hsv_strip, lower_green, upper_green)
        green_sum   = int(np.sum(mask_green))

        # ── Red mask: Computed on every frame so explosions trigger regardless of mode
        RED_STRIP_MIN  = 200
        RED_CENTER_TOL = int(w * 0.45)

        lower_red_lo = np.array([  0,  60,  60])
        upper_red_lo = np.array([ 25, 255, 255])
        lower_red_hi = np.array([140,  60,  60])
        upper_red_hi = np.array([180, 255, 255])
        
        mask_red = cv2.bitwise_or(
            cv2.inRange(hsv_strip, lower_red_lo, upper_red_lo),
            cv2.inRange(hsv_strip, lower_red_hi, upper_red_hi)
        )
        red_strip_px  = int(np.sum(mask_red > 0))
        red_strip_sum = int(np.sum(mask_red))

        # ── Red intersection divert check (red mode only) ──────────────────
        # Trigger: red tape appears in the bottom tracking strip alongside
        # (or instead of) green. No "explosion" required — this fires the
        # moment the robot reaches the crossing region.
        if (self.follow_mode == "red"
                and not self.following_red
                and not self.u_turning
                and red_strip_px >= RED_STRIP_MIN):
            Mr = cv2.moments(mask_red)
            if Mr['m00'] > 0:
                cx_red = int(Mr['m10'] / Mr['m00'])
                if abs(cx_red - w // 2) <= RED_CENTER_TOL:
                    self.following_red = True
                    self.get_logger().info(
                        f"Red tape in strip (px={red_strip_px}, cx={cx_red}) "
                        "— diverting to red line."
                    )
            # Throttled 1-Hz info log so we can see strip values without spam
            if current_time - self._last_log_time >= 1.0:
                self.get_logger().info(
                    f"[RedMode divert check] red_strip_px={red_strip_px}, "
                    f"green_sum={green_sum}, follow_mode={self.follow_mode}, "
                    f"following_red={self.following_red}"
                )

        # ── Choose active tracking mask ────────────────────────────────────
        if self.following_red:
            # Once on red, track it in the bottom strip
            mask = mask_red
            mask_sum = int(np.sum(mask))
            # If red disappears (end of red tape), fall back to green.
            # Use a debounce counter so a single low-pixel frame doesn't abort
            # red following — the AGV may briefly lose the line while steering.
            if self.docking_type != 0 or self.u_turning:
                self._red_lost_frames = 0
            elif red_strip_px < 200:
                self._red_lost_frames += 1
                if self._red_lost_frames >= self.RED_LOST_DEBOUNCE:
                    self.following_red = False
                    self._red_lost_frames = 0
                    self.get_logger().info(
                        f"Red line lost ({self.RED_LOST_DEBOUNCE} consecutive low frames) "
                        "— reverting to green tracking."
                    )
                    mask = mask_green
                    mask_sum = green_sum
                else:
                    self.get_logger().debug(
                        f"Red low-pixel frame {self._red_lost_frames}/{self.RED_LOST_DEBOUNCE} "
                        f"(px={red_strip_px}) — holding red tracking."
                    )
            else:
                # Red is visible — reset the lost-frame counter
                self._red_lost_frames = 0
        else:
            mask = mask_green
            mask_sum = green_sum

        # ── Docking / Explosion Triggers (Regardless of follow_mode) ─────────
        if (not self.u_turning
                and self.docking_type == 0
                and current_time >= self.post_docking_cooldown_until):
            if green_sum > self.EXPLOSION_THRESHOLD:
                # Green explosion -> U-turn then Docking 1
                self.u_turning = True
                self.u_turn_start_time = current_time
                self.current_state = "U-TURN"
                self._publish_state(self.current_state)
                self.pending_docking_type = 1
                self.get_logger().warn("Green explosion -> U-TURN (leads to DOCKING 1)")
            elif red_strip_sum > self.RED_EXPLOSION_PX:
                # Red explosion -> Docking 2
                self.docking_type = 2
                self.docking_phase = 1
                self.docking_timer = current_time
                self.current_state = "DOCKING 2"
                self._publish_state(self.current_state)
                self.get_logger().warn("Red explosion -> DOCKING 2")

        # ── Handle U-turn (Universal for active line color) ──────────────────
        if self.u_turning:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.25
            self.cmd_vel_pub.publish(self.twist)

            # Only check for line after minimum U-turn time
            if current_time - self.u_turn_start_time >= self.U_TURN_MIN_TIME:
                if 0 < mask_sum < max(self.EXPLOSION_THRESHOLD, self.RED_EXPLOSION_PX):
                    M = cv2.moments(mask)
                    if M['m00'] > 0:
                        cx_uturn = int(M['m10'] / M['m00'])
                        err_uturn = cx_uturn - w // 2
                        line_solid   = mask_sum > 100000
                        line_centred = abs(err_uturn) < 80
                        if line_solid and line_centred:
                            self.u_turning = False
                            if self.pending_docking_type == 1:
                                self.docking_type = 1
                                self.docking_phase = 1
                                self.current_state = "DOCKING 1"
                                self._publish_state(self.current_state)
                                self.pending_docking_type = 0
                                self.get_logger().info("U-turn completed. Entering DOCKING 1.")
                            else:
                                self.current_state = "RUNNING"
                                self._publish_state(self.current_state)
                                self._current_linear_x = 0.0
                                self.get_logger().info("U-turn completed. Resuming normal line following.")
                        else:
                            self.get_logger().debug(
                                f"U-turn check: solid={line_solid}, centred={line_centred} "
                                f"(err={err_uturn}, mask_sum={mask_sum}) — continuing turn."
                            )
                else:
                    self.get_logger().debug(
                        f"U-turn: waiting for line (sum={mask_sum}) — continuing turn."
                    )
            return  # Skip normal PD while U-turning

        # ── Handle Docking Protocol ─────────────────────────────────────────
        if self.docking_type == 1:
            if self.docking_phase == 1:
                # Phase 1: Rotate on the spot using PD until aligned with no error
                M = cv2.moments(mask)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    err = cx - w // 2
                    dt = 0.01 if self.last_time is None else current_time - self.last_time
                    self.last_time = current_time

                    derivative = (err - self.last_err) / dt
                    self.last_err = err

                    angular_z = -self.Kp * err - self.Kd * derivative
                    angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)

                    # ── Minimum rotation enforcement for spot-alignment ──
                    if abs(err) > 10:
                        if 0 <= angular_z < self.MIN_ANG_Z_DEADZONE:
                            angular_z = self.MIN_ANG_Z_DEADZONE
                        elif -self.MIN_ANG_Z_DEADZONE < angular_z <= 0:
                            angular_z = -self.MIN_ANG_Z_DEADZONE
                    else:
                        angular_z = 0.0

                    self.twist.linear.x = 0.0
                    self.twist.angular.z = angular_z
                    self.cmd_vel_pub.publish(self.twist)

                    # When aligned
                    if abs(err) <= 3:
                        # ── CA-PP-full gate: nowhere to deliver, hold at Store ──
                        capp_all_full = (
                            any(self.rack_states[k] == 1 for k in ["CAPP-A1", "CAPP-A2", "CAPP-A3"])
                            and any(self.rack_states[k] == 1 for k in ["CAPP-B1", "CAPP-B2", "CAPP-B3"])
                        )
                        if capp_all_full:
                            # Aligned but CA-PP is full — hold here until space opens up
                            if not self.waiting_capp_full_d1:
                                self.waiting_capp_full_d1 = True
                                self.current_state = "WAITING \u2014 NO RACK"
                                self._publish_state(self.current_state)
                                self.get_logger().warn(
                                    "Docking 1 Phase 1: Aligned but CA-PP is full "
                                    "\u2014 waiting for CA-PP slot to open."
                                )
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = 0.0
                            self.cmd_vel_pub.publish(self.twist)
                        else:
                            # CA-PP has space — proceed to Phase 2 (backward)
                            self.waiting_capp_full_d1 = False
                            self.docking_phase = 2
                            self.docking_timer = current_time
                            self.last_err = 0
                            self.get_logger().info("Docking 1 Phase 1: Aligned. Moving backward.")
                else:
                    # Lost line during alignment
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)

            elif self.docking_phase == 2:
                # Phase 2: Move backwards
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = -0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 3
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 1 Phase 2: Done. Phase 3: Waiting.")
            
            elif self.docking_phase == 3:
                # Phase 3: Wait there
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_type = 0
                    self.docking_phase = 0
                    self.current_state = "RUNNING"
                    self._current_linear_x = 0.0  # Reset slew rate for smooth start
                    self.post_docking_cooldown_until = current_time + 5.0  # Prevent immediate re-trigger
                    self.agv_direction = "to_capp"
                    self._publish_state(self.current_state)
                    self.get_logger().info("Docking 1 complete: Switch to Leg 2 (to_capp). Resuming.")
                    # Force a lane update immediately 
                    synthetic: String = String()
                    synthetic.data = "force_update:0:0"
                    self.rack_status_callback(synthetic)
            
            return  # Skip normal PD while docking

        elif self.docking_type == 2:
            if self.docking_phase == 1:
                # Phase 1: Move backwards 0.075 for 1s
                if current_time - self.docking_timer <= 2.0:
                    self.twist.linear.x = -0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 2
                    self.get_logger().info("Docking 2 Phase 1 Done. Aligning...")
            elif self.docking_phase == 2:
                # Phase 2: Align with line using PD
                M = cv2.moments(mask)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    err = cx - w // 2
                    dt = 0.01 if self.last_time is None else current_time - self.last_time
                    self.last_time = current_time

                    derivative = (err - self.last_err) / dt
                    self.last_err = err

                    angular_z = -self.Kp * err - self.Kd * derivative
                    angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)

                    # ── Minimum rotation enforcement for spot-alignment ──
                    if abs(err) > 10:
                        if 0 <= angular_z < self.MIN_ANG_Z_DEADZONE:
                            angular_z = self.MIN_ANG_Z_DEADZONE
                        elif -self.MIN_ANG_Z_DEADZONE < angular_z <= 0:
                            angular_z = -self.MIN_ANG_Z_DEADZONE
                    else:
                        angular_z = 0.0

                    self.twist.linear.x = 0.0
                    self.twist.angular.z = angular_z
                    self.cmd_vel_pub.publish(self.twist)

                    if abs(err) <= 5:
                        # ── Gate 2: target column sensor check ────────────
                        if self.follow_mode == "red":
                            col_occupied = any(
                                self.rack_states[k] == 1
                                for k in ["CAPP-B1", "CAPP-B2", "CAPP-B3"]
                            )
                        else:
                            col_occupied = any(
                                self.rack_states[k] == 1
                                for k in ["CAPP-A1", "CAPP-A2", "CAPP-A3"]
                            )

                        if col_occupied:
                            # Sensor blocked — wait for operator GO
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = 0.0
                            self.cmd_vel_pub.publish(self.twist)
                            self.waiting_operator_confirm = True
                            self.current_state = "WAITING \u2014 CONFIRM"
                            self._publish_state(self.current_state)
                            self.get_logger().warn(
                                "Docking 2 Phase 2: Sensor blocked on target column "
                                "\u2014 waiting for operator confirmation."
                            )
                        else:
                            self.docking_phase = 3
                            self.docking_timer = current_time
                            self.last_err = 0
                            self.get_logger().info("Docking 2 Phase 2: Aligned. Move forward 5s.")
                else:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)

            elif self.docking_phase == 3:
                # Phase 3: Move forward at 0.075 for 5s
                if current_time - self.docking_timer <= 8.0:
                    self.twist.linear.x = 0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 4
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 2 Phase 3 Done. Hold for 5s.")
            elif self.docking_phase == 4:
                # Phase 4: Hold for 5s
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 5
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 2 Phase 4 Done. Moving backward for 5s.")
            elif self.docking_phase == 5:
                # Phase 5: Move backwards then U-turn if Store has material
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = -0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    # ── Gate 1: Store-all-empty — no material to bring back ──
                    store_all_empty = not any(
                        self.rack_states[k] == 1
                        for k in ["Store-A1", "Store-A2", "Store-A3",
                                  "Store-B1", "Store-B2", "Store-B3"]
                    )
                    if store_all_empty:
                        if not self.waiting_store_empty_d2:
                            self.waiting_store_empty_d2 = True
                            self.current_state = "WAITING \u2014 NO RACK"
                            self._publish_state(self.current_state)
                            self.get_logger().warn(
                                "Docking 2 Phase 5: Unloaded but Store is empty "
                                "\u2014 waiting for material at Store before returning."
                            )
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = 0.0
                        self.cmd_vel_pub.publish(self.twist)
                    else:
                        self.waiting_store_empty_d2 = False
                        self.docking_type = 0
                        self.docking_phase = 0
                        self.u_turning = True
                        self.u_turn_start_time = current_time
                        self.current_state = "U-TURN"
                        self.agv_direction = "to_store"
                        self._publish_state(self.current_state)
                        self.get_logger().info("Docking 2 Phase 5 Done. Switch to Leg 1 (to_store). Triggering U-TURN.")
                        # Force a lane update before starting U-turn
                        synthetic: String = String()
                        synthetic.data = "force_update:0:0"
                        self.rack_status_callback(synthetic)
            return

        # ── Normal PD line-following ───────────────────────────────────
        M = cv2.moments(mask)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            err = cx - w // 2
            dt = 0.01 if self.last_time is None else current_time - self.last_time
            self.last_time = current_time

            derivative = (err - self.last_err) / dt
            self.last_err = err

            angular_z = -self.Kp * err - self.Kd * derivative
            angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)

            if abs(angular_z) < self.MIN_ANG_Z_DEADZONE:
                angular_z = 0.0

            # ── Slew-rate limiter ──────────────────────────────────────
            TARGET_LINEAR_X = 0.25
            self._current_linear_x = min(
                self._current_linear_x + LINEAR_SLEW_RATE,
                TARGET_LINEAR_X
            )

            self.twist.linear.x = self._current_linear_x
            self.twist.angular.z = angular_z
            self.cmd_vel_pub.publish(self.twist)

            line_color = "Red" if self.following_red else "Green"
            # Issue 4: throttle to 1 Hz — logging every frame causes measurable overhead
            if current_time - self._last_log_time >= 1.0:
                self.get_logger().info(
                    f"[{line_color}] cx={cx}, cy={cy}, err={err}, ang_z={angular_z:.3f}, "
                    f"lin_x={self._current_linear_x:.3f}, mask_sum={mask_sum}"
                )
                self._last_log_time = current_time
        else:
            # No line detected → stop
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0
            self.cmd_vel_pub.publish(self.twist)
            self.get_logger().warn(f"No line detected — stopping. mask_sum={mask_sum}, following_red={self.following_red}")


def main():
    rclpy.init()
    node = WebcamLineFollow()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
