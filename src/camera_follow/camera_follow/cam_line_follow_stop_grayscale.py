#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from realsense2_camera_msgs.msg import RGBD
from geometry_msgs.msg import Twist


COL, ROW = 848, 480
CV_FONT = cv2.FONT_HERSHEY_SIMPLEX
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
# 白線選択の条件
LINE_MIN_LEN = 50    # 最小長さ(pixel)
LINE_MIN_RATIO = 0.05    # 最小太さ W/L > 0.05 
LINE_MAX_RATIO = 0.3    # 最大太さ W/L < 0.3
class CONT_LINE:
	def __init__(self, contNo, direct, center, boxNP, lineC, lineL):
		self.contNo = contNo    # 輪郭番号
		self.direct = direct    # 縦線(0)/横線(1)
		self.center = center    # 重心位置[x,y]:pixel
		self.boxNP = boxNP        # 白線外形矩形[[x0,y0],[x1,y1],[x2,y2],[x3,y3]]:pixel
		self.lineC = lineC        # センターライン[[xs,ys],[xe,ye]]:pixel
		self.lineLength = lineL    # 白線長さ（boxの長辺)

class ImgReceiver(Node):
	
	def __init__(self):
		super().__init__('cam_line_follow')
		self.bridge = CvBridge()
		self.__camera__subscriber = self.create_subscription(
			RGBD, "/camera/camera/rgbd", self.listener_callback, 10
		)
		self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
		
		self.twist = Twist()	#Twistインスタンス生成
		self.frame = 0
		self.thresh = 160
		self.prevPosCol = int(COL / 2)
		self.prevOffsetL = 0
		self.prevOffsetR = 0
		self.prevL = 0
		self.prevR = 0
        
	def calcCenterPos(self, whiteLines, indexL, indexR):
		if indexL > -1 and indexR > -1:    # 2本の白線がある場合
			xsL = whiteLines[indexL].lineC[0][0]    # 左白線のxs
			xsR = whiteLines[indexR].lineC[0][0]    # 右白線のxs
			posCol = int((xsL + xsR) / 2)
			self.prevOffsetL = posCol - xsL
			self.prevOffsetR = posCol - xsR
		elif indexL > -1:    # 左の白線しかない場合
			xsL = whiteLines[indexL].lineC[0][0]    # 左白線のxs
			posCol = xsL + self.prevOffsetL    # 左白線から右へoffset
			xsR = posCol - self.prevOffsetR
		else:    # indexR > -1　右の白線しかない場合
			xsR = whiteLines[indexR].lineC[0][0]    # 右白線のxs
			posCol = xsR + self.prevOffsetR    # 右白線から左へoffset
			xsL = posCol - self.prevOffsetL
		return posCol, xsL, xsR
	def drawWhiteLines(self, whiteLines, indexL, indexR):
		# 選択された白線(indexL, indexR)を描画
		lines = [indexL, indexR]
		for i in range(2):
			if lines[i] != -1:
				boxNP = whiteLines[lines[i]].boxNP
				[[x0,y0],[x1,y1]] = whiteLines[lines[i]].lineC
				cv2.line(self.frame, (x0, y0), (x1, y1), GREEN, 2)        # センターライン
				cv2.drawContours(self.frame, [boxNP], 0, RED, 2)    # 認識白線を赤で囲む
		c1x, c1y = int(COL/2), 0
		c2x, c2y = int(COL/2), ROW    
		cv2.line(self.frame, (c1x, c1y), (c2x, c2y), YELLOW, 2)        # ラズマウス進行方向
		return
	def isThisWhiteLine(self, cnt, box, rectR, minLen, minRatio, maxRatio):
		# 白線候補を抽出、lineStat=True、中心線：cy = a * x + b 
		if rectR[1][0] > rectR[1][1]:
			boxL, boxW = rectR[1][0], rectR[1][1]
		else:
			boxL, boxW = rectR[1][1], rectR[1][0]
		if boxL < 0.001:
			boxRatio = 10000
		else:
			boxRatio = boxW / boxL
		if boxL >= minLen and (boxRatio > minRatio and boxRatio < maxRatio):
			lineStat = True
			M = cv2.moments(cnt)
			cx = int(M['m10']/M['m00'])        # col
			cy = int(M['m01']/M['m00'])        # row
			boxLen0 = (box[1][0] - box[0][0]) ** 2 + (box[1][1] - box[0][1]) ** 2
			boxLen1 = (box[2][0] - box[1][0]) ** 2 + (box[2][1] - box[1][1]) ** 2
			if boxLen0 < boxLen1:
				bp = [[0, 1], [2, 3]]
			else:
				bp = [[1, 2], [3, 0]]
			bpCx, bpCy = [0,0], [0,0]
			for k in range(2):
				bpCx[k] = int(box[bp[k][0]][0] + (box[bp[k][1]][0] - box[bp[k][0]][0]) / 2.)
				bpCy[k] = int(box[bp[k][0]][1] + (box[bp[k][1]][1] - box[bp[k][0]][1]) / 2.)
			vx = bpCx[1] - bpCx[0]
			vy = bpCy[1] - bpCy[0]
			# 白線の傾きvy/vx、点(bpCx[0],bpCy[0])を通る直線, cy = a * x + b
			if abs(vx) > 0.0:        # 垂直でない場合
				a, c = vy/vx, 1
				b = bpCy[0] - a * bpCx[0]
			else:        # 垂直(vx=0)の場合, x=-b
				a, b, c = 1, -bpCx[0], 0
		else:    # 基準を満たさないbox
			a, b, c, cx, cy = 0, 0, 0, 0, 0
			lineStat = False
		return lineStat, (cx, cy), a, b, c, boxL
	def selectVerticalLines(self, whiteLines):
		# 白線候補の縦線の中から２本選ぶ
		vLines = []
		for k in range(len(whiteLines)):
			if whiteLines[k].direct == 0:# 縦線だけを抽出
				vLines.append([whiteLines[k].lineLength, k])
		if len(vLines) >= 2:# 縦線が２本以上あった場合、長い白線から２本選択
			l0 = vLines.index(max(vLines))
			vLines[l0][0] = 0
			l1 = vLines.index(max(vLines))
			k0, k1 = vLines[l0][1], vLines[l1][1]
			xe0, xe1 = whiteLines[k0].lineC[1][0], whiteLines[k1].lineC[1][0]
			if xe1 < xe0:
				indexL, indexR = k1, k0
				if xe0 < COL/2 and xe1 < COL/2:
					indexL, indexR = k0, -1
				elif xe0 > COL/2 and xe1 > COL/2:
					indexL, indexR = -1, k1
			else:
				indexL, indexR = k0, k1
				if xe0 < COL/2 and xe1 < COL/2:
					indexL, indexR = k1, -1
				elif xe0 > COL/2 and xe1 > COL/2:
					indexL, indexR = -1, k0
			lineStat = True
		elif len(vLines) == 1:    # 縦白線が１本しか検出できない時
			k0 = vLines[0][1]
			if whiteLines[k0].lineC[1][0] >= COL/2:
				indexR, indexL = k0, -1
			else:
				indexR, indexL = -1, k0
			lineStat = True
		else: # 縦白線が認識されなかった時
			lineStat, indexL, indexR = False, -1, -1
		return lineStat, indexL, indexR
	def detectWhiteLines(self):
		# frameの中から、白線の輪郭を検出して、白線候補を検出。
		imgray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)    # 入力画像をグレースケール化
		cv2.imshow('gray',imgray)
		retVal, imgThresh = cv2.threshold(imgray, 90, 255, 1)    # グレースケール画像を閾値で抜き出し
		retVal, imgThresh1 = cv2.threshold(imgray, 60, 255, 0)    # グレースケール画像を閾値で抜き出し
		imgThresh2 = cv2.bitwise_and(imgThresh, imgThresh, mask=imgThresh1)
		contours, hierarchy = cv2.findContours(imgThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		#cv2.imshow('sikiichi',imgThresh)
		#cv2.imshow('sikiichi1',imgThresh1)
		cv2.imshow('sikiichi2',imgThresh2)
		whiteLines=[]
		for i in range(len(contours)):
			if hierarchy[0][i][3] > 0:        # hierarchyの親がなし(-1)、親parentが０の輪郭のみ抽出
				continue
			cnt = contours[i]
			rectR = cv2.minAreaRect(cnt)    # 回転を考慮した外接矩形　rectR : ((x,y), (w,h), angle) 
			box = cv2.boxPoints(rectR)    # 4角のコーナーの座標
			lineStat, (cx, cy), a, b, c, lineLen = self.isThisWhiteLine(cnt, box, rectR, LINE_MIN_LEN, LINE_MIN_RATIO, LINE_MAX_RATIO)
				# 白線の場合lineStat = True、白線の中心線cy = a * x + b
			if not lineStat:    # 白線でない場合
				continue
			boxNP = np.int0(box)    # 整数に
			if ( abs(a) > 0.3 ):    # 縦方向の白線
				direct = 0
				x0, y0, x1, y1 = int(-b / a), 0, int((c * ROW - b) / a), ROW
			else:        #　横方向の白線
				direct = 1
				x0, y0, x1, y1 = 0, int(b), COL, int(a * COL + b)
			whiteLines.append(CONT_LINE(i, direct, [cx,cy], boxNP, [[x0,y0],[x1,y1]], lineLen))
		return whiteLines
	def rasPosition(self, frame):
		self.frame = frame
		whiteLines = self.detectWhiteLines()    # 白線認識
		lineStat, indexL, indexR = self.selectVerticalLines(whiteLines)    #２本の白線を選択
		if lineStat:    # 1本 or ２本選択できた時
			self.drawWhiteLines(whiteLines, indexL, indexR)    # 左右白線の赤枠、センターラインなどを描画
			posCol, xsL, xsR = self.calcCenterPos(whiteLines, indexL, indexR)    # 白線センター位置の計算
		else:
			posCol = self.prevPosCol
			xsL, xsR = self.prevL, self.prevR
		cv2.circle(self.frame,(posCol, 20), 4, RED, -1)        # 白線中央位置の描画
		strData = "{:5d}".format(int(posCol - COL/2))
		cv2.putText(self.frame, strData, (posCol, 50), CV_FONT, 0.5, GREEN, 1, cv2.LINE_AA, False)
		self.prevPosCol = posCol
		self.prevL = xsL
		self.prevR = xsR
		return posCol, self.frame

	def listener_callback(self, data):
		frame = self.bridge.imgmsg_to_cv2(data.rgb, "bgr8")
		depth = self.bridge.imgmsg_to_cv2(data.depth, "passthrough")
		
		self.frame = self.bridge.imgmsg_to_cv2(data.rgb, "bgr8")
		posCol, frame = self.rasPosition(frame) 
		
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		lower_yellow = np.array([20, 80, 10])
		upper_yellow = np.array([50, 255, 255])
		mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
		masked = cv2.bitwise_and(frame, frame, mask = mask)
		
		h, w = frame.shape[:2]
		#print('h:=',h) #D405 480
		#print('w:=',w) #D405 848
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
			#cv2.circle(frame, (cx, cy), 20, (0, 0, 255), -1)	#赤丸を画像に描画
			
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
				err = posCol - w//2
				self.twist.linear.x = 0.2
				self.twist.angular.z = -float(err)/500
			self.cmd_vel_pub.publish(self.twist)
			#distance = depth[cy, cx]
			#self.get_logger().info("vel:=%f" % (self.vel.Linear.x))
			#print('cx: ',cx)
			#print('cy: ',cy)
			#print('distance: ',distance)
		
		else:
			self.twist.linear.x = 0.0
			self.twist.angular.z = 0.2
			self.cmd_vel_pub.publish(self.twist)
			

		#大きすぎるため，サイズ調整
		display_mask = cv2.resize(self.frame, RESIZE)
		display_masked = cv2.resize(masked, RESIZE)
		display_image = cv2.resize(frame, RESIZE)
		
		#display_v1 = cv2.vconcat([display_image, display_image])
		#display_v2 = cv2.vconcat([display_image, display_masked])
		#display_h = cv2.hconcat([display_v1,display_v2])
		
		cv2.imshow('window',self.frame)
		#cv2.imshow('MASK',display_mask)
		#cv2.imshow('MASKED',display_masked)
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
