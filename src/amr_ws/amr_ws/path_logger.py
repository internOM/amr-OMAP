#!/usr/bin/env python3

"""
path_logger.py

Interactive waypoint logger for the AMR.

Usage:
    1. Localise the robot on the map (AMCL must be publishing /amcl_pose).
    2. Drive the robot to each desired waypoint on the production floor.
    3. Press 'l' to log the current pose as a waypoint.
       - You will be prompted to enter a waypoint name.
    4. Press 'u' to undo (remove) the last logged waypoint.
    5. Press 's' to save all logged waypoints to the YAML file.
    6. Press 'q' to save and quit.

Output is written to <amr_ws>/waypoints/waypoints.yaml in the format
expected by orchestrator_node.py:

    waypoints:
      - name: "waypoint_1"
        x: 1.200
        y: 0.450
        yaw: 0.00
      - name: "waypoint_2"
        x: 3.100
        y: 0.450
        yaw: 1.57
"""

import math
import os
import select
import sys
import termios
import tty

import rclpy
import yaml
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Path
from rclpy.node import Node


class ManualPathLogger(Node):
    def __init__(self):
        super().__init__('manual_path_logger')

        # ── Output file ──────────────────────────────────────────────────
        # Default: <amr_ws_src>/waypoints/waypoints.yaml
        self.declare_parameter('output_file', '')
        output_file = (
            self.get_parameter('output_file')
            .get_parameter_value()
            .string_value
        )

        if not output_file:
            try:
                from ament_index_python.packages import get_package_share_directory
                share_dir = get_package_share_directory('amr_ws')
                # Navigate: install/amr_ws/share/amr_ws -> ros2_ws
                ws_root = os.path.abspath(os.path.join(share_dir, '..', '..', '..', '..'))
                output_file = os.path.join(
                    ws_root, 'src', 'amr_ws', 'waypoints', 'waypoints.yaml'
                )
            except ImportError:
                pass
                
        if not output_file:
            # Fallback if ament index fails
            output_file = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'src', 'amr_ws', 'waypoints', 'waypoints.yaml')

        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        # ── Waypoint counter (for auto-naming) ──────────────────────────
        self._auto_counter = 1

        # ── Subscribe to AMCL pose ──────────────────────────────────────
        self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._pose_callback,
            10,
        )

        # ── Path publisher (RViz visualisation) ─────────────────────────
        self.path_pub = self.create_publisher(Path, '/logged_path', 10)
        self.path = Path()
        self.path.header.frame_id = 'map'

        # ── Storage ─────────────────────────────────────────────────────
        self.logged_waypoints = []
        self.latest_pose = None

        self.get_logger().info('─── Path Logger ───')
        self.get_logger().info(f'Output file: {self.output_file}')
        self.get_logger().info("Keys:  'l' = log waypoint  |  'u' = undo last  |  's' = save  |  'q' = save & quit")

        # ── Start keyboard loop ─────────────────────────────────────────
        self._keyboard_loop()

    # ── AMCL callback ────────────────────────────────────────────────────

    def _pose_callback(self, msg: PoseWithCovarianceStamped):
        self.latest_pose = msg

    # ── Keyboard handling ────────────────────────────────────────────────

    def _keyboard_loop(self):
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.1)

                if not self._kbhit():
                    continue

                key = sys.stdin.read(1).lower()

                if key == 'l':
                    self._log_waypoint()
                elif key == 'u':
                    self._undo_last()
                elif key == 's':
                    self._save_to_file()
                elif key == 'q':
                    self._save_to_file()
                    self.get_logger().info('Quitting path logger.')
                    break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    @staticmethod
    def _kbhit() -> bool:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(dr)

    # ── Waypoint operations ──────────────────────────────────────────────

    def _log_waypoint(self):
        if self.latest_pose is None:
            self.get_logger().warn('No AMCL pose received yet — cannot log.')
            return

        msg = self.latest_pose
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        yaw = self._quaternion_to_yaw(msg.pose.pose.orientation)

        # Auto-generate name; user can rename in the YAML later
        name = f'waypoint_{self._auto_counter}'
        self._auto_counter += 1

        waypoint = {
            'name': name,
            'x': round(x, 3),
            'y': round(y, 3),
            'yaw': round(yaw, 3),
        }
        self.logged_waypoints.append(waypoint)

        # Publish path for RViz
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = 'map'
        pose_stamped.header.stamp = msg.header.stamp
        pose_stamped.pose = msg.pose.pose
        self.path.poses.append(pose_stamped)
        self.path_pub.publish(self.path)

        self.get_logger().info(
            f"[{len(self.logged_waypoints)}] Logged '{name}': "
            f'x={waypoint["x"]:.3f}, y={waypoint["y"]:.3f}, yaw={waypoint["yaw"]:.3f}'
        )

    def _undo_last(self):
        if not self.logged_waypoints:
            self.get_logger().warn('Nothing to undo.')
            return

        removed = self.logged_waypoints.pop()
        if self.path.poses:
            self.path.poses.pop()
            self.path_pub.publish(self.path)

        self._auto_counter -= 1
        self.get_logger().info(f"Removed '{removed['name']}'. {len(self.logged_waypoints)} waypoint(s) remain.")

    # ── File I/O ─────────────────────────────────────────────────────────

    def _save_to_file(self):
        if not self.logged_waypoints:
            self.get_logger().warn('No waypoints to save.')
            return

        data = {'waypoints': self.logged_waypoints}

        with open(self.output_file, 'w') as f:
            # Write the header comment
            f.write('# waypoints.yaml  —  auto-generated by path_logger\n')
            f.write('#\n')
            f.write('# Required fields per waypoint: name, x, y, yaw\n')
            f.write('# Optional fields:              xy_tolerance, yaw_tolerance\n')
            f.write('#\n')
            f.write('# yaw is in radians:\n')
            f.write('#   0.0   = facing +X (east)\n')
            f.write('#   1.57  = facing +Y (north)\n')
            f.write('#   3.14  = facing -X (west)\n')
            f.write('#  -1.57  = facing -Y (south)\n\n')
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        self.get_logger().info(
            f'Saved {len(self.logged_waypoints)} waypoint(s) to {self.output_file}'
        )

    # ── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _quaternion_to_yaw(q) -> float:
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)


def main(args=None):
    rclpy.init(args=args)
    node = ManualPathLogger()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()