# AGV Algorithm and Communication Design

## Architecture Overview

The AGV relies on a distributed architecture using ROS 2's Publish-Subscribe (Pub/Sub) communication model. Various hardware components (camera, LiDAR, ultrasonic rack sensors, and the UI) run their own dedicated drivers or bridging nodes, publishing data to specific topics. The core logic of the AGV is centralized in the `webcam_line_follow` node, which acts as the "brain". It subscribes to all necessary sensory topics, processes the data, and publishes velocity commands to the motors.

## Node Communication Flow

Below is the communication breakdown of how different parts of the system interact with the central `webcam_line_follow` node:

### 1. Hardware Inputs & Sensors

*   **Camera Data (`/image_raw`)**:
    *   **Source:** A standard ROS 2 camera driver node (e.g., `v4l2_camera` or `usb_cam`) capturing the physical track line.
    *   **Consumer:** `webcam_line_follow.py`
    *   **Purpose:** Provides the raw BGR images at approximately 10 Hz. The AGV uses these frames for line detection, color masking (green vs. red), intersection detection, and alignment calculation.

*   **LiDAR Safety Data (`/scan`)**:
    *   **Source:** A LiDAR ROS 2 driver node (e.g., `rplidar_ros`) connected to an RPLidar A1/A2/S3 sensor.
    *   **Consumer:** `webcam_line_follow.py`
    *   **Purpose:** Provides 360-degree laser scan data. The AGV evaluates a forward-facing 180-degree cone to implement a tiered safety zone (narrowing cone as distance decreases). If an obstacle is detected, it overrides motor commands to halt the AGV.

*   **Rack Occupancy Data (`/rack_status`)**:
    *   **Source:** `rack_websocket_server.py` (which bridges to ESP32 microcontrollers).
    *   **Consumer:** `webcam_line_follow.py`
    *   **Purpose:** The ESP32 microcontrollers mounted on the physical racks read ultrasonic distance sensors to determine if a slot is full or empty. They send this via WebSockets to the `rack_websocket_server`, which translates it into a ROS 2 `String` message format (`rack_id:status:distance_cm`) and publishes it. The AGV uses this to dynamically switch lanes and block docking actions if a target slot is occupied.

### 2. User Interface (UI) Communication

The AGV is controlled and monitored via a web-based dashboard (`agv_display.html`) which interfaces with ROS 2 via `rosbridge_websocket` (running on the backend). This UI runs in the browser and connects directly to the robot's topics.

*   **Inputs from UI to AGV**:
    *   `/agv/cmd_enable` (Bool): Enables the line following logic. Can also act as an operator confirmation when the AGV is waiting at a sensor gate.
    *   `/agv/cmd_stop` (Bool): Immediately halts the AGV and disables tracking.
    *   `/agv/cmd_mode` (String): Requests a mode switch ("green" or "red" following).

*   **Outputs from AGV to UI**:
    *   `/agv/state` (String): The current operational state of the AGV (e.g., "RUNNING", "WAITING", "DOCKING 1", "OBSTACLE_DETECTED").
    *   `/agv/mode` (String): Confirms the currently active following mode.
    *   `/ui_heartbeat` (String): A ping-pong mechanism to ensure the UI connection is active.

### 3. Motor Control Output & Priority Multiplexing

*   **Velocity Commands (`/cmd_vel_agv`)**:
    *   **Source:** `webcam_line_follow.py`
    *   **Consumer:** `twist_mux` (Twist Multiplexer Node).
    *   **Purpose:** The AGV calculates the required linear and angular velocities (using a PD controller for alignment) and publishes them as `geometry_msgs/Twist` messages to `/cmd_vel_agv`.
    
*   **Twist Multiplexer (`twist_mux`)**:
    *   **Source:** Aggregates various velocity topics (e.g., `/cmd_vel_agv`, `/cmd_vel_teleop`, `/cmd_vel_estop`).
    *   **Consumer:** The physical motor controller driver (typically running on the Raspberry Pi or an Arduino bridge).
    *   **Purpose:** The `twist_mux` node listens to multiple velocity command streams and outputs a single definitive `/cmd_vel` based on predefined priorities located in `twist_mux.yaml`. For example, manual teleoperation (`/cmd_vel_teleop`, Priority 255) will always override the autonomous AGV commands (`/cmd_vel_agv`, Priority 10) if an operator intervenes with a joystick.

*   **Motor Driver**:
    *   **Purpose:** Subscribes to the final multiplexed `/cmd_vel` output by `twist_mux`. It translates the linear (m/s) and angular (rad/s) velocities into specific left/right wheel speeds (RPM or PWM) using a differential drive kinematics model, sending the commands over serial to the physical motor drivers.

## High-Level Algorithm Logic

1.  **Safety First**: The LiDAR callback (`scan_callback`) evaluates incoming scans. If an obstacle enters the tiered safety zones, an `obstacle_detected` flag is set.
2.  **Sensory Aggregation**: The `rack_status_callback` continuously updates an internal dictionary of 12 rack slots (Store and CA-PP). Based on the truth table of these slots, the AGV determines its target lane (green or red).
3.  **Control Loop (Image Callback)**: The `image_callback` drives the main state machine:
    *   **Gate Checks**: It first checks if the AGV is enabled and if the path is clear of obstacles.
    *   **Vision Processing**: It converts the image slice to HSV and applies masks to find green and red pixels.
    *   **Intersection Logic**: If in "red" mode, it checks for red tape in the tracking strip to trigger a seamless divert.
    *   **Explosion Detection**: Large blobs of color trigger specific maneuvers ("Green Explosion" -> U-Turn -> Docking 1; "Red Explosion" -> Docking 2).
    *   **PD Control**: If not docking or U-turning, it calculates the centroid error of the line and applies a Proportional-Derivative (PD) formula to calculate the angular velocity (`angular.z`), ensuring smooth line tracking.
    *   **Actuation**: It publishes the computed Twist message to `/cmd_vel_agv`.
