import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseArray, Pose
import cv_bridge
import cv2
import numpy as np
import tf_transformations as tft

class ArucoNode(Node):
    def __init__(self):
        super().__init__("aruco_node")
        # Subscibe to camera image and info topic
        self.sub = self.create_subscription(Image, "/oak/rgb/image_raw", self.camera_cb, 10)
        self.info_sub = self.create_subscription(CameraInfo, "/oak/rgb/camera_info", self.cam_info_callback, 10)
        self.aruco_pose_pub = self.create_publisher(PoseArray, "/markers", 10)

        self.info_msg = None
        self.intrinsic_mat = None
        self.distortion_vec = None

        # Class for CvBridge to convert between opencv and ROS images
        self.cvBridge = cv_bridge.CvBridge()

        self.aruco_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
        self.aruco_parameters = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dictionary, self.aruco_parameters)

        self.objPoints = np.zeros((4, 3), dtype=float)
        self.markerLength = 0.1
        self.objPoints[0] = (-self.markerLength/2, self.markerLength/2, 0)
        self.objPoints[1] = (self.markerLength/2, self.markerLength/2, 0)
        self.objPoints[2] = (self.markerLength/2, -self.markerLength/2, 0)
        self.objPoints[3] = (-self.markerLength/2, -self.markerLength/2, 0)

    def cam_info_callback(self, info_msg):
        self.info_msg = info_msg
        self.intrinsic_mat = np.reshape(np.array(self.info_msg.k), (3, 3))
        self.distortion_vec = np.array(self.info_msg.d)
        # Assume that camera parameters will remain the same...
        self.destroy_subscription(self.info_sub)
        
    def camera_cb(self, msg):
        cvImg = self.cvBridge.imgmsg_to_cv2(msg, "mono8")

        pose_array = PoseArray()
        pose_array.header.frame_id = "oak-d-base-frame"

        corners, marker_ids, rejected = self.aruco_detector.detectMarkers(cvImg)

        if marker_ids is not None:

            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.markerLength, self.intrinsic_mat, self.distortion_vec
            )

            for i, marker_id in enumerate(marker_ids):

                pose = Pose()
                pose.position.x = tvecs[i][0][0]
                pose.position.y = tvecs[i][0][1]
                pose.position.z = tvecs[i][0][2]
                print(i)

                rot_matrix = np.eye(4)
                rot_matrix[0:3, 0:3] = cv2.Rodrigues(np.array(rvecs[i][0]))[0]
                quat = tft.quaternion_from_matrix(rot_matrix)

                pose.orientation.x = quat[0]
                pose.orientation.y = quat[1]
                pose.orientation.z = quat[2]
                pose.orientation.w = quat[3]

                pose_array.poses.append(pose)

        self.aruco_pose_pub.publish(pose_array)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()