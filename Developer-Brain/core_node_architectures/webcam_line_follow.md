# webcam_line_follow

## Overview
Handles autonomous line tracking, intersection routing, and precision docking based on visual (camera) and physical (LiDAR/ultrasonic) sensors. This node represents the core logic of the AGV paradigm shift.

## Publishers
- `/cmd_vel_agv` (`geometry_msgs/Twist`) — Line-following velocity commands (priority 10).
- `/agv/state` (`std_msgs/String`) — Current AGV behavior state (see State Machine below).
- `/agv/mode` (`std_msgs/String`) — Current tracking mode (`green` or `red`).
- `/ui_heartbeat` (`std_msgs/String`) — Ping echo for the UI dashboard.

## Subscribers
- `/image_raw` (`sensor_msgs/Image`) — Camera feed for OpenCV HSV masking.
- `/scan` (`sensor_msgs/LaserScan`) — LiDAR feed for multi-tier safety zones.
- `/agv/cmd_enable` (`std_msgs/Bool`) — UI GO command / operator confirm during docking.
- `/agv/cmd_stop` (`std_msgs/Bool`) — UI STOP command.
- `/agv/cmd_mode` (`std_msgs/String`) — Manual mode overrides (largely automated now).
- `/agv/cmd_return_empty` (`std_msgs/Bool`) — Toggles Return Empty Box (blue tape) behavior.
- `/rack_status` (`std_msgs/String`) — Rack occupancy string (e.g., `CAPP-A1:1:12.5`).
- `/ui_heartbeat` (`std_msgs/String`) — Ping request from the UI dashboard.

---

## Key State Variables

| Variable | Type | Purpose |
|---|---|---|
| `follow_mode` | `str` | `"green"`, `"red"`, or `"blue"` — which line to track |
| `following_red` | `bool` | True when actively homing on the red line |
| `docking_type` | `int` | 0=none, 1=D1 (STORE), 2=D2 (CAPP) |
| `docking_phase` | `int` | Phase within the active docking sequence (1–4) |
| `pending_docking_type` | `int` | Which docking to enter after U-turn (0/1/2) |
| `u_turning` | `bool` | True during U-turn manoeuvre |
| `idle_capp_full` | `bool` | AGV holding at STORE waiting for CAPP vacancy |
| `idle_store_empty` | `bool` | AGV holding post-D2 waiting for STORE material |
| `return_empty_box` | `bool` | True when Empty mode is armed (passively watching for blue tape) |
| `blue_threshold_pause` | `bool` | True when AGV is paused at a blue threshold marker (`IDLE — RETURN BOX`) |
| `blue_line_exit` | `bool` | True when AGV is exiting a blue threshold, actively following blue until lost |
| `waiting_operator_confirm` | `bool` | AGV paused in D2-Ph3 waiting for operator GO |
| `next_station` | `str \| None` | `"STORE"`, `"CAPP"`, or `"RETURN BOX"` — committed next destination (see below) |

---

## `next_station` Flag (added 2026-06-02)

The most important safety variable for rack-sensor isolation. Tracks **where the AGV is heading next** so that `rack_status_callback` ignores updates from the wrong station.

```
next_station = "CAPP"       →  set when green explosion fires (AGV just arrived at STORE)
next_station = "STORE"      →  set when red explosion fires (AGV just arrived at CAPP), or when blue line is lost
next_station = "RETURN BOX" →  set when Empty button is toggled ON
next_station = None         →  only after node restart
```

The flag is **NOT cleared on docking completion** — it persists through the entire transit leg (docking + U-turn + return navigation) and is only overwritten when the *next* threshold explosion fires. See [[next_station_rack_filter]] for full details.

---

## AGV State Machine

The core operational flow (including transitions between RUNNING, U-TURN, DOCKING 1, DOCKING 2, and IDLE states) is documented in full detail in the dedicated state machine guide:
👉 **[[webcam_state_machine]]**

States published on `/agv/state`:
`WAITING`, `RUNNING`, `STOPPED`, `OBSTACLE_DETECTED`, `U-TURN`, `DOCKING 1`, `DOCKING 2`, `IDLE — CAPP FULL`, `IDLE — STORE EMPTY`, `WAITING — CONFIRM GO`

---

## image_callback Gate Order

1. `not self.enabled` → return
2. `self.obstacle_detected` → publish zero vel, return
3. `time.time() < self.resume_time` → publish zero vel, return
4. `self.idle_store_empty or self.idle_capp_full` → publish zero vel, return
5. Normal image processing / docking state machine

---

## Cross-References
- **Launch Context**: [[launch_behaviors]] (via `bringup_launch.py`).
- **Breakthroughs**: [[docking_and_uturn_logic]], [[line_changing_and_safety]], [[next_station_rack_filter]].
- **Dependencies**: Relies on `/rack_status` from [[rack_websocket_server]]. (Note: `webcam_line_follow.py` normalizes all incoming `rack_id` strings to uppercase to prevent casing mismatches).
- **Persistent State**: Relies on [[agv_state_yaml]] for retaining its destination and [[rack_state_yaml]] for offline resilience.
- **Related Nodes**: Replaced map-based navigation of [[orchestrator_node]].
- **UI Integration**: [[agv_display]], [[ui_integration_flow]].

---

## Resolved Capabilities
- **Blue Lane Return**: The system now seamlessly tracks blue lanes for returning empty boxes, successfully suppressing false-positive green explosions by evaluating `strip_sum` thresholds, and returning to green-line follow mode when blue is lost.
- **Speed Decay**: Implements dynamic speed decay at turns to reduce oscillation.
- **Systemd Audio**: Systemd stability issues with audio feedback have been resolved by delegating audio out of `ffplay` (see [[audio_systemd_stability]]).
