#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import yaml
import math

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowWaypoints
from rclpy.action import ActionClient
from tf_transformations import quaternion_from_euler


class WaypointSender(Node):

    def __init__(self):
        super().__init__('waypoint_sender')

        self.client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

        with open('/home/intern1/rpp_path.yaml', 'r') as f:
            self.points = yaml.safe_load(f)

    def send_waypoints(self):

        goal = FollowWaypoints.Goal()

        for p in self.points:

            pose = PoseStamped()
            pose.header.frame_id = "map"

            pose.pose.position.x = p['x']
            pose.pose.position.y = p['y']

            q = quaternion_from_euler(0,0,p['yaw'])

            pose.pose.orientation.x = q[0]
            pose.pose.orientation.y = q[1]
            pose.pose.orientation.z = q[2]
            pose.pose.orientation.w = q[3]

            goal.poses.append(pose)

        self.client.wait_for_server()

        self.future = self.client.send_goal_async(goal)
        self.get_logger().info("Waypoints sent")


def main():

    rclpy.init()
    node = WaypointSender()

    node.send_waypoints()

    rclpy.spin(node)


if __name__ == '__main__':
    main()