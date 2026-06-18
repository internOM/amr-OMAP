# agv_shutdown_node

## Overview
A lightweight ROS2 service node responsible for intercepting remote shutdown commands from the UI and executing an OS-level halt on the Raspberry Pi.

## Services
- `/agv/shutdown` (`std_srvs/Trigger`) — Exposes an RPC endpoint to initiate system shutdown.

## Architecture
- When triggered, it replies immediately with a success acknowledgment (`response.success = True`) to the rosbridge websocket so the UI can process the confirmation.
- Uses a `create_timer` to introduce a 1.0-second delay before invoking `subprocess.run(['sudo', 'shutdown', '-h', 'now'])`. This ensures the UI receives the service response before the OS actually goes down.

## Cross-References
- **UI Dashboard Panel**: Connected to the physical shutdown button in [[agv_shutdown_controls]].
- **Central Map**: Part of the [[core_node_architectures]].
