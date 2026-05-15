# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Build and Run Commands

**Build the workspace:**
```bash
cd /home/intern1/ros2_ws
colcon build
source install/setup.bash
```

**Run the AGV line-following node:**
```bash
ros2 run amr_ws webcam_line_follow
```

**Run the AGV UI:**
Open `src/html/agv_display.html` in a browser. It connects to rosbridge at `192.168.251.47:9090`.

**Common development workflow:**
1. Make changes to Python files in `src/amr_ws/amr_ws/`
2. Rebuild: `colcon build --packages-select amr_ws`
3. Source: `source install/setup.bash`
4. Restart the node

---

## Project Overview

Oriental Motor Singapore · ROS 2 Jazzy · Raspberry Pi 5
Last updated: May 2026

---

## Package Structure

**Main package:** `amr_ws` located in `src/amr_ws/`

**Key directories:**
- `amr_ws/` — Python modules (all ROS 2 nodes)
- `launch/` — Launch files (currently only slam_toolbox_launch.py)
- `params/` — Parameter files (slam_param.yaml)
- `nav2_params/` — Nav2 configuration (twist_mux.yaml, RPP params)
- `waypoints/` — Navigation waypoints (waypoints.yaml)
- `maps/` — Saved SLAM maps
- `html/` — Web UI files (agv_display.html is the active AGV control interface)

**Entry points** (defined in `setup.py`):
- `webcam_line_follow` — Main AGV line-following node
- `orchestrator_node` — AMR state machine (shelved)
- `localization_node` — AMR localization (shelved)
- `pose_persistence_node` — AMR pose caching (shelved)
- `rack_websocket_server` — ESP32 sensor bridge
- `hsv_probe_node` — HSV color tuning tool

---

## 1. Hardware

| Component | Detail |
|---|---|
| **Frame** | Square aluminium frame, differential drive |
| **Compute** | Raspberry Pi 5 |
| **ROS 2 Distro** | Jazzy |
| **Motor Controller** | Oriental Motor MVC01 — publishes `/odom` at 20 Hz |
| **LiDAR** | RPLiDAR S3 at 10 Hz |
| **Camera** | USB webcam — used for AGV line detection |
| **rosbridge** | Running on RPi 5 at `192.168.251.47:9090` |

**LiDAR obstruction note:** The battery at the rear and the corner aluminium frame supports partially block the LiDAR FOV. This has been worked around by adjusting collision detection thresholds in Nav2 rather than physically relocating the sensor.

---

## 2. AMR Phase (Shelved — resuming after AGV completion)

### Goal
Build a fully autonomous AMR that can boot, self-localize on a pre-built map, and navigate a fixed waypoint loop on the production floor without manual intervention.

### Navigation Stack
- **Mapping:** `slam_toolbox` with a pre-built saved map (localization-only mode at runtime)
- **Localization:** AMCL (particle filter). Convergence confirmed when covariance drops below `0.1`
- **Navigation:** Nav2 with a customized BT navigator and **Regulated Pure Pursuit (RPP)** controller
- **Waypoints:** Defined in `waypoints.yaml`. Waypoint 6 commented out for path efficiency
- **Velocity multiplexing (`twist_mux`):**
  - Priority 255 — `/cmd_vel_estop` — Orchestrator owns this (E-stop, localization spins)
  - Priority 100 — `/cmd_vel_nav` — Nav2 autonomous movement

### Architecture: Key Nodes

**`orchestrator_node.py`** — Central state machine. Strict transitions:
```
WAITING_FOR_LOCALIZATION → LOCALIZING → IDLE → NAVIGATING → TF_RECOVERY → FAULT
```
Cannot re-localize during an active mission. Cannot navigate unless in `IDLE`.

**`localization_node.py`** — Triggered on demand via `/amr/cmd_localize`. Seeds AMCL with an initial pose, then executes a physical spin-in-place sequence (4×90° then 2×180°) on the Priority 255 E-stop channel to force particle filter convergence.

**`pose_persistence_node.py`** — Continuously writes the robot's current pose to `amcl_logger.yaml`. On boot after unexpected shutdown or FAULT, automatically re-seeds AMCL with the last known pose.

**TF Safety Watchdog** — Monitors `/rosout` for "Transform data too old" errors. After 3 consecutive TF errors, enters `TF_RECOVERY`: halts, waits 30s, auto-resumes if stable.

**Halt Burst** — After every Nav2 goal completion, the orchestrator spams zero-velocity on the E-stop channel for 1 second to kill residual RPP wobble and momentum.

### Operational Flow
1. Boot → `WAITING_FOR_LOCALIZATION`
2. User sends `/amr/cmd_localize` → `LOCALIZING`, spin sequence runs
3. AMCL covariance < 0.1 → auto-promoted to `IDLE`
4. User sends `/amr/cmd_navigate` → `NAVIGATING`, waypoints sequenced
5. On completion → Halt Burst fires, returns to `IDLE`
6. TF fault → `TF_RECOVERY` → 30s → auto-resume or escalate
7. E-stop → `FAULT`, Priority 255 holds position
8. User sends `/amr/cmd_recover` → returns to `IDLE`

### Known Issues (at time of shelving)

| Issue | Detail |
|---|---|
| **Manual localization** | Automatic AMCL convergence not always reliable — may still require a manual 2D Pose Estimate click in RViz. No fixed start position defined yet; docking stations are planned for future use |
| **RPP over-rotation** | Robot reaches correct X/Y position but over-rotates on final theta correction. Suspected to be an RPP angular velocity tuning issue in `nav2_params.yaml` |
| **WiFi latency** | SSH-based control from a laptop was unreliable — latency caused command delays and instability. This was the primary reason AMR work was paused |

### Key Files

| File | Role |
|---|---|
| `orchestrator_node.py` | Central state machine, command handling, fault sequencing |
| `localization_node.py` | Spin-in-place localization routine, AMCL seeding |
| `pose_persistence_node.py` | Continuous pose cache, auto-recovery re-seed |
| `waypoints.yaml` | Ordered Nav2 goal poses for the production floor loop |
| `nav2_params.yaml` | RPP tuning, lookahead distance, Nav2 configuration |
| `amcl_logger.yaml` | Last-known-pose store written by pose persistence node |

---

## 3. Transition: AMR → AGV

The AMR was functionally navigating but suffered from **WiFi latency** when controlled over SSH from a laptop — causing command delays and instability. The project was redirected to an AGV (line-following) approach as a more robust near-term solution for the production floor.

The AGV hit the **same WiFi latency problem** initially, but it was resolved by **running all code directly on the Raspberry Pi 5** rather than over SSH. This is now the standard deployment approach for both robots going forward.

---

## 4. AGV Phase (Active)

### Goal
A camera-guided line-following AGV that can follow coloured tape on the production floor, switch between green and red line routes, perform U-turns, and execute docking protocols at rack stations.

### Architecture

**`webcam_line_follow.py`** — The core AGV node. Subscribes to:
- `/image_raw` — webcam frames
- `/scan` — RPLiDAR S3 for obstacle detection
- `/agv/cmd_enable` — GO command from UI
- `/agv/cmd_stop` — STOP command from UI
- `/agv/cmd_mode` — green/red line mode switch from UI
- `/rack_status` — ESP32 ultrasonic sensor bridge (`rack_id:status:distance_cm`)
- `/ui_heartbeat` — ping echo for latency display

Publishes to:
- `/cmd_vel_agv` — velocity commands to twist_mux (Priority 10)
- `/agv/state` — state feedback to UI (1 Hz heartbeat)
- `/agv/mode` — current follow mode feedback to UI

**`twist_mux.yaml`** — Updated priority scheme:

| Topic | Priority | Timeout |
|---|---|---|
| `/cmd_vel_teleop` | 255 | 0.5s |
| `/cmd_vel_estop` | 100 | 0.5s |
| `/cmd_vel_agv` | 10 | 0.5s |
| `/cmd_vel_nav` | 10 | 0.5s |

**Teleop arbitration (no runtime twist_mux modification):** When GO is pressed and the node confirms RUNNING via `/agv/state`, the UI simply stops publishing to `/cmd_vel_teleop` (which normally publishes at 10 Hz). twist_mux times out the teleop topic naturally within 0.5s, ceding control to `/cmd_vel_agv`. STOP re-enables teleop publishing within ~100ms. Clean and requires no dynamic reconfiguration.

**`agv_display.html`** — Browser-based control UI. Dark industrial theme (dark slate palette, JetBrains Mono for state display). 3-column CSS grid landscape layout. Connects to rosbridge at `192.168.251.47:9090`.

### Line Following

- **Sensor:** USB webcam, 20-row HSV strip at 75% of frame height
- **Controller:** PD controller (`Kp=0.0032`, `Kd=0.00072`)
- **Green line:** HSV `[35,40,40]` to `[120,255,255]`
- **Red line:** Dual HSV range to cover the 0°/180° hue wrap
- **Cruise speed:** 0.25 m/s with a slew-rate ramp (0.01 m/s per frame) to prevent jerky starts after obstacle clears
- **Strip optimisation:** HSV mask computed only on the 20-row strip, not the full frame (~40× fewer pixels)

### Follow Modes

**Green mode (default):** Follows green tape continuously. Performs green U-turns at green explosion zones.

**Red mode:** Follows green tape as primary. At intersections where red tape appears in the tracking strip (`red_strip_px ≥ 200`, centroid within ±45% of frame centre), diverts onto the red line. Performs red U-turns at red explosion zones.

**Mode switching** is seamless — motion is never interrupted. Switching green→red while moving simply enables red divert watching. Switching red→green cancels any active red tracking and red U-turns, reverting immediately to green following.

**Rack-triggered mode switching:** The ESP32 ultrasonic sensor bridge publishes to `/rack_status`. Status=1 (FULL) triggers red mode; Status=0 (EMPTY) triggers green mode. Routed through `mode_callback` so all transition logic is reused consistently.

### U-Turn Detection

Triggered by "explosion" — a large pixel sum in the tracking strip indicating the AGV is positioned over a wide tape marker rather than a narrow line.

| Trigger | Threshold | Action |
|---|---|---|
| Green explosion | `green_sum > 1,350,000` | Spin in place (`angular.z = -0.25`) → after 2s minimum, check for solid centred green line → enter Docking 1 |
| Red explosion | `red_strip_sum > 1,350,000` | Skip U-turn → directly enter Docking 2 |

U-turn exit condition: line must be solid (`mask_sum > 100,000`) AND centred (`|error| < 80px`).

### Docking Protocols

**Docking 1** (triggered after green U-turn):
1. Phase 1 — Rotate on spot using PD until `|error| ≤ 10px`
2. Phase 2 — Move backwards at 0.075 m/s for 5 seconds
3. Phase 3 — Hold position for 5 seconds
4. Resume normal line following

**Docking 2** (triggered by red explosion):
1. Phase 1 — Move backwards 0.075 m/s for 1 second
2. Phase 2 — Align with line using PD until `|error| ≤ 10px`
3. Phase 3 — Move forward at 0.075 m/s for 5 seconds
4. Phase 4 — Hold position for 5 seconds
5. Phase 5 — Move backwards for 5 seconds → trigger red U-turn to return

### LiDAR Safety (Tiered Zones)

Four concentric safety cones. Closer objects trigger a narrower cone (fewer false positives from sides); farther objects use a wider cone for early warning.

| Zone | Distance | Cone (total) |
|---|---|---|
| 1 | 0 – 0.15 m | 45° (±22.5°) |
| 2 | 0.15 – 0.25 m | 60° (±30°) |
| 3 | 0.25 – 0.50 m | 90° (±45°) |
| 4 | 0.50 – 0.75 m | 120° (±60°) |

**Obstacle debounce:** 20 consecutive clear frames required before resuming (prevents jitter). On clear, robot waits an additional 3 seconds before resuming line following. Linear speed resets to 0 on obstacle detection so the slew-rate ramp always applies on resume.

**LiDAR frame orientation note:** Forward direction aligns with `angle = ±π` in the RPLiDAR S3 frame (not 0). The scan callback normalises angles to `(-π, π]` and computes forward distance as `|abs(angle) - π|`.

### AGV State Machine

| State | Meaning |
|---|---|
| `WAITING` | Node started, not yet enabled |
| `RUNNING` | Line following active |
| `STOPPED` | STOP command received, teleop restored |
| `OBSTACLE_DETECTED` | LiDAR triggered, robot halted |
| `U-TURN` | Spinning in place |
| `DOCKING 1` | Docking 1 protocol active |
| `DOCKING 2` | Docking 2 protocol active |

### UI: `agv_display.html`

- **Single-client session enforcement:** Each browser tab publishes its `clientId` + `sessionStartTime` to `/ui_active_client`. Newer session wins; older session is shown a "Session Terminated" screen with a reconnect button.
- **Teleop lock overlay:** When AGV state is RUNNING/DOCKING/U-TURN, a blur overlay covers both joystick panels (`z-index: 10`). GO and STOP buttons sit above this overlay (`z-index: 20`) and remain clickable at all times.
- **Ping display:** UI heartbeat echoed back by node; exponential moving average smoothing applied (α=0.3). Green <50ms, amber <150ms, red ≥150ms.
- **Mode button:** Synced to `/agv/mode` (1 Hz node broadcast). Toggle switches between green and red. Publishes to `/agv/cmd_mode`.
- **Node watchdog:** If no `/agv/state` message received for 3 seconds, UI shows INACTIVE and disables all buttons.
- **Responsive layout:** CSS variables + media queries for landscape desktop (3-column grid), landscape mobile (compact), and portrait mobile (2-column stacked).

### Key Files

| File | Role |
|---|---|
| `amr_ws/webcam_line_follow.py` | Core AGV ROS 2 node — line following, obstacle detection, docking |
| `amr_ws/rack_websocket_server.py` | ESP32 ultrasonic sensor bridge → `/rack_status` |
| `amr_ws/hsv_probe_node.py` | HSV color tuning tool for line detection |
| `nav2_params/twist_mux.yaml` | Velocity multiplexer config (teleop 255, estop 100, agv/nav 10) |
| `html/agv_display.html` | Browser control UI — joystick teleop + autonomous control |

---

## Development Notes

**Working with webcam_line_follow.py:**
- Main AGV logic is in `WebcamLineFollow` class
- Image processing uses 20-row HSV strip at 75% of frame height for performance
- LiDAR safety uses tiered zones defined in `SAFETY_TIERS` constant
- PD controller gains: `Kp=0.0032`, `Kd=0.00072`
- State machine transitions are handled via callback methods

**Color tuning:**
- Use `hsv_probe_node.py` to visualize HSV ranges in real-time
- Green line: HSV `[35,40,40]` to `[120,255,255]`
- Red line: Dual HSV range to cover 0°/180° hue wrap

**UI development:**
- UI uses roslib.js for WebSocket connection to rosbridge
- Single-client session enforcement via `/ui_active_client` topic
- Responsive design with CSS variables for different screen sizes

**Deployment:**
- All code runs directly on Raspberry Pi 5 (not over SSH) to avoid WiFi latency
- rosbridge runs at `192.168.251.47:9090`
- UI connects from any device on the same network

---

## 5. What's Next (AGV)

AGV is functional with green/red line following, U-turns, and docking. Remaining work before AMR phase resumes:

- Finalise docking timing and distances for the actual production floor rack positions
- Validate red/green mode switching reliability with the ESP32 rack sensor in-loop
- Any further UI refinements

## 6. What's Next (AMR — resuming after AGV)

- Resolve automatic AMCL convergence on startup (remove dependency on manual RViz pose estimate)
- Tune RPP angular velocity to fix over-rotation on final theta correction
- Define fixed start positions / docking stations for pose seeding
- Validate full autonomous waypoint loop on the production floor
