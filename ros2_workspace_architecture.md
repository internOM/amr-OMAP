# ROS 2 Workspace Architecture: `amr_ws`

## Overview
The ROS 2 workspace (`ros2_ws`) is the primary development environment for the Autonomous Mobile Robot (AMR) and Automated Guided Vehicle (AGV) projects. The workspace is structured using the standard `colcon` build system and contains the main ROS 2 package, `amr_ws`, inside the `src` directory.

The `amr_ws` package is a Python-based ROS 2 package. Although it contains nodes for multiple projects (like AMR navigation and localization), this document focuses specifically on the architecture components relevant to the AGV (Automated Guided Vehicle) line-following project.

## Directory Structure

The core package is located at `~/ros2_ws/src/amr_ws/`. Its structure is as follows:

```text
amr_ws/
├── amr_ws/                 # Python module directory containing node scripts
│   ├── webcam_line_follow.py      # Core AGV node for line tracking and logic
│   ├── rack_websocket_server.py   # WebSocket bridge for ESP32 rack sensors
│   ├── joystick_to_motor.py       # (Legacy/Testing only: not used in final AGV layout)
│   └── ...                        # Other AMR-related nodes
├── html/                   # Web interface files
│   └── agv_display.html           # Main UI dashboard for the AGV
├── launch/                 # ROS 2 launch files
│   ├── bringup_launch.py          # Launch file used on the Raspberry Pi
│   └── slam_toolbox_launch.py
├── params/                 # Configuration parameters
├── nav2_params/            # Navigation 2 parameters
├── maps/                   # Map files for AMR
├── waypoints/              # Waypoint configurations
├── urdf/                   # Robot description files
├── setup.py                # Python package setup and entry points definition
└── package.xml             # ROS 2 package manifest dependencies
```

## AGV Specific Nodes

The AGV operation relies primarily on the following Python scripts located in the `amr_ws/amr_ws/` directory:

1. **`webcam_line_follow.py`**: The central brain of the AGV. It processes camera feeds to track the line, integrates LiDAR for safety, and manages the docking state machines based on rack sensor data.
2. **`rack_websocket_server.py`**: Acts as a bridge between the physical world and ROS 2. It runs a WebSocket server that listens for connections from ESP32 microcontrollers attached to the racks, parses JSON data regarding rack slot occupancy, and publishes it to the ROS 2 `/rack_status` topic.
3. **`agv_display.html`**: While not a ROS 2 node itself, this HTML file (hosted via a simple HTTP server or directly opened) acts as the operator dashboard. It connects to the ROS network via `rosbridge_websocket` to send commands (enable, stop, mode switch) and display real-time status.

*(Note: The `joystick_to_motor.py` script exists in the repository but was strictly used for past testing and is completely bypassed in the active AGV layout.)*

## Build and Execution Process

### Building the Workspace
The workspace is built using `colcon`. To compile the `amr_ws` package, you navigate to the root of the workspace and run the build command.

```bash
cd ~/ros2_ws
colcon build --packages-select amr_ws
```

Since it's a Python package, you can also use the `--symlink-install` flag during development so you don't have to rebuild after every minor script change:

```bash
colcon build --packages-select amr_ws --symlink-install
```

### Sourcing the Environment
After building, the workspace overlay must be sourced in every new terminal before running nodes:

```bash
source ~/ros2_ws/install/setup.bash
```

### Running the Nodes
The AGV system spans across standard PCs and a Raspberry Pi. 

**On the Raspberry Pi:**
The Pi handles hardware interfacing. You can launch the core hardware nodes using the provided launch file:
```bash
# Execute on the Pi (e.g., via SSH: ssh amr@192.168.251.49)
ros2 launch amr_ws bringup_launch.py
```

**On the Base Station/Operator PC:**
```bash
# Run the line following node
ros2 run amr_ws webcam_line_follow

# Run the rack websocket server in a separate terminal
ros2 run amr_ws rack_websocket_server

# Run rosbridge for the web UI
ros2 run rosbridge_server rosbridge_websocket --ros-args -p delay_between_messages:=0.0

# Serve the UI (or just open agv_display.html in a browser)
cd ~/ros2_ws/src/html && python3 -m http.server 8080
```
