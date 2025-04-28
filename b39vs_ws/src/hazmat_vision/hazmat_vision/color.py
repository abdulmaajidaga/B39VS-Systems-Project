import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import os
import signal

pid = os.getpid()

class YellowColorDetector(Node):
    def __init__(self):
        super().__init__('yellow_color_detector')
        self.bridge = CvBridge()

        # Define the color range for yellow in HSV
        self.color_dict = {
            "yellow":  ([15, 120, 20], [35, 255, 255]),
            "red": ([125, 120, 20], [179, 255, 255]),
            "green": ([40, 120, 20], [80, 255, 255]),
            "blue": ([95, 120, 20], [125, 255, 255])
        }

        # Subscriber to the camera feed (CameraImage topic)
        self.subscription = self.create_subscription(
            Image,
            '/oak/cam/rgb',
            self.image_callback,
            10
        )
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan_filtered',
            self.scan_callback,
            10
        )

        self.twist_pub = self.create_publisher(Twist, '/hazmat/cmd_vel', 10)

        self.declare_parameter("target_color", "green")

        self.get_logger().info("Color Detector Node has started!")

        self.scan_data = LaserScan()
        self.closest_distance = 1.0
        

    def scan_callback(self, msg: LaserScan):
        scan = msg
        self.scan_data = msg
        # Define the front sector in radians (e.g., -30° to 30°)
        front_sector_min = -math.radians(80)  # -0.5236 rad
        front_sector_max = math.radians(100)   #  0.5236 rad

        # Calculate the index range corresponding to the front sector
        # LaserScan angles: angle = scan.angle_min + index * scan.angle_increment
        start_index = int((front_sector_min - scan.angle_min) / scan.angle_increment)
        end_index = int((front_sector_max - scan.angle_min) / scan.angle_increment)

        # Ensure indices are within valid bounds
        start_index = max(0, start_index)
        end_index = min(len(scan.ranges) - 1, end_index)

        # Extract the ranges within the desired sector and filter valid readings
        front_ranges = [r for r in scan.ranges[start_index:end_index+1]
                        if scan.range_min <= r <= scan.range_max]

        if front_ranges:
            self.closest_distance = min(front_ranges)
            # print("Closest object in front: %.2f m", self.closest_distance)
        else:
            print("No valid range measurements in the front sector.")

    def image_callback(self, msg):
        target_color = self.get_parameter("target_color").value
        try:
            # Convert ROS Image to OpenCV format
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create a mask for yellow color
            mask = cv2.inRange(hsv, np.array(self.color_dict[target_color][0]), np.array(self.color_dict[target_color][1]))

            # Find contours of the yellow areas
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Get the largest contour
                max_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(max_contour) > 500:  # Ignore small noise
                    x, y, w, h = cv2.boundingRect(max_contour)
                    cx, cy = x + w // 2, y + h // 2  # Center coordinates

                    # Draw bounding box and center point
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"({cx}, {cy})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    frame_diff = frame.shape[1] / 2 - cx

                    twsit_msg = Twist()
                    if self.closest_distance > 0.43:
                        # if (abs(frame_diff) >= 80):
                        #     print("tight/left", self.closest_distance)
                        #     if frame_diff < 0:
                        #         twsit_msg.linear.y = -1.0
                        #     else:
                        #         twsit_msg.linear.y = 1.0
                        # # else:
                        print("ahead", self.closest_distance)
                        twsit_msg.linear.x = 0.65
                        self.twist_pub.publish(twsit_msg)
                    else:
                        twsit_msg.linear.x = 0.0
                        self.twist_pub.publish(twsit_msg)
                        os.kill(pid, signal.SIGTERM)
                    

                    # print("image: ", frame.shape[1] / 2, cx, frame_diff)
                    # print("lidar: ", len(self.scan_data.ranges), np.array(self.scan_data.ranges)[178:182])

            # Display the processed frame
            cv2.imshow("Processed Frame", frame)
            cv2.imshow("Mask", mask)

            # Wait for key press to exit (you may need to press 'q' to close the window)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

def main(args=None):
    rclpy.init(args=args)
    yellow_color_detector = YellowColorDetector()

    try:
        rclpy.spin(yellow_color_detector)
    except KeyboardInterrupt:
        pass
    finally:
        yellow_color_detector.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()