import rclpy
import math
from rclpy.node import Node
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from hazmat_msgs.msg import MecanumCmd
import tf_transformations as tft
from geometry_msgs.msg import Quaternion


# Define wheel parameters 
wheel_radius = 0.1  # Example value
wheel_separation_width = 0.5  # Example value
wheel_separation_length = 0.5  # Example value

class WheelOdom(Node):
    def __init__(self):
        super().__init__('wheel_odom')  

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
            Odometry, #message type
            "/wheel_odom",  # Topic name
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

        # Publish the updated odometry 
        odom_msg = Odometry()  
        odom_msg.header.frame_id = "map"
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        quat = Quaternion()
        q = tft.quaternion_from_euler(0, 0, self.th)
        quat.x = q[0]
        quat.y = q[1]
        quat.z = q[2]
        quat.w = q[3]
        odom_msg.pose.pose.orientation = quat
        # odom_msg.pose.covariance = [0]
        odom_msg.twist.twist.linear.x = self.vx
        odom_msg.twist.twist.linear.y = self.vy
        odom_msg.twist.twist.angular.z = self.vth
        # odom_msg.twist.covariance = [0]
        print(odom_msg.twist.twist.linear)
        self.wheelcmd_pub.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    node = WheelOdom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()