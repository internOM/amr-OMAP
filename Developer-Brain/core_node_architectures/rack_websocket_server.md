# rack_websocket_server

## Overview
Acts as a bridge between the ESP32 ultrasonic sensors (monitoring 12 rack slots) and the ROS 2 ecosystem. It evaluates distance data to determine whether rack slots are `FULL` or `EMPTY`.

## Publishers
- `/rack_status` (`std_msgs/String`) - Broadcasts the occupancy of each slot in the format `rack_id:status:distance_cm`.

## Subscribers
- *None.* (It receives data asynchronously via a WebSocket connection from the physical ESP32 hardware, rather than subscribing to a ROS topic).

## Persistent State
To provide offline resilience to the AGV (e.g. if the robot reboots while out of WiFi range), this server continuously persists a snapshot of the latest rack occupancies to [[rack_state_yaml]] on every sensor update or disconnect.

*Note: The server normalises all `rack_id` strings to uppercase (e.g. `STORE-B1`) when publishing to the ROS topic and writing to the YAML file to prevent downstream casing mismatches.*

## Cross-References
- **Launch Context**: [[launch_behaviors]] (Spun up alongside the web UI components).
- **Breakthroughs**: [[debugging_breakthroughs]] (Crucial enabler for the "Intelligent Lane Prioritization" logic).
- **Consumed By**: [[webcam_line_follow]] (Uses the `/rack_status` data to decide when to switch to the red line or enter `IDLE` states).
- **UI Dashboard**: Visualized beautifully in the `rack_monitoring_dashboard.html`, detailed in [[ui_dashboards]].
