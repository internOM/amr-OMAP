# AGV Control Dashboard (`agv_display.html`)

## Overview

The `agv_display.html` file serves as the primary User Interface (UI) and operator dashboard for the Autonomous Guided Vehicle (AGV). It provides a responsive, web-based control panel that connects directly to the ROS 2 network using `rosbridge_websocket` (`roslibjs`). It allows operators to monitor the AGV's state, issue high-level commands, and view activity logs without needing to access a terminal or run native ROS tools.

## Key Features & UI Components

### 1. Real-Time Status Monitoring
- **Ping/Heartbeat**: The UI constantly publishes and subscribes to a `/ui_heartbeat` topic to measure network latency between the browser and the ROS network, displaying the ping in ms.
- **State Display**: A large central card dynamically updates to show the AGV's current operating state (e.g., `RUNNING`, `STOPPED`, `DOCKING 1`, `WAITING — NO RACK`, `OBSTACLE_DETECTED`). The styling (colors, pulsing borders) changes based on the urgency of the state.

### 2. Operator Controls
- **GO / STOP Buttons**: 
  - **GO** publishes a `True` boolean to `/agv/cmd_enable` to start line following. It also serves as an operator confirmation when the AGV is halted at a sensor gate (e.g., `WAITING — CONFIRM`).
  - **STOP** publishes a `True` boolean to `/agv/cmd_stop`, immediately halting the AGV and transitioning it to a `STOPPED` state.
- **Lane/Mode Selection**: A toggle button allows the operator to manually override or select the tracking mode ("GREEN" or "RED"). This publishes the selected mode string to `/agv/cmd_mode`.

### 3. Activity Logging
- The dashboard features a scrolling activity log panel. It listens to the `/agv/state` and `/agv/mode` topics and logs time-stamped events whenever a state transition occurs. The logs are color-coded (green for running/success, red for stopped/errors, amber for waiting).

### 4. (Future/Optional) Manual Teleoperation
- The UI includes CSS and structural groundwork for on-screen virtual joysticks (publishing to topics like `/cmd_vel_teleop`). However, the primary focus of the AGV in this project is autonomous line-following.

## Network Architecture

The dashboard relies on the `rosbridge_server` package acting as a middleware bridge.
1. The operator opens `agv_display.html` in a standard web browser (served via a simple Python HTTP server or loaded locally).
2. The browser executes `roslib.min.js` to open a WebSocket connection to the robot's IP (typically on port 9090).
3. Once connected, the Javascript handles all ROS message serialization and deserialization, allowing standard HTML buttons to directly influence the Python nodes running on the Raspberry Pi and Base Station.

## Serving the Interface

To use the interface, ensure the `rosbridge_websocket` node is running:
```bash
ros2 run rosbridge_server rosbridge_websocket --ros-args -p delay_between_messages:=0.0
```
Then, serve the HTML directory:
```bash
cd ~/ros2_ws/src/html && python3 -m http.server 8080
```
Operators can then navigate to `http://<Robot_IP>:8080/agv_display.html` on their tablet, phone, or PC.
