# rack_state.yaml

## Overview
A persistent YAML state file that stores the last-known occupancy status of all 12 material racks on the factory floor. It acts as an offline resilience mechanism for the AGV.

## Location
`~/ros2_ws/src/amr_ws/params/rack_state.yaml`

## Mechanism
1. **Written By**: [[rack_websocket_server]] overwrites this file on every single sensor update (or disconnect event) received from the ESP32 hardware.
2. **Read By**: [[webcam_line_follow]] reads this file only once during node startup to pre-populate its internal memory (`self.rack_states`).

## Purpose
If the AGV is rebooted or restarted while physically out of WiFi range (or if the WebSocket server goes down), it will not receive live `/rack_status` updates. By loading `rack_state.yaml` on startup, the AGV has a sensible, last-known snapshot of the racks, preventing it from making incorrect routing decisions based on an "all empty" default state.

## Format
Values use standard uppercase keys (e.g., `STORE-A1`, `CAPP-B3`).
Status values:
- `1` = FULL (occupied)
- `0` = EMPTY (vacant)
- `-1` = DISCONNECTED (sensor offline)
