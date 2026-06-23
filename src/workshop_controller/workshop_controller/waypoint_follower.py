import math
import rclpy

from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Twist
from tf_transformations import euler_from_quaternion


class WaypointFollower(Node):
    def __init__(self):
        super().__init__('waypoint_follower')

        self.path = []
        self.current_waypoint = 0

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.path_sub = self.create_subscription(
            Path,
            '/planned_path',
            self.path_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)

    def path_callback(self, msg):
        self.path = []

        for pose in msg.poses:
            self.path.append((
                pose.pose.position.x,
                pose.pose.position.y
            ))

        self.current_waypoint = 0
        self.get_logger().info(f'Received path with {len(self.path)} waypoints')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]

        _, _, self.yaw = euler_from_quaternion(quat)

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def control_loop(self):
        if len(self.path) == 0:
            return

        if self.current_waypoint >= len(self.path):
            self.stop_robot()
            return

        target_x, target_y = self.path[self.current_waypoint]

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 0.15:
            self.current_waypoint += 1
            return

        target_yaw = math.atan2(dy, dx)
        yaw_error = self.normalize_angle(target_yaw - self.yaw)

        cmd = Twist()

        if abs(yaw_error) > 0.5:
            cmd.linear.x = 0.03
        else:
            cmd.linear.x = 0.15

        cmd.angular.z = 1.5 * yaw_error

        max_angular = 1.2
        cmd.angular.z = max(-max_angular, min(max_angular, cmd.angular.z))

        self.cmd_pub.publish(cmd)

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()