import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class IntegerSubscriber(Node):

    def __init__(self):
        super().__init__('integer_subscriber')

        self.subscription = self.create_subscription(
            Int32,
            'numbers',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = IntegerSubscriber()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()