#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import threading
import sys
import termios
import tty
import select
import time

class AutoDriveOpenLoop(Node):
    def __init__(self):
        super().__init__('auto_drive_open_loop')

        # Publisher for cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # --- Editable instructions ---
        # Each instruction is a dict: type, speed, duration in seconds
        self.instructions = [
            {'type': 'move', 'speed': 0.25, 'duration': 5.0},
            {'type': 'turn', 'speed': -0.75, 'duration': 4.2},
            {'type': 'move', 'speed': 0.25, 'duration': 2.0},
            {'type': 'turn', 'speed': -0.75, 'duration': 4.2},
            {'type': 'move', 'speed': 0.25, 'duration': 5.0},
        ]

        # State
        self.phase_index = 0
        self.phase_start_time = None
        self.paused_time_accum = 0.0  # total paused time in current phase
        self.pause_start_time = None   # timestamp when pause started

        # Pause flag
        self.paused = False

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Start keyboard listener
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
                            # Add paused duration to accumulator
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

    def control_loop(self):
        twist = Twist()

        if self.phase_index >= len(self.instructions):
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            return

        instr = self.instructions[self.phase_index]

        # Initialize phase start time
        if self.phase_start_time is None:
            self.phase_start_time = time.time()
            self.paused_time_accum = 0.0
            self.get_logger().info(f"Phase {self.phase_index}: {instr['type']} for {instr['duration']} sec")

        # Handle pause
        if self.paused:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            return

        # Compute elapsed time excluding pauses
        elapsed = time.time() - self.phase_start_time - self.paused_time_accum

        if elapsed < instr['duration']:
            if instr['type'] == 'move':
                twist.linear.x = instr['speed']
                twist.angular.z = 0.0
            elif instr['type'] == 'turn':
                twist.linear.x = 0.0
                twist.angular.z = instr['speed']
        else:
            # Phase finished
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
