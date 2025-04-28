import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from adafruit_servokit import ServoKit

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')
        
        self.subscription = self.create_subscription(
            JointState,
            '/joint_target',
            self.joint_callback,
            10
        )

        self.get_logger().info("Arm controller has started!")

        self.kit = ServoKit(channels=16)
        
    def joint_callback(self, msg: JointState):
        self.kit.servo[0].angle = msg.position[0]
        self.kit.servo[1].angle = msg.position[1]
        self.kit.servo[2].angle = msg.position[2]
        self.kit.servo[3].angle = msg.position[3]
        

def main(args=None):
    rclpy.init(args=args)
    arm_controller = ArmController()

    try:
        rclpy.spin(arm_controller)
    except KeyboardInterrupt:
        pass
    finally:
        arm_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()