import serial
import rclpy
from hazmat_msgs.msg import MecanumCmd
from rclpy.node import Node
from std_msgs.msg import Int32

class SerialBridge(Node):
    def __init__(self):
        super().__init__("serial_bridge")

        self.create_timer(1, self.serial_tx)
        self.serial_port = serial.Serial("/dev/ttyACM0", 115200)

        self.create_subscription(MecanumCmd, "/wheel_vel", self.wheel_callback, 10)

        self.angle = MecanumCmd()

    def serial_tx(self):
        try:
            self.serial_port.write(f"{int(self.angle.front_left)}{int(self.angle.front_right)}{int(self.angle.rear_left)}{int(self.angle.rear_right)}\n".encode('utf-8'))
            self.serial_port.flush()
            read = self.serial_port.readline()
            self.get_logger().info(f"Serial read: {read}")
            self.get_logger().info(f"Sent angle: {self.angle}{self.angle}{self.angle}{self.angle}\n".encode('utf-8'))
        except Exception as e:
            self.get_logger().error(f"Serial write failed: {str(e)}")

    def wheel_callback(self, msg: MecanumCmd):
        self.angle = msg

def main():
    rclpy.init()
    node = SerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
