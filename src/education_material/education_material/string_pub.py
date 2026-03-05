import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class StringPublisher(Node):

    def __init__(self):
        super().__init__('string_publisher')

        # Publisher for 'chatter' topic
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Timer to publish every second
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.counter = 1  # Start at 1

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World {self.counter}'
        self.publisher_.publish(msg)

        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Cycle 1,2,3 repeatedly
        self.counter += 1
        if self.counter > 3:
            self.counter = 1


def main(args=None):
    rclpy.init(args=args)
    node = StringPublisher()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()