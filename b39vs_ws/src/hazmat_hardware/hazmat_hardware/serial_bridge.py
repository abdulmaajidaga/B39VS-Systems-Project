import serial
import rclpy
from hazmat_msgs.msg import MecanumCmd
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

class SerialBridge(Node):
    def __init__(self):
        super().__init__("serial_bridge")

        self.declare_parameter(
            name="serial_port",
            value="/dev/ttyACM0",
            descriptor=ParameterDescriptor(
                type=ParameterType.PARAMETER_STRING,
                description="Serial port of esp32",
            ),
        )

        self.create_timer(1/100, self.serial_tx)
        self.serial_port = serial.Serial(self.get_parameter("serial_port").get_parameter_value().string_value, 115200)

        self.create_subscription(MecanumCmd, "/wheel_cmd", self.wheel_callback, 10)

        self.encoder_vel_pub = self.create_publisher(MecanumCmd, "/hazmat/encoder_vel", 10)

        self.speeds = MecanumCmd()

    def serial_tx(self):
        try:
            n = 4
            self.serial_port.write(self.packCommand().encode('utf-8'))
            self.get_logger().info(f"Sent command: {self.packCommand()}")
            self.serial_port.flush()
            read = self.serial_port.readline().decode('utf-8')
            self.get_logger().info(f"Serial read: {read}")
            arr = read.replace("\r\n", "").split("|")
            print(arr)
            encoder_vel = MecanumCmd()
            encoder_vel.front_left = int(float(arr[0]))
            encoder_vel.front_right = int(float(arr[1]))
            encoder_vel.rear_left = int(float(arr[2]))
            encoder_vel.rear_right = int(float(arr[3]))
            self.encoder_vel_pub.publish(encoder_vel)
            
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
