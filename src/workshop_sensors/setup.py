from setuptools import find_packages, setup

package_name = 'workshop_sensors'

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
        'lidar_reader = workshop_sensors.lidar_reader:main',
        'odom_reader = workshop_sensors.odom_reader:main',
        'imu_reader = workshop_sensors.imu_reader:main',
        ],
    },
)
