# Expected AGV Behavior & Functional Guidelines

This document outlines the intended functional behaviors of the Automated Guided Vehicle (AGV) on the factory floor. These behaviors serve as the "North Star" for the project and map directly to the technical software implementations detailed in [[core_node_architectures]].

## 1. Autonomous Navigation & Line Following
The AGV must traverse the factory floor continuously without drifting or losing localization.
- **Goal**: Follow colored floor tape (defaulting to green) with perfect repeatability. Dynamically switch to the red line at intersections if target racks are full.
- **Execution**: Managed entirely by [[webcam_line_follow]] using OpenCV HSV masking and a Proportional-Derivative (PD) controller. It uses real-time rack data provided by [[rack_websocket_server]] to make intelligent lane-switching decisions. *(Note: This deterministic approach replaced the legacy SLAM navigation previously handled by [[orchestrator_node]])*.

## 2. Dynamic Safety Stops
The AGV must avoid collisions with unexpected obstacles (humans, forklifts) instantly, without relying on sluggish costmap updates.
- **Goal**: Implement immediate, tiered halting based on physical proximity.
- **Execution**: Handled by [[webcam_line_follow]], which ingests 2D LiDAR scans to enforce a multi-tiered safety cone (Zone 1: 0.225m/90°, Zone 2: 0.3182m/45°, Zone 3: 0.45m/30°). Obstacle clearance is debounced before the AGV gracefully resumes motion. In addition to physical halting, the system triggers audio feedback (horns) via [[agv_audio_node]] to alert nearby personnel.

## 3. Precision Docking Protocols
The AGV must perfectly align itself to physical racks for automated material transfer.
- **Goal**: Execute multi-phase docking sequences (U-Turns, slow approach, alignment correction, and dwell times) when reaching specific unloading (CAPP - Red Threshold) or loading (STORE - Green Threshold) zones.
- **Execution**: Controlled by the granular state machines inside [[webcam_line_follow]]. These states merge linear motion with rotational PD alignment to overcome friction deadzones. The node also enforces `IDLE` holding states, waiting for clearance signals from [[rack_websocket_server]] if a rack is not ready. A dedicated docking chime plays during these procedures via [[agv_audio_node]] to indicate safe autonomous alignment.

## 4. UI & Operator Intervention
- **Goal**: Operators must have a live overview of the AGV's state and the ability to instantly E-Stop or manually teleoperate the robot.
- **Execution**: The AGV logic broadcasts its state for the Web UI, and listens for override commands that preempt autonomous routines, ensuring humans can safely take over at any moment.
- **Remote Shutdown**: Operators can safely power down the AGV via [[agv_shutdown_controls]] without physically pulling power.
