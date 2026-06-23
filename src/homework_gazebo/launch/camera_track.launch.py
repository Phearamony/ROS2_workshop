import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    world_path = os.path.join(
        get_package_share_directory('homework_gazebo'),
        'worlds',
        'homework_track.world'
    )

    model_path = os.path.join(
        get_package_share_directory('homework_gazebo'),
        'models'
    )

    gazebo = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so',
            world_path
        ],
        output='screen'
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'waffle_pi',
            '-file',
            '/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf',
            '-x', '-1.46',
            '-y', '-3.44',
            '-z', '0.01',
            '-Y', '0.02'
        ],
        output='screen'
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_DATABASE_URI',
            value=''
        ),
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=model_path + ':/opt/ros/humble/share/turtlebot3_gazebo/models'
        ),
        gazebo,
        TimerAction(period=5.0, actions=[spawn_robot])
    ])
