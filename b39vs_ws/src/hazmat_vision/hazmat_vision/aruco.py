import rclpy
from sensor_msgs.msg import CompressedImage
import cv_bridge

class ArucoNode(rclpy.Node):
    def __init__(self):
        # Class for CvBridge to convert between opencv and ROS images
        self.cvBridge = cv_bridge.CvBridge()

        # Subscibe to camera topic
        self.sub = self.create_subscription(CompressedImage, "/camera/color/image/compressed", self.camera_cb)

        
    def camera_cb(self, msg):
        cvImg = self.cvBridge.compressed_imgmsg_to_cv2(msg)

if __name__ == '__main__':
    node = ArucoNode()
    rclpy.spin(node)