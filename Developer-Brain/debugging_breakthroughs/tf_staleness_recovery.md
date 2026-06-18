# TF Staleness Recovery

## The Problem
During the AMR phase of development, Nav2 operations would randomly fail and halt the robot due to `Transform data too old` exceptions emitted by `tf_help`. The system would abort the entire navigation sequence instead of recovering.

## The Solution
- **Active Monitoring**: Implemented a monitor on `/rosout` inside the [[orchestrator_node]] to track TF errors in real-time.
- **Fault Debounce**: Created a `TF_FAULT_THRESHOLD`. If errors persisted beyond the threshold, the node preempted the active Nav2 goal, published a zero-velocity halt (`/cmd_vel_estop`), and triggered a `TF_RECOVERY` state.
- **Seamless Resumption**: Once TF health was restored (verified via `can_transform`), the orchestrator seamlessly reinstantiated the interrupted goal.

## Cross-References
- **Affected Node**: [[orchestrator_node]]
- **Launch File**: Highly dependent on the TF tree maintained by [[slam_toolbox_launch]].
- **Legacy Note**: This issue was ultimately entirely sidestepped by the architectural pivot documented in [[amr_to_agv_transition]].
