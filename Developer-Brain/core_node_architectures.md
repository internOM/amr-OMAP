# Core Node Architectures

This document serves as the high-level system directory mapping out the core ROS 2 nodes driving the AGV, outlining how the system's software architecture ties together to achieve the operational goals defined in [[expected_agv_behavior]].

## Primary Nodes
- **[[webcam_line_follow]]**: The central brain of the AGV. It handles computer vision, line following, intersection routing, multi-tier LiDAR safety stops, and precision docking state machines.
- **[[orchestrator_node]]**: The legacy state machine for the AMR's autonomous SLAM navigation. While largely superseded by the AGV line-following logic, it managed Nav2 actions, localization, and TF staleness recovery.
- **[[rack_websocket_server]]**: The bridge between physical ESP32 ultrasonic sensors on the material racks and the ROS 2 ecosystem. It provides the critical occupancy data that allows the AGV to make intelligent lane and docking decisions.
- **[[agv_audio_node]]**: Manages all background music, directional, and docking audio feedback, interfacing directly with the ALSA soundcard.
- **[[agv_shutdown_node]]**: A lightweight service endpoint that allows the UI to safely halt the Pi's OS.

## Architecture Overview
The system successfully shifted from a complex SLAM-based map architecture (relying on `[[orchestrator_node]]`) to a highly deterministic, vision-based Automated Guided Vehicle (AGV) architecture driven primarily by `[[webcam_line_follow]]`. This pivot guaranteed perfect repeatability on the factory floor and allowed for tight integration with the physical environment via `[[rack_websocket_server]]`.

## Persistent State Files
To provide stability against sudden power loss or WiFi disconnection, the system relies on physical file persistence:
- **[[agv_state_yaml]]**: Persists the AGV's destination so it doesn't forget its routing mid-transit.
- **[[rack_state_yaml]]**: Persists a snapshot of rack occupancies so the AGV has sensible sensor data even if booting offline.
