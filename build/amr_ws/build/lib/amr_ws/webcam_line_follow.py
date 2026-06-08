#-----WARNING-----------------------------------------
#This code was first written by an Intern, which has been projected to be passed down to interns after interns

#When I first wrote this code, only God and me knew how this worked.
#Now, only God knows how this code works.

#This code works to a certain extent, and if you add features, be wary of the hours you will have to spend debugging.
#Always remember to push to GitHub to save your progress. 

#Hours spent debugging: 131
#First    Intern: Tan Dong Xu
#Second   Intern: Tang Wei Lun
#Third    Intern: Neo Wei Yuan
#Fourth   Intern: <place name here>
#-----WARNING-----------------------------------------

#!/usr/bin/env python3
import math
import os
import yaml
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

# ── Persistent AGV state file ────────────────────────────────────────────────
# Stores next_station across restarts so the AGV knows where to head after boot.
# Located next to the other parameter files in the package's params/ directory.
AGV_STATE_FILE = os.path.expanduser(
    '~/ros2_ws/src/amr_ws/params/agv_state.yaml'
)

# ── LiDAR tiered safety zones ────────────────────────────────────────────────
# Each entry is (max_distance_m, half_cone_deg).
# A beam triggers an obstacle stop when BOTH conditions are met:
#   • its distance ≤ max_distance_m   AND
#   • its angle from forward is within ±half_cone_deg
# Zones are checked from the narrowest (closest) outward so the first
# matching zone wins — keeps the logic O(zones) not O(zones²).
#
#  Zone │ Distance band │ Cone (total)
#  ─────┼───────────────┼────────────
#    1  │   0 – 0.15 m  │   45°  (±22.5°)
#    2  │ 0.15 – 0.25 m │   60°  (±30°)
#    3  │ 0.25 – 0.50 m │   90°  (±45°)
#    4  │ 0.50 – 0.75 m │  120°  (±60°)
SAFETY_TIERS = [
    (0.225, 90.0),    # zone 1: very close  → narrow  90.0° cone
    (0.3182, 45.0),   # zone 2: close       → narrow  45.0° cone
    (0.45, 30.0),     # zone 3: medium      → medium  30.0° cone
]

# ── Obstacle debounce & slew-rate constants ────────────────────────────────────
# Number of consecutive obstacle-free scan frames required before the robot is
# allowed to resume.  Prevents jitter / false-clear transients.
OBSTACLE_CLEAR_DEBOUNCE = 20   # frames

# Slew-rate limiter: how much linear.x can increase per image frame once the
# robot resumes after an obstacle clear.  Target cruise speed = 0.25 m/s.
# At ~10 Hz image rate this gives ≈ 2.5 s to reach cruise speed.
LINEAR_SLEW_RATE = 0.01        # m/s per frame

# Minimum green pixel sum to trust the green line when reverting from red tracking.
# Used in the no-line-detected fallback. Tune if needed.
GREEN_FALLBACK_MIN = 135000    # = EXPLOSION_THRESHOLD // 10


class WebcamLineFollow(Node):
    def __init__(self):
        super().__init__('webcam_line_follow')

        self.bridge = CvBridge()

        # ── Subscriptions ──────────────────────────────────────────────
        self.create_subscription(Image, '/image_raw', self.image_callback, 1)

        # LiDAR safety sensor
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # UI control topics
        self.create_subscription(Bool,   '/agv/cmd_enable', self.enable_callback, 10)
        self.create_subscription(Bool,   '/agv/cmd_stop',   self.stop_callback,   10)
        self.create_subscription(String, '/agv/cmd_mode',   self.mode_callback,   10)

        # Rack sensor status — published by rack_websocket_server.py
        # Format: "rack_id:status:distance_cm"  (status 1=FULL, 0=EMPTY)
        self.create_subscription(String, '/rack_status', self.rack_status_callback, 10)

        # Ping Echo
        self.create_subscription(String, '/ui_heartbeat', self.heartbeat_callback, 10)

        # ── Publishers ─────────────────────────────────────────────────
        # twist_mux picks this up at priority 10 (same slot as Nav2)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel_agv', 10)

        # State feedback → UI
        self.state_pub = self.create_publisher(String, '/agv/state', 10)

        # Mode feedback → UI  (UI subscribes to keep its button in sync)
        self.mode_pub = self.create_publisher(String, '/agv/mode', 10)

        # Ping Echo pub
        self.heartbeat_pub = self.create_publisher(String, '/ui_heartbeat', 10)

        # ── Follow mode ────────────────────────────────────────────────
        # "green" → always follow green tape
        # "red"   → follow green, but at an intersection divert onto red if
        #           a qualifying red line is visible straight ahead in the
        #           bottom strip of the camera.
        self.follow_mode = "green"

        # Tracks whether we are currently homing onto (following) a red line
        self.following_red = False

        # ── Internal enable gate ───────────────────────────────────────
        # Node starts disabled; GO button on the UI enables it.
        self.enabled = False

        # ── Obstacle detection state ───────────────────────────────────
        # Set True when LiDAR detects something within OBSTACLE_DISTANCE_M
        # in the forward 180° safety cone.  The robot halts but audio keeps
        # playing.  Normal operation resumes once debounce frames pass.
        self.obstacle_detected = False

        # Debounce counter: incremented each scan frame that is obstacle-free.
        # The obstacle flag is only cleared once this reaches OBSTACLE_CLEAR_DEBOUNCE.
        self._clear_frame_count = 0

        # Wait timer for resuming after an obstacle is cleared
        self.resume_time = 0.0

        # Slew-rate limiter: current commanded linear speed.  Reset to 0.0
        # whenever an obstacle is detected so the robot ramps up smoothly
        # on resume instead of jumping straight to cruise speed.
        self._current_linear_x = 0.0

        # ── U-turn detection thresholds ────────────────────────────────
        self.EXPLOSION_THRESHOLD     = 900000  # green strip sum → green U-turn
        self.RED_EXPLOSION_PX        = 900000  # red strip pixels → red U-turn
        self.u_turning               = False
        self.u_turn_start_time       = None
        self.U_TURN_MIN_TIME         = 2.0      # seconds before checking for line again

        # Debounce for "red line lost": number of consecutive frames with
        # red_strip_px < threshold before reverting to green.
        self._red_lost_frames = 0
        self.RED_LOST_DEBOUNCE = 5   # ~0.8 s at 10 Hz image rate

        # ── PD controller ──────────────────────────────────────────────
        self.Kp = 0.0033
        self.Kd = 0.00075
        self.last_err = 0
        self.last_time = None
        self.MAX_ANG_Z = 1.0
        self.MIN_ANG_Z_DEADZONE = 0.05

        # Issue 4: timestamp of the last per-frame info log (throttled to 1 Hz)
        self._last_log_time = 0.0

        # ── Docking Protocol State ─────────────────────────────────────
        self.docking_type = 0
        self.docking_phase = 0
        self.docking_timer = 0.0
        self.pending_docking_type = 0

        # ── Rack sensor state (12 ultrasonic slots) ───────────────────
        self.rack_states = {
            "STORE-A1": 0, "STORE-A2": 0, "STORE-A3": 0,
            "STORE-B1": 0, "STORE-B2": 0, "STORE-B3": 0,
            "CAPP-A1": 0, "CAPP-A2": 0, "CAPP-A3": 0,
            "CAPP-B1": 0, "CAPP-B2": 0, "CAPP-B3": 0,
        }
        self.waiting_operator_confirm = False
        # True when D1 full protocol done but CAPP is full — hold idle at STORE
        self.idle_capp_full = False
        # True when D2 full protocol + U-turn done but STORE is empty — hold idle
        self.idle_store_empty = False
        # True after any docking completes — hold until operator presses GO
        self.waiting_post_dock_confirm = False

        # Cooldown after any docking completes — suppresses explosion re-trigger
        # while the AGV is still physically inside the docking zone.
        self.post_docking_cooldown_until = 0.0

        # ── Next-station flag ─────────────────────────────────────────
        # Set at explosion so lane decision uses only the relevant station.
        # Persisted to AGV_STATE_FILE so the AGV remembers its destination
        # across restarts. Default on first boot: "STORE".
        # Values: None | "STORE" | "CAPP"
        self.next_station: str | None = self._load_next_station()

        self.twist = Twist()

        self.get_logger().info("Webcam Line Follow node started — waiting for /agv/cmd_enable")

        # Broadcast state + mode at 1 Hz so UI always reflects node truth
        self.current_state = "WAITING"
        self.state_timer = self.create_timer(1.0, self.timer_state_callback)
        self._publish_state(self.current_state)
        self._publish_mode(self.follow_mode)

    # ── LiDAR safety callback ──────────────────────────────────────────────────

    def scan_callback(self, msg: LaserScan):
        # ── Override: Ignore obstacles during Docking and U-Turns ──────────────────────
        if self.docking_type in (1, 2) or self.u_turning:
            if self.obstacle_detected:
                self.obstacle_detected = False
                self._clear_frame_count = 0
                self.resume_time = 0.0
            return

       
        # Pre-compute half-cone radians for each tier once per callback
        tiers_rad = [(d, math.radians(h)) for d, h in SAFETY_TIERS]
        # Widest cone among all tiers — used as a fast early-reject gate
        max_half_rad = max(h for d, h in tiers_rad)

        ranges = msg.ranges
        n = len(ranges)
        if n == 0:
            return

        inc = msg.angle_increment
        angle_min = msg.angle_min
        range_min = msg.range_min
        range_max = msg.range_max

        obstacle_found = False
        for i, r in enumerate(ranges):
            # Skip invalid / out-of-range readings first (cheap)
            if not math.isfinite(r) or r < range_min or r > range_max:
                continue

            # Fast gate: skip beams outside the widest possible cone
            angle = angle_min + i * inc
            angle = math.atan2(math.sin(angle), math.cos(angle))  # → (-π, π]

            # Forward direction aligns with angle = ±π in our LiDAR frame
            fwd_dist = abs(abs(angle) - math.pi)   # 0 = dead ahead
            if fwd_dist > max_half_rad:
                continue

            # Find the innermost tier that covers this distance
            for max_dist, half_rad in tiers_rad:
                if r <= max_dist:
                    # Beam is within this tier's distance — check cone
                    if fwd_dist <= half_rad:
                        obstacle_found = True
                    break   # tier matched (cone may or may not have fired)

        # ── State transitions ──────────────────────────────────────────
        if obstacle_found:
            # ── Obstacle present ──────────────────────────────────────
            # Reset the clear-frame debounce counter every time we see an obstacle.
            self._clear_frame_count = 0

            if not self.obstacle_detected:
                self.obstacle_detected = True
                # Reset slew speed so resume is always a smooth ramp-up.
                self._current_linear_x = 0.0
                self.get_logger().warn(
                    "OBSTACLE DETECTED (tiered safety zone triggered) — halting robot. "
                    "Waiting for path to clear…"
                )
                # Immediately stop the robot (if we are running)
                if self.enabled:
                    zero = Twist()
                    self.cmd_vel_pub.publish(zero)
                    if self.current_state == "RUNNING":
                        self.current_state = "OBSTACLE_DETECTED"
                        self._publish_state(self.current_state)

        else:
            # ── No obstacle this frame ────────────────────────────────
            if self.obstacle_detected:
                self._clear_frame_count += 1
                if self._clear_frame_count >= OBSTACLE_CLEAR_DEBOUNCE:
                    # Debounce satisfied — path is genuinely clear.
                    self.obstacle_detected = False
                    self._clear_frame_count = 0
                    self.resume_time = time.time() + 3.0
                    self.get_logger().info(
                        f"Path clear ({OBSTACLE_CLEAR_DEBOUNCE} consecutive clear frames) "
                        "— waiting 3 seconds before resuming line following."
                    )
                else:
                    self.get_logger().debug(
                        f"Obstacle clear frame {self._clear_frame_count}/{OBSTACLE_CLEAR_DEBOUNCE} "
                        "— waiting for debounce."
                    )

    # ── Rack status callback ────────────────────────────────────────────────────

    def rack_status_callback(self, msg: String):
        """
        Receive rack occupancy data from the ESP32 ultrasonic sensor bridge.

        Message format (String): "rack_id:status:distance_cm"
          status == 1  → slot occupied
          status == 0  → slot empty

        Updates self.rack_states per slot.
        Lane/mode decisions are NO LONGER made here — they are made once
        at each explosion trigger (green or red threshold), reading only the
        next station's rack columns at that moment.  This prevents the AGV
        from reacting to sensor noise or cross-station updates mid-transit.
        """
        try:
            parts = msg.data.split(':')
            if len(parts) < 2:
                self.get_logger().warn(
                    f"rack_status_callback: unexpected format '{msg.data}' — ignoring."
                )
                return

            rack_id  = parts[0]
            status   = int(parts[1])
            distance = float(parts[2]) if len(parts) > 2 else 0.0

            if rack_id not in self.rack_states:
                self.get_logger().warn(
                    f"rack_status_callback: unknown rack_id '{rack_id}' — ignoring."
                )
                return

            self.rack_states[rack_id] = status
            status_text = "OCCUPIED" if status == 1 else "EMPTY"
            self.get_logger().info(
                f"[Rack {rack_id}] {status_text} (dist={distance:.1f} cm)"
            )

            # ── IDLE release checks ─────────────────────────────────────────
            # After D1 completes, AGV waits until any CAPP slot becomes empty.
            if self.idle_capp_full:
                capp_still_full = (
                    any(self.rack_states[k] == 1 for k in ["CAPP-A1", "CAPP-A2", "CAPP-A3"])
                    and any(self.rack_states[k] == 1 for k in ["CAPP-B1", "CAPP-B2", "CAPP-B3"])
                )
                if not capp_still_full:
                    self.idle_capp_full = False
                    # AGV is still physically sitting at the green threshold.
                    # Resuming RUNNING would leave it on the explosion spot with no line visible.
                    # Instead: re-trigger the U-turn → Docking 1 sequence directly.
                    self.next_station = "CAPP"
                    self._save_next_station("CAPP")
                    lane_mode = self._decide_lane_for_station("CAPP")
                    self.follow_mode = lane_mode
                    self._publish_mode(lane_mode)
                    self.u_turning = True
                    self.u_turn_start_time = time.time()
                    self.pending_docking_type = 1
                    self.current_state = "U-TURN"
                    self._current_linear_x = 0.0
                    if not self.enabled:
                        self.enabled = True
                    self._publish_state(self.current_state)
                    self.get_logger().info(
                        f"[Rack {rack_id}] CAPP vacancy detected — triggering U-TURN \u2192 DOCKING 1 "
                        f"(lane='{lane_mode}')."
                    )

            # After D2+U-turn, AGV waits until any STORE slot becomes occupied.
            if self.idle_store_empty:
                store_occupied = any(
                    self.rack_states[k] == 1
                    for k in ["STORE-A1", "STORE-A2", "STORE-A3",
                              "STORE-B1", "STORE-B2", "STORE-B3"]
                )
                if store_occupied:
                    self.idle_store_empty = False
                    self.current_state = "RUNNING"
                    self._current_linear_x = 0.0
                    self._publish_state(self.current_state)
                    self.get_logger().info(
                        f"[Rack {rack_id}] STORE material detected — resuming from IDLE\u2014STORE EMPTY."
                    )

            # ── Lane routing deliberately removed from here ─────────────────
            # Mode (green/red) is now decided once at each explosion trigger.
            # See image_callback explosion branches for the lane-selection logic.

        except (ValueError, IndexError) as e:
            self.get_logger().error(
                f"rack_status_callback: failed to parse '{msg.data}': {e}"
            )

    def _decide_lane_for_station(self, station: str) -> str:
        """
        Called exactly once per explosion to pick the follow mode.
        Only the racks belonging to *station* (the next destination) are
        considered — the other station's sensors are completely ignored.

        Returns 'green' or 'red'.
        """
        if station == "CAPP":
            capp_A_full = any(self.rack_states[k] == 1 for k in ["CAPP-A1", "CAPP-A2", "CAPP-A3"])
            capp_B_full = any(self.rack_states[k] == 1 for k in ["CAPP-B1", "CAPP-B2", "CAPP-B3"])
            
            # If both are full, it doesn't matter (IDLE check catches it), but default to green
            mode = "red" if (capp_A_full and not capp_B_full) else "green"
            self.get_logger().info(
                f"[LaneDecision@explosion] next=CAPP | "
                f"capp_A_full={capp_A_full} capp_B_full={capp_B_full} → mode='{mode}'"
            )
        else:  # station == "STORE"
            store_B_full = any(self.rack_states[k] == 1 for k in ["STORE-B1", "STORE-B2", "STORE-B3"])
            store_A_full = any(self.rack_states[k] == 1 for k in ["STORE-A1", "STORE-A2", "STORE-A3"])
            
            # If both are full, it doesn't matter (IDLE check catches it), but default to green
            mode = "red" if (store_B_full and not store_A_full) else "green"
            self.get_logger().info(
                f"[LaneDecision@explosion] next=STORE | "
                f"store_B_full={store_B_full} store_A_full={store_A_full} → mode='{mode}'"
            )
        return mode

    def _rack_stop(self, state: str, reason: str):
        """Stop the AGV due to a rack availability issue."""
        zero = Twist()
        self.cmd_vel_pub.publish(zero)
        self.enabled = False
        self.current_state = state
        self._publish_state(state)
        self.get_logger().warn(f"RACK STOP: {reason}")

    # ── Mode callback ──────────────────────────────────────────────────────────

    def mode_callback(self, msg: String):
        """
        Switch follow mode SEAMLESSLY — motion is never interrupted.

        green mode: follow green continuously, perform green U-turns.
        red   mode: follow green AND divert onto red at intersections;
                    perform red U-turns when on the red segment.

        Toggling can happen at any time while the robot is moving.
        """
        mode = msg.data.lower()
        if mode not in ("green", "red"):
            self.get_logger().warn(f"Unknown follow mode '{msg.data}' — ignoring.")
            return

        if mode == "green" and self.docking_type == 2:
            self.get_logger().debug(
                "Mode → green requested but Docking 2 is active — ignoring to protect D2 sequence."
            )
            self._publish_mode(self.follow_mode)  # reflect actual mode without changing it
            return

        if mode == self.follow_mode:
            # Idempotent — same mode republished (e.g. on reconnect). No action needed.
            self._publish_mode(mode)
            return

        old_mode = self.follow_mode
        self.follow_mode = mode

        if mode == "green":
            # ── Red → Green transition ─────────────────────────────────
            # Stop tracking the red line; the robot will naturally fall
            # back onto the green line it was already moving alongside.
            if self.following_red:
                self.following_red = False
                self.get_logger().info(
                    "Mode → green: stopped red tracking — reverting to green follow."
                )
            # Cancel a bare red U-turn (not post-D2) so the robot resumes green following.
            if self.u_turning and self.pending_docking_type == 0:
                self.u_turning = False
                self.u_turn_start_time = None
                self.current_state = "RUNNING"
                self._publish_state(self.current_state)
                self.get_logger().info("Mode → green: cancelled active red U-turn.")
            # NOTE: green U-turn (u_turning with pending_docking_type=1) and PD state
            # are left intact — the robot keeps moving without any jolt.

        else:  # mode == "red"
            # ── Green → Red transition ─────────────────────────────────
            # No state changes needed. Robot continues following green;
            # image_callback will now also watch for red divert triggers.
            self.get_logger().info(
                "Mode → red: now watching for red tape at intersections "
                "(continuing green follow)."
            )

        self._publish_mode(mode)
        self.get_logger().info(f"Follow mode: '{old_mode}' → '{mode}' (motion uninterrupted)")

    # ── Enable / Stop & Ping callbacks ────────────────────────────────────────

    def heartbeat_callback(self, msg: String):
        # Bounce the ping straight back to the UI
        self.heartbeat_pub.publish(msg)

    def enable_callback(self, msg: Bool):
        # ── Operator confirmation for Docking 2 sensor gate ────────────
        if msg.data and self.waiting_operator_confirm:
            self.waiting_operator_confirm = False
            self.docking_phase = 4          # advance to Phase 4: backward retract
            self.docking_timer = time.time()
            # Ensure the AGV is enabled so image_callback actually executes Phase 4.
            # (Operator may have pressed STOP then GO to confirm, leaving enabled=False.)
            if not self.enabled:
                self.enabled = True
            self.current_state = "DOCKING 2"
            self._publish_state(self.current_state)
            self.get_logger().info(
                "Operator confirmed — advancing Docking 2 to Phase 4 (backward retract)."
            )
            return

        # ── Operator GO after D1 complete OR before D2 Phase 4 (retract) ──────
        if msg.data and self.waiting_post_dock_confirm:
            self.waiting_post_dock_confirm = False
            if not self.enabled:
                self.enabled = True
            if self.docking_type == 2:
                # Pre-D2-retract confirm: operator confirms deposit, start Phase 4 backward retract.
                self.docking_phase = 4
                self.docking_timer = time.time()
                self.current_state = "DOCKING 2"
                self._publish_state(self.current_state)
                self.get_logger().info(
                    "Operator confirmed GO \u2014 starting D2 Phase 4 (backward retract)."
                )
            else:
                # Post-D1 confirm: resume normal line following.
                self.current_state = "RUNNING"
                self._current_linear_x = 0.0
                self._publish_state(self.current_state)
                self.get_logger().info(
                    "Operator confirmed GO after Docking 1 \u2014 resuming line following."
                )
            return

        if msg.data and not self.enabled:
            self.enabled = True
            self.following_red = False
            # If an obstacle is already present, reflect that immediately
            if self.obstacle_detected or time.time() < self.resume_time:
                self.current_state = "OBSTACLE_DETECTED"
            elif self.waiting_post_dock_confirm:
                # waiting_post_dock_confirm already handled above — do nothing extra
                pass
            else:
                self.current_state = "RUNNING"
            self.get_logger().info("AGV ENABLED — line following active")
            self._publish_state(self.current_state)

    def stop_callback(self, msg: Bool):
        if msg.data and self.enabled:
            self.enabled = False
            self.current_state = "STOPPED"
            # Publish a zero Twist immediately to halt the robot
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            self.get_logger().info("AGV STOPPED — cmd_vel_agv zeroed")
            self._publish_state(self.current_state)
            # Reset U-turn state so next GO starts clean
            self.u_turning = False
            self.u_turn_start_time = None
            self.last_err = 0
            self.last_time = None
            # Also clear obstacle flag and red-follow state
            self.obstacle_detected = False
            self.resume_time = 0.0
            self.following_red = False
            self._red_lost_frames = 0
            self.docking_type = 0
            self.docking_phase = 0
            self.pending_docking_type = 0
            self.waiting_operator_confirm = False
            self.waiting_post_dock_confirm = False
            self.idle_capp_full = False
            self.idle_store_empty = False
            self.post_docking_cooldown_until = 0.0
            self.next_station = None

    # ── AGV state persistence helpers ───────────────────────────────────

    def _load_next_station(self) -> str:
        """
        Read next_station from the YAML state file.
        Returns 'STORE' if the file is missing, unreadable, or has no valid entry.
        """
        try:
            path = os.path.realpath(AGV_STATE_FILE)
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                station = data.get('next_station', 'STORE')
                if station in ('STORE', 'CAPP'):
                    self.get_logger().info(
                        f"[State] Loaded next_station='{station}' from {path}"
                    )
                    return station
        except Exception as e:
            self.get_logger().warn(f"[State] Could not load {AGV_STATE_FILE}: {e}")
        self.get_logger().info("[State] Defaulting next_station='STORE'")
        return 'STORE'

    def _save_next_station(self, station: str) -> None:
        """
        Write next_station to the YAML state file.
        Only called with real values ('STORE' or 'CAPP') — never with None,
        so the file always holds the last meaningful destination for restart.
        """
        try:
            path = os.path.realpath(AGV_STATE_FILE)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                yaml.dump({'next_station': station}, f, default_flow_style=False)
            self.get_logger().info(
                f"[State] Saved next_station='{station}' to {path}"
            )
        except Exception as e:
            self.get_logger().warn(f"[State] Could not save {AGV_STATE_FILE}: {e}")

    def _publish_state(self, state: str):
        msg = String()
        msg.data = state
        self.state_pub.publish(msg)

    def _publish_mode(self, mode: str):
        """Broadcast current follow_mode to /agv/mode so the UI stays in sync."""
        msg = String()
        msg.data = mode
        self.mode_pub.publish(msg)

    def timer_state_callback(self):
        """1 Hz heartbeat — keeps UI state and mode button always up to date."""
        self._publish_state(self.current_state)
        self._publish_mode(self.follow_mode)

    # ── Image callback ─────────────────────────────────────────────────────────

    def image_callback(self, msg):
        # Gate 1: do nothing if not enabled
        if not self.enabled:
            return

        # Gate 2: obstacle detected — hold still, let music keep playing
        if self.obstacle_detected:
            self._current_linear_x = 0.0   # ensure slew starts from 0 on resume
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            return

        # Gate 3: 3-second wait after obstacle cleared
        if time.time() < self.resume_time:
            self._current_linear_x = 0.0
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            return
        elif self.current_state == "OBSTACLE_DETECTED":
            # Wait is over, transition back to RUNNING
            self.current_state = "RUNNING"
            self._publish_state(self.current_state)
            self.get_logger().info("Resume wait complete — resuming line following.")

        # Gate 4: AGV is in an idle hold state — CAPP full, STORE empty,
        # or waiting for operator GO after docking. Hold still until cleared.
        if self.idle_store_empty or self.idle_capp_full or self.waiting_post_dock_confirm:
            zero = Twist()
            self.cmd_vel_pub.publish(zero)
            return

        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        h, w = frame.shape[:2]
        current_time = time.time()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # ── Tracking strip bounds ──────────────────────────────────────────
        search_top = (h // 4) * 3
        search_bot = search_top + 20
        # Issue 3: slice HSV to the 20-row strip BEFORE calling inRange — ~40× fewer
        # pixels to process compared to the full frame.
        hsv_strip = hsv[search_top:search_bot, :]

        # ── Green mask: computed only on the strip slice ───────────────────
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([120, 255, 255])
        mask_green  = cv2.inRange(hsv_strip, lower_green, upper_green)
        green_sum   = int(np.sum(mask_green))

        # ── Red mask: Computed on every frame so explosions trigger regardless of mode
        RED_STRIP_MIN  = 200
        RED_CENTER_TOL = int(w * 0.45)

        lower_red_lo = np.array([  0,  60,  60])
        upper_red_lo = np.array([ 25, 255, 255])
        lower_red_hi = np.array([140,  60,  60])
        upper_red_hi = np.array([180, 255, 255])
        
        mask_red = cv2.bitwise_or(
            cv2.inRange(hsv_strip, lower_red_lo, upper_red_lo),
            cv2.inRange(hsv_strip, lower_red_hi, upper_red_hi)
        )
        red_strip_px  = int(np.sum(mask_red > 0))
        red_strip_sum = int(np.sum(mask_red))

        # ── Red intersection divert check (red mode only) ──────────────────
        # Trigger: red tape appears in the bottom tracking strip alongside
        # (or instead of) green. No "explosion" required — this fires the
        # moment the robot reaches the crossing region.
        if (self.follow_mode == "red"
                and not self.following_red
                and not self.u_turning
                and self.docking_type == 0
                and red_strip_px >= RED_STRIP_MIN):
            Mr = cv2.moments(mask_red)
            if Mr['m00'] > 0:
                cx_red = int(Mr['m10'] / Mr['m00'])
                if abs(cx_red - w // 2) <= RED_CENTER_TOL:
                    self.following_red = True
                    self.get_logger().info(
                        f"Red tape in strip (px={red_strip_px}, cx={cx_red}) "
                        "— diverting to red line."
                    )
            # Throttled 1-Hz info log so we can see strip values without spam
            if current_time - self._last_log_time >= 1.0:
                self.get_logger().info(
                    f"[RedMode divert check] red_strip_px={red_strip_px}, "
                    f"green_sum={green_sum}, follow_mode={self.follow_mode}, "
                    f"following_red={self.following_red}"
                )

        # ── Choose active tracking mask ────────────────────────────────────
        if self.following_red:
            # Once on red, track it in the bottom strip
            mask = mask_red
            mask_sum = int(np.sum(mask))
            # If red disappears (end of red tape), fall back to green.
            # Use a debounce counter so a single low-pixel frame doesn't abort
            # red following — the AGV may briefly lose the line while steering.
            if self.docking_type != 0 or self.u_turning:
                self._red_lost_frames = 0
            elif red_strip_px < 200:
                self._red_lost_frames += 1
                if self._red_lost_frames >= self.RED_LOST_DEBOUNCE:
                    self.following_red = False
                    self._red_lost_frames = 0
                    self.get_logger().info(
                        f"Red line lost ({self.RED_LOST_DEBOUNCE} consecutive low frames) "
                        "— reverting to green tracking."
                    )
                    mask = mask_green
                    mask_sum = green_sum
                else:
                    self.get_logger().debug(
                        f"Red low-pixel frame {self._red_lost_frames}/{self.RED_LOST_DEBOUNCE} "
                        f"(px={red_strip_px}) — holding red tracking."
                    )
            else:
                # Red is visible — reset the lost-frame counter
                self._red_lost_frames = 0
        else:
            mask = mask_green
            mask_sum = green_sum

        # ── Docking / Explosion Triggers (Regardless of follow_mode) ─────────
        if (not self.u_turning
                and self.docking_type == 0
                and current_time >= self.post_docking_cooldown_until):
            if green_sum > self.EXPLOSION_THRESHOLD:
                # Green explosion = AGV is at STORE rack.
                
                # Check if CAPP is full before picking up material
                capp_A_full = any(self.rack_states[k] == 1 for k in ["CAPP-A1", "CAPP-A2", "CAPP-A3"])
                capp_B_full = any(self.rack_states[k] == 1 for k in ["CAPP-B1", "CAPP-B2", "CAPP-B3"])
                if capp_A_full and capp_B_full:
                    zero = Twist()
                    self.cmd_vel_pub.publish(zero)
                    self.idle_capp_full = True
                    self.current_state = "IDLE \u2014 CAPP FULL"
                    self._publish_state(self.current_state)
                    self.get_logger().warn(
                        "Green explosion \u2014 but CAPP is FULL. Holding before U-turn."
                    )
                    return

                # Next station (where it's headed after docking) = CAPP.
                # Decide lane NOW using only CAPP rack states.
                self.next_station = "CAPP"
                self._save_next_station("CAPP")
                lane_mode = self._decide_lane_for_station("CAPP")
                self.follow_mode = lane_mode
                self._publish_mode(lane_mode)
                self.u_turning = True
                self.u_turn_start_time = current_time
                self.current_state = "U-TURN"
                self._publish_state(self.current_state)
                self.pending_docking_type = 1
                self.get_logger().warn(
                    f"[THRESHOLD] Green explosion \u2014 at STORE rack. "
                    f"next_station=CAPP. Lane='{lane_mode}'. U-TURN \u2192 DOCKING 1."
                )
            elif red_strip_sum > self.RED_EXPLOSION_PX:
                # Red explosion = AGV is at CAPP rack.
                # Next station (where it's headed after docking) = STORE.
                # Decide lane NOW using only STORE rack states.
                self.next_station = "STORE"
                self._save_next_station("STORE")
                lane_mode = self._decide_lane_for_station("STORE")
                self.follow_mode = lane_mode
                self._publish_mode(lane_mode)
                self.docking_type = 2

                # D2 starts immediately with Phase 1 (backward align).
                # The confirm GO happens after deposit (Phase 3).
                self.docking_phase = 1
                self.docking_timer = current_time
                self.current_state = "DOCKING 2"
                self._publish_state(self.current_state)
                self.get_logger().warn(
                    f"[THRESHOLD] Red explosion \u2014 at CAPP rack. "
                    f"next_station=STORE. Lane='{lane_mode}'. DOCKING 2 Phase 1."
                )

        # ── Handle U-turn (Universal for active line color) ──────────────────
        if self.u_turning:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.25
            self.cmd_vel_pub.publish(self.twist)

            # Only check for line after minimum U-turn time
            if current_time - self.u_turn_start_time >= self.U_TURN_MIN_TIME:
                if 0 < mask_sum < max(self.EXPLOSION_THRESHOLD, self.RED_EXPLOSION_PX):
                    M = cv2.moments(mask)
                    if M['m00'] > 0:
                        cx_uturn = int(M['m10'] / M['m00'])
                        err_uturn = cx_uturn - w // 2
                        line_solid   = mask_sum > 100000
                        line_centred = abs(err_uturn) < 80
                        if line_solid and line_centred:
                            self.u_turning = False
                            if self.pending_docking_type == 1:
                                # U-turn after green explosion — enter Docking 1
                                self.docking_type = 1
                                self.docking_phase = 1
                                self.docking_timer = current_time  # BUGFIX: reset timer so Phase 1 forward window starts now
                                self.current_state = "DOCKING 1"
                                self._publish_state(self.current_state)
                                self.pending_docking_type = 0
                                self.get_logger().info("U-turn completed. Entering DOCKING 1.")
                            elif self.pending_docking_type == 2:
                                # U-turn after D2 retract — check STORE occupancy
                                self.pending_docking_type = 0
                                store_empty = not any(
                                    self.rack_states[k] == 1
                                    for k in ["STORE-A1", "STORE-A2", "STORE-A3",
                                              "STORE-B1", "STORE-B2", "STORE-B3"]
                                )
                                if store_empty:
                                    zero = Twist()
                                    self.cmd_vel_pub.publish(zero)
                                    self.idle_store_empty = True
                                    self.current_state = "IDLE \u2014 STORE EMPTY"
                                    self._publish_state(self.current_state)
                                    self.get_logger().warn(
                                        "U-turn complete (post-D2) \u2014 STORE is empty. "
                                        "Holding until STORE receives material."
                                    )
                                else:
                                    self.current_state = "RUNNING"
                                    self._current_linear_x = 0.0
                                    self._publish_state(self.current_state)
                                    self.get_logger().info(
                                        "U-turn complete (post-D2) \u2014 STORE has material. Resuming."
                                    )
                            else:
                                self.current_state = "RUNNING"
                                self._publish_state(self.current_state)
                                self._current_linear_x = 0.0
                                self.get_logger().info("U-turn completed. Resuming normal line following.")
                        else:
                            self.get_logger().debug(
                                f"U-turn check: solid={line_solid}, centred={line_centred} "
                                f"(err={err_uturn}, mask_sum={mask_sum}) — continuing turn."
                            )
                else:
                    self.get_logger().debug(
                        f"U-turn: waiting for line (sum={mask_sum}) — continuing turn."
                    )
            return  # Skip normal PD while U-turning

        # ── Handle Docking Protocol ─────────────────────────────────────────
        if self.docking_type == 1:
            if self.docking_phase == 1:
                # Phase 1: Move FORWARD at 0.05 m/s for 2.5 s while simultaneously
                # aligning with PD control (no deadzone minimum during combined phase).
                # Non-holonomic AGV needs motion to steer, so both happen together.
                M = cv2.moments(mask)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    err = cx - w // 2
                    dt = 0.01 if self.last_time is None else current_time - self.last_time
                    self.last_time = current_time

                    derivative = (err - self.last_err) / dt
                    self.last_err = err

                    angular_z = -self.Kp * err - self.Kd * derivative
                    angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)
                    # No deadzone minimum — allow small corrections during combined phase

                    elapsed = current_time - self.docking_timer
                    if elapsed <= 5.0:
                        # Still in combined forward + align window
                        self.twist.linear.x = 0.025
                        self.twist.angular.z = angular_z
                        self.cmd_vel_pub.publish(self.twist)
                    else:
                        # 2.5 s elapsed — check strict alignment before proceeding
                        if abs(err) < 3:
                            # Aligned — proceed to Phase 2 (backward+load)
                            # CAPP-full gate is evaluated at the end of Phase 4, not here.
                            self.docking_phase = 2
                            self.docking_timer = current_time
                            self.last_err = 0
                            self.get_logger().info(
                                "Docking 1 Phase 1: Aligned (err<3). Moving backward."
                            )
                        else:
                            # Not aligned yet — keep aligning in place (no forward)
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = angular_z
                            self.cmd_vel_pub.publish(self.twist)
                            self.get_logger().debug(
                                f"Docking 1 Phase 1: still aligning, err={err}"
                            )
                else:
                    # Lost line during alignment
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)

            elif self.docking_phase == 2:
                # Phase 2: Move backwards at -0.075 m/s for 7.5 s
                if current_time - self.docking_timer <= 7.5:
                    self.twist.linear.x = -0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 3
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 1 Phase 2: Done. Phase 3: Waiting.")
            
            elif self.docking_phase == 3:
                # Phase 3: Hold in place for 5 s (loading dwell)
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 4
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 1 Phase 3 Done. Phase 4: Moving forward to exit loading zone.")

            elif self.docking_phase == 4:
                # Phase 4: Move forward at 0.075 m/s for 5.0 s (exit loading zone)
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = 0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    # D1 complete — hold for operator GO confirmation before resuming.
                    # CAPP-full idle check will happen after operator releases the AGV.
                    self.docking_type = 0
                    self.docking_phase = 0
                    self.next_station = None  # clear committed destination
                    self.post_docking_cooldown_until = current_time + 5.0
                    zero = Twist()
                    self.cmd_vel_pub.publish(zero)
                    self.waiting_post_dock_confirm = True
                    self.current_state = "WAITING \u2014 CONFIRM GO"
                    self._publish_state(self.current_state)
                    self.get_logger().warn(
                        "Docking 1 complete \u2014 waiting for operator GO to continue."
                    )
            
            return  # Skip normal PD while docking

        elif self.docking_type == 2:
            if self.docking_phase == 1:
                # Phase 1: Move BACKWARDS at -0.05 m/s for 2.5 s unconditionally to clear the red threshold,
                # then align in place with PD control.
                elapsed = current_time - self.docking_timer
                if elapsed <= 4.5:
                    # Move backward unconditionally
                    self.twist.linear.x = -0.05
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                    self.get_logger().debug(
                        f"Docking 2 Phase 1: moving backward straight (elapsed={elapsed:.1f}s)"
                    )
                else:
                    # Backward movement complete, now try to align
                    M = cv2.moments(mask)
                    if M['m00'] > 0:
                        cx = int(M['m10'] / M['m00'])
                        err = cx - w // 2
                        dt = 0.01 if self.last_time is None else current_time - self.last_time
                        self.last_time = current_time

                        derivative = (err - self.last_err) / dt
                        self.last_err = err

                        angular_z = -self.Kp * err - self.Kd * derivative
                        angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)

                        if abs(err) < 3:
                            self.docking_phase = 2
                            self.docking_timer = current_time
                            self.last_err = 0
                            self.get_logger().info(
                                "Docking 2 Phase 1: Aligned (err<3). Moving forward to deposit."
                            )
                        else:
                            # Still not aligned — rotate in place (no backward)
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = angular_z
                            self.cmd_vel_pub.publish(self.twist)
                            self.get_logger().debug(
                                f"Docking 2 Phase 1: still aligning, err={err}"
                            )
                    else:
                        # Green not visible after backing up
                        if elapsed <= 7.5:
                            # Wait up to 5s for green to reappear
                            self.twist.linear.x = 0.0
                            self.twist.angular.z = 0.0
                            self.cmd_vel_pub.publish(self.twist)
                            self.get_logger().info(
                                f"Docking 2 Phase 1: backward done, waiting for green "
                                f"line to reappear (green_sum={green_sum}, elapsed={elapsed:.1f}s)"
                            )
                        else:
                            # Timeout
                            self.docking_phase = 2
                            self.docking_timer = current_time
                            self.last_err = 0
                            self.get_logger().warn(
                                f"Docking 2 Phase 1: green reappear timeout ({elapsed:.1f}s) — "
                                "advancing to Phase 2 without alignment check."
                            )

            elif self.docking_phase == 2:
                # Phase 2: Move forward at 0.075 for 8s
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = 0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    self.docking_phase = 3
                    self.docking_timer = current_time
                    self.get_logger().info("Docking 2 Phase 2 Done. Hold for 5s.")
            elif self.docking_phase == 3:
                # Phase 3: Post-deposit dwell (5 s), then advance to retract.
                if current_time - self.docking_timer <= 5.0:
                    # Hold in place during dwell
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    # Dwell complete — wait for operator GO before retracting.
                    # We hold at docking_phase 3, but set the confirm flag.
                    zero = Twist()
                    self.cmd_vel_pub.publish(zero)
                    self.waiting_post_dock_confirm = True
                    self.current_state = "WAITING \u2014 CONFIRM GO"
                    self._publish_state(self.current_state)
                    self.get_logger().warn(
                        "Docking 2 Phase 3 Done. Waiting for operator GO to start Phase 4 retract."
                    )
            elif self.docking_phase == 4:
                # Phase 4: Move backwards at -0.075 for 7.5s, then check store state.
                # This is the first point where store-empty is evaluated — after the
                # full deposit cycle (Ph2 forward + Ph3 hold) has completed.
                if current_time - self.docking_timer <= 5.0:
                    self.twist.linear.x = -0.075
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                else:
                    # D2 Phase 4 complete — immediately trigger U-turn.
                    # Operator already confirmed before Phase 1; no second confirm needed.
                    self.docking_type = 0
                    self.docking_phase = 0
                    self.next_station = None
                    self.post_docking_cooldown_until = current_time + 5.0
                    self.pending_docking_type = 2
                    self.u_turning = True
                    self.u_turn_start_time = current_time
                    self.current_state = "U-TURN"
                    self._publish_state(self.current_state)
                    self.get_logger().info(
                        "Docking 2 Phase 4 Done \u2014 starting U-TURN (STORE check after)."
                    )
            return

        # ── Normal PD line-following ───────────────────────────────────
        M = cv2.moments(mask)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            err = cx - w // 2
            dt = 0.01 if self.last_time is None else current_time - self.last_time
            self.last_time = current_time

            derivative = (err - self.last_err) / dt
            self.last_err = err

            angular_z = -self.Kp * err - self.Kd * derivative
            angular_z = max(min(angular_z, self.MAX_ANG_Z), -self.MAX_ANG_Z)

            if abs(angular_z) < self.MIN_ANG_Z_DEADZONE:
                angular_z = 0.0

            # ── Slew-rate limiter ──────────────────────────────────────
            TARGET_LINEAR_X = 0.32
            self._current_linear_x = min(
                self._current_linear_x + LINEAR_SLEW_RATE,
                TARGET_LINEAR_X
            )

            self.twist.linear.x = self._current_linear_x
            self.twist.angular.z = angular_z
            self.cmd_vel_pub.publish(self.twist)

            line_color = "Red" if self.following_red else "Green"
            # Issue 4: throttle to 1 Hz — logging every frame causes measurable overhead
            if current_time - self._last_log_time >= 1.0:
                self.get_logger().info(
                    f"[{line_color}] cx={cx}, cy={cy}, err={err}, ang_z={angular_z:.3f}, "
                    f"lin_x={self._current_linear_x:.3f}, mask_sum={mask_sum}"
                )
                self._last_log_time = current_time
        else:
            # No line detected in active mask.
            # If we were tracking red but green is now visible, revert gracefully.
            if self.following_red and green_sum > GREEN_FALLBACK_MIN:
                self.following_red = False
                self._red_lost_frames = 0
                self.get_logger().info(
                    f"Red lost — green visible (green_sum={green_sum}) — switching to green tracking."
                )
                # Apply PD on green mask this frame so the AGV keeps moving
                M_g = cv2.moments(mask_green)
                if M_g['m00'] > 0:
                    cx_g = int(M_g['m10'] / M_g['m00'])
                    err_g = cx_g - w // 2
                    dt_g = 0.01 if self.last_time is None else current_time - self.last_time
                    self.last_time = current_time
                    deriv_g = (err_g - self.last_err) / dt_g
                    self.last_err = err_g
                    ang_g = -self.Kp * err_g - self.Kd * deriv_g
                    ang_g = max(min(ang_g, self.MAX_ANG_Z), -self.MAX_ANG_Z)
                    if abs(ang_g) < self.MIN_ANG_Z_DEADZONE:
                        ang_g = 0.0
                    self._current_linear_x = min(
                        self._current_linear_x + LINEAR_SLEW_RATE, 0.25
                    )
                    self.twist.linear.x = self._current_linear_x
                    self.twist.angular.z = ang_g
                    self.cmd_vel_pub.publish(self.twist)
            else:
                # Truly no line — stop and warn
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.0
                self.cmd_vel_pub.publish(self.twist)
                self.get_logger().warn(
                    f"No line detected — stopping. "
                    f"mask_sum={mask_sum}, following_red={self.following_red}, green_sum={green_sum}"
                )


def main():
    rclpy.init()
    node = WebcamLineFollow()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
