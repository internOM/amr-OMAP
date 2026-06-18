# Audio Systemd Stability

## The Problem
The `agv_audio_node` originally used `ffplay` with `SIGSTOP`/`SIGCONT` signals to pause and resume music. During manual terminal launches (`ros2 run`), it worked perfectly. However, when deployed as a headless systemd service (`start_agv.service`), the audio would either fail entirely or loop the first 1 second of audio repeatedly before crashing.

## Root Cause
- **PulseAudio / SDL Deprivation**: `ffplay` relies heavily on SDL (Simple DirectMedia Layer) for its audio backend. When run under a headless `systemd` user session, the environment variables required to access the user's PulseAudio daemon or ALSA default devices were missing or permissions were insufficient.
- **Hardware Device Locking**: Trying to overlay sound effects (horn/docking) on top of paused music caused `Device or resource busy` errors. `SIGSTOP` suspends a process but *does not* release its hold on the physical ALSA device.

## The Solution
1. **Direct ALSA Routing via FFmpeg**: We migrated from `ffplay` to standard `ffmpeg` acting as an audio decoder directly piping to ALSA hardware using `-f alsa plughw:2,0`. This bypassed SDL entirely and removed the dependency on an active desktop session.
2. **Hard-Kill vs. Pause**: Instead of using `SIGSTOP`, the node now forcefully terminates (`_kill_music()`) the `ffmpeg` subprocess whenever music needs to pause or an SFX needs to play. This guarantees the ALSA device is released.
3. **Seek-Resume Logging**: To maintain the "pause/resume" illusion, the node manually tracks the playback duration (`_music_position`). When resuming, it spawns a fresh `ffmpeg` process using the `-ss <seconds>` seek flag to pick up exactly where the music was cut off.

## Impact
This stabilized the AGV's headless boot process. Audio now reliably plays from the physical speaker on startup and cleanly swaps between background music and safety chimes (see [[agv_audio_node]]).
