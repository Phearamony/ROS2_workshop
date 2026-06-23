import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class ImuReader(Node):
    def __init__(self):
        super().__init__('imu_reader')
        self.sub = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
            10
        )

    def imu_callback(self, msg):
        wz = msg.angular_velocity.z
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y

        self.get_logger().info(
            f'Angular z={wz:.4f} | Accel x={ax:.3f}, y={ay:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ImuReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

