#!/usr/bin/env python3
"""
agv_audio_node.py
-----------------
Plays audio synced with AGV movement by subscribing to:
  /agv/cmd_enable  (std_msgs/Bool) -> True  : Start / Resume playback
  /agv/cmd_stop    (std_msgs/Bool) -> True  : Pause playback

Uses ffmpeg launched as a subprocess writing directly to ALSA (plughw:2,0).
This bypasses SDL and PulseAudio entirely, making it compatible with
headless systemd service environments.

Pause/resume is done via OS signals:
  SIGSTOP -> suspends the process (pause)
  SIGCONT -> resumes the process  (unpause)
"""

import os
import time
import subprocess
import glob
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


AUDIO_DIR = '/home/amr/ros2_ws/src/amr_ws/AGV_playlist'
SFX_HORN = '/home/amr/ros2_ws/src/amr_ws/AGV_horn/horn.mp3'
SFX_DOCKING = '/home/amr/ros2_ws/src/amr_ws/AGV_horn/docking.mp3'
ALSA_DEVICE = 'plughw:2,0'


class AgvAudioNode(Node):

    def __init__(self):
        super().__init__('agv_audio_node')

        self._proc = None        # subprocess.Popen handle for ffmpeg music
        self._music_running = False  # True when music should be playing (not killed by SFX)

        # Position tracking — simulates true pause via -ss seek on resume.
        # _music_position accumulates seconds played before each kill.
        # _music_start_time is the wall-clock time the current session started.
        self._music_position = 0.0
        self._music_start_time = None

        # Inherit environment as-is — ffmpeg talks directly to ALSA,
        # no SDL or PulseAudio session variables needed.
        self._audio_env = os.environ.copy()

        # SFX State tracking
        self._sfx_proc = None
        self._horn_timer = None
        self._paused_by_sfx = False   # True if music was killed to make room for SFX
        self._current_sfx_state = "STOPPED"

        self._playlist = sorted(glob.glob(os.path.join(AUDIO_DIR, '*.mp3')))
        self._track_idx = 0
        if not self._playlist:
            self.get_logger().warn(f'No MP3 files found in {AUDIO_DIR}!')

        self.create_subscription(
            Bool,
            '/agv/cmd_enable',
            self._on_enable,
            10,
        )
        self.create_subscription(
            Bool,
            '/agv/cmd_stop',
            self._on_stop,
            10,
        )
        self.create_subscription(
            String,
            '/agv/state',
            self._on_state,
            10,
        )

        # Timer to poll if the current track has finished
        self.create_timer(1.0, self._check_track_finished)

        self.get_logger().info('AGV Audio Node started. Waiting for commands…')

    # ------------------------------------------------------------------
    # Subscriber Callbacks & Timers
    # ------------------------------------------------------------------

    def _check_track_finished(self):
        """Polls ffmpeg to see if the current track has finished automatically."""
        if self._proc is not None and not self._paused_by_sfx:
            if self._proc.poll() is not None:
                if self._playlist:
                    self._track_idx = (self._track_idx + 1) % len(self._playlist)
                    self._music_position = 0.0   # reset position for the new track
                    self._music_start_time = None
                    self.get_logger().info(f'Track finished. Moving to track {self._track_idx + 1}/{len(self._playlist)}')
                    self._start_audio()

    def _on_state(self, msg: String):
        """Called when AGV state changes. Manages SFX overlays like horn and docking."""
        new_state = msg.data

        if new_state == self._current_sfx_state:
            return  # No change

        self._current_sfx_state = new_state

        if new_state == "OBSTACLE_DETECTED":
            self._start_sfx_mode()
            self.get_logger().info('Obstacle detected. Playing horn.')
            self._play_horn_once()
            self._horn_timer = self.create_timer(1.0, self._play_horn_once)
        elif new_state in ("DOCKING 1", "DOCKING 2"):
            self._start_sfx_mode()
            self.get_logger().info(f'{new_state} started. Playing docking audio.')
            self._play_docking_loop()
        else:
            # Not in an alert state anymore — stop SFX and resume music.
            self._stop_sfx_mode()

    def _on_enable(self, msg: Bool):
        """Called when GO is pressed on the web UI."""
        if not msg.data:
            return

        self._music_running = True
        if self._proc is None or self._proc.poll() is not None:
            if not self._paused_by_sfx:  # don't start music while SFX is active
                self._start_audio()
        else:
            self.get_logger().info('Audio already playing — ignoring duplicate GO')

    def _on_stop(self, msg: Bool):
        """Called when STOP is pressed on the web UI."""
        if not msg.data:
            return

        self._music_running = False
        self._stop_sfx_mode()
        self._paused_by_sfx = False
        self._kill_music()

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _start_sfx_mode(self):
        """Prepares for SFX by killing music so the ALSA device is fully released."""
        self._kill_sfx()
        if self._proc is not None and self._proc.poll() is None:
            # Hard-kill the music process — SIGSTOP keeps it holding the hw device,
            # which prevents a second ffmpeg from opening plughw:2,0.
            self._kill_music()
            self._paused_by_sfx = True
            self.get_logger().info('Music killed to release ALSA device for SFX.')

    def _stop_sfx_mode(self):
        """Kills any active SFX and restarts music from the same track if it was interrupted."""
        self._kill_sfx()
        if self._paused_by_sfx and self._music_running:
            self._paused_by_sfx = False
            self._start_audio()  # restart from the same track index
            self.get_logger().info('SFX done — restarting music track.')
        else:
            self._paused_by_sfx = False

    def _kill_sfx(self):
        """Terminate SFX processes and timers."""
        if self._horn_timer is not None:
            self._horn_timer.cancel()
            self._horn_timer = None

        if self._sfx_proc is not None and self._sfx_proc.poll() is None:
            self._sfx_proc.terminate()
            try:
                self._sfx_proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._sfx_proc.kill()
        self._sfx_proc = None

    def _play_horn_once(self):
        """Plays the horn sound exactly once."""
        if not os.path.exists(SFX_HORN):
            self.get_logger().warn(f'Horn file not found: {SFX_HORN}')
            return
        cmd = [
            'ffmpeg', '-y',
            '-i', SFX_HORN,
            '-f', 'alsa', ALSA_DEVICE,
        ]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=self._audio_env,
        )

    def _play_docking_loop(self):
        """Plays the docking sound on a continuous loop."""
        if not os.path.exists(SFX_DOCKING):
            self.get_logger().warn(f'Docking file not found: {SFX_DOCKING}')
            return
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1',
            '-i', SFX_DOCKING,
            '-f', 'alsa', ALSA_DEVICE,
        ]
        self._sfx_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=self._audio_env,
        )

    def _start_audio(self):
        """Launch ffmpeg for the current track, seeking to the saved position for true-pause resume."""
        if not self._playlist:
            self.get_logger().warn('Playlist is empty, cannot start audio.')
            return

        seek_pos = self._music_position
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(seek_pos),        # seek before decode — resumes from paused position
            '-i', self._playlist[self._track_idx],
            '-f', 'alsa', ALSA_DEVICE,
        ]

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=self._audio_env,
            )
            self._music_start_time = time.time()
            track_name = os.path.basename(self._playlist[self._track_idx])
            self.get_logger().info(
                f'Audio playback started (PID {self._proc.pid}): {track_name} '
                f'[seek={seek_pos:.1f}s]'
            )
        except FileNotFoundError:
            self.get_logger().error(
                'ffmpeg not found! Install it with: sudo apt install ffmpeg'
            )

    def _kill_music(self):
        """Snapshot playback position, then terminate the music ffmpeg process."""
        # Accumulate how many seconds have played so resume can seek back here.
        if self._music_start_time is not None:
            self._music_position += time.time() - self._music_start_time
            self._music_start_time = None

        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self.get_logger().info(
                f'Music paused at {self._music_position:.1f}s (process terminated).'
            )
        self._proc = None

    def _kill_audio(self):
        """Terminate all audio (music + SFX) cleanly on shutdown."""
        self._kill_sfx()
        self._kill_music()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def destroy_node(self):
        self._kill_audio()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = AgvAudioNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
