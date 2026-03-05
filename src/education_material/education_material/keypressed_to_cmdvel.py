#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import TwistStamped
import threading
import time
import sys, termios, tty, select, atexit, signal, os

class KeyboardToTwistStamped(Node):
    def __init__(self):
        super().__init__('keyboard_to_twist_stamped')

        # Parameters
        self.robot_ns = self.declare_parameter('robot_ns', 'tb1').value  # default tb1
        self.linear_speed = self.declare_parameter('linear_speed', 2.0).value
        self.angular_speed = self.declare_parameter('angular_speed', 1.0).value

        # Publishers & Subscriptions
        self.pub = self.create_publisher(TwistStamped, f'{self.robot_ns}/cmd_vel', 10)
        self.sub = self.create_subscription(String, 'key_input', self.key_callback, 10)

        # Keyboard handling
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        atexit.register(self.restore_terminal)
        signal.signal(signal.SIGINT, self._sigint_handler)

        # Key tracking
        self.key_set = set()
        self.lock = threading.Lock()

        # Continuous publishing
        self.timer = self.create_timer(0.05, self.publish_twist)  # 20 Hz
        self._running = True

        self.get_logger().info(f'Ready for fluid WASD control on {self.robot_ns}.')

    def _sigint_handler(self, signum, frame):
        self.shutdown_node()

    def restore_terminal(self):
        try:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        except Exception:
            pass

    def key_callback(self, msg: String):
        key = msg.data.upper()

        with self.lock:
            if key in ['W', '<UP>']:
                self.key_set.add('W')
            elif key in ['S', '<DOWN>']:
                self.key_set.add('S')
            elif key in ['A', '<LEFT>']:
                self.key_set.add('A')
            elif key in ['D', '<RIGHT>']:
                self.key_set.add('D')
            elif key == 'Q':
                self.get_logger().info('Detected "Q". Shutting down node.')
                self.shutdown_node()
            else:
                return

        # Remove key after 0.2 sec if not pressed again (simulate release)
        threading.Thread(target=self._remove_key_later, args=(key, 0.2), daemon=True).start()

    def _remove_key_later(self, key, delay):
        time.sleep(delay)
        with self.lock:
            self.key_set.discard(key)

    def publish_twist(self):
        twist_stamped = TwistStamped()
        twist_stamped.header.stamp = self.get_clock().now().to_msg()
        twist_stamped.header.frame_id = 'base_link'

        with self.lock:
            # WASD logic
            if 'W' in self.key_set:
                twist_stamped.twist.linear.x += self.linear_speed
            if 'S' in self.key_set:
                twist_stamped.twist.linear.x -= self.linear_speed
            if 'A' in self.key_set:
                twist_stamped.twist.angular.z += self.angular_speed
            if 'D' in self.key_set:
                twist_stamped.twist.angular.z -= self.angular_speed

        self.pub.publish(twist_stamped)

    def shutdown_node(self):
        if not self._running:
            return
        self._running = False
        self.restore_terminal()
        self.get_logger().info('Node shutting down...')
        try:
            rclpy.shutdown()
        except Exception:
            pass
        os._exit(0)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardToTwistStamped()
    try:
        while rclpy.ok() and node._running:
            rclpy.spin_once(node, timeout_sec=0.02)
    except KeyboardInterrupt:
        node.shutdown_node()

if __name__ == '__main__':
    main()