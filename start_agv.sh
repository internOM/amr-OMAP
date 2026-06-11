#!/bin/bash

# Explicitly set HOME so ROS2 tools behave correctly under systemd
export HOME=/home/amr

# Source ROS2 Jazzy base
source /opt/ros/jazzy/setup.bash

# Source your workspace overlay
source /home/amr/ros2_ws/install/setup.bash

# Replace this shell process with the ROS2 launch process
# so systemd tracks the correct PID
exec ros2 launch amr_ws bringup_launch.py
