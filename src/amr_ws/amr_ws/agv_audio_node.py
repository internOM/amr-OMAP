#!/usr/bin/env python3
"""
agv_audio_node.py
-----------------
Plays audio synced with AGV movement by subscribing to:
  /agv/cmd_enable  (std_msgs/Bool) -> True  : Start / Resume playback
  /agv/cmd_stop    (std_msgs/Bool) -> True  : Pause playback

Uses ffplay launched as a subprocess. Pause/resume is done via OS signals:
  SIGSTOP -> suspends the process (pause)
  SIGCONT -> resumes the process  (unpause)

NOTE: ffplay does NOT respond to stdin 'p' when launched with a pipe —
its keyboard handler is SDL/terminal-based, not stdin-based.
"""

import os
import signal
import subprocess
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


AUDIO_FILE = '/home/intern1/Downloads/AGV_JC.mp3'

# ffplay flags:
#   -nodisp     : no video window
#   -loglevel quiet : suppress console spam
#   Note: we intentionally omit -autoexit so the process stays alive to resume
FFPLAY_CMD = [
    'ffplay',
    '-nodisp',
    '-loglevel', 'quiet',
    AUDIO_FILE,
]


class AgvAudioNode(Node):

    def __init__(self):
        super().__init__('agv_audio_node')

        self._proc = None        # subprocess.Popen handle for ffplay
        self._is_paused = False  # True when we have sent a pause command

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

        self.get_logger().info('AGV Audio Node started. Waiting for commands…')

    # ------------------------------------------------------------------
    # Subscriber Callbacks
    # ------------------------------------------------------------------

    def _on_enable(self, msg: Bool):
        """Called when GO is pressed on the web UI."""
        if not msg.data:
            return  # Ignore False messages

        if self._proc is None or self._proc.poll() is not None:
            # Process not running — start fresh
            self._start_audio()
        elif self._is_paused:
            # Process alive but paused — send 'p' to unpause
            self._toggle_pause()  # unpause
        else:
            self.get_logger().info('Audio already playing — ignoring duplicate GO')

    def _on_stop(self, msg: Bool):
        """Called when STOP is pressed on the web UI."""
        if not msg.data:
            return  # Ignore False messages

        if self._proc is not None and self._proc.poll() is None and not self._is_paused:
            self._toggle_pause()  # pause
        else:
            self.get_logger().info('Audio already paused or not running — ignoring duplicate STOP')

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _start_audio(self):
        """Launch ffplay as a background process."""
        try:
            self._proc = subprocess.Popen(
                FFPLAY_CMD,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._is_paused = False
            self.get_logger().info(f'Audio playback started (PID {self._proc.pid})')
        except FileNotFoundError:
            self.get_logger().error(
                'ffplay not found! Install it with: sudo apt install ffmpeg'
            )

    def _toggle_pause(self):
        """
        Pause or resume ffplay using OS signals:
          SIGSTOP - suspends the process (keeps position)
          SIGCONT - resumes from where it was
        This is the reliable approach on Linux since ffplay's 'p' key
        is handled by SDL and is NOT available via a stdin pipe.
        """
        if self._proc is None or self._proc.poll() is not None:
            self.get_logger().warn('Tried to toggle pause but ffplay is not running')
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
            self.get_logger().error(f'Failed to signal ffplay: {e}')
            self._proc = None

    def _kill_audio(self):
        """Terminate ffplay cleanly."""
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
