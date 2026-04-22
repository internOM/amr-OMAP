#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

class WebcamLineFollow(Node):
    def __init__(self):
        super().__init__('webcam_line_follow')

        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image, '/image_raw', self.image_callback, 10
        )
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.twist = Twist()

        # U-turn and line detection thresholds
        self.EXPLOSION_THRESHOLD = 670000  # Green area for "explosion"
        self.u_turning = False
        self.u_turn_start_time = None
        self.U_TURN_MIN_TIME = 2.0  # seconds before checking line

        # PD controller for line following
        self.Kp = 0.0032
        self.Kd = 0.00067
        self.last_err = 0
        self.last_time = None
        self.MAX_ANG_Z = 1.0
        self.MIN_ANG_Z_DEADZONE = 0.01

        self.get_logger().info("Webcam Line Follow node started")

    def image_callback(self, msg):
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

        # --- U-turn detection ---
        if not self.u_turning and mask_sum > self.EXPLOSION_THRESHOLD:
            self.u_turning = True
            self.u_turn_start_time = current_time
            self.get_logger().warn("Green area explosion detected! Starting U-turn.")

        # --- Handle U-turn ---
        if self.u_turning:
            # Keep spinning in place
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.25
            self.cmd_vel_pub.publish(self.twist)

            # Only check for line after minimum U-turn time
            if current_time - self.u_turn_start_time >= self.U_TURN_MIN_TIME:
                M = cv2.moments(mask)
                if M['m00'] > 0:  # Line detected → U-turn completed
                    self.u_turning = False
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                    self.get_logger().info("U-turn completed, line back to normal.")
            return  # Skip line-following while turning

        # --- Normal PD line-following ---
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

            self.twist.linear.x = 0.25 #linear speed
            self.twist.angular.z = angular_z
            self.cmd_vel_pub.publish(self.twist)

            self.get_logger().info(
                f"Line detected: cx={cx}, cy={cy}, err={err}, angular_z={angular_z:.3f}, mask_sum={mask_sum}"
            )
        else:
            # No line detected → stop
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0
            self.cmd_vel_pub.publish(self.twist)
            self.get_logger().warn(f"No line detected! Stopping robot. mask_sum={mask_sum}")


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