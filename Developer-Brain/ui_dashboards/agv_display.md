# agv_display

**Parent Node**: [[ui_dashboards]]

## Overview
Primary HMI for the AGV, designed for tablets on the factory floor. Operators can monitor state, intervene during docking, and drive manually via on-screen joysticks.

## HTML/JS Components & Displayed Data

### State Card
- **AGV State** — bold, color-coded label reflecting `/agv/state`:

| State string | CSS class | Color |
|---|---|---|
| `RUNNING` | `running` | Green (pulsing) |
| `STOPPED` / `INACTIVE` / `OBSTACLE` | `stopped` | Red |
| `DOCKING 1` / `DOCKING 2` | `docking` | Purple |
| `WAITING` / `U-TURN` / `CONFIRM GO` | `waiting` | Amber |

- **Subtitle** — short plain-English description of the state.
- **Next Station badge** *(added 2026-06-02)* — pill indicator below the subtitle showing where the AGV will head after its current action:
  - 🟢 **STORE** (green pill) — AGV is heading to STORE next
  - 🔴 **CAPP** (red pill) — AGV is heading to CAPP next
  - 🔵 **RETURN BOX** (blue pill, pulsing dot) — AGV is returning an empty box via the blue line
  - Hidden (`--`) — no committed destination (RUNNING, STOPPED, WAITING, OBSTACLE)

  The badge is inferred from the state topic since `next_station` is not published separately:

  | State | Badge |
  |---|---|
  | DOCKING 1 (at STORE) | 🔴 CAPP |
  | DOCKING 2 (at CAPP) | 🟢 STORE |
  | IDLE — CAPP FULL | 🔴 CAPP |
  | IDLE — STORE EMPTY | 🟢 STORE |
  | CONFIRM GO (D2 sensor wait) | 🟢 STORE |
  | IDLE — RETURN BOX | 🔵 RETURN BOX |

### Control Buttons
The button area uses a 2×2 grid layout:
- **GO (START)** (Top Left) — publishes `true` to `/agv/cmd_enable`. Also serves as **operator confirmation** when state is `WAITING — CONFIRM` or to exit `IDLE — RETURN BOX`.
- **STOP** (Top Right) — publishes `true` to `/agv/cmd_stop`.
- **Mode toggle** (Bottom Left) — publishes to `/agv/cmd_mode`. Button icon and color update to match the current mode broadcast by the node on `/agv/mode`.
- **Empty toggle** (Bottom Right) — publishes to `/agv/cmd_return_empty`. Sets AGV to passively look for blue tape.

### Joystick Panels
- Left joystick: vertical slider → `linear.x` on `/cmd_vel_teleop`
- Right joystick: horizontal slider → `angular.z` on `/cmd_vel_teleop`
- Both joysticks are **locked** (blur overlay) while AGV is in autonomous mode (`setAgvRunning(true)`)

### Ping Badge
- Header displays EMA-smoothed round-trip latency via `/ui_heartbeat`.
- Color: green < 50 ms, amber < 150 ms, red ≥ 150 ms.

## Communication Layer
- **Protocol**: `rosbridge_websocket` via `roslib.min.js` on port 9090.
- **Subscriptions**: `/agv/state`, `/agv/mode`, `/ui_heartbeat`, `/ui_active_client`.
- **Publications**: `/agv/cmd_enable`, `/agv/cmd_stop`, `/agv/cmd_mode`, `/cmd_vel_teleop`, `/ui_heartbeat`, `/ui_active_client`.
- **Single-client enforcement**: Each tab broadcasts a `clientId` + `sessionStartTime` on `/ui_active_client`. Older sessions are force-terminated to prevent conflicting commands.

## Cross-References
- **Backend node**: [[webcam_line_follow]]
- **Interaction loop**: [[ui_integration_flow]]
- **Next-station logic**: [[next_station_rack_filter]]
