import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
from operator import itemgetter
import time

class YellowColorDetector(Node):
    def __init__(self):
        super().__init__('arm')
        self.bridge = CvBridge()

        # Define the color range for yellow in HSV
        self.color_dict = {
            "yellow":  ([15, 120, 120], [35, 255, 255]),
            "red": ([125, 120, 20], [179, 255, 255]),
            "green": ([40, 70, 20], [80, 255, 255]),
            "blue": ([95, 120, 20], [125, 255, 255]),
            "purple": ([125, 60, 20], [175, 255, 255])
        }

        # Subscriber to the camera feed (CameraImage topic)
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        self.join_pub = self.create_publisher(
            JointState,
            '/joint_target',
            10
        )

        self.get_logger().info("Arm commander has started.")

        self.base_angle = 180.0

        self.neutral_position = [self.base_angle, 20.0, 80.0, 0.0]
        self.joint_msg = JointState()
        self.joint_msg.position = self.neutral_position
        self.join_pub.publish(self.joint_msg)

        self.stationary_counter = 0

    def move_base(self, angle):
        self.base_angle = min(max(0.0, angle), 180.0)
        self.joint_msg.position = [self.base_angle, 20.0, 80.0, 0.0]
        self.join_pub.publish(self.joint_msg)

    def pickup_obj(self):
        self.joint_msg.position = [self.base_angle, 85.0, 55.0, 0.0]
        self.join_pub.publish(self.joint_msg)
        time.sleep(1)
        self.joint_msg.position = [self.base_angle, 85.0, 55.0, 30.0]
        self.join_pub.publish(self.joint_msg)
        time.sleep(1)
        self.joint_msg.position = [self.base_angle, 20.0, 80.0, 30.0]
        self.join_pub.publish(self.joint_msg)
        time.sleep(1)

        
    def image_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV format
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create a mask for yellow color
            mask = cv2.inRange(hsv, np.array(self.color_dict["green"][0]), np.array(self.color_dict["green"][1])) + cv2.inRange(hsv, np.array(self.color_dict["yellow"][0]), np.array(self.color_dict["yellow"][1]))

            # Find contours of the yellow areas
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            regions = []

            if contours:
                # Get the largest contour
                for c in contours:
                    if cv2.contourArea(c) > 500:
                        x, y, w, h = cv2.boundingRect(c)
                        cx, cy = x + w // 2, y + h // 2  # Center coordinates
                        regions.append([cx, cy])
                        print(regions)

                        # Draw bounding box and center point
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                        cv2.putText(frame, f"({cx}, {cy})", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                        
                    

                    # print("image: ", frame.shape[1] / 2, cx, frame_diff)
                    # print("lidar: ", len(self.scan_data.ranges), np.array(self.scan_data.ranges)[178:182])

            if (len(regions) == 3):
                yellow_bounds = max(regions, key=itemgetter(1))
                regions.remove(yellow_bounds)
                right_finger = max(regions, key=itemgetter(0))
                regions.remove(right_finger)
                left_finger = regions[0]
                arm_centre = (right_finger[0] + left_finger[0]) // 2
                diff = yellow_bounds[0] - arm_centre
                if (abs(diff) > 25):
                    self.stationary_counter = 0
                    if (diff < 0):
                        self.move_base(self.base_angle + 1.0)
                        print("moving left", diff)
                    else:
                        self.move_base(self.base_angle - 1.0)
                        print("moving right", diff)
                else:    
                    print(yellow_bounds[0], arm_centre, left_finger, right_finger)
                    self.stationary_counter += 1
                    print(self.stationary_counter)
                    if (self.stationary_counter == 5):
                        # Do pickup
                        # print("nnigga")
                        self.pickup_obj()




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