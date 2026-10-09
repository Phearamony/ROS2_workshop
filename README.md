# ROS 2 Robotics Workshop

Course material and code for a hands-on **ROS 2 Humble** workshop. Students start with a first
publisher/subscriber and work up to a TurtleBot3 that maps, plans and navigates in Gazebo.

📑 Slides: [Week 1](slides/ROS2%20Robotics%20Workshop%20(week1).pdf) · [Week 2](slides/ROS2%20Robotics%20Workshop%20(week2).pdf)

---

## Packages

| Package | What it teaches | Nodes / launch files |
|---|---|---|
| `my_robot` | ROS 2 basics: topics, publishers, subscribers | `counter_publisher`, `counter_subscriber`, `talker_listener.launch.py` |
| `workshop_sensors` | Reading robot sensors | `lidar_reader`, `odom_reader`, `imu_reader` |
| `workshop_controller` | Reactive and goal-based control | `motor_controller`, `obstacle_avoidance`, `wall_follower`, `waypoint_follower` |
| `workshop_mapping` | Publishing a known occupancy map | `known_map_publisher` |
| `workshop_planner` | Path planning with A* | `astar_map_planner` |
| `workshop_gazebo` | Classroom simulation world | `classroom_world.launch.py` |
| `workshop_description` | RViz configuration | `rviz/workshop.rviz` |
| `workshop_bringup` | Runs everything together | `full_system.launch.py` |
| `homework_gazebo` | Homework: camera lane-following track | `camera_track.launch.py` |
| `homework_vision` | Homework: OpenCV lane follower | `lane_follower` |

## Setup

Tested on **Ubuntu 22.04 + ROS 2 Humble** with TurtleBot3 and Gazebo.

```bash
sudo apt install ros-humble-turtlebot3* ros-humble-gazebo-ros-pkgs ros-humble-cv-bridge python3-opencv

mkdir -p ~/ros2_ws && cd ~/ros2_ws
git clone https://github.com/Phearamony/ROS2_workshop.git
mv ROS2_workshop/src . && rm -rf ROS2_workshop     # or keep the repo as your workspace root
colcon build --symlink-install
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
```

## Try it

```bash
# 1. Hello ROS 2
ros2 launch my_robot talker_listener.launch.py

# 2. Full system: Gazebo classroom + known map + A* planner + waypoint follower + RViz
ros2 launch workshop_bringup full_system.launch.py

# 3. Homework: camera lane following
ros2 launch homework_gazebo camera_track.launch.py
ros2 run homework_vision lane_follower
```
