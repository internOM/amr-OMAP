import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'camera_follow'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='om',
    maintainer_email='om@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	"image_sub = camera_follow.image_sub:main",
        	"cam_line_follow = camera_follow.cam_line_follow:main",
        	"webcam_line_follow = camera_follow.webcam_line_follow:main",
        	"cam_line_search = camera_follow.cam_line_search:main",
        	"cam_line_follow_stop = camera_follow.cam_line_follow_stop:main",
        	"cam_line_follow_stop_early = camera_follow.cam_line_follow_stop_early:main",
        	"cam_line_follow_stop_early_2line = camera_follow.cam_line_follow_stop_early_2line:main",
        	"hand_eye_mrc01 = camera_follow.hand_eye_mrc01:main",
        	"hand_eye_petbottle = camera_follow.hand_eye_petbottle:main",
        	"cam_line_follow_stop_black = camera_follow.cam_line_follow_stop_black:main",
        	"cam_line_follow_stop_edge = camera_follow.cam_line_follow_stop_edge:main",
        	"cam_line_follow_stop_grayscale = camera_follow.cam_line_follow_stop_grayscale:main",
        	"cam_line_follow_d435if_nonshow = camera_follow.cam_line_follow_d435if_nonshow:main",
        ],
    },
)
