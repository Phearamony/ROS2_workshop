from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot',
            executable='counter_publisher',
            name='counter_publisher',
            output='screen',
        ),
        Node(
            package='my_robot',
            executable='counter_subscriber',
            name='counter_subscriber',
            output='screen',
        ),
    ])
