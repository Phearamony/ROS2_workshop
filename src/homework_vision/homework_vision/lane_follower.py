import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge


class LaneFollower(Node):
    def __init__(self):
        super().__init__('lane_follower')

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.linear_speed = 0.04

        self.kp = 0.003
        self.kd = 0.001
        self.prev_error = 0.0

        self.last_lane_center = None

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        height, width, _ = frame.shape

        roi_y_start = int(height * 0.45)
        roi = frame[roi_y_start:height, :]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 160])
        upper_white = np.array([180, 90, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        centers = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < 80:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if h < 10:
                continue

            cx = x + w // 2
            centers.append(cx)

        cmd = Twist()
        image_center = width // 2

        if len(centers) >= 2:
            centers = sorted(centers)

            left_lane = centers[0]
            right_lane = centers[-1]

            lane_center = (left_lane + right_lane) // 2
            error = image_center - lane_center

            derivative = error - self.prev_error
            angular = self.kp * error + self.kd * derivative
            self.prev_error = error

            cmd.linear.x = self.linear_speed
            cmd.angular.z = angular

            self.last_lane_center = lane_center

            self.get_logger().info(
                f'LEFT={left_lane}, RIGHT={right_lane}, CENTER={lane_center}, ERROR={error}'
            )

        elif len(centers) == 1:
            line_center = centers[0]

            if line_center < image_center:
                lane_center = line_center + 180
            else:
                lane_center = line_center - 180

            error = image_center - lane_center

            cmd.linear.x = 0.05
            cmd.angular.z = self.kp * error

            self.last_lane_center = lane_center

            self.get_logger().warn(
                f'Only one lane visible. Estimated center={lane_center}'
            )

        else:
            cmd.linear.x = 0.02
            cmd.angular.z = 0.3
            self.get_logger().warn('No lane detected')

        self.cmd_pub.publish(cmd)

        debug = roi.copy()

        cv2.line(debug, (image_center, 0), (image_center, debug.shape[0]), (255, 0, 0), 2)

        if self.last_lane_center is not None:
            cv2.line(debug, (self.last_lane_center, 0), (self.last_lane_center, debug.shape[0]), (0, 255, 0), 2)

        cv2.imshow('Lane Debug', debug)
        cv2.imshow('White Mask', mask)
        cv2.waitKey(1)

    def search_with_memory(self, cmd):
        cmd.linear.x = 0.03

        if self.last_lane_center is None:
            cmd.angular.z = 0.3
            self.get_logger().warn('Lane lost. Searching...')
            return

        image_center_guess = 320

        if self.last_lane_center < image_center_guess:
            cmd.angular.z = 0.3
        else:
            cmd.angular.z = -0.3

        self.get_logger().warn('Lane unclear. Using last known lane center.')


def main(args=None):
    rclpy.init(args=args)
    node = LaneFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()