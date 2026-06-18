# The Paradigm Shift: AMR to AGV Transition

## The Problem
Early in development, the system was configured as an Autonomous Mobile Robot (AMR) relying heavily on SLAM (Simultaneous Localization and Mapping), Nav2, and AMCL via the [[orchestrator_node]]. While flexible, this approach introduced massive complexity in path planning, severe susceptibility to TF (Transform) staleness, and unpredictability in dynamic environments. 

## The Breakthrough
- **Architectural Pivot**: We fundamentally shifted the architecture from a generalized mapping system to a deterministic Automated Guided Vehicle (AGV) model. 
- **Vision-Based Navigation**: Map-based routing was completely replaced with computer vision (OpenCV). The [[webcam_line_follow]] node was introduced to track colored tape on the floor using HSV masking.
- **Deterministic Reliability**: Navigation became perfectly repeatable, eliminating localization drift and allowing for precision docking based on colored threshold "explosions".

## Cross-References
- **Deprecated Node**: The [[orchestrator_node]] was largely sidelined.
- **New Core**: The [[webcam_line_follow]] node took over all movement execution.
- **Launch Impact**: [[bringup_launch]] was rewritten to drop Nav2 in favor of the camera and line-following nodes.
- **Previous Hurdles**: This pivot solved the unresolvable issues documented in [[tf_staleness_recovery]].
