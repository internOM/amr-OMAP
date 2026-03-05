#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from realsense2_camera_msgs.msg import RGBD
from geometry_msgs.msg import Twist

class ImgReceiver(Node):
	
	def __init__(self):
		super().__init__('cam_line_follow')
		self.bridge = CvBridge()
		self.__camera__subscriber = self.create_subscription(
			RGBD, "/camera/camera/rgbd", self.listener_callback, 10
		)
		self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
		
		self.twist = Twist()	#Twistインスタンス生成
	
	def listener_callback(self, data):
		frame = self.bridge.imgmsg_to_cv2(data.rgb, "bgr8")
		depth = self.bridge.imgmsg_to_cv2(data.depth, "passthrough")
		
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		lower_yellow = np.array([20, 80, 10])
		upper_yellow = np.array([50, 255, 255])
		mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
		masked = cv2.bitwise_and(frame, frame, mask = mask)
		
		h, w = frame.shape[:2]
		print('h:=',h) #D405 480
		print('w:=',w) #D405 848
		RESIZE = (w//2, h//2)
		search_top = (h//4)*3
		search_bot = search_top + 20
		mask[0:search_top, 0:w] = 0
		mask[search_bot:h, 0:w] = 0
		#距離によるマスク
		#for hM in range(search_top,search_bot):
		#	for wM in range(0,w):
		#		distance = depth[hM, wM]
		#		if distance == 0 or 400 < distance:
		#			mask[hM, wM] = 0
		
		M = cv2.moments(mask)	#maskにおける1の部分の重心
		if M['m00'] > 0:	#重心が存在する
			cx = int(M['m10']/M['m00'])	#重心のx座標
			cy = int(M['m01']/M['m00'])	#重心のy座標
			cv2.circle(frame, (cx, cy), 20, (0, 0, 255), -1)	#赤丸を画像に描画
			
			for f in range(100,w-100):
				distance = depth[h//2, f]
				#print('distance: ',distance)
				if 0 < distance < 300:#mm #405のみ対応
					mode = "stop"
					cv2.circle(frame, (f, h//2), 20, (0, 255, 0), -1)	#緑丸を画像に描画
					break
				else:
					mode = "run"
				
			if mode == "stop":
				self.twist.linear.x = 0.0
				self.twist.angular.z = 0.0
			else:
				#P制御
				err = cx - w//2
				print('err: ',err)
				#self.twist.linear.x = 0.667
				if err == 0:
					self.twist.linear.x = 0.667
				else:
					self.twist.linear.x = 0.667 - float(abs(err) )/600.0 #0.667 - (abs(float(err))/1000)
				self.twist.angular.z = -float(err)/400
			self.cmd_vel_pub.publish(self.twist)
			#distance = depth[cy, cx]
			#self.get_logger().info("vel:=%f" % (self.vel.Linear.x))
			#print('cx: ',cx)
			#print('cy: ',cy)
			#print('distance: ',distance)
		
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
	image_sub = ImgReceiver()
	try:
		rclpy.spin(image_sub)
	except KeyboardInterrupt:
		pass
	rclpy.shutdown()
