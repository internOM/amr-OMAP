#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# ●対象機種:
#       MOBI-CON
#
# ●コントローラ設定:
#
# ●launchファイル設定:
#       com:="/dev/ttyUSB0" topicID:=1 baudrate:=230400 updateRate:=1000 firstGen:="" secondGen:="1," globalID:="-1" axisNum:="1"
#
# ●処理内容:
#       Read/Writeにより速度情報をMOBI-CONに送信し、MOBI-CONから位置データを受信する
#       

import os
import sys
import numpy as np
import math

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from rclpy.node import Node
import time
import rclpy
from mvc01_msgs.msg import IO
from mvc01_msgs.msg import Response
from utils import const
from utils.clientasync import ClientAsync
from om_msgs.msg import Query
from om_msgs.msg import Response
from om_msgs.msg import State
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import String
from geometry_msgs.msg import Twist,PoseStamped,TransformStamped,Pose,Point,Quaternion
from std_msgs.msg import Header
from nav_msgs.msg import Path, Odometry
from tf2_ros.transform_broadcaster import TransformBroadcaster

# グローバル変数
_state_driver = 0  # 0:通信可能 1:通信中
_state_mes = 0  # 0:メッセージなし 1:メッセージ到達 2:メッセージエラー
_state_error = 0  # 0:エラーなし 1:無応答 2:例外応答
msg = Query()
odom_pose = Pose()
odom_header = Header()
odom_twist = Twist()
odom = Odometry()
_x_spd = 0
_y_spd = 0
_z_ang = 0
_pos_x = 0
_pos_y = 0
_pos_z = 0
_quat_x = 0
_quat_y = 0
_quat_z = 0
_quat_w = 0
_yaw = 0


# 定数
const.QUEUE_SIZE = 1


class MobiconSubscription(Node):
    def __init__(self):
        super().__init__("mobiCon_sub")
        self.sub1 = self.create_subscription(
            Response, "om_response0", self.response_callback, const.QUEUE_SIZE
        )
        self.sub2 = self.create_subscription(
            State, "om_state0", self.state_callback, const.QUEUE_SIZE
        )
        self.sub3 = self.create_subscription(
            Twist, "cmd_vel", self.cmdVel_callback, 10
        )
        self.ioPub = self.create_publisher(
			IO, 'mvc01_IO', 10
		)
        self.odomPub = self.create_publisher(
            Odometry, "/odom", 10
        )
        self._tf_Odompublisher = TransformBroadcaster(self)
        self.ca = ClientAsync("sub")
        self.io = IO()
        
        #odom_header.stamp = self.get_clock().now().to_msg()
        odom_header.frame_id = "map"
        #odom_header.child_frame_id = "base_link"
        odom_pose.position.x = 0.0
        odom_pose.position.y = 0.0
        odom_pose.position.z = 0.0
        #update_quaternion = quaternion_from_euler(0,0,float(_yaw))
        odom_pose.orientation.x = 0.0
        odom_pose.orientation.y = 0.0
        odom_pose.orientation.z = 0.0
        odom_pose.orientation.w = 0.0
        

        #self.odomPub.publish(odom_pose)
        
        odom.header = odom_header
        odom.child_frame_id = "base_link"
        odom.pose.pose = odom_pose
        odom.twist.twist = odom_twist
        
        self.odomPub.publish(odom)
        

    def __del__(self):
        self.ca.destroy_node()

    def response_callback(self, res):
        global _pos_x, _pos_y, _pos_z
        global _ori_x, _ori_y, _ori_z, _ori_w
        global _yaw
        # ID Shareモード、function code=0x17のとき
        if (res.slave_id == 1) & (res.func_code == 0x17):
            _pos_x = float(res.data[0]/1000.0)
            _pos_y = float(res.data[1]/1000.0)
            _pos_z = float(0.0)
            _quat_x = float(0.0)
            _quat_y = float(0.0)
            _quat_z = float(0.0)
            _quat_w = float(0.0)
            _yaw = float(res.data[2]/1000000.0)
            #print("{:20}  {:20}".format("", "Mobile Robot Controller"))
            #print("--------------------------------------------")
            #print("{:20}: {:10}".format("PosX", res.data[0]))
            #print("{:20}: {:10}".format("PosY", res.data[1]))
            #print("{:20}: {:10}".format("PosAng.", res.data[2]))
            
            odom_header.stamp = self.get_clock().now().to_msg()
            #odom_header.frame_id = "map"
            #odom_header.child_frame_id = "base_link"
            odom_pose.position.x = float(_pos_x)
            odom_pose.position.y = float(_pos_y)
            odom_pose.position.z = float(_pos_z)
            update_quaternion = quaternion_from_euler(0,0,float(_yaw))
            odom_pose.orientation.w = update_quaternion[0]
            odom_pose.orientation.x = update_quaternion[1]
            odom_pose.orientation.y = update_quaternion[2]
            odom_pose.orientation.z = update_quaternion[3]
            
            odom_twist.linear.x = float(res.data[5]/1000.0)
            odom_twist.linear.y = float(res.data[7]/1000.0)
            odom_twist.angular.z = float(res.data[6]/1000000.0)
            
            #update timestamp
            odom.header = odom_header
            #odom.child_frame_id = "base_link"
            odom.pose.pose = odom_pose
            odom.twist.twist = odom_twist
            
            #update TF
            map_frame = TransformStamped()
            map_frame.header.stamp = self.get_clock().now().to_msg()
            map_frame.header.frame_id = "odom"
            map_frame.child_frame_id = "base_link"
            map_frame.transform.translation.x = odom_pose.position.x
            map_frame.transform.translation.y = odom_pose.position.y
            map_frame.transform.translation.z = odom_pose.position.z
            map_frame.transform.rotation.w = odom_pose.orientation.w
            map_frame.transform.rotation.x = odom_pose.orientation.x
            map_frame.transform.rotation.y = odom_pose.orientation.y
            map_frame.transform.rotation.z = odom_pose.orientation.z
            
            self.odomPub.publish(odom)
            self._tf_Odompublisher.sendTransform(map_frame)
            
            self.io.output = int(res.data[9])
            self.ioPub.publish(self.io)
            
            
    def state_callback(self, res):
        global _state_driver
        global _state_mes
        global _state_error
        _state_driver = res.state_driver
        _state_mes = res.state_mes
        _state_error = res.state_error

    def cmdVel_callback(self, msg):
        global _x_spd, _y_spd, _z_ang
        _x_spd = msg.linear.x * 1000.0
        _y_spd = msg.linear.y * 1000.0
        _z_ang = msg.angular.z * 1000000.0
        #print("{:20}: {:10}".format("Speed Vx [m/s]", msg.linear.x))
        #print("{:20}: {:10}".format("Speed Vy [m/s]", msg.linear.y))
        #print("{:20}: {:10}".format("Speed ω [rad/s]", msg.angular.z))

class MobiconPublisher(Node):
    def __init__(self):
        super().__init__("mobiCon_pub")
        self.seq = 0
        self.pub = self.create_publisher(Query, "om_query0", const.QUEUE_SIZE)

        self.timer = self.create_timer(0.05, self.timer_callback)
        self.ca = ClientAsync("pub")

    def __del__(self):
        self.ca.destroy_node()

    def timer_callback(self):
        if _state_driver == 1:
            return
        if self.seq == 0:
            self.seq = 1
        elif self.seq == 1:
            self.set_data()
            self.seq = 2
        elif self.seq == 2:
            self.set_drive_operation()
            self.seq = 2
        else:
            pass


    def set_drive_operation(self):
        global msg
        global odom_trans
        global _x_spd, _y_spd, _z_ang
        global _pos_x, _pos_y, _pos_z
        global _ori_x, _ori_y, _ori_z, _ori_w
        global _yaw
        print("{:20}: {:10}".format("Speed Vx [m/s]", _x_spd/1000.0))
        print("{:20}: {:10}".format("Speed Vy [m/s]", _y_spd/1000.0))
        print("{:20}: {:10}".format("Speed ω [rad/s]", _z_ang/1000000.0))
        # vω制御モードで動作させる
        msg.slave_id = 1  # スレーブID
        msg.func_code = 2  # ファンクションコード: 2:Read/Write
        msg.read_addr = 4928  # 読み出すアドレスの起点
        msg.read_num = 10  # 読み出すデータ数*軸数=24
        msg.write_addr = 4960  # 書き込むアドレスの起点
        msg.write_num = 5  # 書き込むデータ数*軸数=12
        # 送信データ
        msg.data[0] = 1  # DD運転方式 1:vw制御
        msg.data[1] = _x_spd  # DD前後並進速度
        msg.data[2] = _z_ang # DD角速度
        msg.data[3] = _y_spd  # DD左右並進速度
        msg.data[4] = 1  # 反映トリガ
        # 配信
        self.pub.publish(msg)


    # 各軸のID Shareモードの設定を行う
    def set_data(self):
        global msg

        # ユニキャストモードで通信するため、global_idを-1に設定する
        self.ca.set_parameters_from_another_node("om_node", "global_id", -1)

        # 1軸目の設定
        msg.slave_id = 1  # 書き込むドライバのスレーブID
        msg.func_code = 1  # 1:Write
        msg.write_addr = 0x1300  # 書き込みの起点：Share Control Global IDのアドレス
        msg.write_num = 32  # 書き込む数
        msg.data[0] = 1069  # Read data[0] → 現在位置(検出)X[1=0.001m]
        msg.data[1] = 1070  # Read data[1] → 現在位置(検出)Y[1=0.001m]
        msg.data[2] = 1071  # Read data[2] → 現在位置(検出)θ[1=0.000001rad]
        msg.data[3] = 163  # Read data[3] → 電源電圧[1=0.1V]
        msg.data[4] = 169  # Read data[4] → Bootからの経過時間[1=1ms]
        msg.data[5] = 1246 # Read data[5] → 前後並進速度(検出) Vx
        msg.data[6] = 1247  # Read data[6] → 現在角速度(検出) ω
        msg.data[7] = 1248  # Read data[7] → 左右並進速度(検出) Vy
        msg.data[8] = 62  # Read data[8] → Remote-IO-Input
        msg.data[9] = 63  # Read data[9] → Remote-IO-Output
        msg.data[10] = 0  # Read data[10] → 
        msg.data[11] = 0  # Read data[11] → 
        msg.data[12] = 0  # Read data[0] → 
        msg.data[13] = 0  # Read data[1] → 
        msg.data[14] = 0  # Read data[2] → 
        msg.data[15] = 0  # Read data[3] → 

        msg.data[16] = 993 # Write data[0] → DD運転方式
        msg.data[17] = 994 # Write data[1] → DD前後並進速度(Vx)
        msg.data[18] = 995 # Write data[2] → DD角速度(ω)
        msg.data[19] = 996 # Write data[3] → DD左右並進速度(Vy)
        msg.data[20] = 1015  # Write data[4] → 反映トリガ
        msg.data[21] = 0  # Write data[5] →
        msg.data[22] = 0  # Write data[6] →
        msg.data[23] = 0  # Write data[7] →
        msg.data[24] = 0  # Write data[8] →
        msg.data[25] = 0  # Write data[9] →
        msg.data[26] = 0  # Write data[10] →
        msg.data[27] = 0  # Write data[11] →
        msg.data[28] = 0  # Write data[12] →
        msg.data[29] = 0  # Write data[13] →
        msg.data[30] = 0  # Write data[14] →
        msg.data[31] = 0  # Write data[15] →

        self.pub.publish(msg)  # 配信
        


    # t[s]待機する
    def wait(self, t):
        time.sleep(t)
        while _state_driver == 1:
            pass

def euler_from_quaternion(x,y,z,w):
    sinr_cosp = 2* (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctans(sinr_cosp, cosr_cosp)
    
    sinp = 2 * (w * z + x * y)
    pitch = np.arcsin(sinp)
    
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 -2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)
    
    return roll, pitch, yaw
		
def quaternion_from_euler(roll, pitch, yaw):
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    
    q = [0] *4
    q[0] = cy * cp * cr + sy * sp * sr
    q[1] = cy * cp * sr - sy * sp * cr
    q[2] = sy * cp * sr + cy * sp * cr
    q[3] = sy * cp * cr - cy * sp * sr
    
    return q



def main(args=None):
    rclpy.init(args=args)
    try:
        pub = MobiconPublisher()
        sub = MobiconSubscription()
        executor = MultiThreadedExecutor()
        executor.add_node(pub)
        executor.add_node(sub)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        pub.destroy_node()
        sub.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
