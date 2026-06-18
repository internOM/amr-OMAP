# UI Dashboards & Web Interfaces

This document explains the HTML-based user interfaces located in the `ros2_ws/src/html/` directory. These pages serve as the primary HMI (Human-Machine Interface) for monitoring, controlling, and debugging the AGV. They connect to the ROS 2 ecosystem primarily via `rosbridge_websocket` (port 9090).

## 1. Primary Control Hub: [[agv_display]]
This is the flagship control page for the AGV, designed for use on tablets and phones on the factory floor. (See also: [[agv_shutdown_controls]] for its power management component).

### Key Features:
* **Single Client Enforcement**: It implements a session lock on the `/ui_active_client` topic. If a new operator opens the dashboard, the old session is forcibly terminated to prevent conflicting commands from multiple devices.
* **State Visualization**: Subscribes to `/agv/state` and visually indicates if the AGV is `RUNNING` (with a pulsing green glow), `STOPPED`, `DOCKING`, or `WAITING`.
* **Motion Control**:
  * **GO Button**: Publishes to `/agv/cmd_enable`.
  * **STOP Button (E-Stop)**: Publishes to `/agv/cmd_stop` to halt the AGV instantly.
* **Security Keypad**: Critical actions like entering manual mode or initiating a hard recovery require a 4-digit PIN (currently hardcoded as `8888`) to prevent unauthorized operation.
* **Activity Log**: Maintains a live, color-coded rolling log of system messages and statuses.

---

## 2. Teleoperation: [[manual_teleop]]
This page provides physical override capabilities when the AGV's autonomous logic is stopped or faulted.
* **Virtual Joysticks**: Provides two virtual, touch-responsive thumbsticks. 
  * Left Joystick: Forward / Reverse.
  * Right Joystick: Turn Left / Turn Right.
* **Twist Mux Priority**: The joysticks publish `Twist` messages to the `/cmd_vel_teleop` topic. In the `twist_mux` configuration, this topic has a high priority (255), allowing the operator to completely override Nav2 or Line Following (priority 10) as long as the joystick is being moved.
* **Joystick Lock**: If the AGV is `RUNNING` autonomously, a glassmorphic lock overlay covers the joysticks to prevent accidental interference.

---

## 3. Sensor Visualization: [[rack_monitoring_dashboard]]
This is a specialized dashboard used to monitor the state of the material handling racks.
* **Visual Grid**: Renders a graphical representation of the 3-layer storage racks (STORE and CAPP stations), divided into Columns A and B.
* **Live Statuses**: Displays real-time states for all 12 rack slots (e.g., `EMPTY`, `FULL`, `INACTIVE`) and shows the live distance in centimeters reported by the ESP32 ultrasonic arrays.
* **Bridge Toggle**: Can connect directly to the ESP32 websocket server (Port 8001) or bridge through ROS (Port 9090) depending on network configurations.

---

---

## 4. Interactive Simulation: `rack_control_dashboard.html`
A new interactive mock dashboard derived from the monitoring dashboard, created to allow manual overrides of rack states for simulation and testing.
* **Interactive UI**: Users can click on any individual rack slot (e.g., `CAPP-A1` or `STORE-B2`) to toggle its state between `OCCUPIED` and `VACANT`.
* **State Injection**: On click, it seamlessly transmits a synthetic JSON payload via Direct WebSocket (Port 8000) or ROSBridge (Port 9090) to the `rack_websocket_server.py`.
* **Docking Simulation**: This enables developers to easily simulate physical material deposits and pickups to trigger the AGV's line-switching logic and docking state machines inside `webcam_line_follow.py` without requiring physical ESP32 sensors or boxes.

---

## 5. Hardware Debugging: [[camera_feed]]
A lightweight debugging tool used exclusively to inspect what the AGV is "seeing".
* **Topic Subscription**: Subscribes directly to `/image_raw` or `/image_compressed`.
* **Raw Decoding**: Contains custom JavaScript logic to decode raw ROS image encodings (`yuyv`, `bgr8`, `mono8`) onto an HTML5 Canvas.
* **Performance Metrics**: Calculates and displays live FPS and stream latency. This is crucial for verifying that the image processing pipeline is not lagging before attempting high-speed line following.

---

## 6. Legacy/Alternative Pages
* **`Auto.html`**: Originally used heavily during the AMR (SLAM/Nav2) phase of development. Contains Nav2 specific buttons (`Auto Localize`, `Start Navigation`, `Return Home`) and a mini debug console drawer.
* **`AGV page.html`**: An early minimal test page featuring battery mocks and a simple Auto toggle. 
