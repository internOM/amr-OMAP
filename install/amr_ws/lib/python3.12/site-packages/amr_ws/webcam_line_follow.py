#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

class WebcamLineFollow(Node):
    def __init__(self):
        super().__init__('webcam_line_follow')

        self.bridge = CvBridge()

        # ── Subscriptions ──────────────────────────────────────────────
        self.create_subscription(Image, '/image_raw', self.image_callback, 1)

        # UI control topics
        self.create_subscription(Bool, '/agv/cmd_enable', self.enable_callback, 10)
        self.create_subscription(Bool, '/agv/cmd_stop',   self.stop_callback,   10)
        
        # Ping Echo
        self.create_subscription(String, '/ui_heartbeat', self.heartbeat_callback, 10)

        # ── Publishers ─────────────────────────────────────────────────
        # twist_mux picks this up at priority 10 (same slot as Nav2)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel_agv', 10)

        # State feedback → UI
        self.state_pub = self.create_publisher(String, '/agv/state', 10)
        
        # Ping Echo pub
        self.heartbeat_pub = self.create_publisher(String, '/ui_heartbeat', 10)

        # ── Internal enable gate ───────────────────────────────────────
        # Node starts disabled; GO button on the UI enables it.
        self.enabled = False

        # ── U-turn detection thresholds ────────────────────────────────
        self.EXPLOSION_THRESHOLD = 1500000
        self.u_turning = False
        self.u_turn_start_time = None
        self.U_TURN_MIN_TIME = 2.0      # seconds before checking for line again

        # ── PD controller ──────────────────────────────────────────────
        self.Kp = 0.0032
        self.Kd = 0.00072
        self.last_err = 0
        self.last_time = None
        self.MAX_ANG_Z = 1.0
        self.MIN_ANG_Z_DEADZONE = 0.05

        self.twist = Twist()

        self.get_logger().info("Webcam Line Follow node started — waiting for /agv/cmd_enable")

        # Broadcast state at 1Hz so UI knows the node is active
        self.current_state = "WAITING"
        self.state_timer = self.create_timer(1.0, self.timer_state_callback)
        self._publish_state(self.current_state)

    # ── Enable / Stop & Ping callbacks ───────────────────────────────────

    def heartbeat_callback(self, msg: String):
        # Bounce the ping straight back to the UI
        self.heartbeat_pub.publish(msg)

    def enable_callback(self, msg: Bool):
        if msg.data and not self.enabled:
            self.enabled = True
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

    def _publish_state(self, state: str):
        msg = String()
        msg.data = state
        self.state_pub.publish(msg)

    def timer_state_callback(self):
        self._publish_state(self.current_state)

    # ── Image callback ────────────────────────────────────────────────

    def image_callback(self, msg):
        # Gate: do nothing if not enabled
        if not self.enabled:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([95, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Crop bottom strip for line detection
        h, w = frame.shape[:2]
        search_top = (h // 4) * 3
        search_bot = search_top + 20
        mask[0:search_top, :] = 0
        mask[search_bot:h, :] = 0

        mask_sum = np.sum(mask)
        current_time = time.time()

        # ── U-turn detection ──────────────────────────────────────────
        if not self.u_turning and mask_sum > self.EXPLOSION_THRESHOLD:
            self.u_turning = True
            self.u_turn_start_time = current_time
            self.get_logger().warn("Green area explosion detected! Starting U-turn.")

        # ── Handle U-turn ─────────────────────────────────────────────
        if self.u_turning:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.25
            self.cmd_vel_pub.publish(self.twist)

            # Only check for line after minimum U-turn time
            if current_time - self.u_turn_start_time >= self.U_TURN_MIN_TIME:
                M = cv2.moments(mask)
                if M['m00'] > 0:
                    cx_uturn = int(M['m10'] / M['m00'])
                    err_uturn = cx_uturn - w // 2
                    # Require a solid line (not just a sliver) AND reasonably centred.
                    # mask_sum < 50 000 → still catching a corner/edge of tape.
                    # |err| > 80 px   → line is still too far off-centre.
                    line_solid = mask_sum > 50000
                    line_centred = abs(err_uturn) < 80
                    if line_solid and line_centred:
                        self.u_turning = False
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = 0.0
                        self.cmd_vel_pub.publish(self.twist)
                        self.get_logger().info(
                            f"U-turn completed — cx={cx_uturn}, err={err_uturn}, "
                            f"mask_sum={mask_sum}. Resuming line following."
                        )
                    else:
                        self.get_logger().debug(
                            f"U-turn check: solid={line_solid}, centred={line_centred} "
                            f"(err={err_uturn}, mask_sum={mask_sum}) — continuing turn."
                        )
            return  # Skip normal PD while U-turning

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

            self.twist.linear.x = 0.25     # linear speed
            self.twist.angular.z = angular_z
            self.cmd_vel_pub.publish(self.twist)

            self.get_logger().info(
                f"Line: cx={cx}, cy={cy}, err={err}, ang_z={angular_z:.3f}, mask_sum={mask_sum}"
            )
        else:
            # No line detected → stop
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0
            self.cmd_vel_pub.publish(self.twist)
            self.get_logger().warn(f"No line detected — stopping. mask_sum={mask_sum}")


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