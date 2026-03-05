import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class IntegerPublisher(Node):

    def __init__(self):
        super().__init__('integer_publisher')

        # Create publisher
        self.publisher_ = self.create_publisher(Int32, 'numbers', 10)

        # Create timer (1 second)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.counter = 0

    def timer_callback(self):
        msg = Int32()
        msg.data = self.counter
        self.publisher_.publish(msg)

        self.get_logger().info(f'Publishing: {msg.data}')

        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = IntegerPublisher()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()