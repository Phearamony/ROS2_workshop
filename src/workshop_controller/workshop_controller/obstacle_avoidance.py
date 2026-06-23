import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.front_dist = math.inf
        self.left_dist = math.inf
        self.right_dist = math.inf

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)

    def clean_min(self, values):
        valid = [
            v for v in values
            if not math.isinf(v) and not math.isnan(v)
        ]
        return min(valid) if valid else math.inf

    def scan_callback(self, msg):
        ranges = msg.ranges

        front = ranges[0:15] + ranges[-15:]
        left = ranges[70:110]
        right = ranges[250:290]

        self.front_dist = self.clean_min(front)
        self.left_dist = self.clean_min(left)
        self.right_dist = self.clean_min(right)

    def control_loop(self):
        cmd = Twist()

        if self.front_dist < 0.45:
            cmd.linear.x = 0.0

            if self.left_dist > self.right_dist:
                cmd.angular.z = 0.6
                direction = 'turning left'
            else:
                cmd.angular.z = -0.6
                direction = 'turning right'

            self.get_logger().info(
                f'Obstacle ahead: {self.front_dist:.2f} m, {direction}'
            )

        else:
            cmd.linear.x = 0.18
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

