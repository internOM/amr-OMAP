from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():

    pkg_share = FindPackageShare('sam_bot_description').find('sam_bot_description')

    default_model_path = os.path.join(
        pkg_share, 'src', 'description', 'sam_bot_description.urdf.xacro'
    )

    default_rviz_config_path = os.path.join(
        pkg_share, 'rviz', 'config.rviz'
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command([
                'xacro ', LaunchConfiguration('model')
            ])
        }],
        output='screen'
    )

    # Joint State Publisher (no GUI)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # Gazebo Harmonic
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen'
    )

    # Spawn robot into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'sam_bot',
            '-topic', 'robot_description'
        ],
        output='screen'
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        output='screen'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            name='model',
            default_value=default_model_path,
            description='Absolute path to robot urdf xacro'
        ),

        DeclareLaunchArgument(
            name='rvizconfig',
            default_value=default_rviz_config_path,
            description='RViz config file'
        ),

        gz_sim,
        joint_state_publisher_node,
        robot_state_publisher_node,

        # give gz time to start
        ExecuteProcess(cmd=['sleep', '3']),

        spawn_entity,
        rviz_node
    ])
