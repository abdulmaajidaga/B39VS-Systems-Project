from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Joy node for gettinng joystick inputs
        Node(
            package="joy",
            executable="joy_node",
            output='screen',
        ),

        # Teleop node for converting joystick commands to Twist messages
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            output='screen',
            parameters=[{
                "axis_linear.x": 1,
                "axis_linear.y": 0,
                "scale_linear.x": 3.0,
                "scale_linear.y": 3.0, 
                "scale_angular.yaw": 3.0,
                "require_enable_button": False
            }],
            remappings=[("/cmd_vel", "/hazmat/cmd_vel")]
        )
    ])