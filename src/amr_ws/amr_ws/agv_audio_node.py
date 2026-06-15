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
import signal
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

        self._proc = None        # subprocess.Popen handle for ffmpeg
        self._is_paused = False  # True when we have sent a SIGSTOP

        # Inherit environment as-is — ffmpeg talks directly to ALSA,
        # no SDL or PulseAudio session variables needed.
        self._audio_env = os.environ.copy()

        # SFX State tracking
        self._sfx_proc = None
        self._horn_timer = None
        self._paused_by_sfx = False
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
        if self._proc is not None and not self._is_paused:
            if self._proc.poll() is not None:
                if self._playlist:
                    self._track_idx = (self._track_idx + 1) % len(self._playlist)
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

        if self._proc is None or self._proc.poll() is not None:
            self._start_audio()
        elif self._is_paused:
            self._toggle_pause()  # unpause
        else:
            self.get_logger().info('Audio already playing — ignoring duplicate GO')

    def _on_stop(self, msg: Bool):
        """Called when STOP is pressed on the web UI."""
        if not msg.data:
            return

        self._stop_sfx_mode()
        self._paused_by_sfx = False

        if self._proc is not None and self._proc.poll() is None and not self._is_paused:
            self._toggle_pause()  # pause
        else:
            self.get_logger().info('Audio already paused or not running — ignoring duplicate STOP')

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _start_sfx_mode(self):
        """Prepares for SFX by killing old SFX and pausing main playlist."""
        self._kill_sfx()
        if self._proc is not None and not self._is_paused:
            self._toggle_pause()
            self._paused_by_sfx = True

    def _stop_sfx_mode(self):
        """Kills any active SFX and resumes main playlist if it was paused by SFX."""
        self._kill_sfx()
        if self._paused_by_sfx:
            self._toggle_pause()
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
        """Launch ffmpeg as a background process for the current track."""
        if not self._playlist:
            self.get_logger().warn('Playlist is empty, cannot start audio.')
            return

        cmd = [
            'ffmpeg', '-y',
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
            self._is_paused = False
            track_name = os.path.basename(self._playlist[self._track_idx])
            self.get_logger().info(f'Audio playback started (PID {self._proc.pid}): {track_name}')
        except FileNotFoundError:
            self.get_logger().error(
                'ffmpeg not found! Install it with: sudo apt install ffmpeg'
            )

    def _toggle_pause(self):
        """
        Pause or resume ffmpeg using OS signals:
          SIGSTOP - suspends the process (keeps position)
          SIGCONT - resumes from where it was
        """
        if self._proc is None or self._proc.poll() is not None:
            self.get_logger().warn('Tried to toggle pause but ffmpeg is not running')
            return
        try:
            if self._is_paused:
                os.kill(self._proc.pid, signal.SIGCONT)
            else:
                os.kill(self._proc.pid, signal.SIGSTOP)
            self._is_paused = not self._is_paused
            state = 'PAUSED' if self._is_paused else 'PLAYING'
            self.get_logger().info(f'Audio state -> {state}')
        except OSError as e:
            self.get_logger().error(f'Failed to signal ffmpeg: {e}')
            self._proc = None

    def _kill_audio(self):
        """Terminate ffmpeg cleanly."""
        self._kill_sfx()
        if self._proc is not None and self._proc.poll() is None:
            self.get_logger().info('Terminating audio playback…')
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
            self._is_paused = False

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