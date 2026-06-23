import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('angular_speed', 0.0)

        self.timer = self.create_timer(0.1, self.control_loop)

    def control_loop(self):
        linear_speed = self.get_parameter('linear_speed').value
        angular_speed = self.get_parameter('angular_speed').value

        cmd = Twist()
        cmd.linear.x = linear_speed
        cmd.angular.z = angular_speed

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = MotorController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
