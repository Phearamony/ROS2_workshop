import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose


class KnownMapPublisher(Node):
    def __init__(self):
        super().__init__('known_map_publisher')

        self.map_pub = self.create_publisher(
            OccupancyGrid,
            '/map',
            10
        )

        self.resolution = 0.05
        self.width = 120
        self.height = 120
        self.origin_x = -3.0
        self.origin_y = -3.0

        self.timer = self.create_timer(1.0, self.publish_map)

    def world_to_grid(self, x, y):
        gx = int((x - self.origin_x) / self.resolution)
        gy = int((y - self.origin_y) / self.resolution)
        return gx, gy

    def set_obstacle_rect(self, grid, center_x, center_y, size_x, size_y):
        min_x = center_x - size_x / 2.0
        max_x = center_x + size_x / 2.0
        min_y = center_y - size_y / 2.0
        max_y = center_y + size_y / 2.0

        gx_min, gy_min = self.world_to_grid(min_x, min_y)
        gx_max, gy_max = self.world_to_grid(max_x, max_y)

        gx_min = max(0, min(self.width - 1, gx_min))
        gx_max = max(0, min(self.width - 1, gx_max))
        gy_min = max(0, min(self.height - 1, gy_min))
        gy_max = max(0, min(self.height - 1, gy_max))

        for gy in range(gy_min, gy_max + 1):
            for gx in range(gx_min, gx_max + 1):
                index = gy * self.width + gx
                grid[index] = 100 #occupied (walls)

    def publish_map(self):
        msg = OccupancyGrid()

        msg.header.frame_id = 'odom'
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.info.resolution = self.resolution
        msg.info.width = self.width
        msg.info.height = self.height

        msg.info.origin = Pose()
        msg.info.origin.position.x = self.origin_x
        msg.info.origin.position.y = self.origin_y
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0

        grid = [0 for _ in range(self.width * self.height)]

        # Outer walls
        self.set_obstacle_rect(grid, 0.0, -3.0, 6.0, 0.2)
        self.set_obstacle_rect(grid, 0.0, 3.0, 6.0, 0.2)
        self.set_obstacle_rect(grid, -3.0, 0.0, 0.2, 6.0)
        self.set_obstacle_rect(grid, 3.0, 0.0, 0.2, 6.0)

        # Inner obstacles
        self.set_obstacle_rect(grid, -1.0, 0.8, 2.0, 0.2)
        self.set_obstacle_rect(grid, 1.0, -0.8, 2.0, 0.2)

        msg.data = grid

        self.map_pub.publish(msg)
        self.get_logger().info('Published pre-known classroom map')


def main(args=None):
    rclpy.init(args=args)
    node = KnownMapPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
