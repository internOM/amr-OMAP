#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import threading
import sys
import termios
import tty
import select
import time
import numpy as np

class AutoDriveOpenLoop(Node):
    def __init__(self):
        super().__init__('auto_drive_open_loop')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.instructions = [
            {'type': 'move', 'speed': 0.25, 'duration': 28},
            {'type': 'turn', 'speed': -0.25, 'duration': 4.2},
            #{'type': 'move', 'speed': 0.75, 'duration': 48.0},
        ]

        self.phase_index = 0
        self.phase_start_time = None
        self.paused_time_accum = 0.0
        self.pause_start_time = None

        self.paused = False
        self.obstacle_paused = False

        self.obstacle_distance_thresh = 0.45
        self.bubble_angle = np.deg2rad(15)
        self.closest_distance = np.nan

        self.slow_distance = 0.30
        self.stop_distance = 0.15

        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.control_loop)

        self.keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.keyboard_thread.start()

    def keyboard_listener(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == 'x':
                        self.paused = not self.paused
                        if self.paused:
                            self.pause_start_time = time.time()
                        else:
                            self.paused_time_accum += time.time() - self.pause_start_time
                            self.pause_start_time = None
                        state = "PAUSED" if self.paused else "RESUMED"
                        self.get_logger().info(f"Safety toggle (x): {state}")
                    elif key.lower() == 'q':
                        self.get_logger().info("Shutdown command (q) received.")
                        rclpy.shutdown()
                        break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def scan_callback(self, scan: LaserScan):
        num_points = len(scan.ranges)
        angles = np.linspace(scan.angle_min, scan.angle_max, num_points)
        mask = np.abs(angles) <= self.bubble_angle / 2

        ranges = np.array(scan.ranges)
        ranges[~mask] = np.nan
        ranges[ranges < 0.05] = np.nan

        in_range_indices = np.where(ranges < self.obstacle_distance_thresh)[0]

        if len(in_range_indices) > 0:
            closest_idx = in_range_indices[np.nanargmin(ranges[in_range_indices])]
            self.closest_distance = ranges[closest_idx]
            closest_angle = angles[closest_idx]

            if not self.obstacle_paused:
                self.obstacle_paused = True
                self.paused = True
                self.pause_start_time = time.time()
                self.get_logger().warn(f"Obstacle detected in front! Pausing...")
                self.get_logger().warn(f"Closest obstacle at distance: {self.closest_distance:.2f} m, angle: {np.rad2deg(closest_angle):.1f}°")
        else:
            self.closest_distance = np.nan
            if self.obstacle_paused:
                self.obstacle_paused = False
                self.paused = False
                if self.pause_start_time is not None:
                    self.paused_time_accum += time.time() - self.pause_start_time
                    self.pause_start_time = None
                self.get_logger().info("Obstacle cleared. Resuming...")

    def control_loop(self):
        twist = Twist()

        # --- Immediate stop for any pause ---
        if self.paused:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            return

        if self.phase_index >= len(self.instructions):
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            return

        instr = self.instructions[self.phase_index]

        if self.phase_start_time is None:
            self.phase_start_time = time.time()
            self.paused_time_accum = 0.0
            self.get_logger().info(f"Phase {self.phase_index}: {instr['type']} for {instr['duration']} sec")

        linear_speed = instr['speed'] if instr['type'] == 'move' else 0.0
        angular_speed = instr['speed'] if instr['type'] == 'turn' else 0.0

        slow_factor = 1.0
        if instr['type'] == 'move' and not np.isnan(self.closest_distance):
            if self.closest_distance < self.stop_distance:
                linear_speed = 0.0
                slow_factor = 0.01
            elif self.closest_distance < self.slow_distance:
                linear_speed *= (self.closest_distance - self.stop_distance) / (self.slow_distance - self.stop_distance)
                slow_factor = linear_speed / instr['speed']

        twist.linear.x = linear_speed
        twist.angular.z = angular_speed

        elapsed = time.time() - self.phase_start_time - self.paused_time_accum
        adjusted_elapsed = elapsed * slow_factor

        if adjusted_elapsed >= instr['duration']:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.phase_index += 1
            self.phase_start_time = None
            self.paused_time_accum = 0.0
            self.pause_start_time = None

        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = AutoDriveOpenLoop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
