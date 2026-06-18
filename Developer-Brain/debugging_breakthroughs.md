# Major Debugging Breakthroughs

Over the last 6 months of development, several critical bottlenecks and logic flaws were identified and resolved, resulting in a highly robust AGV system.

## The Paradigm Shift: Transitioning from AMR to AGV
**The Problem**: Early in development, the system was configured as an Autonomous Mobile Robot (AMR) relying heavily on SLAM (Simultaneous Localization and Mapping), Nav2, and AMCL (via the `orchestrator_node.py`). While flexible, this approach introduced significant complexity in path planning, susceptibility to TF (Transform) staleness, and unpredictability in dynamic factory environments.
**The Breakthrough**:
- **Architectural Pivot**: We fundamentally shifted the architecture from a generalized AMR mapping system to a deterministic Automated Guided Vehicle (AGV) model. 
- **Vision-Based Line Following**: We replaced map-based routing with computer vision (OpenCV) using the onboard camera. The `webcam_line_follow.py` node was introduced to track colored tape (green/red) on the floor using HSV masking and Proportional-Derivative (PD) control.
- **Deterministic Reliability**: By transitioning to physical line-following, the robot's navigation became perfectly repeatable, eliminating localization drift and allowing for precision docking at racks using colored threshold "explosions".
- **Enhanced Safety**: SLAM-based obstacle avoidance was replaced with a multi-tiered, latency-free LiDAR safety cone system directly tied to the line-following logic.

## 1. Refining the AGV Docking State Machines
**The Problem**: The AGV frequently stalled during Docking 2 at the red threshold and relied on loose conditional gates, leading to unpredictable sequencing. The AGV would erroneously enter a permanent "STOPPED" state when a rack was empty instead of continuing its sequence.
**The Breakthrough**:
- Transitioned from ad-hoc `if/else` logic to explicit, granular state machine structures for each docking phase.
- Re-sequenced the D2 protocol to ensure the deposit sequence completed fully, followed by a U-turn.
- Created explicit `IDLE` holding states (`IDLE - CAPP FULL` and `IDLE - STORE EMPTY`). Instead of failing or hard-stopping, the AGV safely holds its position and resumes seamlessly once rack vacancies/occupancies change via ultrasonic sensor callbacks.

## 2. Simultaneous Motion & Alignment in Docking
**The Problem**: Non-holonomic constraints of the AGV caused it to struggle with alignment. The old logic required the AGV to steer in place, but physical friction made this inconsistent, requiring an overly loose alignment error deadzone (`err <= 5`).
**The Breakthrough**: 
- Combined linear movement with PD rotational alignment in Docking Phase 1. By moving forward at `0.05 m/s` while applying PD corrections without a minimum angular deadzone, the AGV smoothly steers into place.
- This allowed the enforcement of strict alignment gates (`err < 3`) before advancing to Phase 2 (backward loading), drastically improving physical docking reliability.

## 3. Red-to-Green Line Transition Logic
**The Problem**: The "stop-on-no-line" bug. When transitioning from a red diverted line back to the main green loop, the AGV would lose the red line from its camera view and trigger an emergency stop.
**The Breakthrough**:
- Implemented a debounce mechanism (`RED_LOST_DEBOUNCE`).
- If the red line is lost, the state machine now elegantly reverts to the green tracking mask (which it was already physically parallel to) rather than throwing an error, allowing uninterrupted motion at intersections.

## 4. Intelligent Lane Prioritization
**The Problem**: The AGV previously defaulted to red line behavior, leading to incorrect rack targeting and inefficiencies.
**The Breakthrough**:
- Defaulted the routing logic to prioritize the Green line.
- Integrated the `rack_status_callback` (consuming data from the ESP32 array) to evaluate `CAPP-A1` and `CAPP-B1` states. The AGV only diverts to Red when `CAPP-A1` is full and `CAPP-B1` has space, dynamically balancing material loads.

## 5. TF Staleness Recovery
**The Problem**: Nav2 operations would randomly fail and halt the robot due to `Transform data too old` exceptions emitted by `tf_help`.
**The Breakthrough**:
- Implemented an active monitor on `/rosout` in `orchestrator_node.py` to track TF errors.
- Created a `TF_FAULT_THRESHOLD` (debounce). If errors persist, the node preempts the active Nav2 goal, publishes a zero-velocity halt, and triggers a `TF_RECOVERY` state.
- Once TF health is restored (verified via `can_transform`), the orchestrator seamlessly reinstantiates the interrupted goal.

## 6. Docking 1 Phase 1 Skipping Forward Movement
**The Problem**: After a U-turn completed and Docking 1 was entered, Phase 1 would immediately evaluate the 2.5 s forward-movement window as already elapsed, skipping straight to the alignment gate. The AGV would see `err < 3` (it was already roughly centred from the U-turn) and jump directly to Phase 2 (backward movement) without ever moving forward to align.
**Root Cause**: `self.docking_timer` was set when the *green explosion* triggered the U-turn (in the explosion branch), not when D1 was actually entered. By the time the U-turn completed (~2–5 s later), `elapsed = current_time - self.docking_timer` was already well above the 2.5 s window, so the forward phase was silently skipped on the very first frame.
**The Fix**: Added `self.docking_timer = current_time` immediately when setting `docking_type = 1 / docking_phase = 1` inside the U-turn completion block (line ~701 in `webcam_line_follow.py`). This resets the Phase 1 timer to the moment D1 actually begins, giving the AGV its full 2.5 s forward-alignment window.

## 7. Docking 2 Aborted by Automatic Rack Sensor Mode Change
**The Problem**: The red threshold explosion correctly set `docking_type = 2`, but the AGV immediately stopped and never progressed through the D2 phases. Logs showed `AGV STOPPED` and audio `PAUSED` shortly after the `DOCKING 2` log entry.
**Root Cause**: `rack_status_callback` fires whenever any ultrasonic sensor updates — including the CAPP sensor that just triggered D2. It always recomputes `desired_mode` (which evaluates to `"green"` when `capp_a1_full and not capp_b1_full` is false) and calls `mode_callback("green")` via a synthetic String. Inside `mode_callback`, the green branch previously cancelled any active D2 by resetting `docking_type = 0` and `docking_phase = 0`, effectively aborting the sequence on the same frame it started. It also reset `following_red = False` *before* the cancellation check, corrupting the PD tracking mask for D2 Phase 1.
**The Fix**: Added an early-return guard at the *very top* of the `mode == "green"` branch in `mode_callback`: if `self.docking_type == 2`, the function publishes the current mode unchanged and returns immediately — no state is touched. This ensures that only a deliberate operator stop (via `stop_callback`) can abort an active D2 sequence.

## 8. Docking 2 Silent Freeze During Threshold Transit
**The Problem**: When the AGV encountered the red threshold tape in D2 Phase 1, it silently froze and did not proceed backward.
**Root Cause**: The red threshold tape obscured the green tracking line entirely (setting `green_sum=0`). The PD alignment logic required a visible tracking line to compute the center `cx`; without it, the AGV zeroed its twist commands and essentially aborted the sequence without advancing phases.
**The Fix**: Refactored D2 Phase 1 logic inside `[[core_node_architectures#webcam_line_follow.py]]`. During the initial 2.5-second backward movement across the threshold, the AGV now maintains a straight reverse trajectory (`angular_z = 0`) if the line is momentarily lost. It only resumes PD alignment and advances to Phase 2 once the green line is successfully re-acquired.

## 9. Permanent "Red Tracking" State Bug (Mode Switching)
**The Problem**: After completing Docking 2 (a red line docking sequence), the AGV got permanently stuck following the red line instead of switching back to green tracking when the UI/rack system sent the "green" mode command.
**Root Cause**: In `mode_callback`, a guard was added to protect the D2 sequence from being cancelled by synthetic "green" mode commands sent by `rack_status_callback`. However, this guard was placed *after* the internal state variable `self.follow_mode` was updated to `"green"`. Because the early return triggered, the actual cleanup code (`self.following_red = False`) was skipped. The AGV remained physically on red tracking but mentally recorded itself in green mode. When D2 finished and "green" was requested again, the callback deemed it an idempotent request and ignored it forever.
**The Fix**: Moved the D2 protection guard above the `self.follow_mode = mode` assignment in `mode_callback()`. This ensures that if the switch to green is ignored, the internal state accurately reflects that the AGV is still in red mode, allowing the state transition to complete successfully after docking is finished.

## 10. Correcting Lane Prioritization Logic
**The Problem**: The AGV was ignoring the red lane even when the primary CAPP lane was full, leading to incorrect rack targeting and inefficiencies.
**Root Cause**: The lane routing condition only checked if `CAPP-A1` was full, instead of checking the whole columns for CAPP and STORE simultaneously.
**The Fix**: Updated `rack_status_callback` to use proper conditional column checking. It now correctly switches to the red line if and only if `(CAPP-A is full AND CAPP-B is empty) OR (STORE-B is full AND STORE-A is empty)`. Otherwise, it correctly defaults to the green line.

## 11. Rack Sensor Cross-Contamination During Transit (2026-06-02)
**The Problem**: `rack_status_callback` fires on every ultrasonic update — from both STORE and CAPP simultaneously. While navigating CAPP → STORE, a CAPP sensor update would call `mode_callback("red")`, diverting the AGV back toward CAPP mid-transit. The same problem occurred in reverse (STORE → CAPP leg: STORE sensor flipping mode to green).
**Root Cause**: `rack_status_callback` always called `mode_callback` regardless of which station's sensor fired and where the AGV was heading. No destination context existed.
**The Fix**: Introduced `self.next_station: str | None` — set to `"CAPP"` at the green explosion (AGV leaves STORE) and to `"STORE"` at the red explosion (AGV leaves CAPP). Added an early-return guard in `rack_status_callback` that skips the `mode_callback` call entirely if the incoming sensor update belongs to the non-authoritative station. Critically, the flag is **never cleared on docking completion** — it persists through the full transit leg (docking + U-turn + return journey) and is only overwritten by the next threshold explosion or cleared by STOP. See [[next_station_rack_filter]] for the full deep-dive.

## 12. Operator Confirm GO Skipping Backward Retract (2026-06-02)
**The Problem**: After D2 Phase 3 detected a box on the CAPP sensor (`WAITING — CONFIRM`), pressing GO caused the AGV to freeze in place and then jump directly to the U-turn, completely skipping Phase 4's backward retract (−0.075 m/s for 7.5 s).
**Root Cause**: If the operator pressed STOP before pressing GO to confirm, `self.enabled` was `False`. `enable_callback` correctly advanced `docking_phase = 4` and reset `docking_timer`, but `image_callback` exited immediately on the `not self.enabled` gate — so Phase 4 never executed. An unrelated code path eventually triggered the U-turn.
**The Fix**: The operator confirm branch in `enable_callback` now also sets `self.enabled = True` (if it was False) and updates `current_state` to `"DOCKING 2"` before returning, guaranteeing `image_callback` runs Phase 4 on the very next frame. See [[docking_and_uturn_logic]].

## 13. Headless Audio Playback Crashes on Raspberry Pi (2026-06-12)
**The Problem**: After deploying `agv_audio_node.py` to the separate Raspberry Pi, the AGV speaker produced no sound and rapidly skipped tracks (advancing exactly every 1.0 seconds).
**Root Cause**: The node was originally designed for a desktop environment and used `ffplay` launched via `subprocess.Popen` with `stderr=subprocess.DEVNULL` (which swallowed the error). `ffplay` attempts to initialize SDL video/audio and connects to the default ALSA or PulseAudio device. On a headless systemd service without proper environment variables, it failed to find a valid default audio sink and instantly crashed. Because `self._proc.poll() is not None` returned true immediately, the node's 1.0-second timer aggressively cycled to the next track. Furthermore, the ALSA hardware speaker on the Pi was located at a specific non-default hardware port (`plughw:2,0`).
**The Fix**: 
1. Updated `AUDIO_DIR`, `SFX_HORN`, and `SFX_DOCKING` absolute paths to reflect the `amr` user's workspace structure on the Raspberry Pi.
2. Migrated the underlying subprocess command to use `ffmpeg` writing directly to the ALSA hardware port (`-f alsa ALSA_DEVICE`). This completely bypasses SDL and PulseAudio dependencies, making it robust for headless systemd service environments.
3. Explicitly routed the audio output to the correct hardware port (verified via `speaker-test -D plughw:2,0`) to ensure systemd could properly access the speaker.
