#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import depthai as dai
from sensor_msgs.msg import Image, Imu, CameraInfo
from cv_bridge import CvBridge
import numpy as np

class OakCamNode(Node):
    def __init__(self):
        super().__init__('oak_cam_node')
        
        # Declare camera and IR parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('confidence_threshold', 230),
                ('min_depth', 500),
                ('max_depth', 6000),
                ('stereo_preset', 'HIGH_ACCURACY'),
                ('lr_check', True),
                ('subpixel', True),
                ('speckle_range', 20),
                ('temporal_alpha', 0.4),
                ('temporal_delta', 10),
                ('spatial_hole_radius', 3),
                ('spatial_iterations', 2),
                ('spatial_alpha', 0.35),
                ('spatial_delta', 15),
                # IR Dot Projector and Flood Light
                ('ir_dot_projector_intensity', 1.0),  # 0..1
                ('ir_flood_light_intensity', 1.0),    # 0..1
            ]
        )
        
        # Get parameters
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.min_depth = self.get_parameter('min_depth').value
        self.max_depth = self.get_parameter('max_depth').value
        self.stereo_preset = self.get_parameter('stereo_preset').value
        self.lr_check = self.get_parameter('lr_check').value
        self.subpixel = self.get_parameter('subpixel').value
        self.speckle_range = self.get_parameter('speckle_range').value
        self.temporal_alpha = self.get_parameter('temporal_alpha').value
        self.temporal_delta = self.get_parameter('temporal_delta').value
        self.spatial_hole_radius = self.get_parameter('spatial_hole_radius').value
        self.spatial_iterations = self.get_parameter('spatial_iterations').value
        self.spatial_alpha = self.get_parameter('spatial_alpha').value
        self.spatial_delta = self.get_parameter('spatial_delta').value
        self.ir_dot_projector_intensity = self.get_parameter('ir_dot_projector_intensity').value
        self.ir_flood_light_intensity = self.get_parameter('ir_flood_light_intensity').value
        
        # Initialize CvBridge
        self.bridge = CvBridge()
        
        # Publishers
        self.rgb_pub = self.create_publisher(Image, '/oak/cam/rgb', 10)
        self.depth_pub = self.create_publisher(Image, '/oak/cam/depth', 10)
        self.imu_pub = self.create_publisher(Imu, '/oak/imu/data', 10)
        self.cam_info_pub = self.create_publisher(CameraInfo, '/oak/cam/info', 10)
        
        # Create DepthAI pipeline
        self.pipeline = dai.Pipeline()
        
        # =======================================
        #         Color Camera Configuration
        # =======================================
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        # Downscale to 640x480 for lower bandwidth; done on-device
        cam_rgb.setPreviewSize(640, 480)
        cam_rgb.setFps(30)
        
        # XLink output node for RGB
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)
        
        # =======================================
        #         Mono / Stereo Configuration
        # =======================================
        mono_left = self.pipeline.create(dai.node.MonoCamera)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setFps(30)
        
        mono_right = self.pipeline.create(dai.node.MonoCamera)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setFps(30)
        
        # StereoDepth node for on-device depth processing
        stereo = self.pipeline.create(dai.node.StereoDepth)
        preset_map = {
            'HIGH_ACCURACY': dai.node.StereoDepth.PresetMode.HIGH_ACCURACY,
            'HIGH_DENSITY': dai.node.StereoDepth.PresetMode.HIGH_DENSITY
        }
        stereo.setDefaultProfilePreset(preset_map[self.stereo_preset])
        stereo.setLeftRightCheck(self.lr_check)
        stereo.setSubpixel(self.subpixel)
        stereo.setConfidenceThreshold(self.confidence_threshold)
        
        # Apply depth post-processing filters on-device
        config = stereo.initialConfig.get()
        config.postProcessing.speckleFilter.enable = True
        config.postProcessing.speckleFilter.speckleRange = self.speckle_range
        
        config.postProcessing.temporalFilter.enable = True
        config.postProcessing.temporalFilter.alpha = self.temporal_alpha
        config.postProcessing.temporalFilter.delta = self.temporal_delta
        
        config.postProcessing.spatialFilter.enable = True
        config.postProcessing.spatialFilter.holeFillingRadius = self.spatial_hole_radius
        config.postProcessing.spatialFilter.numIterations = self.spatial_iterations
        config.postProcessing.spatialFilter.alpha = self.spatial_alpha
        config.postProcessing.spatialFilter.delta = self.spatial_delta
        
        stereo.initialConfig.set(config)
        
        # Link the mono cameras to the stereo node
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)
        
        # Output node for depth
        xout_depth = self.pipeline.create(dai.node.XLinkOut)
        xout_depth.setStreamName("depth")
        stereo.depth.link(xout_depth.input)
        
        # =========================
        #      IMU Configuration
        # =========================
        imu = self.pipeline.create(dai.node.IMU)
        xout_imu = self.pipeline.create(dai.node.XLinkOut)
        xout_imu.setStreamName("imu")
        
        # Enable IMU sensors (accelerometer, gyro, rotation vector) on-device
        imu.enableIMUSensor(
            [
                dai.IMUSensor.ACCELEROMETER,
                dai.IMUSensor.GYROSCOPE_CALIBRATED,
                dai.IMUSensor.ROTATION_VECTOR
            ],
            100
        )
        
        imu.setBatchReportThreshold(1)
        imu.setMaxBatchReports(10)
        
        # Link IMU to output
        imu.out.link(xout_imu.input)
        
        # Start the pipeline on the OAK device
        self.device = dai.Device(self.pipeline)
        
        # Configure IR projectors (on-device)
        # WARNING: Adjust intensities only if you have eye-safety compliance
        self.device.setIrLaserDotProjectorIntensity(self.ir_dot_projector_intensity)
        self.device.setIrFloodLightIntensity(self.ir_flood_light_intensity)
        
        # Create output queues (host side) to retrieve frames/data
        self.q_rgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.q_depth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        self.q_imu = self.device.getOutputQueue(name="imu", maxSize=50, blocking=False)
        
        # Timers for publishing frames and IMU data
        self.create_timer(1/30.0, self.publish_frames)   # ~30 FPS for RGB/depth
        # IMU can arrive up to 100+ Hz; poll frequently
        self.create_timer(1/200.0, self.publish_imu_data)
        
        self.get_logger().info('OAK-CAM Node with IMU (Accel/Gyro/Orientation) initialized on-device.')

        self.cam_info = CameraInfo()
        self.cam_info.distortion_model = "rational_polynomial"
        self.cam_info.width = 1280
        self.cam_info.height = 720
        self.cam_info.header.frame_id = "camera_link"
        self.cam_info.d = [12.394248962402344, 
                        8.096855163574219, 
                        6.784557626815513e-05, 
                        -0.0006477058632299304, 
                        -2.903660297393799, 
                        12.360657691955566, 
                        11.882957458496094, 
                        -3.034278154373169]
        self.cam_info.k = [763.7289428710938,
                        0.0,
                        645.0989990234375,
                        0.0,
                        763.1572265625,
                        342.0258483886719,
                        0.0,
                        0.0,
                        1.0]
        self.cam_info.r = [1.0,
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                        1.0]
        self.cam_info.p = [763.7289428710938,
                        0.0,
                        645.0989990234375,
                        0.0,
                        0.0,
                        763.1572265625,
                        342.0258483886719,
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                        0.0]

    def publish_imu_data(self):
        """
        Retrieve IMU packets from the queue, parse them, and publish 
        a standard sensor_msgs/Imu message with orientation, angular velocity, 
        and linear acceleration if available.
        """
        try:
            imu_data = self.q_imu.get()
            if imu_data is None:
                return
            
            for imu_packet in imu_data.packets:
                imu_msg = Imu()
                imu_msg.header.stamp = self.get_clock().now().to_msg()
                imu_msg.header.frame_id = 'imu_link'
                
                # Default covariance: 0 or fill with -1 for 'unknown'
                imu_msg.orientation_covariance = [0.0]*9
                imu_msg.angular_velocity_covariance = [0.0]*9
                imu_msg.linear_acceleration_covariance = [0.0]*9
                
                has_acc = False
                has_gyro = False
                has_rv = False

                # Accelerometer (m/s^2)
                if imu_packet.acceleroMeter is not None:
                    acc_data = imu_packet.acceleroMeter
                    imu_msg.linear_acceleration.x = acc_data.x
                    imu_msg.linear_acceleration.y = acc_data.y
                    imu_msg.linear_acceleration.z = acc_data.z
                    has_acc = True
                
                # Gyroscope (rad/s)
                if imu_packet.gyroscope is not None:
                    gyro_data = imu_packet.gyroscope
                    imu_msg.angular_velocity.x = gyro_data.x
                    imu_msg.angular_velocity.y = gyro_data.y
                    imu_msg.angular_velocity.z = gyro_data.z
                    has_gyro = True
                
                # Rotation Vector -> Orientation (quaternion)
                if imu_packet.rotationVector is not None:
                    rv = imu_packet.rotationVector
                    imu_msg.orientation.w = rv.real
                    imu_msg.orientation.x = rv.i
                    imu_msg.orientation.y = rv.j
                    imu_msg.orientation.z = rv.k
                    has_rv = True

                # Publish only if we actually received data
                if has_acc or has_gyro or has_rv:
                    self.imu_pub.publish(imu_msg)

        except Exception as e:
            self.get_logger().error(f"Error publishing IMU data: {e}")

    def publish_frames(self):
        """
        Publish RGB and depth frames at ~30Hz.
        """
        try:
            # Get RGB frame (already resized on-device to 640x480)
            rgb_data = self.q_rgb.get()
            if rgb_data is not None:
                rgb_frame = rgb_data.getCvFrame()
                rgb_msg = self.bridge.cv2_to_imgmsg(rgb_frame, encoding="bgr8")
                rgb_msg.header.stamp = self.get_clock().now().to_msg()
                rgb_msg.header.frame_id = "camera_link"
                self.rgb_pub.publish(rgb_msg)
            
            # Get depth frame (in uint16)
            depth_data = self.q_depth.get()
            if depth_data is not None:
                depth_frame = depth_data.getFrame()
                # Clip depth to a desired range
                depth_frame = np.clip(depth_frame, self.min_depth, self.max_depth)
                depth_frame = depth_frame.astype(np.uint16)
                
                depth_msg = self.bridge.cv2_to_imgmsg(depth_frame, encoding="16UC1")
                depth_msg.header.stamp = self.get_clock().now().to_msg()
                depth_msg.header.frame_id = "camera_link"
                self.depth_pub.publish(depth_msg)

            # Publish camera intrinsic parameters
            self.cam_info_pub.publish(self.cam_info)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing frames: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = OakCamNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down OAK-CAM node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
