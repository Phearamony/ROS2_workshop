import math
import heapq
import rclpy

from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path, Odometry
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped


class AStarMapPlanner(Node):
    def __init__(self):
        super().__init__('astar_map_planner')
        
        # World coordinates in meters
        self.robot_x = None
        self.robot_y = None
        self.goal_world = None

        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        self.path_pub = self.create_publisher(
            Path,
            '/planned_path',
            10
        )
        

        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.map_received = False
        self.grid = []
        self.width = 0
        self.height = 0
        self.resolution = 0.0
        self.origin_x = 0.0
        self.origin_y = 0.0


        self.timer = self.create_timer(1.0, self.plan_loop)
        
    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

    def goal_callback(self, msg):
        self.goal_world = (
            msg.pose.position.x,
            msg.pose.position.y
        )
        self.get_logger().info(f'Goal set: {self.goal_world}')

    def map_callback(self, msg):
        self.width = msg.info.width
        self.height = msg.info.height
        self.resolution = msg.info.resolution
        self.origin_x = msg.info.origin.position.x
        self.origin_y = msg.info.origin.position.y

        self.grid = list(msg.data)
        self.map_received = True

    def world_to_grid(self, x, y):
        gx = int((x - self.origin_x) / self.resolution)
        gy = int((y - self.origin_y) / self.resolution)
        return gx, gy

    def grid_to_world(self, gx, gy):
        x = self.origin_x + (gx + 0.5) * self.resolution
        y = self.origin_y + (gy + 0.5) * self.resolution
        return x, y

    def index(self, gx, gy):
        return gy * self.width + gx

    def is_free(self, gx, gy):
        if gx < 0 or gy < 0 or gx >= self.width or gy >= self.height:
            return False

        value = self.grid[self.index(gx, gy)]

        # 0 = free, 100 = obstacle, -1 = unknown
        return value == 0

    def heuristic(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return math.sqrt(2) * min(dx, dy) + abs(dx - dy)

    def get_neighbors(self, node):
        gx, gy = node

        directions = [
            (1, 0, 1.0),
            (-1, 0, 1.0),
            (0, 1, 1.0),
            (0, -1, 1.0),
            (1, 1, math.sqrt(2)),
            (1, -1, math.sqrt(2)),
            (-1, 1, math.sqrt(2)),
            (-1, -1, math.sqrt(2)),
        ]

        neighbors = []

        for dx, dy, cost in directions:
            nx = gx + dx
            ny = gy + dy

            if self.is_free(nx, ny):
                neighbors.append(((nx, ny), cost))

        return neighbors

    def astar(self, start, goal):
        open_heap = []
        heapq.heappush(open_heap, (0.0, start)) # auto sort for us

        came_from = {}
        g_score = {start: 0.0}
        closed_set = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed_set:
                continue

            if current == goal:
                return self.reconstruct_path(came_from, current)

            closed_set.add(current)

            for neighbor, move_cost in self.get_neighbors(current):
                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (f_score, neighbor))

        return []

    def reconstruct_path(self, came_from, current):
        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path

    def publish_path(self, grid_path):
        path_msg = Path()
        path_msg.header.frame_id = 'odom'
        path_msg.header.stamp = self.get_clock().now().to_msg()

        for gx, gy in grid_path:
            x, y = self.grid_to_world(gx, gy)

            pose = PoseStamped()
            pose.header.frame_id = 'odom'
            pose.header.stamp = self.get_clock().now().to_msg()

            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.05
            pose.pose.orientation.w = 1.0

            path_msg.poses.append(pose)

        self.path_pub.publish(path_msg)

    def plan_loop(self):
        if not self.map_received:
            self.get_logger().warn('Waiting for /map...')
            return

        if self.robot_x is None or self.robot_y is None:
            self.get_logger().warn('Waiting for /odom...')
            return

        if self.goal_world is None:
            self.get_logger().warn('Waiting for RViz 2D Goal Pose...')
            return

        start = self.world_to_grid(self.robot_x, self.robot_y)

        goal = self.world_to_grid(
            self.goal_world[0],
            self.goal_world[1]
        )

        if not self.is_free(start[0], start[1]):
            self.get_logger().error(f'Start cell blocked: {start}')
            return

        if not self.is_free(goal[0], goal[1]):
            self.get_logger().error(f'Goal cell blocked: {goal}')
            return

        grid_path = self.astar(start, goal)

        if not grid_path:
            self.get_logger().error('No path found')
            return

        self.publish_path(grid_path)

        self.get_logger().info(
            f'Published path: {len(grid_path)} points | start={start} goal={goal}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = AStarMapPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()