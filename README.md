Here is the collated README with my comments inline as blockquotes:

---

# AGV Project — README

**语言：** 🇬🇧 [English](https://github.com/internOM/amr-OMAP/blob/main/README.md) | 🇨🇳 [简体中文](https://github.com/internOM/amr-OMAP/blob/main/README_CN.md)

> **Overall comment:** The documentation is well-structured and technically accurate. The main gaps are: no troubleshooting section, no hardware wiring reference, and the operational flow described in the walkthrough files doesn't fully reflect the latest changes (sensor gate logic, WAITING — NO RACK, WAITING — CONFIRM states). These should be updated once the new code is finalised. I'd also recommend adding a quick-start section at the top for operators who don't need the full technical detail.

---

## Table of Contents
1. [Project Overview](#overview)
2. [System Architecture](#architecture)
3. [Workspace Structure](#workspace)
4. [Nodes & Components](#nodes)
5. [Running the System](#running)
6. [AGV Operational Logic](#logic)
7. [Operator Dashboard](#dashboard)

---

## 1. Project Overview

This project implements a camera-based Autonomous Guided Vehicle (AGV) system built on ROS 2. The AGV follows coloured tape lines (green and red) on a factory floor to shuttle material boxes between two permanent rack stations:

- **Store** — the loading station, where the AGV picks up boxes
- **CA-PP** — the unloading station, where the AGV drops off boxes

The AGV runs a continuous loop between the two stations. Lane selection, docking behaviour, and safety responses are all handled autonomously, with a web-based operator dashboard for monitoring and manual override.

> **Comment:** Good summary. Consider adding one line on the hardware platform — what robot base, what compute (Raspberry Pi + base station PC), and what sensors (camera model, LiDAR model). This is the first thing a new team member will want to know.

---

## 2. System Architecture

The AGV relies on a distributed ROS 2 Publish-Subscribe architecture. Hardware components publish raw sensor data to topics. The core logic node (`webcam_line_follow.py`) subscribes to all sensors, processes them, and publishes velocity commands. A web-based UI connects via `rosbridge_websocket`.

### Node Communication Map

| Topic | Direction | Type | Purpose |
|---|---|---|---|
| `/image_raw` | → node | `sensor_msgs/Image` | Camera frames for line detection |
| `/scan` | → node | `sensor_msgs/LaserScan` | LiDAR obstacle detection |
| `/rack_status` | → node | `std_msgs/String` | ESP32 rack slot occupancy |
| `/agv/cmd_enable` | → node | `std_msgs/Bool` | GO / operator confirm |
| `/agv/cmd_stop` | → node | `std_msgs/Bool` | Emergency stop |
| `/agv/cmd_mode` | → node | `std_msgs/String` | Manual lane override |
| `/cmd_vel_agv` | node → | `geometry_msgs/Twist` | Velocity commands to twist_mux |
| `/agv/state` | node → | `std_msgs/String` | Current AGV state to UI |
| `/agv/mode` | node → | `std_msgs/String` | Current lane mode to UI |
| `/ui_heartbeat` | both | `std_msgs/String` | Ping/latency measurement |

### Velocity Priority (twist_mux)

| Topic | Priority | Timeout |
|---|---|---|
| `/cmd_vel_teleop` | 255 | 0.5s |
| `/cmd_vel_estop` | 100 | 0.5s |
| `/cmd_vel_agv` | 10 | 0.5s |

> **Comment:** The communication map is clear and complete. One thing worth adding here is a note explaining the teleop handoff mechanism — that the UI stops publishing `/cmd_vel_teleop` when GO is pressed, causing it to time out in twist_mux within 0.5s, naturally ceding control to `/cmd_vel_agv`. This is non-obvious and has caused confusion before.

---

## 3. Workspace Structure

```text
ros2_ws/
└── src/
    └── amr_ws/
        ├── amr_ws/
        │   ├── webcam_line_follow.py       # Core AGV brain
        │   ├── rack_websocket_server.py    # ESP32 WebSocket bridge
        │   └── joystick_to_motor.py        # Legacy testing only — not used
        ├── html/
        │   └── agv_display.html            # Operator dashboard
        ├── launch/
        │   └── bringup_launch.py           # Hardware launch (run on Pi)
        ├── params/                         # Configuration parameters
        └── setup.py                        # Entry points
```

> **Comment:** Clean. Consider adding a note that `joystick_to_motor.py` is deliberately kept for reference but should not be launched. Also worth noting which files live on the Pi vs. the base station PC, since the system is split across two machines.

---

## 4. Nodes & Components

### `webcam_line_follow.py` — Core AGV Brain

The central controller. Integrates vision, safety, rack sensor logic, and motor control into a single state machine.

**Key subsystems:**

**Vision Processing**
- Subscribes to `/image_raw` at ~10 Hz
- Slices each frame to a 20-pixel tracking strip at 3/4 height to minimise processing overhead
- Converts strip to HSV and applies separate green and red colour masks
- Calculates line centroid via image moments (`m10 / m00`)

**PD Controller**
- Error = centroid X position minus image centre (`w // 2`)
- P term reacts to current error; D term damps oscillation
- Output drives `angular.z`; `linear.x` is separately managed via slew-rate limiter
- Parameters: `Kp = 0.0032`, `Kd = 0.00072`, `MAX_ANG_Z = 1.0`

**LiDAR Tiered Safety**
- Four safety zones, each with a distance threshold and cone angle
- Closer objects use a narrower cone to reduce false positives from side structures
- Requires 20 consecutive clear frames before declaring path clear
- 3-second wait after clearing before resuming, with slew-rate ramp-up

| Zone | Distance | Cone |
|---|---|---|
| 1 | 0–0.225 m | ±45° |
| 2 | 0.225–0.318 m | ±22.5° |
| 3 | 0.318–0.45 m | ±15° |
| 4 | 0.45–0.588 m | ±11.25° |

**Rack Sensor Integration**
- Maintains a dictionary of 12 slot states across Store and CA-PP stations
- Rack IDs: `Store-A1` through `Store-B3`, `CAPP-A1` through `CAPP-B3`
- Column A or B is considered occupied if **any** of its 3 row sensors reads `1`
- Lane is re-evaluated on every sensor update and applied seamlessly via `mode_callback`

> **Comment:** Good level of detail. The LiDAR zone table values look like they may be slightly different from the actual code constants — worth double-checking these match `SAFETY_TIERS` in `webcam_line_follow.py` exactly before publishing this README.

---

### `rack_websocket_server.py` — ESP32 Bridge

Runs a WebSocket server (default port 8000) that accepts connections from ESP32 microcontrollers mounted on the racks. Parses incoming JSON and publishes to `/rack_status`.

**Message format received from ESP32:**
```json
{ "rack_id": "CAPP-A1", "status": 1, "distance_cm": 4.2 }
```

**Message format published to ROS:**
```
rack_id:status:distance_cm
e.g. "CAPP-A1:1:4.2"
```

Each ESP32 implements its own debounce state machine (5 frames) before changing status, preventing false triggers from transient readings.

> **Comment:** Good. Worth adding a note here about what happens if an ESP32 disconnects mid-run — does the node retain the last known state or reset to 0? This is an important edge case for production. Currently the node retains the last known value, which is the safer default, but it should be documented explicitly.

---

### `agv_display.html` — Operator Dashboard

Web-based control panel connecting to ROS via `rosbridge_websocket` on port 9090. Served via Python HTTP server on port 8080.

**Features:**
- Real-time AGV state display with colour-coded styling
- GO / STOP buttons publishing to `/agv/cmd_enable` and `/agv/cmd_stop`
- Lane mode toggle publishing to `/agv/cmd_mode`
- Ping/latency display via `/ui_heartbeat` round-trip measurement
- Scrolling activity log with timestamped state transitions
- Single-session enforcement via `/ui_active_client` — only one browser tab may control the AGV at a time; a second tab connecting will terminate the first
- Joystick teleoperation via `/cmd_vel_teleop` (lock overlay shown during autonomous operation)

> **Comment:** The single-session enforcement is an important safety feature that deserves a clearer callout here — explain what happens to a displaced session (they see a "Session Terminated" screen with a Reconnect button). Also, the activity log section mentions it listens to `/agv/state` and `/agv/mode` — worth clarifying that log entries are generated on state *transitions*, not on every 1Hz heartbeat republish, otherwise operators might wonder why the log isn't updating constantly.

---

## 5. Running the System

### Prerequisites
- ROS 2 installed and sourced
- `rosbridge_server` package installed
- `twist_mux` package installed and configured

### Build
```bash
cd ~/ros2_ws
colcon build --packages-select amr_ws --symlink-install
source ~/ros2_ws/install/setup.bash
```

### On the Raspberry Pi (hardware)
```bash
ros2 launch amr_ws bringup_launch.py
```

### On the Base Station PC (terminals)
```bash
# Terminal 1 — Core AGV node
ros2 run amr_ws webcam_line_follow

# Terminal 2 — Rack sensor bridge
ros2 run amr_ws rack_websocket_server

# Terminal 3 — ROS bridge for web UI
ros2 run rosbridge_server rosbridge_websocket --ros-args -p delay_between_messages:=0.0

# Terminal 4 — Serve the operator dashboard
cd ~/ros2_ws/src/amr_ws/html && python3 -m http.server 8080
```

Operators navigate to `http://<Robot_IP>:8080/agv_display.html` on any device on the same network.

> **Comment:** This section is functional but minimal. Strongly recommend adding: (1) a note on the order of startup — the AGV node should ideally start after the camera and LiDAR drivers are confirmed running, otherwise it will silently miss early frames; (2) the rosbridge IP dependency — `agv_display.html` connects to `window.location.hostname:9090`, so the HTML must be served from the same machine running rosbridge, or the IP must be manually edited; (3) a shutdown procedure — just `Ctrl+C` each terminal in reverse order, but worth stating explicitly for operators unfamiliar with ROS.

---

## 6. AGV Operational Logic

### Continuous Loop

The AGV runs a perpetual loop between two stations:

```
[Store — Loading] ──green line──▶ [Green Explosion] ──▶ [U-Turn] ──▶ [Docking 1 — CA-PP Unload]
        ▲                                                                          │
        └───────────────────────red line──── [Docking 2 — Store Load] ◀───────────┘
```

### Lane Selection

Lane is determined continuously from live rack sensor state and re-applied whenever sensor data changes.

**At Store (green explosion — loading). Go where material is. A takes priority:**

| store_A | store_B | Lane |
|---|---|---|
| 0 | 0 | Stop — nothing to load |
| 0 | 1 | Red |
| 1 | 0 | Green |
| 1 | 1 | Green |

**At CA-PP (red explosion — unloading). Avoid full columns. Default green:**

| capp_A | capp_B | Lane |
|---|---|---|
| 0 | 0 | Green |
| 0 | 1 | Green |
| 1 | 0 | Red |
| 1 | 1 | Stop — both full |

### State Transition Diagram

```
STOPPED ──GO──▶ RUNNING ──green explosion──▶ U-TURN ──▶ DOCKING 1
                   │                                         │
                   │◀────────────────────────────────────────┘ (complete)
                   │
                   └──red explosion──▶ DOCKING 2 ──▶ U-TURN ──▶ RUNNING
                   │
                   └──obstacle──▶ OBSTACLE DETECTED ──(clear)──▶ RUNNING
                   │
                   └──rack full──▶ WAITING — NO RACK ──(rack clears)──▶ RUNNING
                   │
                   └──slot blocked──▶ WAITING — CONFIRM ──(operator GO)──▶ DOCKING 2 Phase 3
```

### Docking 1 — Unload at CA-PP
Triggered by green explosion, entered after U-turn completes.

| Phase | Action | Duration |
|---|---|---|
| 1 | Spot alignment using PD (linear.x = 0) | Until error ≤ 10px |
| 2 | Reverse into station | 5 seconds |
| 3 | Hold — unloading | 5 seconds |
| Complete | Resume RUNNING | — |

### Docking 2 — Load at Store
Triggered directly by red explosion.

| Phase | Action | Duration |
|---|---|---|
| 1 | Reverse to position | 1.5 seconds |
| 2 | Spot alignment using PD | Until error ≤ 10px |
| 3 | Forward into station | 5 seconds |
| 4 | Hold — loading. **Sensor gate: if slot occupied, enter WAITING — CONFIRM** | 5 seconds |
| 5 | Reverse out | 5 seconds |
| Complete | Trigger U-turn | — |

> **Comment:** The docking tables are clear. One correction to flag: based on the agreed summary, the sensor gate in Docking 2 is at the transition between Phase 2 and Phase 3 (after alignment, before moving forward), not during Phase 4. Verify this against the final code and update accordingly. Also worth noting that LiDAR obstacle detection is **disabled** during docking and U-turns to prevent false stops from rack structures.

---

## 7. Operator Dashboard Reference

### State Display Colours

| State | Colour | Meaning |
|---|---|---|
| RUNNING | Green | Line following active |
| STOPPED | Red | Halted by operator |
| OBSTACLE DETECTED | Red | LiDAR blocked — waiting to clear |
| U-TURN | Amber | Executing turn manoeuvre |
| DOCKING 1 / 2 | Purple | Docking protocol active |
| WAITING — NO RACK | Red | No rack available at station |
| WAITING — CONFIRM | Amber | Slot sensor blocked — press GO to proceed |

### Button Reference

| Button | Topic | Effect |
|---|---|---|
| GO | `/agv/cmd_enable` | Start line following, or confirm sensor gate |
| STOP | `/agv/cmd_stop` | Immediately halt AGV |
| Mode toggle | `/agv/cmd_mode` | Switch between green and red lane manually |

> **Comment:** Good reference table. Worth adding a note that manual mode toggle is overridden by automatic lane switching from rack sensors — if the operator toggles to red but the sensor logic says green, the node will switch back within one sensor update cycle. This can be confusing for operators who expect the toggle to be persistent.

---

> **Final comment:** Once the new sensor gate code is written and tested, come back and update sections 4 (rack sensor integration detail), 6 (docking phase table — confirm which phase the sensor gate sits in), and the state transition diagram. The README is otherwise comprehensive enough to hand to a new team member. Consider adding a known issues / limitations section at the end once the system has been tested end-to-end.