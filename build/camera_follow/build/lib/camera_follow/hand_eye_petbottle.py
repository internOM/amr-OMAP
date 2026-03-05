#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from realsense2_camera_msgs.msg import RGBD
from mrc01_msgs.msg import DDmove

class ImgReceiver(Node):
	
	def __init__(self):
		super().__init__('cam_line_search')
		self.bridge = CvBridge()
		self.__camera__subscriber = self.create_subscription(
			RGBD, "/camera/camera/rgbd", self.listener_callback, 10
		)
		self._publisher = self.create_publisher(
			DDmove,'mrc01_ddmove', 20
		)
		self.pos = DDmove()
	
	def listener_callback(self, data):
		frame = self.bridge.imgmsg_to_cv2(data.rgb, "bgr8")
		depth = self.bridge.imgmsg_to_cv2(data.depth, "passthrough")
		
		#距離でmask
		mask3 = (0 == depth) | (500 < depth)
		depth_fil = np.where(np.broadcast_to(mask3[:,:,None],frame.shape),0 ,frame)
		
		#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		hsv = cv2.cvtColor(depth_fil, cv2.COLOR_BGR2HSV)
		lower_yellow = np.array([0, 64, 0])
		upper_yellow = np.array([30, 255, 255])
		lower1_yellow = np.array([150, 64, 0])
		upper1_yellow = np.array([180, 255, 255])
		mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
		mask1 = cv2.inRange(hsv, lower1_yellow, upper1_yellow)
		mask2 = mask + mask1
		
		h, w = frame.shape[:2]
		RESIZE = (w//2, h//2)
		search_top = (h//4)*3
		search_bot = search_top + 20
		#mask[0:search_top, 0:w] = 0
		#mask[search_bot:h, 0:w] = 0
		#距離によるマスク
		#for hM in range(0,h):
		#	for wM in range(0,w):
		#		distance = depth[hM, wM]
		#		if distance == 0 or 500 < distance:
		#			mask2[hM, wM] = 0
		masked = cv2.bitwise_and(frame, frame, mask=mask2)
		
		M = cv2.moments(mask2)	#maskにおける1の部分の重心
		if M['m00'] > 0:	#重心が存在する
			cx = int(M['m10']/M['m00'])	#重心のx座標
			cy = int(M['m01']/M['m00'])	#重心のy座標
			cv2.circle(frame, (cx, cy), 20, (0, 0, 255), -1)	#赤丸を画像に描画
			
			if self.pos.trg == 0:
				self.pos.trg = 1
			else:
				self.pos.trg = 0
			self.pos.cmdtype = 30
			self.pos.posz = 100.0	#mm
			self.pos.vel = 20.0	#mm/s
			self.pos.acc = 1200.0	#mm/s2
			self.pos.dec = 1200.0	#mm/s2
			self.pos.camnum = 1
			self.pos.camposx = float(cx)
			self.pos.camposy = float(cy)
			
			self._publisher.publish(self.pos)

		#大きすぎるため，サイズ調整
		display_mask = cv2.resize(mask2, RESIZE)
		display_masked = cv2.resize(masked, RESIZE)
		display_image = cv2.resize(frame, RESIZE)
		
		cv2.imshow('window',display_image)
		cv2.imshow('MASK',display_mask)
		cv2.imshow('MASKED',display_masked)
		cv2.waitKey(3)
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
