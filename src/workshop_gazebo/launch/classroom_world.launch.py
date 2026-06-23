import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    world_path = os.path.join(
        get_package_share_directory('workshop_gazebo'),
        'worlds',
        'classroom.world'
    )

    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

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

    spawn_turtlebot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'turtlebot3_burger',
            '-file', os.path.join(
                turtlebot3_gazebo_dir,
                'models',
                'turtlebot3_burger',
                'model.sdf'
            ),
            '-x', '-2.0',
            '-y', '-2.0',
            '-z', '0.01'
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
            value=os.path.join(turtlebot3_gazebo_dir, 'models')
        ),
        gazebo,
        TimerAction(period=5.0, actions=[spawn_turtlebot])
    ])