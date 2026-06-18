# bringup_launch.py

## Overview
This is the primary launch file responsible for spinning up the complete hardware and software stack of the AGV.

## Launched Components & Nodes
- **Motor Control**: Includes `om_MVC01_bringup_launch.py` for physical motor bridging.
- **LiDAR**: Includes `rplidar_s3_launch.py` for spatial awareness.
- **USB Camera**: Launches `usb_cam_node_exe` configured for `/dev/video0` (YUYV format).
- **Audio System**: Starts `agv_audio_node`.
- **Core AGV Logic**: Launches the [[webcam_line_follow]] node.
- **Rack Integration**: Starts the [[rack_websocket_server]] node.
- **Command Arbitration**: Runs `twist_mux` using `twist_mux.yaml`.
- **UI Backend**: Starts `rosbridge_websocket` and a local Python HTTP server on port 8080.

## Dependencies & Communication
- The [[agv_display]] and [[rack_monitoring_dashboard]] UIs depend on the `rosbridge_websocket` and HTTP server started here.
- The [[webcam_line_follow]] node directly consumes the images published by the `usb_cam_node_exe` initiated in this file.
- The `twist_mux` configuration here resolves conflicts between autonomous commands and manual overrides from [[manual_teleop]].

## Breakthroughs
- This file was stabilized after the architectural shift away from the AMR paradigm; see [[amr_to_agv_transition]] for context on why `nav2` nodes were deprecated from the primary bringup.
