# Core Navigation and Docking

## Paradigm Overview
The system operates as a deterministic Automated Guided Vehicle (AGV) rather than a SLAM-based Autonomous Mobile Robot (AMR). This architectural pivot guarantees perfectly repeatable, drift-free navigation in dynamic factory environments. (See [[amr_to_agv_transition]]).

## Line Following Execution
- **Functional Node**: [[webcam_line_follow]].
- **Methodology**: The AGV tracks a green or red tape line on the floor using OpenCV HSV masking to calculate a centroid. It applies a Proportional-Derivative (PD) controller to generate angular velocity commands, prioritizing smooth, continuous forward motion.

## Precision Docking
The AGV must physically align itself with material racks without relying on LiDAR mapping.
- **Triggers**: Detecting a horizontal green threshold triggers `Docking 1` (STORE). Detecting a red threshold triggers `Docking 2` (CAPP).
- **Simultaneous Motion**: To overcome friction-induced deadzones (non-holonomic constraints), docking applies simultaneous linear motion (`0.05 m/s`) and angular PD correction. This breakthrough (see [[docking_and_uturn_logic]]) allows for extremely tight alignment tolerances (`err < 3`).
- **Wait States**: If a rack is not ready (e.g., CAPP is full), the AGV enters an `IDLE` state, waiting for [[rack_websocket_server]] to broadcast clearance, rather than faulting out.
- **Operator Confirm**: In D2 Phase 3, if the CAPP sensor detects the deposited box, the AGV holds and waits for the operator to press GO before continuing to Phase 4 (backward retract). The GO button doubles as the confirm trigger.

## Rack Sensor Isolation During Transit (added 2026-06-02)
Both STORE and CAPP racks broadcast ultrasonic sensor updates continuously. The expected behavior is:

- **AGV heading to CAPP** (just left STORE after D1): only CAPP sensor updates should affect lane mode. STORE updates must be silently ignored.
- **AGV heading to STORE** (just left CAPP after D2): only STORE sensor updates should affect lane mode. CAPP updates must be silently ignored.

This is enforced by the `next_station` flag in [[webcam_line_follow]]:

| AGV position / action | `next_station` | Authoritative sensors |
|---|---|---|
| Just fired green explosion (at STORE) | `"CAPP"` | CAPP only |
| During D1 / return to CAPP | `"CAPP"` | CAPP only |
| Just fired red explosion (at CAPP) | `"STORE"` | STORE only |
| During D2 / U-turn / return to STORE | `"STORE"` | STORE only |
| After STOP | `None` | Both (combined logic) |

The flag persists through the **entire transit leg** — not just during docking — and is only overwritten when the next threshold explosion fires. See [[next_station_rack_filter]].

## Multi-Tier Safety
- **Functional Node**: `rplidar_s3_launch.py` (via [[bringup_launch]]) feeds data to [[webcam_line_follow]].
- **Methodology**: The system uses a 3-tier safety cone:
  - **Zone 1 (Stop)**: 0.225 m, 90° arc. Immediate halt.
  - **Zone 2 (Caution)**: 0.3182 m, 45° arc.
  - **Zone 3 (Warn)**: 0.45 m, 30° arc.
- This deterministic, latency-free approach replaced the sluggish SLAM local costmap (see [[line_changing_and_safety]]).
