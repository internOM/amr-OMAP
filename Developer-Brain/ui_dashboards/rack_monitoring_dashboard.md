# rack_monitoring_dashboard

**Parent Node**: [[ui_dashboards]]

## Overview
A specialized dashboard used to visualize the real-time state of the physical material handling racks (STORE and CAPP stations) before the robot interacts with them.

## HTML/JS Components & Displayed Data
- **DOM Elements**: Renders a dynamic CSS Grid layout mimicking the physical 3-layer racks (Rows 1-3, Columns A-B).
- **Displayed Data**: Shows live ultrasonic distance metrics (in centimeters) and color-coded occupancy statuses (`EMPTY`, `FULL`, `INACTIVE`) for all 12 rack slots, updating instantly as material is added or removed.

## Communication Layer
- **Protocol**: Connects via standard WebSockets directly to the physical ESP32 bridge (Port 8001), or bridged through `rosbridge_websocket`.
- **Data Flow**: Parses the incoming JSON string containing the status array of the ultrasonic sensors.
- **Backend Node**: This UI is the visual representation of the exact same data generated and broadcast by the [[rack_websocket_server]] node in `core_node_architectures`. The data visualized here is what drives the intelligent lane prioritization in the AGV logic.

## Integration
- Essential for operators to verify that the physical loading constraints match the system logic mapped in [[ui_integration_flow]].
