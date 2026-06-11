import subprocess
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class AgvShutdownNode(Node):
    def __init__(self):
        super().__init__('agv_shutdown_node')
        self.srv = self.create_service(
            Trigger,
            '/agv/shutdown',
            self.shutdown_callback
        )
        self.get_logger().info('Shutdown service ready — listening on /agv/shutdown')

    def shutdown_callback(self, request, response):
        self.get_logger().info('Shutdown requested via /agv/shutdown — shutting down Pi...')
        response.success = True
        response.message = 'Shutdown initiated'
        # Small delay so the response can be sent back to rosbridge before OS shuts down
        self.create_timer(1.0, self.do_shutdown)
        return response

    def do_shutdown(self):
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])


def main(args=None):
    rclpy.init(args=args)
    node = AgvShutdownNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()