# AGV Handover

Last reviewed: 2026-06-16

This handover covers the AGV line-following project. The workspace also contains an older AMR/Nav2 project; that material is included only as legacy context where it explains why the current AGV architecture exists.

Primary reference folder: `Developer-Brain/`

## 1. Project Split

### Active AGV project

The active AGV project is a deterministic line-following robot. It uses a USB camera to follow colored tape, LiDAR for direct obstacle stops, rack ultrasonic sensors for lane/docking decisions, and a web UI for operator control.

Main package:

- `src/amr_ws`

Main runtime launch:

- `src/amr_ws/launch/bringup_launch.py`

Main runtime node:

- `src/amr_ws/amr_ws/webcam_line_follow.py`

### Legacy AMR project

The previous AMR project used SLAM, AMCL, Nav2, waypoint navigation, and an orchestrator state machine. This path is not the normal AGV operating mode now.

Legacy/AMR files still present:

- `src/amr_ws/amr_ws/orchestrator_node.py`
- `src/amr_ws/amr_ws/localization_node.py`
- `src/amr_ws/amr_ws/return_home_node.py`
- `src/amr_ws/amr_ws/path_logger.py`
- `src/amr_ws/amr_ws/path_publisher.py`
- `src/amr_ws/nav2_params/*`
- `src/amr_ws/waypoints/*`
- `src/html/Auto.html`

Reason for transition: the AMR/Nav2 path suffered from TF staleness, localization drift, costmap latency, and unpredictable behavior in a dynamic factory environment. The AGV line-following approach was adopted for repeatable physical routes and tighter docking.

## 2. Folder Structure

Important AGV folders:

- `src/amr_ws/amr_ws/`
  - Python ROS 2 nodes.
- `src/amr_ws/launch/`
  - AGV bringup and SLAM launch files.
- `src/amr_ws/params/`
  - Runtime persistent state and SLAM params.
- `src/amr_ws/nav2_params/`
  - Nav2 params plus the existing `twist_mux.yaml`.
- `src/amr_ws/maps/`
  - Legacy/SLAM maps.
- `src/amr_ws/urdf/`
  - Robot xacro.
- `src/amr_ws/waypoints/`
  - Legacy AMR waypoint and AMCL pose files.
- `src/html/`
  - Browser-based HMI dashboards.
- `src/rplidar_ros/`
  - RPLidar driver.
- `src/camera_follow/`
  - Older camera-follow experiments and variants.
- `Developer-Brain/`
  - Human-readable design notes, debugging history, and architecture reference.

## 3. Launch Files

### Active AGV launch

`src/amr_ws/launch/bringup_launch.py`

Starts the hardware and AGV software stack:

- Includes `om_mvc01/launch/om_MVC01_bringup_launch.py`
  - Motor bridge for the physical AGV.
  - Launch argument: `updateRate=10`.
- Includes `rplidar_ros/launch/rplidar_s3_launch.py`
  - Starts the S3 lidar driver.
- Starts `usb_cam/usb_cam_node_exe`
  - `video_device=/dev/video0`
  - `image_width=320`
  - `image_height=240`
  - `framerate=15.0`
  - `pixel_format=yuyv`
- Starts `amr_ws/agv_audio_node`
  - Background music, obstacle horn, docking audio.
- Starts `amr_ws/webcam_line_follow`
  - Core AGV line-following and docking logic.
- Starts `rosbridge_server/rosbridge_websocket`
  - Web UI bridge, expected by dashboards on port `9090`.
- Starts `twist_mux/twist_mux`
  - Arbitrates teleop, e-stop, AGV, and Nav2 velocity channels.
  - Remaps `cmd_vel_out` to `/cmd_vel`.
- Starts `amr_ws/rack_websocket_server`
  - ESP32 rack sensor bridge.
- Starts `python3 -m http.server 8080`
  - Serves `src/html` style dashboards from `/home/amr/ros2_ws/src/amr_ws/html` in the launch file.
- Starts `amr_ws/agv_shutdown_node`
  - Remote shutdown service.

Notes to verify before deployment:

- The launch file points `twist_mux` at `/home/amr/ros2_ws/src/amr_ws/params/twist_mux.yaml`, but the source tree currently has `twist_mux.yaml` under `src/amr_ws/nav2_params/`.
- The launch file serves HTTP from `/home/amr/ros2_ws/src/amr_ws/html`, while this workspace has the HTML folder at `src/html/`.
- `setup.py` registers `agv_shutdown_node = amr_ws.agv_shutdown_node:main`, but the source file is named `agv_shudown_node.py`.

### SLAM launch

`src/amr_ws/launch/slam_toolbox_launch.py`

Starts:

- `slam_toolbox/sync_slam_toolbox_node`

Uses:

- `src/amr_ws/params/slam_param.yaml`

Current role:

- Mostly legacy or mapping-specific.
- Standard AGV operation bypasses SLAM/Nav2.

### Supporting launch files

- `src/rplidar_ros/launch/rplidar_s3_launch.py`
  - Starts `rplidar_node`.
  - Defaults include serial channel, baud `256000`, frame `laser`, scan mode `DenseBoost`.
- `src/ros2_system_webview/launch/main.launch.py`
  - System web dashboard, HTTP server, optional rosbridge.
- `src/camera_follow/launch/linetrace_launch.py`
  - Older camera-follow launch, not the current AGV bringup.
- `src/ros2-slam-auto-navigation/launch/*`
  - Simulation/older navigation examples.
- `src/tb3_multi_robot/launch/*`
  - TurtleBot multi-robot simulation.

## 4. Main ROS 2 Nodes

### `webcam_line_follow`

File:

- `src/amr_ws/amr_ws/webcam_line_follow.py`

Role:

- Core AGV brain.
- Processes `/image_raw` with OpenCV HSV masks.
- Tracks green, red, and blue tape.
- Publishes AGV velocity to `/cmd_vel_agv`.
- Runs U-turn and docking state machines.
- Performs direct LiDAR obstacle stops.
- Reads rack state and persistent next-station state.

Important states published on `/agv/state`:

- `WAITING`
- `RUNNING`
- `STOPPED`
- `OBSTACLE_DETECTED`
- `U-TURN`
- `DOCKING 1`
- `DOCKING 2`
- `WAITING - CONFIRM GO`
- `IDLE - CAPP FULL`
- `IDLE - STORE EMPTY`
- `IDLE - RETURN BOX`

The source currently uses some Unicode dash variants in state strings; check exact strings in the code/UI if matching state names programmatically.

### `rack_websocket_server`

File:

- `src/amr_ws/amr_ws/rack_websocket_server.py`

Role:

- WebSocket server for ESP32 ultrasonic rack sensors.
- Publishes rack occupancy into ROS 2.
- Broadcasts updates to dashboards.
- Persists last-known rack status to `rack_state.yaml`.

Defaults:

- `ws_host=0.0.0.0`
- `ws_port=8000`

### `agv_audio_node`

File:

- `src/amr_ws/amr_ws/agv_audio_node.py`

Role:

- Plays background music on GO.
- Stops music on STOP.
- Plays horn on obstacle.
- Plays docking audio during `DOCKING 1` and `DOCKING 2`.

Implementation note:

- Uses `ffmpeg` routed directly to ALSA device `plughw:2,0`.
- This replaced older `ffplay`/PulseAudio-style playback because systemd/headless audio was unstable.

### `agv_shutdown_node`

File in source:

- `src/amr_ws/amr_ws/agv_shudown_node.py`

Role:

- Provides `/agv/shutdown` service.
- Returns success first, then runs `sudo shutdown -h now` after a short timer.

Deployment note:

- The file is misspelled as `agv_shudown_node.py`, but `setup.py` references `amr_ws.agv_shutdown_node`. Fixing this mismatch would be needed for a clean install/run path.

### `joystick_to_motor`

File:

- `src/amr_ws/amr_ws/joystick_to_motor.py`

Role:

- Converts `/html_direction` to `/cmd_vel`.
- Older/manual direction interface.
- Uses an internal timeout to stop if the joystick disconnects.

### Legacy AMR nodes

These are mostly from the previous AMR project:

- `orchestrator_node`
  - Nav2 state machine.
  - Handles localization commands, waypoint navigation, return-home, e-stop, TF recovery.
- `localization_node`
  - Calls `/set_initial_pose`, spins robot for AMCL convergence.
- `return_home_node`
  - Sends a `NavigateToPose` goal home.
- `path_logger`
  - Logs AMCL pose/path into waypoint files.
- `path_publisher`
  - Sends waypoints via `FollowWaypoints`.
- `pose_persistence_node`
  - Saves/restores AMCL pose.
- `cmdvelsmoothed_to_cmdvel`
  - Legacy Nav2 velocity forwarder.

## 5. Topics

### Core AGV command/control topics

Published by UI, consumed by `webcam_line_follow`:

- `/agv/cmd_enable` (`std_msgs/Bool`)
  - GO command.
  - Also acts as operator confirm during docking wait states.
- `/agv/cmd_stop` (`std_msgs/Bool`)
  - STOP command.
  - Immediately disables AGV line-following and publishes zero velocity.
- `/agv/cmd_mode` (`std_msgs/String`)
  - Follow-mode override: `green` or `red`.
- `/agv/cmd_return_empty` (`std_msgs/Bool`)
  - Toggles Return Empty Box / blue-line mode.

Published by `webcam_line_follow`, consumed by UI/audio:

- `/agv/state` (`std_msgs/String`)
  - Main AGV state.
- `/agv/mode` (`std_msgs/String`)
  - Current lane mode.
- `/agv/next_station` (`std_msgs/String`)
  - Current committed next station, usually `STORE` or `CAPP`.
- `/ui_heartbeat` (`std_msgs/String`)
  - Echo/ping flow with UI.

### Motion topics

- `/cmd_vel_agv` (`geometry_msgs/Twist`)
  - Published by `webcam_line_follow`.
  - Routed through `twist_mux`.
- `/cmd_vel_teleop` (`geometry_msgs/Twist`)
  - Published by manual teleop UI.
  - Highest priority manual override.
- `/cmd_vel_estop` (`geometry_msgs/Twist`)
  - Used by legacy AMR orchestrator/localization for halt/spin behavior.
  - Higher priority than AGV/Nav2 in `twist_mux`.
- `/cmd_vel_nav` (`geometry_msgs/Twist`)
  - Nav2 velocity channel in legacy AMR path.
- `/cmd_vel`
  - Final motor command output from `twist_mux`.

### Sensor topics

- `/image_raw` (`sensor_msgs/Image`)
  - Published by USB camera.
  - Consumed by `webcam_line_follow` and camera dashboards.
- `/scan` (`sensor_msgs/LaserScan`)
  - Published by `rplidar_node`.
  - Consumed by `webcam_line_follow`, `compass`, Nav2/SLAM configs.
- `/rack_status` (`std_msgs/String`)
  - Published by `rack_websocket_server`.
  - Format: `RACK_ID:STATUS:DISTANCE_CM`
  - Example: `CAPP-A1:1:12.5`
  - `STATUS`: `1=FULL`, `0=EMPTY`, `-1=DISCONNECTED`.

### UI/session topics

- `/ui_active_client` (`std_msgs/String`)
  - Used by dashboards for single-client/session locking.
- `/html_direction` (`std_msgs/String`)
  - Older manual direction input used by `joystick_to_motor`.

### Legacy AMR topics

Used by `orchestrator_node` and related Nav2/AMCL nodes:

- `/amr/state`
- `/robot_status`
- `/amr/fault_trigger`
- `/amr/cmd_localize`
- `/amr/cmd_recover_localize`
- `/amr/cmd_navigate`
- `/amr/cmd_return_home`
- `/amr/cmd_estop`
- `/amr/cmd_recover`
- `/amcl_pose`
- `/odom`
- `/rosout`
- `/initialpose`
- `/logged_path`

## 6. Services

### Active AGV

- `/agv/shutdown` (`std_srvs/srv/Trigger`)
  - Intended to shut down the Raspberry Pi from the UI.
  - Implemented in `agv_shudown_node.py`.

### Legacy AMR/Nav2

- `/set_initial_pose` (`nav2_msgs/srv/SetInitialPose`)
  - Used by `localization_node` and `orchestrator_node`.

## 7. Actions

### Legacy AMR/Nav2

- `navigate_to_pose` (`nav2_msgs/action/NavigateToPose`)
  - Used by `orchestrator_node` and `return_home_node`.
- `follow_waypoints` (`nav2_msgs/action/FollowWaypoints`)
  - Used by `path_publisher`.

No custom AGV action interface is used by the active line-following workflow.

## 8. Parameters and State Files

### Active AGV state files

`src/amr_ws/params/agv_state.yaml`

- Persists `next_station`.
- Current source value: `STORE`.
- Purpose: after restart, the AGV remembers which station it is committed to.

`src/amr_ws/params/rack_state.yaml`

- Persists all 12 rack slots.
- Keys include:
  - `STORE-A1`, `STORE-A2`, `STORE-A3`
  - `STORE-B1`, `STORE-B2`, `STORE-B3`
  - `CAPP-A1`, `CAPP-A2`, `CAPP-A3`
  - `CAPP-B1`, `CAPP-B2`, `CAPP-B3`
- Values:
  - `1=FULL`
  - `0=EMPTY`
  - `-1=DISCONNECTED`

### `webcam_line_follow` internal constants

Important constants from code:

- Safety tiers:
  - `0.225 m`, `90 deg`
  - `0.3182 m`, `45 deg`
  - `0.45 m`, `30 deg`
- Obstacle clear debounce:
  - `20` consecutive clear scan frames.
- Resume delay:
  - `3 seconds` after debounce.
- Linear slew:
  - `0.0025 m/s` per processed image frame.
- PD gains:
  - `Kp=0.0033`
  - `Kd=0.00073`
- Max angular velocity:
  - `1.0 rad/s`
- Normal cruise target:
  - `0.28 m/s`
- Sharp-turn target:
  - `0.24 m/s`
- U-turn angular velocity:
  - `-0.25 rad/s`
- U-turn minimum time:
  - `2.0 seconds`

### `twist_mux`

Existing file:

- `src/amr_ws/nav2_params/twist_mux.yaml`

Configured priorities:

- `/cmd_vel_teleop`
  - Priority `255`
  - Manual operator override.
- `/cmd_vel_estop`
  - Priority `100`
  - E-stop/localization/legacy orchestrator channel.
- `/cmd_vel_agv`
  - Priority `10`
  - Active line-following AGV.
- `/cmd_vel_nav`
  - Priority `10`
  - Legacy Nav2.

Design assumption:

- AGV line-following and Nav2 are not run at the same time.

### SLAM/Nav2 params

Legacy/AMR-related:

- `src/amr_ws/params/slam_param.yaml`
- `src/amr_ws/nav2_params/nav2_params.yaml`
- `src/amr_ws/nav2_params/nav2_rpp_params.yaml`
- `src/amr_ws/nav2_params/nav2_rotational_shim_controller.yaml`
- `src/amr_ws/nav2_params/custom_recovery_bt.xml`
- `src/amr_ws/waypoints/waypoints.yaml`

## 9. How The AGV Starts

Normal operating flow:

1. Launch `bringup_launch.py`.
2. Motor bridge, LiDAR, USB camera, rosbridge, HTTP server, rack bridge, audio, `twist_mux`, and `webcam_line_follow` start.
3. `webcam_line_follow` boots in `WAITING`.
4. It loads:
   - `next_station` from `agv_state.yaml`.
   - rack slot states from `rack_state.yaml`.
5. UI connects through rosbridge.
6. Operator presses GO.
7. UI publishes `/agv/cmd_enable=True`.
8. `webcam_line_follow` sets `enabled=True`.
9. If no obstacle or hold condition is active, state becomes `RUNNING`.
10. Camera frames begin producing `/cmd_vel_agv`.
11. `twist_mux` outputs the selected velocity to `/cmd_vel`.

## 10. How The AGV Stops

### Operator STOP

1. UI publishes `/agv/cmd_stop=True`.
2. `webcam_line_follow` sets `enabled=False`.
3. It publishes zero `Twist` to `/cmd_vel_agv`.
4. State becomes `STOPPED`.
5. U-turn, docking, obstacle, and wait flags are cleared.
6. `next_station` is deliberately preserved so the UI and restart behavior still know the committed destination.

### Obstacle stop

1. `webcam_line_follow` detects a LiDAR beam inside one of the safety zones.
2. It sets `obstacle_detected=True`.
3. It publishes zero `Twist`.
4. State becomes `OBSTACLE_DETECTED`.
5. Once path is clear for 20 scan frames, it waits another 3 seconds.
6. It resumes line following with speed ramped from zero.

### No-line stop

If the active color mask loses the line and cannot fall back safely, `webcam_line_follow` publishes zero velocity and logs a warning.

### Rack hold states

The robot stops but does not fault:

- `IDLE - CAPP FULL`
  - STORE pickup would be pointless because CAPP has no receiving capacity.
- `IDLE - STORE EMPTY`
  - CAPP deposit/return leg finished but STORE has no material.
- `IDLE - RETURN BOX`
  - Blue return-box threshold reached.
- `WAITING - CONFIRM GO`
  - Docking dwell completed and operator confirmation is required.

## 11. Core Navigation and Docking Flow

### Normal line following

- Default line is green.
- Red is used as a conditional lane/diversion.
- Blue is used for Return Empty Box behavior.
- HSV masks are computed from a narrow strip near the lower part of the camera frame.
- The centroid of the active mask drives a PD controller.

### Lane decision

Lane selection is based on the next station's rack state:

- Heading to `CAPP`:
  - Inspect CAPP racks only.
  - Use red when CAPP A is full and CAPP B has space.
  - Otherwise use green.
- Heading to `STORE`:
  - Inspect STORE racks only.
  - Use red when STORE B is full and STORE A has space.
  - Otherwise use green.

### `next_station`

Critical concept:

- `next_station` means where the robot is going, not where it is.

Assignments:

- Green threshold/explosion at STORE:
  - `next_station="CAPP"`
- Red threshold/explosion at CAPP:
  - `next_station="STORE"`
- Blue-line exit complete:
  - `next_station="STORE"`

Purpose:

- Prevents rack sensor cross-contamination.
- STORE and CAPP sensors broadcast continuously, but only the authoritative station should affect lane mode during a committed transit leg.

### Docking 1: STORE loading

Trigger:

- Large green threshold marker.

Flow:

1. Check if CAPP is full.
2. If CAPP full, enter `IDLE - CAPP FULL`.
3. Set `next_station="CAPP"`.
4. Decide lane mode for CAPP.
5. Enter `U-TURN`.
6. Once line is reacquired, enter `DOCKING 1`.
7. Phase 1:
   - Move forward slowly while applying PD alignment.
8. Phase 2:
   - Move backward into loading position.
9. Phase 3:
   - Hold/dwell.
10. Enter `WAITING - CONFIRM GO`.
11. Operator presses GO.
12. Phase 4:
   - Move forward to exit loading zone.
13. Resume `RUNNING`.

### Docking 2: CAPP deposit

Trigger:

- Large red threshold marker.

Flow:

1. Set `next_station="STORE"`.
2. Decide lane mode for STORE.
3. Enter `DOCKING 2`.
4. Phase 1:
   - Reverse away from/through threshold, then align.
5. Phase 2:
   - Move forward to deposit material.
6. Phase 3:
   - Hold/dwell.
7. Enter `WAITING - CONFIRM GO`.
8. Operator presses GO.
9. Phase 4:
   - Reverse/retract.
10. Enter `U-TURN`.
11. After U-turn, check STORE occupancy.
12. If STORE empty, enter `IDLE - STORE EMPTY`.
13. Otherwise resume `RUNNING`.

### Return Empty Box / blue line

Flow:

1. UI toggles `/agv/cmd_return_empty=True`.
2. AGV watches for blue tape while continuing its route.
3. When blue appears, it follows blue using the same PD style.
4. A large blue threshold pauses the AGV in `IDLE - RETURN BOX`.
5. Operator GO clears the pause.
6. AGV follows blue until the blue line is lost.
7. It then sets `next_station="STORE"`, recalculates lane, and returns to normal green/red behavior.

## 12. Safety Logic

### LiDAR safety tiers

Implemented in:

- `webcam_line_follow.scan_callback`

Behavior:

- Reads `/scan`.
- Treats forward direction as angle near `+/- pi` in this lidar frame.
- Ignores invalid ranges.
- Checks distance and angle against tiered cones.
- First matching tier triggers obstacle stop.

Important limitation:

- Obstacle detection is bypassed during docking and U-turns. This was likely done to avoid false stops from racks/thresholds during close maneuvers. Treat this carefully in any future safety review.

### Manual override

Manual teleop publishes `/cmd_vel_teleop`.

`twist_mux` gives this priority `255`, higher than AGV autonomy.

### E-stop style path

The legacy AMR path uses `/cmd_vel_estop`, priority `100`, for fault halt and localization spins. The active AGV STOP path uses `/agv/cmd_stop` and zeroes `/cmd_vel_agv`.

### Audio safety feedback

`agv_audio_node` listens to `/agv/state`:

- `OBSTACLE_DETECTED`
  - Repeating horn.
- `DOCKING 1` / `DOCKING 2`
  - Docking audio/chime.

## 13. UI Dashboards

Located in:

- `src/html/`

Important pages:

- `agv_display.html`
  - Primary AGV HMI.
  - Connects to rosbridge at `ws://<host>:9090`.
  - Publishes GO, STOP, mode, return-empty, shutdown.
  - Subscribes to `/agv/state` and `/agv/next_station`.
  - Uses `/ui_active_client` session locking.
- `Manual.html`
  - Manual teleop interface.
  - Publishes `/cmd_vel_teleop`.
  - Subscribes to `/agv/state`.
- `rack_monitoring_dashboard.html`
  - Rack status viewer.
  - Can connect direct WebSocket or rosbridge.
- `rack_control_dashboard.html`
  - Test/simulation dashboard.
  - Allows clicking rack slots to inject synthetic rack states.
- `camera_feed.html`
  - Camera stream debugging.
- `Auto.html`
  - Legacy AMR/Nav2 dashboard.
  - Includes localization/navigation/return-home concepts.
- `AGV page.html`
  - Older/minimal AGV page.

## 14. Related Changes Tried / Debugging History

This section summarizes the major changes recorded in `Developer-Brain/debugging_breakthroughs*`.

### AMR to AGV transition

Tried:

- SLAM, AMCL, Nav2, waypoint navigation, and `orchestrator_node`.

Issues:

- TF staleness.
- Localization drift.
- Costmap latency.
- Less predictable behavior around factory racks.

Result:

- Standard operation moved to camera-based deterministic line following in `webcam_line_follow.py`.

### Direct LiDAR safety instead of costmap avoidance

Tried:

- Nav2/local-costmap style obstacle handling.

Issue:

- Too slow and complex for immediate factory-floor stops.

Result:

- Replaced by direct `/scan` tiered safety cones in `webcam_line_follow.py`.

### Red-to-green no-line bug

Issue:

- When leaving a red diversion and returning to green, the red line could disappear from the camera view and cause a stop.

Change:

- Added red-lost debounce and fallback to green if green is visible.

Result:

- Intersections became smoother.

### Docking state-machine overhaul

Issue:

- Docking logic was ad hoc and could stall or skip phases.

Changes:

- Split docking into explicit phases.
- Added `docking_type`, `docking_phase`, `pending_docking_type`, U-turn state, and idle hold states.

Result:

- More predictable STORE/CAPP docking behavior.

### Simultaneous docking motion and alignment

Issue:

- Rotating in place did not reliably align the non-holonomic AGV due to friction/deadzones.

Change:

- Docking Phase 1 combines slow linear motion with PD angular correction.

Result:

- Alignment could use a strict `err < 3` gate.

### Docking 1 timer reset

Issue:

- D1 Phase 1 sometimes skipped forward movement after U-turn because `docking_timer` was started too early.

Change:

- Reset `docking_timer` when actually entering D1.

Result:

- D1 receives its intended forward/alignment window.

### Docking 2 green-mode cancellation

Issue:

- Rack updates could synthesize a green-mode switch that cancelled active D2.

Change:

- Guarded mode changes so active Docking 2 is protected.

Result:

- Only deliberate STOP should abort D2.

### Docking 2 red threshold freeze

Issue:

- Red threshold could obscure the green line, causing D2 Phase 1 to freeze.

Change:

- Initial D2 reverse motion runs straight even when the line is temporarily hidden; alignment resumes when the line reappears.

Result:

- D2 can clear the red threshold.

### Permanent red-tracking bug

Issue:

- A guard around D2 mode changes left `following_red=True` while `follow_mode` said green.

Change:

- Move the D2 protection guard before mutating `follow_mode`.

Result:

- Mode state and physical tracking state remain consistent.

### Lane prioritization logic

Issue:

- Early lane decisions checked only narrow rack cases and could choose red/green incorrectly.

Change:

- Column-level decisions:
  - CAPP A full and CAPP B not full -> red.
  - STORE B full and STORE A not full -> red.
  - Otherwise green.

Result:

- Better load balancing between rack columns.

### `next_station` rack isolation

Issue:

- STORE and CAPP sensors publish continuously, so the wrong station could flip the lane mode mid-transit.

Change:

- Added/persisted `next_station`.
- Only the station the AGV is heading toward should influence lane decisions.

Result:

- Prevents cross-station sensor updates from rerouting the robot.

Note:

- The Developer-Brain notes say some sessions inverted this logic. Correct semantics:
  - At STORE after green threshold: next station is CAPP.
  - At CAPP after red threshold: next station is STORE.

### Operator confirm GO skipping D2 retract

Issue:

- If STOP was pressed before operator GO confirmation, `enabled=False`, so D2 Phase 4 did not run.

Change:

- Confirm-GO branch re-enables the AGV and sets state back to `DOCKING 2`.

Result:

- GO confirm runs Phase 4 retract before U-turn.

### Audio stability on Raspberry Pi/systemd

Issue:

- `ffplay` crashed or looped under headless systemd.
- `SIGSTOP` did not release ALSA hardware for SFX.

Change:

- Switched to `ffmpeg` direct ALSA output on `plughw:2,0`.
- Kill/restart music processes with tracked playback position instead of pausing them.

Result:

- More reliable music and SFX on the Raspberry Pi.

### Legacy TF staleness recovery

Issue:

- AMR/Nav2 path saw repeated `Transform data too old` failures.

Change:

- `orchestrator_node` monitored `/rosout`, debounced TF errors, cancelled Nav2 goals, published halt commands, entered `TF_RECOVERY`, then resumed when TF recovered.

Result:

- Improved AMR path, but standard operations still moved to the AGV line-follow approach.

## 15. Current Risks / Things To Verify

- `bringup_launch.py` references `params/twist_mux.yaml`, but source has `nav2_params/twist_mux.yaml`.
- `bringup_launch.py` references an HTML path under `/home/amr/ros2_ws/src/amr_ws/html`; this workspace has `src/html`.
- `setup.py` references `amr_ws.agv_shutdown_node`, but source file is `agv_shudown_node.py`.
- Some comments in `Developer-Brain` say STOP clears `next_station=None`, but current `webcam_line_follow.py` deliberately preserves `next_station` on STOP.
- `twist_mux` gives `/cmd_vel_agv` and `/cmd_vel_nav` the same priority. This is acceptable only if AGV line following and Nav2 are not active at the same time.
- LiDAR obstacle safety is disabled during docking and U-turns. This may be intentional for close rack maneuvers, but it should be reviewed against site safety requirements.
- Absolute paths differ between `/home/intern1/ros2_ws` and `/home/amr/ros2_ws`; deployment machine paths should be confirmed.

## 16. Quick Operator Commands

Typical AGV bringup:

```bash
ros2 launch amr_ws bringup_launch.py
```

SLAM/mapping launch:

```bash
ros2 launch amr_ws slam_toolbox_launch.py
```

Run only the core AGV node:

```bash
ros2 run amr_ws webcam_line_follow
```

Run rack WebSocket bridge:

```bash
ros2 run amr_ws rack_websocket_server
```

Run audio node:

```bash
ros2 run amr_ws agv_audio_node
```

Open dashboard after bringup:

```text
http://<robot-ip>:8080/agv_display.html
```

ROS bridge expected by dashboard:

```text
ws://<robot-ip>:9090
```

Rack WebSocket default:

```text
ws://<robot-ip>:8000
```
