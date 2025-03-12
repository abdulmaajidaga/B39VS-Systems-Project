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


def launch_setup(context, *args, **kwargs):

    return [
        LoadComposableNodes(
            composable_node_descriptions=[
                ComposableNode(
                    package="image_proc",
                    plugin="image_proc::RectifyNode",
                    name="rectify_color_node",
                    namespace=namespace,
                    remappings=[
                        ("image", f"{name}/{color_sens_name}/image_raw"),
                        ("camera_info", f"{name}/{color_sens_name}/camera_info"),
                        ("image_rect", f"{name}/{color_sens_name}/image_rect"),
                        (
                            "image_rect/compressed",
                            f"{name}/{color_sens_name}/image_rect/compressed",
                        ),
                        (
                            "image_rect/compressedDepth",
                            f"{name}/{color_sens_name}/image_rect/compressedDepth",
                        ),
                        (
                            "image_rect/theora",
                            f"{name}/{color_sens_name}/image_rect/theora",
                        ),
                    ],
                )
            ],
        ),
        LoadComposableNodes(
            composable_node_descriptions=[
                ComposableNode(
                    package="depth_image_proc",
                    plugin="depth_image_proc::PointCloudXyzrgbNode",
                    name="point_cloud_xyzrgb_node",
                    remappings=[
                        (
                            "depth_registered/image_rect",
                            f"{name}/{stereo_sens_name}/{depth_topic_suffix}",
                        ),
                        (
                            "rgb/image_rect_color",
                            f"{name}/{color_sens_name}/image_rect",
                        ),
                        ("rgb/camera_info", f"{name}/{color_sens_name}/camera_info"),
                        ("points", "/oak/points"),
                    ],
                ),
            ],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="hazmat_vision",
            executable="odom",
            output='screen',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory("depthai_ros_driver"), "launch", "camera.launch.py")
            ),
            launch_arguments={
                "pointcloud.enable": "true",
                "params_file": "", # TODO!
                "parent_frame": "camera_link"
            }
        )
    ])