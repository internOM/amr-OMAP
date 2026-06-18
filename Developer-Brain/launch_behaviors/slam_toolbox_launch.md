# slam_toolbox_launch.py

## Overview
This launch file is dedicated exclusively to mapping and localization tasks. 

## Launched Components & Nodes
- **SLAM Node**: Launches `sync_slam_toolbox_node`.
- **Configuration**: Loads parameters from `amr_ws/params/slam_param.yaml`.

## Dependencies & Communication
- Historically consumed by [[orchestrator_node]] during the AMR phase of development to maintain the `/map` to `/odom` TF tree.
- Currently, this file is largely bypassed in standard operations due to the transition to deterministic line-following. 

## Breakthroughs
- Intimately tied to the localization issues documented in [[tf_staleness_recovery]], which eventually catalyzed the shift to the AGV paradigm (see [[amr_to_agv_transition]]).
