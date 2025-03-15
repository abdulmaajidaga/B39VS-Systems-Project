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
    print(os.path.join(get_package_share_directory("depthai_ros_driver"), 'launch'))
    config_dir = os.path.join(get_package_share_directory('hazmat_vision'), 'config')

    return LaunchDescription([
        # Node for publish wheel encoder odometry
        Node(
            package="hazmat_vision",
            executable="odom",
            output='screen',
        ),
        
        # Cartographer occupancy grid publisher
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            arguments=['-resolution', '0.05',
                       '-publish_period_sec', '1.0']
        ),
        # # Cartographer SLAM node
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            # output='screen',
            arguments=['-configuration_directory', config_dir,
                       '-configuration_basename', "carto_oak.lua"],
            remappings=[
                ("points2", "oak/points"),
                ("imu", "oak/imu/data")
            ]
        ),
       
        # Launching the rplidar A3
        # Node(
        #     package='sllidar_ros2',
        #     executable='sllidar_node',
        #     name='sllidar_node',
        #     output='screen',
        #     parameters=[{'channel_type':"serial",
        #                  'serial_port': "/dev/ttyUSB0", 
        #                  'serial_baudrate': 256000, 
        #                  'frame_id': "laser",
        #                  'inverted': "false",
        #                  'angle_compensate': "true", 
        #                  'scan_mode': "Sensitivity"}],
        #     ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(get_package_share_directory("sllidar_ros2"), 'launch'), "/sllidar_a3_launch.py"], 
            ),
            launch_arguments={
                "frame_id": "scan_link"
            }.items()
        ),

        # Start the OAK camera
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(get_package_share_directory("depthai_ros_driver"), 'launch'), "/camera.launch.py"], 
            ),
            launch_arguments={
                "pointcloud.enable": "true",
                "params_file": os.path.join(config_dir, "params.yaml"),
                "parent_frame": "camera_link"
            }.items()
        ),

    ])