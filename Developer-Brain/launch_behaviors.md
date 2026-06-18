# Launch Behaviors

This document details the primary launch configurations used in the AMR workspace over the last 6 months.

## 1. Bringup Launch (`bringup_launch.py`)
This is the main launch file used to spin up the entire AGV hardware and software stack. It initializes the following components:
- **Motor Control**: Includes `om_MVC01_bringup_launch.py` to bridge ROS commands to the AGV's physical motors.
- **LiDAR**: Includes `rplidar_s3_launch.py` for spatial awareness and safety zone enforcement.
- **USB Camera**: Starts `usb_cam_node_exe` configured for `/dev/video0` at 320x240 resolution, 15 FPS, and YUYV pixel format for optimized computer vision processing.
- **Audio & Vision Nodes**: Launches custom logic nodes including `agv_audio_node`, `webcam_line_follow`, and `rack_websocket_server`.
- **Twist Mux**: Launches `twist_mux` to handle command velocity priorities (e.g., prioritizing `cmd_vel_estop` over `cmd_vel_nav` or line-following inputs).
- **Web UI**: Initiates `rosbridge_websocket` for ROS-web integration and spins up a local Python `http.server` on port 8080 to serve the HTML dashboards (e.g., `agv_display.html`, rack status UI).

## 2. SLAM Launch (`slam_toolbox_launch.py`)
Dedicated to mapping and localization.
- **SLAM Toolbox**: Launches `sync_slam_toolbox_node`.
- **Configuration**: Dynamically loads SLAM parameters from `params/slam_param.yaml` located within the `amr_ws` share directory.
