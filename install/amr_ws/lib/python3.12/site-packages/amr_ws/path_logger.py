#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseWithCovarianceStamped
import yaml
import os
import math
import sys
import termios
import tty
import select

class ManualPathLogger(Node):
    def __init__(self):
        super().__init__('manual_rpp_path_logger')

        # Subscribe to AMCL pose
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.pose_callback,
            10
        )

        # Publisher for Path (optional visualization)
        self.path_pub = self.create_publisher(Path, '/logged_path', 10)
        self.path = Path()
        self.path.header.frame_id = "map"

        # Storage
        self.logged_points = []
        self.log_file = os.path.join(os.path.expanduser('~'), 'rpp_path.yaml')

        # Latest pose cache
        self.latest_pose = None

        self.get_logger().info("Manual logger initialized. Press 'l' to log the current robot pose.")

        # Run the keyboard loop
        self.keyboard_loop()

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        self.latest_pose = msg

    def keyboard_loop(self):
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.1)

                if self.kbhit():
                    c = sys.stdin.read(1)
                    if c.lower() == 'l':
                        self.log_current_pose()
                    elif c.lower() == 'q':
                        self.get_logger().info("Quitting manual logger.")
                        break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def kbhit(self):
        # Return True if a key was pressed
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        return dr != []

    def log_current_pose(self):
        if self.latest_pose is None:
            self.get_logger().warn("No pose received yet.")
            return

        msg = self.latest_pose
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        yaw = self.quaternion_to_yaw(msg.pose.pose.orientation)

        # Append to YAML list
        self.logged_points.append({'x': x, 'y': y, 'yaw': yaw})

        # Update Path for RViz visualization
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = "map"
        pose_stamped.header.stamp = msg.header.stamp
        pose_stamped.pose = msg.pose.pose
        self.path.poses.append(pose_stamped)
        self.path_pub.publish(self.path)

        # Save to file
        with open(self.log_file, 'w') as f:
            yaml.dump(self.logged_points, f)

        self.get_logger().info(f"Logged point: x={x:.3f}, y={y:.3f}, yaw={yaw:.2f}")

    def quaternion_to_yaw(self, q):
        # Convert quaternion to yaw
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)


def main(args=None):
    rclpy.init(args=args)
    node = ManualPathLogger()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()