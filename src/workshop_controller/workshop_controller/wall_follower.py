import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
    
        self.left_distance = 0.0
        self.front_distance = 0.0
        
        self.target_distance = 0.25
        self.kp = 0.2
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.timer = self.create_timer(0.1, self.control_loop)
    
    def clean_min(self, values):
        valid = [v for v in values if not math.isinf(v) and not math.isnan(v)]
        return min(valid) if valid else 10.0
    
    def scan_callback(self, msg):
        ranges = msg.ranges
        
        self.front_distance = self.clean_min(
            ranges[0:10] + ranges[-10:]
        )

        self.left_distance = self.clean_min(
            ranges[80:100]
        )
    
    def control_loop(self):
        cmd = Twist()

        if self.front_distance < 0.3:
            cmd.linear.x = 0.0
            cmd.angular.z = -0.7
        else:
            error = self.target_distance - self.left_distance
            cmd.linear.x = 0.15
            cmd.angular.z = self.kp * error
            
        self.cmd_pub.publish(cmd)
        
def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()   
        

