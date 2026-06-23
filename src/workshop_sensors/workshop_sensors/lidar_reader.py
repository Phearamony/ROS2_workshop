import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LidarReader(Node):
    def __init__(self):
        super().__init__('lidar_reader')
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
    
    def scan_callback(self, msg):
        ranges = msg.ranges
        front = ranges[0:10] + ranges[-10:] # take 0 to 9 degree + 350 -359 degree
        left = ranges[80:100]
        right = ranges[260:280]

        def clean_min(values):
            valid = [v for v in values if not math.isinf(v) and not math.isnan(v)]
            return min(valid) if valid else float('inf')

        front_dist = clean_min(front)
        left_dist = clean_min(left)
        right_dist = clean_min(right)

        self.get_logger().info(
            f'Front: {front_dist:.2f} m | Left: {left_dist:.2f} m | Right: {right_dist:.2f} m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = LidarReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
