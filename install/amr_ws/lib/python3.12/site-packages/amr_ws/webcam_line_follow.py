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

# ── LiDAR safety constants ─────────────────────────────────────────────────────
# The safety cone covers ±90° around the robot's forward direction (0 rad).
# Any valid range reading inside this 180° arc that is ≤ OBSTACLE_DISTANCE_M
# will trigger an OBSTACLE_DETECTED stop.
OBSTACLE_DISTANCE_M = 0.32      # metres – stop threshold
SAFETY_CONE_HALF_DEG = 60.0    # degrees each side of forward → total 120°

# ── Obstacle debounce & slew-rate constants ────────────────────────────────────
# Number of consecutive obstacle-free scan frames required before the robot is
# allowed to resume.  Prevents jitter / false-clear transients.
OBSTACLE_CLEAR_DEBOUNCE = 5   # frames

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
        self.RED_EXPLOSION_PX        = 1350000  # red strip pixels → red U-turn
        self.u_turning               = False
        self.u_turn_start_time       = None
        self.red_u_turning           = False
        self.red_u_turn_start_time   = None
        self.U_TURN_MIN_TIME         = 2.0      # seconds before checking for line again

        # ── PD controller ──────────────────────────────────────────────
        self.Kp = 0.0032
        self.Kd = 0.00072
        self.last_err = 0
        self.last_time = None
        self.MAX_ANG_Z = 1.0
        self.MIN_ANG_Z_DEADZONE = 0.05

        # Issue 4: timestamp of the last per-frame info log (throttled to 1 Hz)
        self._last_log_time = 0.0

        self.twist = Twist()

        self.get_logger().info("Webcam Line Follow node started — waiting for /agv/cmd_enable")

        # Broadcast state + mode at 1 Hz so UI always reflects node truth
        self.current_state = "WAITING"
        self.state_timer = self.create_timer(1.0, self.timer_state_callback)
        self._publish_state(self.current_state)
        self._publish_mode(self.follow_mode)

    # ── LiDAR safety callback ──────────────────────────────────────────────────

    def scan_callback(self, msg: LaserScan):
        """
        Check the forward 180° cone of the LaserScan.

        The LaserScan convention:
          angle_min  → first beam angle (radians)
          angle_max  → last beam angle (radians)
          angle_increment → step between beams

        Index of a given angle θ:
          i = round((θ - angle_min) / angle_increment)

        We want all beams whose angle θ satisfies:
          -SAFETY_CONE_HALF_DEG ≤ θ ≤ +SAFETY_CONE_HALF_DEG   (in radians)
        """
        half_rad = math.radians(SAFETY_CONE_HALF_DEG)

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
            # Angle of this beam
            angle = angle_min + i * inc

            # Normalise to (-π, π)
            angle = math.atan2(math.sin(angle), math.cos(angle))

            # Only consider beams inside the ±90° forward cone
            if abs(abs(angle) - math.pi) > half_rad:
                continue

            # Skip invalid / out-of-range readings
            if not math.isfinite(r) or r < range_min or r > range_max:
                continue

            if r <= OBSTACLE_DISTANCE_M:
                obstacle_found = True
                break

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
                    f"OBSTACLE DETECTED within {OBSTACLE_DISTANCE_M}m — halting robot. "
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
            # A red U-turn is red-specific; cancel it so the robot resumes
            # green following without finishing an irrelevant manoeuvre.
            if self.red_u_turning:
                self.red_u_turning = False
                self.red_u_turn_start_time = None
                self.get_logger().info("Mode → green: cancelled active red U-turn.")
            # NOTE: green U-turn (u_turning) and PD state are left intact —
            # the robot keeps moving without any jolt.

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

        # ── Red mask: only computed when red mode (or red following) active ──
        # Issue 2: skip all red-mask work in pure green mode to save CPU.
        RED_STRIP_MIN  = 500
        RED_CENTER_TOL = int(w * 0.45)

        if self.follow_mode == "red" or self.following_red:
            lower_red_lo = np.array([  0,  60,  60])
            upper_red_lo = np.array([ 25, 255, 255])
            lower_red_hi = np.array([140,  60,  60])
            upper_red_hi = np.array([180, 255, 255])
            mask_red = cv2.bitwise_or(
                cv2.inRange(hsv_strip, lower_red_lo, upper_red_lo),
                cv2.inRange(hsv_strip, lower_red_hi, upper_red_hi)
            )
            # Issue 5: compute pixel count once and reuse everywhere below
            red_strip_px  = int(np.sum(mask_red > 0))
            red_strip_sum = int(np.sum(mask_red))
        else:
            mask_red      = None
            red_strip_px  = 0
            red_strip_sum = 0

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
            self.get_logger().debug(
                f"Strip check: red_strip_px={red_strip_px}, green_sum={green_sum}"
            )

        # ── Choose active tracking mask ────────────────────────────────────
        if self.following_red:
            # Once on red, track it in the bottom strip
            mask = mask_red
            mask_sum = int(np.sum(mask))
            # If red disappears (end of red tape), fall back to green
            # Issue 5: reuse already-computed red_strip_px instead of recalculating
            if red_strip_px < 200:
                self.following_red = False
                self.get_logger().info("Red line lost — reverting to green tracking.")
                mask = mask_green
                mask_sum = green_sum
        else:
            mask = mask_green
            mask_sum = green_sum

        # ── U-turn detection (suppressed in red mode when red visible) ────────
        if not self.following_red:
            if not self.u_turning and green_sum > self.EXPLOSION_THRESHOLD:
                # In red mode, don't U-turn if red tape is present in the strip
                if self.follow_mode == "green" or red_strip_px < RED_STRIP_MIN:
                    self.u_turning = True
                    self.u_turn_start_time = current_time
                    self.get_logger().warn("Green area explosion detected! Starting green U-turn.")

        # ── Red U-turn detection ───────────────────────────────────────────
        # When following red and the strip is flooded with red pixels
        # (robot nose is in a big red zone = end-of-red-section marker),
        # do a U-turn and wait for the red line to reappear centred.
        if (self.following_red
                and not self.red_u_turning
                and red_strip_sum > self.RED_EXPLOSION_PX):
            self.red_u_turning         = True
            self.red_u_turn_start_time = current_time
            self.get_logger().warn(
                f"Red area explosion (sum={red_strip_sum}) — starting red U-turn."
            )


        # ── Handle green U-turn ─────────────────────────────────────────────
        if self.u_turning:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.25
            self.cmd_vel_pub.publish(self.twist)

            # Only check for line after minimum U-turn time
            if current_time - self.u_turn_start_time >= self.U_TURN_MIN_TIME:
                M = cv2.moments(mask_green)
                if M['m00'] > 0:
                    cx_uturn = int(M['m10'] / M['m00'])
                    err_uturn = cx_uturn - w // 2
                    line_solid   = green_sum > 50000
                    line_centred = abs(err_uturn) < 80
                    if line_solid and line_centred:
                        self.u_turning = False
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = 0.0
                        self.cmd_vel_pub.publish(self.twist)
                        self.get_logger().info(
                            f"Green U-turn completed — cx={cx_uturn}, err={err_uturn}, "
                            f"mask_sum={green_sum}. Resuming green following."
                        )
                    else:
                        self.get_logger().debug(
                            f"Green U-turn check: solid={line_solid}, centred={line_centred} "
                            f"(err={err_uturn}, mask_sum={green_sum}) — continuing turn."
                        )
            return  # Skip normal PD while U-turning

        # ── Handle red U-turn ───────────────────────────────────────────────
        if self.red_u_turning:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.25
            self.cmd_vel_pub.publish(self.twist)

            if current_time - self.red_u_turn_start_time >= self.U_TURN_MIN_TIME:
                # Look for a thin, centred red line in the strip (not a flood)
                if 0 < red_strip_sum < self.RED_EXPLOSION_PX:
                    Mr = cv2.moments(mask_red)
                    if Mr['m00'] > 0:
                        cx_red_ut = int(Mr['m10'] / Mr['m00'])
                        err_red   = cx_red_ut - w // 2
                        line_centred = abs(err_red) < 80
                        if line_centred:
                            self.red_u_turning = False
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = 0.0
                            self.cmd_vel_pub.publish(self.twist)
                            self.get_logger().info(
                                f"Red U-turn completed — cx={cx_red_ut}, err={err_red}, "
                                f"red_strip_sum={red_strip_sum}. Resuming red following."
                            )
                        else:
                            self.get_logger().debug(
                                f"Red U-turn check: centred={line_centred} "
                                f"(err={err_red}, sum={red_strip_sum}) — continuing turn."
                            )
                else:
                    self.get_logger().debug(
                        f"Red U-turn: waiting for line (sum={red_strip_sum}) — continuing turn."
                    )
            return  # Skip normal PD while red-U-turning

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