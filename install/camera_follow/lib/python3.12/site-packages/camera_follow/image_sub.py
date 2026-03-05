#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

class ImgReceiver(Node):
	
	def __init__(self):
		super().__init__('image_sub')
		self.subscription = self.create_subscription(
			Image,
			'image_raw',
			self.image_callback,
			qos_profile_sensor_data)
	
	def image_callback(self, data):
		self.get_logger().info('get image!')
		pass

def main():
	rclpy.init()
	image_sub = ImgReceiver()
	try:
		rclpy.spin(image_sub)
	except KeyboardInterrupt:
		pass
	rclpy.shutdown()
