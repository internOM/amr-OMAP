# UI Integration and Control Flow

## Overview
The AGV's higher-level operation relies heavily on human supervision via tablets, but the autonomous state machines are designed to execute without constant polling. The UI merely injects priority commands into the running loop.

## Teleoperation Priority Flow
- **Standard Autonomy**: [[webcam_line_follow]] calculates `cmd_vel_agv` at priority level 10 inside the `twist_mux` node (configured in [[bringup_launch]]).
- **Manual Override**: The [[manual_teleop]] dashboard publishes `cmd_vel_teleop` at priority 255. When a human touches the joystick, the AGV instantly abandons autonomous routing for direct manual control. Once the joystick is released (after a 0.5s timeout), the autonomous priority 10 channel regains control seamlessly.

## State Handshakes
- The core AGV logic broadcasts its intent (`RUNNING`, `STOPPED`, `DOCKING`) via `/agv/state` to [[agv_display]]. 
- When the AGV is in a `RUNNING` state, the [[manual_teleop]] joysticks are visually locked behind a glassmorphic shield. The operator must press the physical STOP button (which publishes `/agv/cmd_stop`) to force the AGV into a `STOPPED` state, which unlocks the manual joysticks.
- This creates a safe, deterministic control loop between human intent and the underlying Python nodes.

## Data Visualization
- The system heavily relies on physical sensors (Ultrasonics, LiDAR) which are inherently difficult to debug raw. 
- [[rack_monitoring_dashboard]] translates raw ESP32 JSON dumps into a clean, 12-slot visual grid, directly mirroring the array that [[webcam_line_follow]] uses for Lane Prioritization (see [[line_changing_and_safety]]).
- [[camera_feed]] pulls the `usb_cam` output from [[bringup_launch]] to allow operators to verify that the floor lines fall squarely within the HSV masking thresholds.
