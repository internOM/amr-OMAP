from setuptools import find_packages, setup

package_name = 'education_material'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'int_pub=education_material.int_pub:main',
            'int_sub=education_material.int_sub:main',
            'string_pub=education_material.string_pub:main',
            'string_sub=education_material.string_sub:main',
            'evenodd_checker=education_material.evenodd_checker:main',
            'keypressed_talker=education_material.keypressed_talker:main',
            'keypressed_calculator=education_material.keypressed_calculator:main',
            'keypressed_to_cmdvel=education_material.keypressed_to_cmdvel:main',

        ],
    },
)
