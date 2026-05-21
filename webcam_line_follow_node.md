# Webcam Line Follow Node: Deep Dive

## Overview
The `webcam_line_follow.py` node is the core controller of the AGV. It is a highly integrated ROS 2 Python node that combines computer vision, safety LIDAR processing, rack sensor logic, and precise motor control into a cohesive state machine. 

## Core Subsystems

### 1. Vision Processing
Instead of processing full 1080p or 720p frames, the node slices the incoming BGR image to extract only a narrow "tracking strip" near the bottom of the frame (roughly rows corresponding to the 3/4 mark down the image, 20 pixels high). 
- It converts this strip to HSV color space.
- It applies distinct masks to isolate green and red pixels.
- It calculates the image moments (specifically the `m10` and `m00` moments) to find the centroid (the X-coordinate) of the detected line.

### 2. PD Controller
Normal forward motion is governed by a Proportional-Derivative (PD) controller:
- **Error Calculation:** The difference between the line's centroid and the exact center of the image width (`w // 2`).
- **Proportional (P):** Reacts to the current error.
- **Derivative (D):** Reacts to the rate of change of the error, damping the oscillation to ensure smooth line tracking.
- The output of the PD controller directly dictates the angular velocity (`angular.z`), while linear velocity (`linear.x`) remains constant.

### 3. LiDAR Tiered Safety System
The `scan_callback` overrides motion if an obstacle is near:
- It defines multiple "zones" (e.g., very close narrow cone vs. medium wide cone).
- If an obstacle breaches a zone, the AGV halts and enters the `OBSTACLE_DETECTED` state.
- It employs a "debounce" mechanism: it requires 20 consecutive clear frames before it registers the path as clear, followed by a 3-second wait before smoothly ramping up the linear speed (slew-rate limiter) to prevent jolting.

### 4. Dynamic Rack Integration
The node subscribes to `/rack_status`. As the ESP32 sensors report slot occupancies:
- It maintains a real-time truth table of the 12 slots (Store and CA-PP stations).
- Based on the AGV's current direction leg (`to_store` or `to_capp`), it automatically decides whether to track the primary green line or divert to the secondary red line to avoid full drop-off locations or target loaded pick-up locations.

---

## Follow Modes & Lane Switching

The AGV operates in two primary visual modes:
- **Green Mode:** The AGV tracks the green line. If it sees red tape alongside it, it ignores the red tape.
- **Red Mode:** The AGV tracks the green line by default. However, when an intersection approaches and a sufficient amount of red tape enters the tracking strip, it executes a "dynamic divert" and seamlessly shifts its tracking target to the red centroid. If the red line ends, it seamlessly falls back to green.

---

## Maneuvers and State Machines

When the AGV approaches specific markers, the camera detects a massive spike in pixel count (an "explosion"). This halts the standard PD controller and hands control over to dedicated maneuver state machines. The current state is continuously published to `/agv/state` and displayed on the operator dashboard (`agv_display.html`).

### State Transition Diagram

Here is the flow of how the AGV transitions between states:

*   **STOPPED**: The initial state, or when the operator presses STOP.
    *   `-> RUNNING` (Operator presses GO and path is clear).
*   **RUNNING**: Default state utilizing the PD controller to follow the line.
    *   `-> STOPPED` (Operator presses STOP).
    *   `-> OBSTACLE_DETECTED` (LiDAR detects an obstacle in a safety zone).
    *   `-> U-TURN` (Green explosion detected).
    *   `-> DOCKING 2` (Red explosion detected).
*   **OBSTACLE_DETECTED**: AGV halted due to LiDAR.
    *   `-> RUNNING` (Path clears for 20 frames + 3-second wait period).
*   **U-TURN**: Rotating on the spot to face the opposite direction.
    *   `-> DOCKING 1` (If U-Turn was triggered by a green explosion, it inherently leads into Docking 1).
    *   `-> RUNNING` (If U-Turn was triggered post-Docking 2 to simply resume tracking).
*   **DOCKING 1**: Drop-off sequence at CA-PP.
    *   `-> WAITING — NO RACK` (If CA-PP slots are full during Phase 1 alignment).
    *   `-> RUNNING` (Upon successful completion of all Docking 1 phases).
*   **DOCKING 2**: Pick-up sequence at the Store.
    *   `-> WAITING — CONFIRM` (If Store slot is full during Phase 4 loading).
    *   `-> U-TURN` (Upon successful completion of all Docking 2 phases, to exit the station).
*   **WAITING (NO RACK / CONFIRM)**: Blocked state waiting for physical clearance or operator override.
    *   `-> DOCKING 1 / DOCKING 2` (When slot clears or operator confirms via UI).

### 1. U-Turn Maneuver
**Trigger:** Triggered by a "Green Explosion" (large block of green tape) or immediately after completing Docking 2.
**Behavior:**
- The AGV sets `linear.x` to 0.0 and applies a constant negative `angular.z` (rotating right).
- It ignores the camera feed for a minimum time limit (e.g., 2 seconds) to avoid immediately locking onto the line it just left.
- Once the time limit passes, it searches for a solid, centered line to lock onto, completing the turn.

### 2. Docking 1 (Drop-off at CA-PP)
**Trigger:** Entered immediately after completing a U-Turn caused by a green explosion.
**Phases:**
- **Phase 1 (Spot Alignment):** Uses the PD controller to rotate purely on the spot (`linear.x = 0`) until the error is minimal. 
    - *Sensor Gate:* If the CA-PP slots are completely full, the AGV blocks here and enters a `WAITING — NO RACK` state until a slot opens.
- **Phase 2 (Reverse):** Drives backward at a slow speed for 5 seconds to back into the station.
- **Phase 3 (Wait):** Halts for 5 seconds to simulate unloading.
- **Resolution:** Completes docking, applies a 5-second cooldown to prevent immediate re-triggering of explosions, updates its internal leg to `to_capp` (meaning next stop is Store), and transitions back to `RUNNING`.

### 3. Docking 2 (Pick-up at Store)
**Trigger:** Triggered by a "Red Explosion" (large block of red tape).
**Phases:**
- **Phase 1 (Reverse):** Moves backward slightly for 2 seconds to position itself perfectly over the intersection.
- **Phase 2 (Spot Alignment):** Rotates on the spot using the PD controller until perfectly aligned with the target line.
- **Phase 3 (Forward):** Drives forward into the docking station for 5 seconds.
- **Phase 4 (Wait/Load):** Halts for 5 seconds.
    - *Sensor Gate:* If the target Store slot is occupied (preventing safe operation), the AGV halts in a `WAITING — CONFIRM` state. The UI (`agv_display.html`) must publish a `/agv/cmd_enable` command to act as an operator override to proceed.
- **Resolution:** Completes the docking, then immediately flags a pending U-Turn to exit the station and transitions to `U-TURN`.

## Expected Overall Behavior
1. The user enables the AGV via the UI (`agv_display.html`).
2. The AGV enters `RUNNING` state, following the green path.
3. Approaching a fork, the rack status logic determines whether to switch the AGV into `red` mode based on slot availability.
4. If in `red` mode, it takes the branch and eventually hits a red explosion, transitioning to `DOCKING 2` (Pick-up), followed by a `U-TURN`.
5. If in `green` mode, it continues until a green explosion, executes a `U-TURN`, then transitions to `DOCKING 1` (Drop-off).
6. Obstacles safely pause the operation at any time (`OBSTACLE_DETECTED`) without resetting the internal state machines, resuming smoothly when clear.
