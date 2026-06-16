#!/usr/bin/env python3
"""
HSV Probe Node — Diagnostic tool for colour-tape tuning
=========================================================
Subscribes to /image_raw and logs HSV statistics every second so you can
point the camera at the tape and read the real HSV values from the terminal.

Output every frame (throttled to ~1 Hz):
  - CENTER PATCH  : mean H/S/V of a 30×30 px patch at the image centre
  - BOTTOM STRIP  : mean H/S/V of the standard tracking strip (75-80% height)
  - HUE HISTOGRAM : pixel counts bucketed into 12 × 30° hue bands
  - CURRENT MASKS : pixel counts for the current green & red HSV ranges
    so you can see at a glance whether detection agrees with reality.

Usage:
  ros2 run amr_ws hsv_probe_node
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

# ── Tune these to match your current webcam_line_follow.py values ─────────────
LOWER_GREEN = np.array([ 35,  40,  40])
UPPER_GREEN = np.array([120, 255, 255])

LOWER_RED_LO = np.array([  0,  60,  60])
UPPER_RED_LO = np.array([ 25, 255, 255])
LOWER_RED_HI = np.array([140,  60,  60])
UPPER_RED_HI = np.array([180, 255, 255])

LOWER_BLUE = np.array([ 90,  50,  50])
UPPER_BLUE = np.array([135, 255, 255])
# ─────────────────────────────────────────────────────────────────────────────

PATCH_SIZE  = 30   # px — size of the centre-point sample square
LOG_EVERY_S = 1.0  # seconds between log lines


class HsvProbeNode(Node):
    def __init__(self):
        super().__init__('hsv_probe_node')
        self.bridge     = CvBridge()
        self._last_log  = 0.0
        self.create_subscription(Image, '/image_raw', self.cb, 1)
        self.get_logger().info(
            "HSV Probe running — drive toward the tape and watch the logs."
        )

    def cb(self, msg):
        now = time.time()
        if now - self._last_log < LOG_EVERY_S:
            return
        self._last_log = now

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        h, w  = frame.shape[:2]
        hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        sep = "=" * 72

        # ── 1. Centre patch ──────────────────────────────────────────────────
        cy, cx   = h // 2, w // 2
        half     = PATCH_SIZE // 2
        patch    = hsv[cy - half : cy + half, cx - half : cx + half]
        pm       = patch.reshape(-1, 3)
        p_mean   = pm.mean(axis=0)
        p_min    = pm.min(axis=0)
        p_max    = pm.max(axis=0)

        # ── 2. Bottom tracking strip (same as line-follow node) ──────────────
        strip_top = (h // 4) * 3
        strip_bot = strip_top + 20
        strip     = hsv[strip_top:strip_bot, :]
        sm        = strip.reshape(-1, 3)
        s_mean    = sm.mean(axis=0)
        s_min     = sm.min(axis=0)
        s_max     = sm.max(axis=0)

        # ── 3. Hue histogram (12 bands × 30°) ───────────────────────────────
        hue_ch = hsv[:, :, 0].flatten()
        bins   = np.arange(0, 195, 15)          # 0,15,30,...,180
        hist   = np.histogram(hue_ch, bins=bins)[0]
        band_labels = [f"H{b:3d}-{b+14}" for b in bins[:-1]]
        hist_lines  = []
        for label, count in zip(band_labels, hist):
            bar = "█" * min(40, int(count / max(1, hue_ch.size) * 200))
            hist_lines.append(f"  {label}: {count:7d}  {bar}")

        # ── 4. Current mask pixel counts ────────────────────────────────────
        green_mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
        red_mask   = cv2.bitwise_or(
            cv2.inRange(hsv, LOWER_RED_LO, UPPER_RED_LO),
            cv2.inRange(hsv, LOWER_RED_HI, UPPER_RED_HI),
        )
        blue_mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

        green_px = int(np.sum(green_mask > 0))
        red_px   = int(np.sum(red_mask   > 0))
        blue_px  = int(np.sum(blue_mask  > 0))

        # Strip-only counts (what the PD controller actually sees)
        green_strip_mask = green_mask[strip_top:strip_bot, :]
        red_strip_mask   = red_mask  [strip_top:strip_bot, :]
        blue_strip_mask  = blue_mask [strip_top:strip_bot, :]

        green_strip_px   = int(np.sum(green_strip_mask > 0))
        red_strip_px     = int(np.sum(red_strip_mask   > 0))
        blue_strip_px    = int(np.sum(blue_strip_mask  > 0))

        # ── Print ────────────────────────────────────────────────────────────
        self.get_logger().info(
            f"\n{sep}\n"
            f"  IMAGE  {w}×{h}   strip rows {strip_top}–{strip_bot}\n"
            f"{sep}\n"
            f"  CENTER PATCH ({PATCH_SIZE}×{PATCH_SIZE} px at {cx},{cy})\n"
            f"    H  mean={p_mean[0]:5.1f}  min={p_min[0]:3d}  max={p_max[0]:3d}\n"
            f"    S  mean={p_mean[1]:5.1f}  min={p_min[1]:3d}  max={p_max[1]:3d}\n"
            f"    V  mean={p_mean[2]:5.1f}  min={p_min[2]:3d}  max={p_max[2]:3d}\n"
            f"{sep}\n"
            f"  BOTTOM STRIP  (rows {strip_top}–{strip_bot})\n"
            f"    H  mean={s_mean[0]:5.1f}  min={s_min[0]:3d}  max={s_max[0]:3d}\n"
            f"    S  mean={s_mean[1]:5.1f}  min={s_min[1]:3d}  max={s_max[1]:3d}\n"
            f"    V  mean={s_mean[2]:5.1f}  min={s_min[2]:3d}  max={s_max[2]:3d}\n"
            f"{sep}\n"
            f"  HUE HISTOGRAM (full frame)\n"
            + "\n".join(hist_lines) + "\n"
            f"{sep}\n"
            f"  CURRENT MASK COUNTS\n"
            f"    Green  full={green_px:7d} px   strip={green_strip_px:6d} px\n"
            f"    Red    full={red_px:7d} px   strip={red_strip_px:6d} px\n"
            f"    Blue   full={blue_px:7d} px   strip={blue_strip_px:6d} px\n"
            f"{sep}"
        )


def main():
    rclpy.init()
    node = HsvProbeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
