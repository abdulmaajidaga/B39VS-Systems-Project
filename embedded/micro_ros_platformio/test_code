#include <Arduino.h>
#include <Wire.h>
#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>
#include <sensor_msgs/msg/joint_state.h>
#include <hazmat_msgs/msg/mecanum_cmd.h>
#include "mecanum.h"
#include <Adafruit_PWMServoDriver.h>

#if !defined(MICRO_ROS_TRANSPORT_ARDUINO_SERIAL)
#error This example is only available for Arduino framework with serial transport.
#endif

// Motor objects
mecanum m1, m2, m3, m4;
int m1s = 0, m2s = 0, m3s = 0, m4s = 0;

// Motor Driver (Bank A) - ESP32 Pin Assignments
#define ENA1 17
#define IN1_1 8
#define IN2_1 18
#define ENB1 11
#define IN3_2 9
#define IN4_2 10

// Motor Driver (Bank B) - ESP32 Pin Assignments
#define ENA2 2
#define IN1_3 6
#define IN2_3 5
#define ENB2 16
#define IN3_4 7
#define IN4_4 15

// Encoder Connections (ESP32 Pins)
#define ENC1_A 21
#define ENC1_B 20
#define ENC2_A 45
#define ENC2_B 0
#define ENC3_A 35
#define ENC3_B 38
#define ENC4_A 47
#define ENC4_B 48

Adafruit_PWMServoDriver PWM = Adafruit_PWMServoDriver(0x40);
int currentAngle3 = 90;  // Store the last angle for Servo 3
// Declare the moveToAngle3 function to fix the scope error
void moveToAngle3(int targetAngle);

#define I2C_SDA 20 
#define I2C_SCL 19

#define SERVO1_MIN 120   // Servo 1 range (0-270°)
#define SERVO1_MAX 470  
#define SERVO2_MIN 120   // Servo 2 range (0-270°)
#define SERVO2_MAX 470  
#define SERVO3_NEUTRAL 340  
#define SERVO3_CW 470       
#define SERVO3_CCW 210      
#define SERVO4_MIN 120   // Servo 4 range (0-270°)
#define SERVO4_MAX 470 

#define ANALOG1_PIN 3
#define ANALOG2_PIN 12
#define ANALOG3_PIN 13
#define ANALOG4_PIN 14

// ROS2 objects
rcl_timer_t timer;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

rcl_publisher_t mecanum_publisher;
rcl_subscription_t mecanum_subscriber;
rcl_publisher_t joint_publisher;
rcl_subscription_t joint_subscriber;

hazmat_msgs__msg__MecanumCmd mecanum_recv_msg;
hazmat_msgs__msg__MecanumCmd mecanum_msg;

sensor_msgs__msg__JointState joint_cmd_msg;
sensor_msgs__msg__JointState joint_state_msg;

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();} }
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){} }

void error_loop() {
  while (1) {
    delay(100);
  }
}

// Timer callback for publishing encoder speeds
void timer_callback(rcl_timer_t *timer, int64_t last_call_time) {
  RCLC_UNUSED(last_call_time);

  if (timer != NULL) {
    mecanum_msg.front_left = m1.get_speed_enc();
    mecanum_msg.front_right = m2.get_speed_enc();
    mecanum_msg.rear_left = m3.get_speed_enc();
    mecanum_msg.rear_right = m4.get_speed_enc();

    RCSOFTCHECK(rcl_publish(&mecanum_publisher, &mecanum_msg, NULL));

    // Read analog values and map them to joint positions
    int analogValue1 = analogRead(ANALOG1_PIN);
    int analogValue2 = analogRead(ANALOG2_PIN);
    int analogValue3 = analogRead(ANALOG3_PIN);
    int analogValue4 = analogRead(ANALOG4_PIN);

    joint_state_msg.position.data[0] = map(analogValue1, 250, 2203, 0, 195);
    joint_state_msg.position.data[1] = map(analogValue2, 250, 2203, 0, 195);
    joint_state_msg.position.data[2] = map(analogValue3, 343, 3006, 0, 180);
    joint_state_msg.position.data[3] = map(analogValue4, 250, 2203, 0, 195);

    // Publish the joint state message
    RCSOFTCHECK(rcl_publish(&joint_publisher, &joint_state_msg, NULL));
  }
}

// Mecanum command subscription callback
void mecanum_subscription_callback(const void *msgin) {
  const hazmat_msgs__msg__MecanumCmd *msg = (const hazmat_msgs__msg__MecanumCmd *)msgin;

  m1s = msg->front_left;
  m2s = msg->front_right;
  m3s = msg->rear_left;
  m4s = msg->rear_right;

  m1.set_power(m1s);
  m2.set_power(m2s);
  m3.set_power(m3s);
  m4.set_power(m4s);
}

void joint_cmd_callback(const void *msgin) {
    const sensor_msgs__msg__JointState *msg = (const sensor_msgs__msg__JointState *)msgin;

    int angle1 = (int)msg->position.data[0];
    int angle2 = (int)msg->position.data[1];
    int angle3 = (int)msg->position.data[2];
    int angle4 = (int)msg->position.data[3];


    if (angle1 >= 15 && angle1 <= 152 && angle2 >= 0 && angle2 <= 270 &&
        angle3 >= 0 && angle3 <= 360 && angle4 >= 0 && angle4 <= 196) {
        
        int pulse1 = map(angle1, 0, 270, SERVO1_MIN, SERVO1_MAX);
        int pulse2 = map(angle2, 0, 270, SERVO2_MIN, SERVO2_MAX);
        int pulse4 = map(angle4, 0, 270, SERVO4_MIN, SERVO4_MAX);

        // Servo 3 Handling
        moveToAngle3(angle3);

        PWM.setPWM(0, 0, pulse1);
        PWM.setPWM(1, 0, pulse2);
        PWM.setPWM(3, 0, pulse4);
    }
}

void setup() {
  Serial.begin(115200);

  Wire.begin(I2C_SDA, I2C_SCL);
  PWM.begin();
  PWM.setPWMFreq(50);

  m1.attach(ENA1, IN1_1, IN2_1, ENC1_A, ENC1_B);
  m2.attach(ENB1, IN4_2, IN3_2, ENC2_A, ENC2_B);
  m3.attach(ENA2, IN1_3, IN2_3, ENC3_A, ENC3_B);
  m4.attach(ENB2, IN4_4, IN3_4, ENC4_A, ENC4_B);

  set_microros_serial_transports(Serial);
  delay(2000);

  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "mecanum_node", "", &support));

  RCCHECK(rclc_publisher_init_default(&mecanum_publisher, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd), "hazmat/encoder_vel"));
  RCCHECK(rclc_subscription_init_default(&mecanum_subscriber, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd), "/hazmat/wheel_cmd"));
  RCCHECK(rclc_publisher_init_default(&joint_publisher, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, JointState), "arm/joint_state"));
  RCCHECK(rclc_subscription_init_default(&joint_subscriber, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, JointState), "arm/joint_cmd"));


  const unsigned int timer_timeout = 100;
  RCCHECK(rclc_timer_init_default(&timer, &support, RCL_MS_TO_NS(timer_timeout), timer_callback));

  RCCHECK(rclc_executor_init(&executor, &support.context, 2, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  mecanum_msg.front_left = 0;
  mecanum_msg.front_right = 0;
  mecanum_msg.rear_left = 0;
  mecanum_msg.rear_right = 0;

  double joint_positions[4] = {0, 0, 0, 0};
  joint_state_msg.position.data = joint_positions;
  joint_state_msg.position.size = 4;
  joint_state_msg.position.capacity = 4;
  

  RCCHECK(rclc_executor_add_subscription(&executor, &mecanum_subscriber, &mecanum_recv_msg, &mecanum_subscription_callback, ON_NEW_DATA));
  RCCHECK(rclc_executor_add_subscription(&executor, &joint_subscriber, &joint_cmd_msg, &joint_cmd_callback, ON_NEW_DATA));
}

void loop() {
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10)));
  delay(10);
}

void moveToAngle3(int targetAngle) {
    int angleDifference = targetAngle - currentAngle3;
    int moveDuration = map(abs(angleDifference), 0, 360, 0, 1000);

    if (angleDifference > 0) {
        PWM.setPWM(2, 0, SERVO3_CW);
    } 
    else if (angleDifference < 0) {
        PWM.setPWM(2, 0, SERVO3_CCW);
    }

    delay(moveDuration);
    PWM.setPWM(2, 0, SERVO3_NEUTRAL);
    currentAngle3 = targetAngle;
}
