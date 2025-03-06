#include <Arduino.h>
#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>
#include <hazmat_msgs/msg/mecanum_cmd.h>
#include "mecanum.h"

// Ensure that the transport layer being used is Arduino Serial.
// If it's not, compilation is stopped and error is printed.
#if !defined(MICRO_ROS_TRANSPORT_ARDUINO_SERIAL)
#error This example is only available for Arduino framework with serial transport.
#endif

// Motor objects for controlling mecanum wheels
mecanum m1;
mecanum m2;
mecanum m3;
mecanum m4;
int m1s = 0, m2s = 0, m3s = 0, m4s = 0;

// Motor Driver (Bank A) - ESP32 Pin Assignments
#define ENA1 17
#define IN1_1 8
#define IN2_1 18
#define ENB1 11
#define IN3_2 9
#define IN4_2 10

// Motor Driver (Bank B) - ESP32 Pin Assignments
#define ENA2 4
#define IN1_3 6
#define IN2_3 5
#define ENB2 16
#define IN3_4 7
#define IN4_4 15

// Encoder Connections (ESP32 Pins)
#define ENC1_A 40 // Orange 35
#define ENC1_B 39 // Green 36
#define ENC2_A 41 // Orange 47
#define ENC2_B 42 // Green 48
#define ENC3_A 38 // Orange 41
#define ENC3_B 37 // Green 42
#define ENC4_A 35 // Orange 14
#define ENC4_B 36 // Green 13

// Encoder pulse counters
volatile int pulseCount1 = 0, pulseCount2 = 0, pulseCount3 = 0, pulseCount4 = 0;

// Define ROS2 objects
rcl_timer_t timer;

// rcl_publisher_t publisher;
// std_msgs__msg__Int32 msg;

// rcl_subscription_t subscriber;
// std_msgs__msg__Int32 recv_msg;

rcl_subscription_t mecanum_subscriber;
hazmat_msgs__msg__MecanumCmd mecanum_recv_msg;

rcl_publisher_t mecanum_publisher;
hazmat_msgs__msg__MecanumCmd mecanum_msg;

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

// Macros for checking return of ROS2 functions
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// Function to calculate RPM (adjusted for your motor's encoder PPR)
// float calculateRPM(volatile int &pulseCount) {
//   int pulsesPerRevolution = 150; // Adjust based on your motor specs
//   float rpm = (pulseCount / (float)pulsesPerRevolution); // Convert to RPM
//   pulseCount = 0; // Reset pulse count for next cycle
//   return rpm;
// }

void stopMotors() {
  digitalWrite(ENA1, LOW); digitalWrite(ENB1, LOW);
  digitalWrite(ENA2, LOW); digitalWrite(ENB2, LOW);
}

// // Interrupt service routines (ISR) for encoders
// void IRAM_ATTR enc1_ISR() {
//   if (digitalRead(ENC1_B) == HIGH) pulseCount1++; // Forward
//   else pulseCount1--; // Backward
// }

// void IRAM_ATTR enc2_ISR() {
//   if (digitalRead(ENC2_B) == HIGH) pulseCount2++;
//   else pulseCount2--;
// }

// void IRAM_ATTR enc3_ISR() {
//   if (digitalRead(ENC3_B) == HIGH) pulseCount3++;
//   else pulseCount3--;
// }

// void IRAM_ATTR enc4_ISR() {
//   if (digitalRead(ENC4_B) == HIGH) pulseCount4++;
//   else pulseCount4--;
// }

// Infinite error loop function
void error_loop() {
  while(1) {
    delay(100);
  }
}

// Timer callback function - publishes regular updates
void timer_callback(rcl_timer_t * timer, int64_t last_call_time) {
  RCLC_UNUSED(last_call_time);
  if (timer != NULL) {
    // Update message values before publishing
    // msg.data++;
    
    // Update mecanum message with current motor speeds and encoder readings
    mecanum_msg.front_left = m1.get_speed_enc();
    mecanum_msg.front_right = m2.get_speed_enc();
    mecanum_msg.rear_left = m3.get_speed_enc();
    mecanum_msg.rear_right = m4.get_speed_enc();
    
    
    // Publish our messages
    // RCSOFTCHECK(rcl_publish(&publisher, &msg, NULL));
    RCSOFTCHECK(rcl_publish(&mecanum_publisher, &mecanum_msg, NULL));
  }
}

// Standard Int32 subscription calmecanum_vellback
// void subscription_callback(const void * msgin)
// {
//   const std_msgs__msg__Int32 * msg = (const std_msgs__msg__Int32 *)msgin;
//   printf("Received: %d\n", msg->data);
// }

// Mecanum command subscription callback - updates motor speeds
void mecanum_subscription_callback(const void * msgin)
{
  const hazmat_msgs__msg__MecanumCmd * msg = (const hazmat_msgs__msg__MecanumCmd *)msgin;
  printf("Received mecanum cmd: %d %d %d %d\n", 
         msg->front_left, msg->front_right, 
         msg->rear_left, msg->rear_right);
         
  // Update motor speeds from received command
  m1s = msg->front_left;
  m2s = msg->front_right;
  m3s = msg->rear_left;
  m4s = msg->rear_right;
  
  // Apply the new speeds to the motors
  m1.set_power(m1s);
  m2.set_power(m2s);
  m3.set_power(m3s);
  m4.set_power(m4s);
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize motor controllers
  m1.attach(ENA1, IN1_1, IN2_1, ENC1_A, ENC1_B);
  m2.attach(ENB1, IN4_2, IN3_2, ENC2_A, ENC2_B);
  m3.attach(ENA2, IN1_3, IN2_3, ENC3_A, ENC3_B);
  m4.attach(ENB2, IN4_4, IN3_4, ENC4_A, ENC4_B);
 
  // // Set encoder pins as inputs
  // pinMode(ENC1_A, INPUT_PULLUP); pinMode(ENC1_B, INPUT_PULLUP);
  // pinMode(ENC2_A, INPUT_PULLUP); pinMode(ENC2_B, INPUT_PULLUP);
  // pinMode(ENC3_A, INPUT_PULLUP); pinMode(ENC3_B, INPUT_PULLUP);
  // pinMode(ENC4_A, INPUT_PULLUP); pinMode(ENC4_B, INPUT_PULLUP);
  
  // // Attach interrupts for encoder readings
  // attachInterrupt(digitalPinToInterrupt(ENC1_A), enc1_ISR, RISING);
  // attachInterrupt(digitalPinToInterrupt(ENC2_A), enc2_ISR, RISING);
  // attachInterrupt(digitalPinToInterrupt(ENC3_A), enc3_ISR, RISING);
  // attachInterrupt(digitalPinToInterrupt(ENC4_A), enc4_ISR, RISING);
  
  // Setup micro-ROS
  set_microros_serial_transports(Serial);
  delay(2000);

  // Initialize ROS node and communications
  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "mecanum_node", "", &support));

  // Initialize publishers
  // RCCHECK(rclc_publisher_init_default(
  //   &publisher,
  //   &node,
  //   ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
  //   "/meow"));

  RCCHECK(rclc_publisher_init_default(
    &mecanum_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "hazmat/encoder_vel"));
    
  // Initialize timer for regular updates
  const unsigned int timer_timeout = 100; // Update at 10Hz instead of 1Hz for more responsive feedback
  RCCHECK(rclc_timer_init_default(
    &timer,
    &support,
    RCL_MS_TO_NS(timer_timeout),
    timer_callback));

  // Initialize executor
  RCCHECK(rclc_executor_init(&executor, &support.context, 3, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  // Initialize message data
  // msg.data = 0;
  mecanum_msg.front_left = 0;
  mecanum_msg.front_right = 0;
  mecanum_msg.rear_left = 0;
  mecanum_msg.rear_right = 0;

  // Initialize subscribers
  // RCCHECK(rclc_subscription_init_default(
  //   &subscriber,
  //   &node,
  //   ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
  //   "/bark"));

  RCCHECK(rclc_subscription_init_default(
    &mecanum_subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "/hazmat/wheel_cmd"));

  // Add subscribers to executor
  // RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &recv_msg, &subscription_callback, ON_NEW_DATA));
  RCCHECK(rclc_executor_add_subscription(&executor, &mecanum_subscriber, &mecanum_recv_msg, &mecanum_subscription_callback, ON_NEW_DATA));
}

void loop() {
  // Handle ROS communication
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10)));

  
  delay(10); // Short delay to prevent CPU hogging
}