# manual_teleop

**Parent Node**: [[ui_dashboards]]

## Overview
Provides physical override capabilities when the AGV's autonomous logic is stopped, faulted, or paused by an operator.

## HTML/JS Components & Displayed Data
- **DOM Elements**: Features two touch-responsive virtual thumbsticks (HTML/CSS circles) with pointer event tracking built in JavaScript. 
- **Displayed Data**: Primarily displays a visual lock overlay. When the AGV is running autonomously, a glassmorphic shield covers the joysticks to prevent accidental touches from interfering with the robot.
- **Interaction**: Captures complex touch/pointer vector math to calculate linear (forward/reverse) and angular (turn L/R) velocities.

## Communication Layer
- **Protocol**: Connects via `rosbridge_websocket` (`roslibjs`).
- **Topics**: Publishes `geometry_msgs/Twist` messages directly to the `/cmd_vel_teleop` topic at a high rate (10Hz) when the joystick is moved.
- **Backend Node**: Interfaces primarily with the `twist_mux` node (priority 255) to forcefully override the base autonomy provided by [[webcam_line_follow]] (priority 10). It listens to `/agv/state` from [[webcam_line_follow]] to determine when to trigger the visual UI lock.

## Integration
- This represents a critical safety and fallback mechanism, forming the manual branch of the architecture outlined in [[ui_integration_flow]].
