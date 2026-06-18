# agv_audio_node

## Overview
Handles playback of background music and audio alerts (SFX like horn and docking) synced with the AGV's state. It directly pipes audio via ALSA (`plughw:2,0`) to a physical speaker, making it robust in headless environments.

## Subscriptions
- `/agv/cmd_enable` (`std_msgs/Bool`) — Resumes background music playback.
- `/agv/cmd_stop` (`std_msgs/Bool`) — Pauses background music playback.
- `/agv/state` (`std_msgs/String`) — Tracks AGV status (`OBSTACLE_DETECTED`, `DOCKING 1`, `DOCKING 2`) to trigger appropriate sound effects.

## Architecture
- **Direct ALSA Routing**: Avoids systemd and PulseAudio environment issues by using `ffmpeg` to directly output to ALSA (`plughw:2,0`).
- **OS-Level Pause/Resume**: Instead of simply stopping `ffmpeg`, it terminates the process and uses the `-ss` flag to resume playback exactly where it was stopped, releasing the hardware device completely when SFX needs to play.
- **Playlist Looping**: Automatically polls the track state and advances to the next `.mp3` in the `AGV_playlist` directory when a track finishes.

## Key Behaviors
- **Music Suspension**: When the AGV encounters an obstacle or starts docking, the background music is cleanly terminated, yielding the audio hardware to the SFX track. Once the alert condition clears, the music resumes.
- **Horn & Docking Overlays**: Plays a continuous looping chime during `DOCKING` states and repeats a horn sound every 1 second during `OBSTACLE_DETECTED` states.

## Cross-References
- **Breakthroughs**: [[audio_systemd_stability]]
- **UI Integration**: Responds to the same stop/go commands issued by [[agv_display]].
- **Central Map**: Part of the [[core_node_architectures]].
