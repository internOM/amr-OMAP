# Next-Station Rack Filter — Safety Isolation

**Date**: 2026-06-02
**Files changed**: `webcam_line_follow.py`, `agv_display.html`

---

## The Problem

The AGV operates a loop between two stations: **STORE** (green line) and **CAPP** (red line). The `rack_status_callback` in [[webcam_line_follow]] subscribes to ultrasonic sensor data from both racks simultaneously. This created a dangerous race condition:

- While navigating from **STORE → CAPP**, a STORE sensor update would fire and call `mode_callback("green")`, flipping the AGV back to the green line mid-transit.
- While navigating from **CAPP → STORE**, a CAPP sensor update would fire and call `mode_callback("red")`, diverting the AGV onto the wrong lane.

Both stations broadcast sensor updates continuously. With no gating, both could affect the mode at any time — even when the AGV was already committed to a destination.

---

## The Fix — `next_station` Flag

A new instance variable `self.next_station: str | None` was introduced to track the AGV's **committed next destination** throughout an entire transit leg.

### Assignment (threshold explosions in `image_callback`)

```python
# Green explosion = AGV is at STORE. Next destination = CAPP.
self.next_station = "CAPP"   # set at green explosion

# Red explosion = AGV is at CAPP. Next destination = STORE.
self.next_station = "STORE"  # set at red explosion
```

> **Important**: `next_station` represents **where the AGV is going**, not where it is.

### Early-exit guard in `rack_status_callback`

```python
incoming_station = "CAPP" if rack_id.startswith("CAPP") else "STORE"

if self.next_station is not None and incoming_station != self.next_station:
    # Wrong station fired — skip mode update entirely.
    return
```

This causes IDLE release checks to still run (they are evaluated before the guard), but the `mode_callback` is never called for non-authoritative stations.

### Persistence (the key insight)

Early attempts cleared `next_station = None` when docking completed. This was wrong. The flag should persist through:

```
Green explosion → next_station="CAPP"
  → D1 docking at STORE         (flag: "CAPP", STORE ignored ✓)
  → D1 complete, navigate to CAPP (flag: "CAPP", STORE ignored ✓)
Red explosion → next_station="STORE"   ← overwrites "CAPP"
  → D2 docking at CAPP          (flag: "STORE", CAPP ignored ✓)
  → D2 complete, U-turn         (flag: "STORE", CAPP ignored ✓)
  → navigate back to STORE      (flag: "STORE", CAPP ignored ✓)
Green explosion → next_station="CAPP"  ← overwrites "STORE"
```

`next_station` is only ever:
1. **Overwritten** by a new threshold explosion (green or red).
2. **Cleared to `None`** by `stop_callback` (full reset on STOP).

### Debugging — Two rounds of inverted logic

The `next_station` assignments were inverted **twice** during development, causing confusion:

| Round | Green explosion set | Red explosion set | Effect |
|---|---|---|---|
| Session 1 (correct) | `"CAPP"` | `"STORE"` | Filter worked for STORE→CAPP leg |
| Session 2 (bug introduced) | `"STORE"` | `"CAPP"` | Filter worked in reverse — CAPP→STORE leg OK but STORE→CAPP broke |
| Session 3 (restored) | `"CAPP"` | `"STORE"` | Both legs correct |

The user confirmed the correct semantics: **"at STORE, next station should be CAPP; at CAPP, next station should be STORE."**

---

## Operator Confirm GO Bug (fixed same session)

While `waiting_operator_confirm = True` (box detected on CAPP sensor, AGV paused in D2 Phase 3), pressing the GO button should advance to **Phase 4 (backward retract at −0.075 m/s for 7.5s)** before triggering the U-turn.

**Bug**: If the operator had pressed STOP before pressing GO to confirm, `self.enabled` was `False`. The `enable_callback` correctly set `docking_phase = 4` and reset `docking_timer`, but `image_callback` gated out immediately on the `not self.enabled` check — so Phase 4's backward motion never executed. The AGV sat still, then jumped directly to the U-turn.

**Fix**: The operator confirm branch in `enable_callback` now also:
1. Sets `self.enabled = True` if it was `False`.
2. Sets `self.current_state = "DOCKING 2"` (clears the `WAITING — CONFIRM` state from UI).
3. Calls `_publish_state()` immediately.

```python
if msg.data and self.waiting_operator_confirm:
    self.waiting_operator_confirm = False
    self.docking_phase = 4
    self.docking_timer = time.time()
    if not self.enabled:
        self.enabled = True          # ← KEY FIX
    self.current_state = "DOCKING 2"
    self._publish_state(self.current_state)
    return
```

---

## Cross-References

- **Node changed**: [[webcam_line_follow]]
- **UI updated**: [[agv_display]] (added Next Station badge)
- **Related behavior**: [[core_navigation_and_docking]]
- **Previous docking fixes**: [[docking_and_uturn_logic]]
