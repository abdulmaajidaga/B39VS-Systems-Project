import serial
import rclpy
from hazmat_msgs.msg import MecanumCmd
from rclpy.node import Node
from std_msgs.msg import Int32

class SerialBridge(Node):
    def __init__(self):
        super().__init__("serial_bridge")

        self.create_timer(1/100, self.serial_tx)
        self.serial_port = serial.Serial("/dev/ttyACM0", 115200)

        self.create_subscription(MecanumCmd, "/wheel_cmd", self.wheel_callback, 10)

        self.speeds = MecanumCmd()

    def serial_tx(self):
        try:
            n = 4
            self.serial_port.write(self.packCommand().encode('utf-8'))
            self.serial_port.flush()
            read = self.serial_port.readline()
            self.get_logger().info(f"Serial read: {read}")
            self.get_logger().info(f"Sent angle: {self.packCommand()}")
        except Exception as e:
            self.get_logger().error(f"Serial write failed: {str(e)}")

    def wheel_callback(self, msg: MecanumCmd):
        self.speeds = msg

    def packCommand(self):
        cmd = ""
        cmd += str(self.speeds.front_left).zfill(4)
        cmd += str(self.speeds.front_right).zfill(4)
        cmd += str(self.speeds.rear_left).zfill(4)
        cmd += str(self.speeds.rear_right).zfill(4)

        return cmd

def main():
    rclpy.init()
    node = SerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
