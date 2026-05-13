from setuptools import find_packages, setup

package_name = 'amr_ws'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Add these two lines to install launch files and params
        ('share/' + package_name + '/launch', ['launch/slam_toolbox_launch.py']),
        ('share/' + package_name + '/params', ['params/slam_param.yaml']),
        ('share/' + package_name + '/waypoints', ['waypoints/waypoints.yaml']),
        ('share/' + package_name + '/nav2_params', ['nav2_params/twist_mux.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='intern1',
    maintainer_email='intern1@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'compass = amr_ws.compass:main',
            'joystick_to_motor = amr_ws.joystick_to_motor:main',
            'Demo_Automation = amr_ws.Demo_Automation:main',
            'keyboard_listener = amr_ws.keyboard_listener:main',
            'Automation_and_Lidar = amr_ws.Automation_and_Lidar:main',
            'baselink_laser_tf = amr_ws.baselink_laser_tf:main',
            'Automation_and_Lidar2 = amr_ws.Automation_and_Lidar2:main',
            'camera_follow = amr_ws.camera_follow:main',
            'webcam_line_follow = amr_ws.webcam_line_follow:main',
            'cmdvelsmoothed_to_cmdvel=amr_ws.cmdvelsmoothed_to_cmdvel:main',
            'path_logger=amr_ws.path_logger:main',
            'path_publisher=amr_ws.path_publisher:main',
            'localization_node = amr_ws.localization_node:main',
            'return_home_node = amr_ws.return_home_node:main',
            'orchestrator_node = amr_ws.orchestrator_node:main',
            'pose_persistence_node = amr_ws.pose_persistence_node:main',
            'agv_audio_node = amr_ws.agv_audio_node:main',
            'hsv_probe_node = amr_ws.hsv_probe_node:main',
            'rack_websocket_server = amr_ws.rack_websocket_server:main',
        ],
    },
)
