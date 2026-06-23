from setuptools import find_packages, setup

package_name = 'workshop_controller'

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
    maintainer='admins',
    maintainer_email='admins@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'obstacle_avoidance = workshop_controller.obstacle_avoidance:main',
            'motor_controller = workshop_controller.motor_controller:main',
            'wall_follower = workshop_controller.wall_follower:main',
            'waypoint_follower = workshop_controller.waypoint_follower:main',
        ],
    },
)
