#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

class WebcamLineFollow(Node):
	
	def __init__(self):
		super().__init__('webcam_line_follow')
		self.bridge = CvBridge()
		self.__camera__subscriber = self.create_subscription(
			Image, "/image_raw", self.listener_callback, 10
		)
		self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
		
		self.twist = Twist()	#Twistインスタンス生成
	
	def listener_callback(self, data):
		frame = self.bridge.imgmsg_to_cv2(data, "bgr8")
		
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		lower_yellow = np.array([20, 80, 10])
		upper_yellow = np.array([50, 255, 255])
		mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
		masked = cv2.bitwise_and(frame, frame, mask = mask)
		
		h, w = frame.shape[:2]
		RESIZE = (w//2, h//2)
		search_top = (h//4)*3
		search_bot = search_top + 20
		mask[0:search_top, 0:w] = 0
		mask[search_bot:h, 0:w] = 0
		
		M = cv2.moments(mask)	#maskにおける1の部分の重心
		if M['m00'] > 0:	#重心が存在する
			cx = int(M['m10']/M['m00'])	#重心のx座標
			cy = int(M['m01']/M['m00'])	#重心のy座標
			cv2.circle(frame, (cx, cy), 20, (0, 0, 255), -1)	#赤丸を画像に描画
			
			#P制御
			err = cx - w//2
			self.twist.linear.x = 0.2
			self.twist.angular.z = -float(err)/500
			self.cmd_vel_pub.publish(self.twist)
			#self.get_logger().info("vel:=%f" % (self.vel.Linear.x))
			#print('cx: ',cx)
			#print('cy: ',cy)
		
		else:
			self.twist.linear.x = 0.0
			self.twist.angular.z = 0.0
			self.cmd_vel_pub.publish(self.twist)
			

		#大きすぎるため，サイズ調整
		display_mask = cv2.resize(mask, RESIZE)
		display_masked = cv2.resize(masked, RESIZE)
		display_image = cv2.resize(frame, RESIZE)
		
		#display_v1 = cv2.vconcat([display_image, display_image])
		#display_v2 = cv2.vconcat([display_image, display_masked])
		#display_h = cv2.hconcat([display_v1,display_v2])
		
		cv2.imshow('window',display_image)
		cv2.imshow('MASK',display_mask)
		cv2.imshow('MASKED',display_masked)
		#cv2.imshow('SUM',display_h)
		cv2.waitKey(3)
		#self.get_logger().info('get image!')
		pass

def main():
	rclpy.init()
	webcam_line_follow = WebcamLineFollow()
	try:
		rclpy.spin(webcam_line_follow)
	except KeyboardInterrupt:
		pass
	rclpy.shutdown()
