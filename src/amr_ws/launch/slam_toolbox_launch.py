from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Correct YAML filename
    param_file = os.path.join(
        get_package_share_directory('amr_ws'),
        'params',
        'slam_param.yaml'   # <-- use the actual file name here
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',  # or async
        name='slam_toolbox',
        output='screen',
        parameters=[param_file]
    )

    return LaunchDescription([slam_node])
