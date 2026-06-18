# Line Changing and Safety Sensor Integration

## The Problem
Two critical issues plagued the AGV's physical movement:
1. **The "Stop-on-No-Line" Bug**: When transitioning from a diverted red line back to the main green loop, the AGV's camera would temporarily lose sight of the red line, throwing an exception and triggering an emergency stop at intersections.
2. **Obstacle Avoidance Latency**: The SLAM-based local costmap approach was too slow and complex for dynamic factory floors, leading to near-misses.

## The Solution
- **Debounce Recovery**: Implemented a `RED_LOST_DEBOUNCE` counter in [[webcam_line_follow]]. If the red line vanishes, the node gracefully falls back to the green tracking mask (which it is already physically parallel to) rather than faulting.
- **Multi-Tiered LiDAR Zones**: Scrapped the costmap in favor of a direct multi-tiered safety cone system tied to the LiDAR data (launched via [[bringup_launch]]). Zone 1 (0.225m, 90°), Zone 2 (0.3182m, 45°), and Zone 3 (0.45m, 30°) provide instantaneous, latency-free stopping.
- **Intelligent Lane Prioritization**: Integrated the [[rack_websocket_server]] data feed. The AGV defaults to the green line and only diverts to the red lane if `CAPP-A` column is full and `CAPP-B` is empty, or `STORE-B` is full and `STORE-A` is empty.

---

## Rack Sensor Isolation (added 2026-06-02)

A further refinement to lane prioritization. Even with correct routing logic, both STORE and CAPP racks broadcast sensor updates continuously. Without isolation, a CAPP sensor firing while the AGV was en route to STORE could flip `follow_mode` to `"red"`, sending the AGV onto the wrong lane.

**Solution**: The `next_station` flag (see [[next_station_rack_filter]]) causes `rack_status_callback` to perform an early return for any update from the non-authoritative station:

```python
incoming_station = "CAPP" if rack_id.startswith("CAPP") else "STORE"
if self.next_station is not None and incoming_station != self.next_station:
    return  # skip mode update — wrong station fired
```

The flag persists through the entire transit leg (docking + return), not just during docking itself.

---

## Cross-References
- **Fixed Node**: [[webcam_line_follow]]
- **Safety detail**: [[next_station_rack_filter]]
- **Expected Behavior**: [[core_navigation_and_docking]]
