#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math


# ─── Configuration ────────────────────────────────────────────────────────────

# Home position — same as your known starting coordinates
HOME_X   = 12.249
HOME_Y   =  13.069
HOME_YAW = -0.1184

# ──────────────────────────────────────────────────────────────────────────────


class ReturnHomeNode(Node):

    def __init__(self):
        super().__init__('return_home_node')

        # Action client for Nav2 NavigateToPose
        self.action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.get_logger().info('Return home node started.')
        self.get_logger().info('Waiting for Nav2 NavigateToPose action server...')

        # Wait for Nav2 to be ready
        self.action_client.wait_for_server()
        self.get_logger().info('Nav2 is ready. Sending robot home...')

        # Send the home goal
        self.send_home_goal()

    # ── Build Goal ────────────────────────────────────────────────────────────

    def send_home_goal(self):
        """Build and send the NavigateToPose goal to home position."""

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        # Position
        goal_msg.pose.pose.position.x = HOME_X
        goal_msg.pose.pose.position.y = HOME_Y
        goal_msg.pose.pose.position.z = 0.0

        # Orientation — convert yaw to quaternion
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(HOME_YAW / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(HOME_YAW / 2.0)

        self.get_logger().info(
            f'Sending home goal: x={HOME_X}, y={HOME_Y}, yaw={HOME_YAW}'
        )

        # Send goal and register callbacks
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def goal_response_callback(self, future):
        """Called when Nav2 accepts or rejects the goal."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('✗ Home goal was rejected by Nav2.')
            rclpy.shutdown()
            return

        self.get_logger().info('Home goal accepted. Robot is navigating home...')

        # Wait for the result
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        """Called periodically with navigation feedback — distance remaining."""
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'Distance remaining: {distance:.2f} m')

    def result_callback(self, future):
        """Called when navigation is complete."""
        result = future.result()

        if result.status == 4:  # STATUS_SUCCEEDED = 4 in action_msgs
            self.get_logger().info('✓ Robot has successfully returned home.')
        else:
            self.get_logger().error(
                f'✗ Navigation failed with status: {result.status}. '
                'Check if path is clear or AMCL is still localized.'
            )

        rclpy.shutdown()


# ── Entry Point ────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = ReturnHomeNode()
    rclpy.spin(node)


if __name__ == '__main__':
    main()