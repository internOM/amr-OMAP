from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
	
	camera_info_file = "file://" + get_package_share_directory(
		"camera_follow") + "/config/mcm303_info.yaml"
	usb_cam_node = Node(
		package="usb_cam",
		executable="usb_cam_node_exe",
		parameters=[
			{"video_device":"/dev/video2"},
			{"frame_id":"camera_color_optical_frame"},
			{"camera_info_url":camera_info_file},
			{"pixel_format":"yuyv2rgb"}
		],
	),
	
	image_sub_node = Node(
		package="image_sub",
		executable="image_sub_node",
		output="screen",
	
	),
	return LaunchDescription([
		usb_cam_node,
		image_sub_node
	])

#ros2 run usb_cam usb_cam_node_exe --ros-args --remap video_device:=/dev/video2
#ros2 run camera_follow image_sub 
