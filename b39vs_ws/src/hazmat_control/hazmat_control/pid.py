import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from hazmat_msgs.msg import MecanumCmd
import time

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, setpoint, actual):
        # Calculate error
        error = setpoint - actual

        # Proportional term
        p_term = self.kp * error

        # Integral term
        self.integral += error
        i_term = self.ki * self.integral

        # Derivative term
        d_term = self.kd * (error - self.previous_error)

        # Update previous error for next iteration
        self.previous_error = error

        # PID output (velocity adjustment)
        return p_term + i_term + d_term

class MecanumControllerNode(Node):
    def __init__(self):
        super().__init__('mecanum_controller_node')

        # PID Controllers for each wheel
        self.pid_fl = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.pid_fr = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.pid_rl = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.pid_rr = PIDController(kp=1.0, ki=0.1, kd=0.05)

        # Publisher for the wheel velocities
        self.publisher_ = self.create_publisher(MecanumCmd, "/hazmat/wheel_cmd", 10)

        # Subscriber for the current wheel velocities
        self.create_subscription(MecanumCmd, '/hazmat/wheel_cmd_raw', self.velocities_callback, 10)

        # Target velocities (setpoint)
        self.target_fl = 0
        self.target_fr = 0
        self.target_rl = 0
        self.target_rr = 0

        self.timer = self.create_timer(0.1, self.control_loop)  # control loop every 100ms

    def velocities_callback(self, msg):
        # Update current velocities from the sensor or feedback system
        self.current_fl = msg.front_left
        self.current_fr = msg.front_right
        self.current_rl = msg.rear_left
        self.current_rr = msg.rear_right

    def control_loop(self):
        # Compute PID adjustments for each wheel
        fl_adjustment = self.pid_fl.compute(self.target_fl, self.current_fl)
        fr_adjustment = self.pid_fr.compute(self.target_fr, self.current_fr)
        rl_adjustment = self.pid_rl.compute(self.target_rl, self.current_rl)
        rr_adjustment = self.pid_rr.compute(self.target_rr, self.current_rr)

        # Apply adjustments to the target velocities
        adjusted_fl = int(self.target_fl + fl_adjustment)
        adjusted_fr = int(self.target_fr + fr_adjustment)
        adjusted_rl = int(self.target_rl + rl_adjustment)
        adjusted_rr = int(self.target_rr + rr_adjustment)

        # Publish adjusted velocities
        msg = MecanumCmd()
        msg.front_left = adjusted_fl
        msg.front_right = adjusted_fr
        msg.rear_left = adjusted_rl
        msg.rear_right = adjusted_rr

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg}')

def main(args=None):
    rclpy.init(args=args)
    mecanum_controller_node = MecanumControllerNode()
    rclpy.spin(mecanum_controller_node)
    mecanum_controller_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
