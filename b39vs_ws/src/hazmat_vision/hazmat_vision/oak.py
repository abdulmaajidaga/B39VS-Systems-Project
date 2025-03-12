import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import open3d as o3d
import numpy as np
from sensor_msgs_py import point_cloud2
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from std_msgs.msg import Header

class PointCloudFilterNode(Node):
    def __init__(self):
        super().__init__('pointcloud_filter_node')

        # Declare parameters (optional)
        self.declare_parameter('input_topic', '/oak/points')
        self.declare_parameter('output_topic', '/filtered_pointcloud')

        # Get parameters
        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        # Create subscriber and publisher
        self.subscription = self.create_subscription(
            PointCloud2,
            input_topic,
            self.process_pointcloud,
            qos_profile=QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                                   durability=DurabilityPolicy.VOLATILE,
                                    history=HistoryPolicy.KEEP_LAST,
                                    depth=5
                                    )
        )
        self.publisher = self.create_publisher(PointCloud2, output_topic, 10)

    def ros_to_open3d(self, pc2_msg):
        """Convert ROS PointCloud2 message to Open3D point cloud."""
        points = []
        for point in point_cloud2.read_points(pc2_msg, skip_nans=True):
            points.append([point[0], point[1], point[2]])
        o3d_pc = o3d.geometry.PointCloud()
        arr = np.array(points)
        print(arr.shape)
        o3d_pc.points = o3d.utility.Vector3dVector(arr)
        return o3d_pc

    def open3d_to_ros(self, o3d_pc, frame_id):
        """Convert Open3D point cloud to ROS PointCloud2 message."""
        points = np.asarray(o3d_pc.points)
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = "oak_rgb_frame"
        pc2_msg = point_cloud2.create_cloud_xyz32(header, points)
        pc2_msg.header.frame_id = frame_id
        return pc2_msg

    def process_pointcloud(self, pc2_msg):
        """Callback function for processing incoming PointCloud2 messages."""
        # Convert ROS PointCloud2 to Open3D PointCloud
        o3d_pc = self.ros_to_open3d(pc2_msg)

        # Apply Statistical Outlier Removal filter
        cl, ind = o3d_pc.remove_statistical_outlier(nb_neighbors=20, std_ratio=1.0)
        filtered_pc = o3d_pc.select_by_index(ind)

        # Convert filtered Open3D PointCloud back to ROS PointCloud2
        filtered_pc2_msg = self.open3d_to_ros(filtered_pc, pc2_msg.header.frame_id)

        # Publish the filtered point cloud
        print("publishing...z")
        self.publisher.publish(filtered_pc2_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFilterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()