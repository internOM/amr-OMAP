import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    motor_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('om_mvc01'),
                         'launch', 'om_MVC01_bringup_launch.py')
        ),
        launch_arguments={'updateRate': '10'}.items()
    )

    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rplidar_ros'),
                         'launch', 'rplidar_s3_launch.py')
        )
    )

    usb_cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        output='screen',
        parameters=[{
            'video_device': '/dev/video0',
            'image_width': 320,
            'image_height': 240,
            'framerate': 15.0,
            'pixel_format': 'yuyv',
        }]
    )

    agv_audio_node = Node(
        package='amr_ws',
        executable='agv_audio_node',
        output='screen',
    )

    webcam_line_follow_node = Node(
        package='amr_ws',
        executable='webcam_line_follow',
        output='screen',
    )

    rosbridge_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        output='screen',
        parameters=[{
            'delay_between_messages': 0.0,
        }]
    )

    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        parameters=[
            '/home/amr/ros2_ws/src/amr_ws/params/twist_mux.yaml'
        ],
        remappings=[
            ('cmd_vel_out', '/cmd_vel')
        ]
    )

    rack_websocket_node = Node(
        package='amr_ws',
        executable='rack_websocket_server',
        output='screen',
    )

    http_server = ExecuteProcess(
        cmd=['python3', '-m', 'http.server', '8080'],
        cwd='/home/amr/ros2_ws/src/amr_ws/html',
        output='screen',
    )

    return LaunchDescription([
        motor_launch,
        lidar_launch,
        usb_cam_node,
        agv_audio_node,
        webcam_line_follow_node,
        rosbridge_node,
        twist_mux_node,
        rack_websocket_node,
        http_server,
    ])
