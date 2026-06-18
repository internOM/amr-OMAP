# Webcam Line Follow: State Machine Architecture

The `webcam_line_follow.py` node operates on a highly deterministic state machine. This architecture ensures the AGV behaves predictably, handles physical interruptions safely, and manages non-holonomic constraints during complex docking maneuvers.

---

## High-Level States

The `current_state` variable tracks the primary state of the AGV. It is broadcasted on the `/agv/state` topic at 1 Hz (and immediately on transitions) so the UI Dashboard always reflects the physical reality of the robot.

| State String | Description |
|---|---|
| **`WAITING`** | The default boot state. The node is running, but motors are disabled until the operator presses GO. |
| **`RUNNING`** | Normal operation. The AGV is actively following the green/red line and watching for intersection triggers. |
| **`STOPPED`** | The operator pressed STOP. All active docking, U-turn, and obstacle timers are flushed, but `next_station` is preserved. |
| **`OBSTACLE_DETECTED`** | The LiDAR safety tiers have tripped. The AGV halts immediately but remains logically active (waiting for a clear path). |
| **`U-TURN`** | The AGV is rotating ~180° to re-acquire the line. This can happen after arriving at STORE or after depositing at CAPP. |
| **`DOCKING 1`** | The sequence for loading materials at the STORE rack. |
| **`DOCKING 2`** | The sequence for depositing materials at the CAPP rack. |
| **`WAITING — CONFIRM GO`** | The AGV has completed the payload transfer phase of a docking sequence and is waiting for a human operator to press GO before retracting/exiting. |
| **`IDLE — CAPP FULL`** | The AGV arrived at the STORE, but the target CAPP rack is entirely full. It holds position before the U-turn to avoid picking up a payload it cannot deliver. |
| **`IDLE — STORE EMPTY`** | The AGV completed a CAPP deposit and U-turn, but the STORE is empty. It holds position to conserve battery and track space until material is available. |
| **`IDLE — RETURN BOX`** | The AGV is in Return Empty Box mode, reached a blue threshold marker, and decelerated to a stop using the slew rate limiter. It holds position until the operator presses GO. |

---

## Detailed State Flows

### 1. The Normal Loop (RUNNING)
Once enabled (`cmd_enable=True`), the AGV enters `RUNNING`. The camera continuously processes images to calculate PD control for the motors.
- If the LiDAR detects an object within its tiered safety cones, the AGV halts (`OBSTACLE_DETECTED`).
- Once the path clears for 20 consecutive frames, a 3-second safety timer starts. When it expires, the AGV resumes `RUNNING`.

### 2. Arrival at STORE (Green Explosion)
When the AGV detects a massive green block (the threshold marker at the STORE rack):
1. **Capacity Check**: It immediately queries the latest `rack_states`. If all CAPP slots are occupied, it enters `IDLE — CAPP FULL` and waits.
2. **Lane Decision**: It evaluates the STORE occupancy to determine the `follow_mode` (`green` or `red`) for the next leg. It sets `next_station = "CAPP"`.
3. **U-Turn**: It enters the `U-TURN` state.
4. **Docking 1**: Once the line is re-acquired post-U-turn, it transitions to `DOCKING 1`.

### 3. Docking 1 Sequence (Loading at STORE)
- **Phase 1 (Align & Advance)**: Moves forward at `0.025 m/s` for 5s while applying PD alignment. Waits until alignment error is `< 3` pixels.
- **Phase 2 (Load Entry)**: Moves backward at `-0.075 m/s` for 7.5s to slot into the rack.
- **Phase 3 (Dwell & Wait)**: Holds in place for 5s to allow material loading. Then, transitions to `WAITING — CONFIRM GO` and disables motors.
- **Operator GO**: The operator presses GO on the UI.
- **Phase 4 (Exit)**: Moves forward at `0.075 m/s` for 5s to clear the rack, then resumes `RUNNING`.

### 4. Arrival at CAPP (Red Explosion)
When the AGV is tracking the red line and detects the red threshold block at the CAPP rack:
- It immediately enters `DOCKING 2`.
- (Lane decisions and U-turns happen *after* deposit for D2).

### 5. Docking 2 Sequence (Depositing at CAPP)
- **Phase 1 (Align & Entry)**: Moves backward at `-0.05 m/s` for up to 6s to clear the threshold, applying PD alignment. Waits until alignment error is `< 3` pixels.
- **Phase 2 (Deposit)**: Moves forward at `0.05 m/s` for 8s to push the material into the CAPP rack.
- **Phase 3 (Dwell & Wait)**: Holds in place for 5s to ensure the payload settles. Then, transitions to `WAITING — CONFIRM GO` and disables motors.
- **Operator GO**: The operator presses GO on the UI.
- **Phase 4 (Retract)**: Moves backward at `-0.075 m/s` for 7.5s to exit the rack.
- **U-Turn**: Completes D2 and immediately enters `U-TURN`.

### 6. Post-Deposit Check (STORE Vacancy)
After the post-D2 U-Turn completes, the AGV checks the `rack_states` for the STORE.
- If the STORE is empty (all 6 slots `0`), it transitions to `IDLE — STORE EMPTY`.
- It will remain paused here until `rack_websocket_server.py` pushes an update showing a slot has become `FULL`, at which point it automatically transitions back to `RUNNING`.

### 7. Return Empty Box Sequence (Blue Line Tracking)
When the operator toggles the "Empty" button on the UI:
1. **Passive Arming**: The AGV sets `next_station = "RETURN BOX"` and `return_empty_box = True`. The overall state remains `RUNNING`. If no blue tape is visible, the AGV continues following its current green/red route.
2. **Active Tracking**: Once the AGV spots a blue line (`blue_strip_px >= BLUE_LINE_MIN_PX`), it intercepts the loop and follows the blue line using PD control.
3. **Threshold Halt**: When it reaches a large blue threshold marker (`blue_strip_px >= BLUE_THRESHOLD_PX`), it decelerates to `0 m/s` using a linear slew rate and transitions to `IDLE — RETURN BOX`.
4. **Operator GO**: The operator presses GO to clear the pause, triggering `blue_line_exit` mode. The state returns to `RUNNING`.
5. **Exit & Resume**: The AGV actively follows the blue line until the line ends. When the blue line is completely lost, it sets `next_station = "STORE"`, decides the correct lane based on rack status, transitions to `green` tracking mode, and resumes normal operations.

---

## State Interruptions & Resiliency

1. **Physical Stops (LiDAR)**:
   Obstacles do *not* break the state machine. `image_callback` checks `self.obstacle_detected` at the very top of the loop. If true, it forces `Twist=0` and returns immediately, "freezing" the active docking or U-turn timer. When the obstacle clears, the state resumes exactly where it left off.

2. **Operator Stops (STOP Button)**:
   Pressing STOP forcibly wipes all `docking_phase`, `docking_timer`, and `u_turning` flags. This is intentional: if an operator hits STOP, the AGV is likely out of alignment and requires manual repositioning before pressing GO again.

3. **Node Reboots (YAML Persistence)**:
   If the AGV completely powers off, `agv_state.yaml` restores `next_station`, and `rack_state.yaml` restores `rack_states`. This prevents the AGV from booting into an incorrect `IDLE` state or driving toward the wrong lane.
