import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch_ros.actions import ComposableNodeContainer, LoadComposableNodes, Node
from launch_ros.descriptions import ComposableNode
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    return LaunchDescription([
        # Node for converting Twist commands to individual wheel velocities
        Node(
            package="hazmat_control",
            executable="mecanum",
            output='screen',
        ),

        # Node for micro ROS communication (with ESP)
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['serial',
                       '--dev', '/dev/ttyACM0']
        ),

        # Publishes TF tree from URDF file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(get_package_share_directory("hazmat_bringup"), 'launch'), "/hazmat_state_publisher.launch.py"], 
            )
        ),

        # Start the vision nodes
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(get_package_share_directory("hazmat_vision"), 'launch'), "/vision.launch.py"], 
            ),
        ),

    ])