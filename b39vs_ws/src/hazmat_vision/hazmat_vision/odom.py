import rclpy
import math
from rclpy.node import Node
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty
from hazmat_msgs.msg import MecanumCmd

# Define wheel parameters (update these values as needed)
wheel_radius = 0.1  # Example value
wheel_separation_width = 0.5  # Example value
wheel_separation_length = 0.5  # Example value

class WheelOdom(Node):
    def __init__(self):
        super().__init__('wheel_odom')  # Initialize the Node with a name

        # Define the positions
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0

        # Define the velocities
        self.vx = 0.0
        self.vy = 0.0
        self.vth = 0.0

        # Initialize time
        self.time = self.get_clock().now()

        # Create a subscriber for encoder velocities
        self.create_subscription(
            MecanumCmd,
            "/hazmat/encoder_vel",  # Topic name
            self.encoder_callback,  # Callback function
            10  # Queue size
        )

        # Create a publisher for wheel odometry
        self.wheelcmd_pub = self.create_publisher(
            Odometry,  # Replace with the correct message type (e.g., Odometry)
            "/wheel_cmd",  # Topic name
            10  # Queue size
        )

    def rpm_to_aps(self, rpm):
        # Convert RPM to angular velocity in radians per second (APS)
        return rpm * (2 * math.pi) / 60

    def encoder_callback(self, msg):
        # Get the current time
        new_time = self.get_clock().now()

        # Example RPM values (replace with actual values from the message)
        rpm_front_left = 0.0
        rpm_front_right = 0.0
        rpm_rear_left = 0.0
        rpm_rear_right = 0.0

        # Convert RPM to angular velocities
        v_front_left = self.rpm_to_aps(rpm_front_left)
        v_front_right = self.rpm_to_aps(rpm_front_right)
        v_rear_left = self.rpm_to_aps(rpm_rear_left)
        v_rear_right = self.rpm_to_aps(rpm_rear_right)

        # Compute the velocities through forward kinematics
        self.vx = (v_front_left + v_front_right + v_rear_left + v_rear_right) * wheel_radius / 4
        self.vy = (-v_front_left + v_front_right + v_rear_left - v_rear_right) * wheel_radius / 4
        self.vth = (-v_front_left + v_front_right - v_rear_left + v_rear_right) * wheel_radius / (4 * (wheel_separation_width + wheel_separation_length))

        # Calculate time difference
        dt = (new_time - self.time).nanoseconds / 1e9  # Convert to seconds
        self.time = new_time

        # Update position
        delta_x = (self.vx * math.cos(self.th) - (self.vy * math.sin(self.th))) * dt
        delta_y = (self.vx * math.sin(self.th) + (self.vy * math.cos(self.th))) * dt
        delta_th = self.vth * dt

        self.x += delta_x
        self.y += delta_y
        self.th += delta_th

        # Publish the updated odometry (replace with the correct message type)
        odom_msg = Odometry()  
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
     #   odom_msg.pose.pose.position.th = self.th
      #  odom_msg.pose.pose.position.vx = self.vx
       # odom_msg.pose.pose.position.vy = self.vy
        #odom_msg.pose.pose.position.vth = self.vth
        self.wheelcmd_pub.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    node = WheelOdom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()