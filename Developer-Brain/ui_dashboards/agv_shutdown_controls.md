# agv_shutdown_controls

**Parent Node**: [[ui_dashboards]]

## Overview
A dedicated control interface within the primary dashboard (`agv_display.html`) that allows operators to safely and remotely power down the AGV's internal Raspberry Pi without physically pulling power.

## Implementation Details
- **Trigger**: Activated via a prominent shutdown button in the UI.
- **Service Call**: When clicked, a JavaScript routine invokes a service call to `/agv/shutdown` using the `std_srvs/Trigger` message type over `rosbridge_websocket` (Port 9090).
- **Graceful Halt**: By using the ROS service instead of a hard power cut, it ensures that all running ROS nodes, logging systems, and persistent state saving (like `rack_state.yaml` and `agv_state.yaml`) have a chance to flush data to the disk safely.

## Cross-References
- **Backend Node**: Triggers the system halt logic in [[agv_shutdown_node]].
- **Primary Dashboard**: Resides inside [[agv_display]].
