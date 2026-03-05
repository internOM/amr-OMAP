import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class EvenOddSubscriber(Node):
    def __init__(self):
        super().__init__('even_odd_subscriber')

        # Subscribe to 'numbers' topic
        self.subscription = self.create_subscription(
            Int32,
            'numbers',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        number = msg.data
        even_odd = "Even" if number % 2 == 0 else "Odd"
        self.get_logger().info(f'Received: {number} → {even_odd}')


def main(args=None):
    rclpy.init(args=args)
    node = EvenOddSubscriber()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()