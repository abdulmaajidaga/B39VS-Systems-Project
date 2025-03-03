import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import cv_bridge
import cv2
import numpy as np
import depthai as dai

class OakNode(Node):
    def __init__(self):
        super().__init__("oak_node")
        self.logger = self.get_logger()
        
        # Publishers for raw camera data
        self.rgb_pub = self.create_publisher(Image, "/camera/rgb", 10)
        self.depth_pub = self.create_publisher(Image, "/camera/depth", 10)
        self.cam_info_pub = self.create_publisher(CameraInfo, "/cam_info", 10)

        # Class for CvBridge to convert between opencv and ROS images
        self.cvBridge = cv_bridge.CvBridge()

        pipeline = dai.Pipeline()

        rgb_cam = pipeline.create(dai.node.Camera)
        rgb_cam.setImageOrientation(dai.CameraImageOrientation.VERTICAL_FLIP)
        rgb_cam.setSize(640, 480)
        rgb_cam.setFps(30)
        vidOut = pipeline.create(dai.node.XLinkOut)
        vidOut.setStreamName("video")
        rgb_cam.video.link(vidOut.input)
        

        device = dai.Device(pipeline)
        
        self.rgb_queue = device.getOutputQueue("video", 1, False)

        self.create_timer(1 / 30.0, self.publish_frames)


    def publish_frames(self):
        try:
            data = self.rgb_queue.get()
            if data is not None:
                img = data.getCvFrame()
                img_msg = self.cvBridge.cv2_to_imgmsg(img, "bgr8")
                img_msg.header.frame_id = "oak_rgb_frame"
                img_msg.header.stamp = self.get_clock().now().to_msg()
                self.rgb_pub.publish(img_msg)

        except Exception as e:
            self.logger.error(f"Error in publishing rgb/depth frame {e}")
        
    

def main(args=None):
    rclpy.init(args=args)
    node = OakNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()