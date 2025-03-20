#include <Arduino.h>
#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>
#include <hazmat_msgs/msg/mecanum_cmd.h>
#include "mecanum.h"

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
#define ENA2 4
#define IN1_3 6
#define IN2_3 5
#define ENB2 16
#define IN3_4 7
#define IN4_4 15

// Encoder Connections (ESP32 Pins)
#define ENC1_A 40
#define ENC1_B 39
#define ENC2_A 41
#define ENC2_B 42
#define ENC3_A 38
#define ENC3_B 37
#define ENC4_A 35
#define ENC4_B 36

// ROS2 objects
rcl_timer_t timer;
rcl_subscription_t mecanum_subscriber;
rcl_publisher_t mecanum_publisher;

hazmat_msgs__msg__MecanumCmd mecanum_recv_msg;
hazmat_msgs__msg__MecanumCmd mecanum_msg;

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

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

void setup() {
  Serial.begin(115200);

  m1.attach(ENA1, IN1_1, IN2_1, ENC1_A, ENC1_B);
  m2.attach(ENB1, IN4_2, IN3_2, ENC2_A, ENC2_B);
  m3.attach(ENA2, IN1_3, IN2_3, ENC3_A, ENC3_B);
  m4.attach(ENB2, IN4_4, IN3_4, ENC4_A, ENC4_B);

  set_microros_serial_transports(Serial);
  delay(2000);

  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  RCCHECK(rclc_node_init_default(&node, "mecanum_node", "", &support));

  RCCHECK(rclc_publisher_init_default(
    &mecanum_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "hazmat/encoder_vel"));

  const unsigned int timer_timeout = 100;
  RCCHECK(rclc_timer_init_default(
    &timer,
    &support,
    RCL_MS_TO_NS(timer_timeout),
    timer_callback));

  RCCHECK(rclc_executor_init(&executor, &support.context, 2, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  mecanum_msg.front_left = 0;
  mecanum_msg.front_right = 0;
  mecanum_msg.rear_left = 0;
  mecanum_msg.rear_right = 0;

  RCCHECK(rclc_subscription_init_default(
    &mecanum_subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "/hazmat/wheel_cmd"));

  RCCHECK(rclc_executor_add_subscription(&executor, &mecanum_subscriber, &mecanum_recv_msg, &mecanum_subscription_callback, ON_NEW_DATA));
}

void loop() {
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10)));
  delay(10);
}