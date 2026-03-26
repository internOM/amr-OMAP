#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

class CmdVelTranslator(Node):
    def __init__(self):
        super().__init__('cmd_vel_translator')

        # QoS profile to match most publishers/subscribers
        qos = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # Subscriber reads from cmd_vel_smoothed
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel_smoothed',
            self.cmd_vel_callback,
            qos
        )

        # Publisher sends to cmd_vel
        self.pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            qos
        )

        self.get_logger().info('CmdVelTranslator node started. Translating /cmd_vel_smoothed -> /cmd_vel')

    def cmd_vel_callback(self, msg: Twist):
        # Forward the message as-is
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelTranslator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()