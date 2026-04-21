#!/usr/bin/env python3

import os
import yaml
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import String

POSE_FILE = '/home/intern1/ros2_ws/src/amr_ws/waypoints/amcl_logger.yaml'

class PosePersistenceNode(Node):
    def __init__(self):
        super().__init__('pose_persistence_node')
        
        self.latest_pose = None
        
        # Subscribe to amcl_pose to always know the latest pose
        self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._amcl_cb,
            10
        )
        
        # Subscribe to fault trigger
        self.create_subscription(
            String,
            '/amr/fault_trigger',
            self._fault_trigger_cb,
            10
        )
        
        # Publisher to initialpose to seed AMCL on restart
        self._initialpose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            10
        )
        
        # Give publisher a little time to set up before publishing
        self.create_timer(1.0, self._startup_routine)
        self._startup_done = False
        
        self.get_logger().info('Pose persistence node started.')

    def _amcl_cb(self, msg: PoseWithCovarianceStamped):
        self.latest_pose = msg
        
    def _fault_trigger_cb(self, msg: String):
        if not self.latest_pose:
            self.get_logger().warn('Received fault trigger, but no AMCL pose is known yet!')
            return
            
        self.get_logger().info(f'Fault trigger received: {msg.data}. Saving pose to disk.')
        
        pose_dict = {
            'header': {
                'frame_id': self.latest_pose.header.frame_id,
            },
            'pose': {
                'pose': {
                    'position': {
                        'x': float(self.latest_pose.pose.pose.position.x),
                        'y': float(self.latest_pose.pose.pose.position.y),
                        'z': float(self.latest_pose.pose.pose.position.z),
                    },
                    'orientation': {
                        'x': float(self.latest_pose.pose.pose.orientation.x),
                        'y': float(self.latest_pose.pose.pose.orientation.y),
                        'z': float(self.latest_pose.pose.pose.orientation.z),
                        'w': float(self.latest_pose.pose.pose.orientation.w),
                    }
                },
                'covariance': [float(val) for val in self.latest_pose.pose.covariance]
            }
        }
        
        os.makedirs(os.path.dirname(POSE_FILE), exist_ok=True)
        with open(POSE_FILE, 'w') as f:
            yaml.dump(pose_dict, f, default_flow_style=False)
            
        self.get_logger().info(f'Pose successfully saved to {POSE_FILE}')
        
    def _startup_routine(self):
        if self._startup_done:
            return
        self._startup_done = True
        
        if os.path.exists(POSE_FILE):
            self.get_logger().info(f'Found saved pose at {POSE_FILE}. Loading and publishing to /initialpose.')
            try:
                with open(POSE_FILE, 'r') as f:
                    pose_dict = yaml.safe_load(f)
                    
                msg = PoseWithCovarianceStamped()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = pose_dict['header']['frame_id']
                
                msg.pose.pose.position.x = pose_dict['pose']['pose']['position']['x']
                msg.pose.pose.position.y = pose_dict['pose']['pose']['position']['y']
                msg.pose.pose.position.z = pose_dict['pose']['pose']['position']['z']
                
                msg.pose.pose.orientation.x = pose_dict['pose']['pose']['orientation']['x']
                msg.pose.pose.orientation.y = pose_dict['pose']['pose']['orientation']['y']
                msg.pose.pose.orientation.z = pose_dict['pose']['pose']['orientation']['z']
                msg.pose.pose.orientation.w = pose_dict['pose']['pose']['orientation']['w']
                
                msg.pose.covariance = pose_dict['pose']['covariance']
                
                self._initialpose_pub.publish(msg)
                self.get_logger().info('Published recovered pose to /initialpose.')
                
                # Delete the file so it is not reused on next normal startup
                os.remove(POSE_FILE)
                self.get_logger().info('Deleted saved pose file.')
            except Exception as e:
                self.get_logger().error(f'Failed to load saved pose: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = PosePersistenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
