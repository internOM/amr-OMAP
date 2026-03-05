#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import cv2
import numpy as np

class LineFollower(Node):
    def __init__(self):
        super().__init__('line_follower')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.twist = Twist()

        # OpenCV camera capture
        self.cap = cv2.VideoCapture(0)  # /dev/video0
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.timer = self.create_timer(0.03, self.timer_callback)  # ~30Hz

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Camera frame not received!')
            return

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Green line detection
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([90, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Focus on bottom of image
        h, w = mask.shape
        search_top = (h * 3) // 4
        search_bot = search_top + 20
        mask[0:search_top, :] = 0
        mask[search_bot:h, :] = 0

        # Compute centroid
        M = cv2.moments(mask)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            error = cx - w // 2
            self.twist.linear.x = 0.2
            self.twist.angular.z = -float(error) / 500
        else:
            # Stop if no line detected
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0

        self.cmd_pub.publish(self.twist)

        # Optional display
        resize_dim = (w // 2, h // 2)
        cv2.imshow('Camera', cv2.resize(frame, resize_dim))
        cv2.imshow('Mask', cv2.resize(mask, resize_dim))
        cv2.imshow('Masked', cv2.resize(masked_frame, resize_dim))
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = LineFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
