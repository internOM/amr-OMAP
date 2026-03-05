import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import math


class CompassDistanceNode(Node):

    def __init__(self):
        super().__init__('compass_distance_node')

        self.publisher = self.create_publisher(
            String,
            'compass_distance',
            10
        )

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )

        self.get_logger().info('Compass Distance Node started')

    def angle_to_index(self, angle, msg):
        index = int((angle - msg.angle_min) / msg.angle_increment)
        return max(0, min(index, len(msg.ranges) - 1))

    def safe_range(self, value):
        if math.isinf(value) or math.isnan(value):
            return -1.0
        return value

    def listener_callback(self, msg):
        # 🔁 Corrected angles for YOUR LiDAR orientation
        FRONT = math.pi
        BACK  = 0.0
        LEFT  = -math.pi / 2
        RIGHT = math.pi / 2

        front_idx = self.angle_to_index(FRONT, msg)
        back_idx  = self.angle_to_index(BACK, msg)
        left_idx  = self.angle_to_index(LEFT, msg)
        right_idx = self.angle_to_index(RIGHT, msg)

        front_dist = self.safe_range(msg.ranges[front_idx])
        back_dist  = self.safe_range(msg.ranges[back_idx])
        left_dist  = self.safe_range(msg.ranges[left_idx])
        right_dist = self.safe_range(msg.ranges[right_idx])

        msg_out = String()
        msg_out.data = (
            f"Front: {front_dist:.2f} m | "
            f"Left: {left_dist:.2f} m | "
            f"Right: {right_dist:.2f} m | "
            f"Back: {back_dist:.2f} m"
        )

        self.publisher.publish(msg_out)
        self.get_logger().info(msg_out.data)


def main(args=None):
    rclpy.init(args=args)
    node = CompassDistanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
