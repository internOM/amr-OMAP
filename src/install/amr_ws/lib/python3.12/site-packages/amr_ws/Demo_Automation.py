#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from math import sqrt, atan2, pi

class AutoDriveNode(Node):
    def __init__(self):
        super().__init__('auto_drive_node')

        # Publisher for cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber for odometry
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Current odometry
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # --- Editable instructions ---
        # Each instruction is a dictionary: type = 'move' or 'turn', value = meters or radians
        self.instructions = [
            {'type': 'move', 'value': 2.0},    # move forward 2 meters
            {'type': 'turn', 'value': pi/2},   # turn 90 degrees
            {'type': 'move', 'value': 1.0},    # move forward 1 meter
            {'type': 'turn', 'value': pi/2},   # turn 90 degrees
            {'type': 'move', 'value': 2.0},    # return 2 meters
        ]
        self.linear_speed = 0.2   # m/s
        self.angular_speed = 0.5  # rad/s

        # State
        self.phase_index = 0
        self.start_x = None
        self.start_y = None
        self.start_yaw = None

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = atan2(siny_cosp, cosy_cosp)

    def distance_moved(self):
        dx = self.current_x - self.start_x
        dy = self.current_y - self.start_y
        return sqrt(dx*dx + dy*dy)

    def angle_turned(self):
        # Handle wrap-around of yaw
        delta = self.current_yaw - self.start_yaw
        while delta > pi:
            delta -= 2*pi
        while delta < -pi:
            delta += 2*pi
        return abs(delta)

    def control_loop(self):
        twist = Twist()

        if self.phase_index >= len(self.instructions):
            # Finished all instructions
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            return

        instr = self.instructions[self.phase_index]

        if instr['type'] == 'move':
            if self.start_x is None:
                self.start_x = self.current_x
                self.start_y = self.current_y
                self.get_logger().info(f"Phase {self.phase_index}: moving {instr['value']} m")

            if self.distance_moved() < instr['value']:
                twist.linear.x = self.linear_speed
            else:
                twist.linear.x = 0.0
                self.phase_index += 1
                self.start_x = None
                self.start_y = None

        elif instr['type'] == 'turn':
            if self.start_yaw is None:
                self.start_yaw = self.current_yaw
                self.get_logger().info(f"Phase {self.phase_index}: turning {instr['value']} rad")

            if self.angle_turned() < instr['value']:
                twist.angular.z = self.angular_speed
            else:
                twist.angular.z = 0.0
                self.phase_index += 1
                self.start_yaw = None

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = AutoDriveNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
