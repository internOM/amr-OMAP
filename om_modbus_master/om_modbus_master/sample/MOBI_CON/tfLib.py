#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import math

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
