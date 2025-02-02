import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from hazmat_msgs.msg import MecanumCmd

class Mecanum(Node):
    def __init__(self):
        super().__init__("mecanum")

        self.create_subscription(Twist, "/hazmat/cmd_vel", self.twistCallback, 10)
        self.wheelCmd = self.create_publisher(MecanumCmd, "/wheel_cmd", 10)

        self.LENGTH_X = 0.5
        self.LENGTH_Y = 0.5
        self.WHEEL_R = 38.5
        self.LENGTH_SUM = self.LENGTH_X + self.LENGTH_Y
        self.WHEEL_R_INV = 1 / self.WHEEL_R

    def twistCallback(self, msg: Twist):
        # Reference: https://www.ijcaonline.org/archives/volume113/number3/19804-1586/
        wheelCmd = MecanumCmd()
        velocity_result = msg.linear.x + msg.linear.y
        velocity_diff = msg.linear.x - msg.linear.y
        angular_term = self.LENGTH_SUM * msg.angular.z
        
        wheelCmd.front_left = (velocity_diff - angular_term) * self.WHEEL_R_INV
        wheelCmd.front_right = (velocity_result + angular_term) * self.WHEEL_R_INV
        wheelCmd.rear_left = (velocity_result - angular_term) * self.WHEEL_R_INV
        wheelCmd.rear_right = (velocity_diff + angular_term) * self.WHEEL_R_INV

        self.wheelCmd.publish(wheelCmd)
        

def main():
    rclpy.init()
    node = Mecanum()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()