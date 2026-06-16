import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32 # message type: a single integer

class CounterPublisher(Node):
    def __init__(self):
        super().__init__('counter_publisher')
        # Create a publisher on topic '/counter', message type Int32
        self.pub = self.create_publisher(Int32, '/counter', 10)
                                             # ^^^^ ^^^^^^^ ^^ queue size
        self.count = 0
        self.create_timer(1.0, self.publish_count)

    def publish_count(self):
        msg = Int32() # create an empty Int32 message
        msg.data = self.count # fill in the value
        self.pub.publish(msg) # send it
        self.get_logger().info(f'Publishing: {self.count}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(CounterPublisher())
    rclpy.shutdown()
