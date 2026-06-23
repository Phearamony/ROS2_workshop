import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    gazebo_launch = os.path.join(
        get_package_share_directory('workshop_gazebo'),
        'launch',
        'classroom_world.launch.py'
    )

    rviz_config = os.path.join(
        get_package_share_directory('workshop_description'),
        'rviz',
        'workshop.rviz'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )

    known_map = Node(
        package='workshop_mapping',
        executable='known_map_publisher',
        name='known_map_publisher',
        output='screen'
    )

    astar = Node(
        package='workshop_planner',
        executable='astar_map_planner',
        name='astar_map_planner',
        output='screen'
    )

    waypoint_follower = Node(
        package='workshop_controller',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        gazebo,

        TimerAction(period=3.0, actions=[known_map]),
        TimerAction(period=4.0, actions=[astar]),
        TimerAction(period=5.0, actions=[waypoint_follower]),
        TimerAction(period=6.0, actions=[rviz]),
    ])
