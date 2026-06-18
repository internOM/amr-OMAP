# Docking and U-Turn Logic Overhaul

## The Problem
During development, the AGV frequently stalled during the "Docking 2" phase at the red threshold. The logic relied on loose, sequential `if/else` conditional gates, leading to unpredictable sequencing. Critically, the AGV would erroneously enter a permanent "STOPPED" state when a rack was empty, requiring manual intervention.

## The Solution
- **State Machine Refactoring**: We completely overhauled the core logic inside the [[webcam_line_follow]] node, transitioning to granular, explicit state machines for both Docking 1 and Docking 2.
- **Simultaneous Motion & Alignment**: To overcome non-holonomic constraints, we combined linear movement with Proportional-Derivative (PD) rotational alignment. Moving forward at `0.05 m/s` while applying corrections eliminated friction-based deadzones and allowed strict alignment gates (`err < 3`).
- **Idle Holding States**: We created explicit `IDLE — CAPP FULL` and `IDLE — STORE EMPTY` states. Instead of halting and failing, the AGV now waits patiently and resumes automatically once [[rack_websocket_server]] broadcasts a vacancy or restocking event.

---

## Operator Confirm GO Bug (fixed 2026-06-02)

**Symptom**: After the box was detected on the CAPP sensor in D2 Phase 3 (`WAITING — CONFIRM` state), pressing the GO button caused the AGV to sit still, then jump straight to the U-turn, skipping Phase 4's backward retract (−0.075 m/s, 7.5 s).

**Root Cause**: If the operator had pressed STOP at any point before pressing GO to confirm, `self.enabled` was `False`. The `enable_callback` correctly advanced `docking_phase = 4` and reset `docking_timer`, but `image_callback` gated out at the very first check (`not self.enabled`) so Phase 4 never ran. Eventually some other path triggered the U-turn.

**Fix**: The operator confirm branch now also:
1. Re-enables the AGV if it was disabled (`self.enabled = True`).
2. Sets `self.current_state = "DOCKING 2"` so the UI reflects the correct state.
3. Calls `_publish_state()` immediately.

Correct sequence after fix: **GO confirm → Phase 4 backward 7.5s → U-turn → STORE check**.

---

## Cross-References
- **Faulty Node**: [[webcam_line_follow]]
- **System Expectations**: [[core_navigation_and_docking]]
- **Rack sensor isolation**: [[next_station_rack_filter]]
