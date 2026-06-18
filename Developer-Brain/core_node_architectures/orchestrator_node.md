# orchestrator_node

## Overview
The Orchestrator Node acts as the central state machine for the AMR's autonomous navigation operations, connecting Nav2 actions, localization, and handling TF staleness. It was the primary driver before the paradigm shift to vision-based line following.

## Publishers
- `/cmd_vel_estop` (`geometry_msgs/Twist`) - Priority halt commands.
- `/cmd_vel_nav` (`geometry_msgs/Twist`) - Standard navigation velocity commands.
- `/amr/state` (`std_msgs/String`) - Current state machine status.
- `/robot_status` (`std_msgs/String`) - High-level robot health/status.
- `/amr/fault_trigger` (`std_msgs/String`) - Triggers for system faults (e.g., TF staleness).

## Subscribers
- `/amr/cmd_localize` (`std_msgs/Bool`)
- `/amr/cmd_recover_localize` (`std_msgs/Bool`)
- `/amr/cmd_navigate` (`std_msgs/Bool`)
- `/amr/cmd_return_home` (`std_msgs/Bool`)
- `/amr/cmd_estop` (`std_msgs/Bool`)
- `/amr/cmd_recover` (`std_msgs/Bool`)
- `/odom` (`nav_msgs/Odometry`)
- `/cmd_vel` (`geometry_msgs/Twist`)
- `/rosout` (`rcl_interfaces/msg/Log`) - Monitored for `Transform data too old` errors.

## Cross-References
- **Launch Context**: [[launch_behaviors]] (Spun up during the SLAM/Nav2 AMR phase).
- **Breakthroughs**: [[debugging_breakthroughs]] (See "TF Staleness Recovery" and "The Paradigm Shift: Transitioning from AMR to AGV").
- **Related Nodes**: Parallels and was largely superseded in navigation by [[webcam_line_follow]].
