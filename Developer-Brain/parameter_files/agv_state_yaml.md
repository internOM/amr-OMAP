# agv_state.yaml

## Overview
A persistent YAML state file that records the AGV's committed next destination (the `next_station` flag).

## Location
`~/ros2_ws/src/amr_ws/params/agv_state.yaml`

## Mechanism
1. **Written By**: [[webcam_line_follow]] overwrites this file the moment it evaluates an intersection threshold (the "green explosion" or "red explosion"). 
2. **Read By**: [[webcam_line_follow]] reads this file during node startup to initialize its `self.next_station` variable.

## Purpose
This prevents the AGV from forgetting where it was going if it gets powered off mid-transit. Without this, an AGV restarted in the middle of the track would default to `STORE` and potentially follow the wrong colored line, resulting in catastrophic routing failure.

It works closely with the [[next_station_rack_filter]] logic to ensure the AGV only listens to rack sensors relevant to its current destination.
