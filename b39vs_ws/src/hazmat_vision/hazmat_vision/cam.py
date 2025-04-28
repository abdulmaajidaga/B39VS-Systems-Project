import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class VideoCaptureNode(Node):
    def __init__(self):
        super().__init__('video_capture_node')
        
        # Create a VideoCapture object to read from the webcam (0 is the default camera)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not self.cap.isOpened():
            self.get_logger().error("Could not open video device")
            return
        
        # Create a CvBridge instance to convert OpenCV images to ROS messages
        self.bridge = CvBridge()
        
        # Create a publisher for the RGB image topic
        self.image_pub = self.create_publisher(Image, '/image_raw', 10)
        
        # Set a timer to periodically capture and publish frames
        self.timer = self.create_timer(1 / 10, self.timer_callback)  # 10 Hz
    
    def timer_callback(self):
        # Capture a frame from the video feed
        ret, frame = self.cap.read()
        
        if not ret:
            self.get_logger().warn("Failed to capture frame")
            return
        
        # Convert the frame from BGR (OpenCV format) to RGB (ROS format)
        frame = frame[0:720, 2560 // 2:  2560]
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert the RGB frame to a ROS Image message
        ros_image = self.bridge.cv2_to_imgmsg(rgb_image, encoding='rgb8')
        
        # Publish the Image message
        self.image_pub.publish(ros_image)
        self.get_logger().info('Publishing frame')

    def __del__(self):
        # Release the video capture when the node is destroyed
        if self.cap.isOpened():
            self.cap.release()


def main(args=None):
    rclpy.init(args=args)
    video_capture_node = VideoCaptureNode()
    rclpy.spin(video_capture_node)
    video_capture_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
