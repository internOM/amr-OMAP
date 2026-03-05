import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist

import time


class HtmlToCmdVel(Node):
    def __init__(self):
        super().__init__('html_to_cmd_vel')

        # Tunable parameters
        self.linear_speed = 0.2
        self.angular_speed = 0.8
        self.timeout_sec = 0.5   # disconnect timeout

        # State
        self.last_msg_time = time.time()
        self.current_direction = "Center"
        self.stopped = True

        # ROS interfaces
        self.sub = self.create_subscription(
            String,
            '/html_direction',
            self.direction_callback,
            10
        )

        self.pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.safety_check)

        self.get_logger().info("html_to_cmd_vel node started")

    def direction_callback(self, msg: String):
        self.current_direction = msg.data
        self.last_msg_time = time.time()

        twist = self.direction_to_twist(msg.data)
        self.pub.publish(twist)

        self.stopped = (msg.data == "Center")

    def safety_check(self):
        # Stop ONLY if joystick is disconnected
        if time.time() - self.last_msg_time > self.timeout_sec:
            if not self.stopped:
                self.pub.publish(Twist())
                self.stopped = True
                self.get_logger().warn("Joystick disconnected — stopping robot")

    def direction_to_twist(self, direction: str) -> Twist:
        twist = Twist()

        if direction == "Forward":
            twist.linear.x = self.linear_speed
        elif direction == "Backward":
            twist.linear.x = -self.linear_speed
        elif direction == "Left":
            twist.angular.z = -self.angular_speed
        elif direction == "Right":
            twist.angular.z = self.angular_speed
        # Center → zero twist (intentional stop)

        return twist


def main():
    rclpy.init()
    node = HtmlToCmdVel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
