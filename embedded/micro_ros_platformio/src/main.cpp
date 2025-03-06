#include <Arduino.h>
#include <micro_ros_platformio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>
#include <hazmat_msgs/msg/mecanum_cmd.h>

// Ensure that the transport layer being used is Arduino Serial.
// If it's not, compilation is stopped and error is printed.
#if !defined(MICRO_ROS_TRANSPORT_ARDUINO_SERIAL)
#error This example is only available for Arduino framework with serial transport.
#endif

// Define ROS2 objects for a publisher, a message, an executor, support objects, an allocator, a node, and a timer
rcl_timer_t timer;

rcl_publisher_t publisher;
std_msgs__msg__Int32 msg;

rcl_subscription_t subscriber;
std_msgs__msg__Int32 recv_msg;

rcl_subscription_t mecanum_subscriber;
hazmat_msgs__msg__MecanumCmd mecanum_recv_msg;

rcl_publisher_t mecanum_publisher;
hazmat_msgs__msg__MecanumCmd mecanum_msg;

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

// Macros for checking return of ROS2 functions and entering an infinite error loop in case of error
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// Infinite error loop function. If something fails, the device will get stuck here
void error_loop() {
  while(1) {
    delay(100);
  }
}

// This is the function that will be called every time the timer expires
void timer_callback(rcl_timer_t * timer, int64_t last_call_time) {
  RCLC_UNUSED(last_call_time);
  if (timer != NULL) {
    // Update message values before publishing
    msg.data++;
    
    // Update mecanum message values
    mecanum_msg.front_left = 1;
    mecanum_msg.front_right = 2;
    mecanum_msg.rear_left = 3;
    mecanum_msg.rear_right = 4;
    
    // We publish our messages
    RCSOFTCHECK(rcl_publish(&publisher, &msg, NULL));
    RCSOFTCHECK(rcl_publish(&mecanum_publisher, &mecanum_msg, NULL));
  }
}

void subscription_callback(const void * msgin)
{
  const std_msgs__msg__Int32 * msg = (const std_msgs__msg__Int32 *)msgin;
  printf("Received: %d\n", msg->data);
}

void mecanum_subscription_callback(const void * msgin)
{
  const hazmat_msgs__msg__MecanumCmd * msg = (const hazmat_msgs__msg__MecanumCmd *)msgin;
  printf("Received mecanum cmd: %d %d %d %d\n", 
         msg->front_left, msg->front_right, 
         msg->rear_left, msg->rear_right);
}

void setup() {
  Serial.begin(115200);
  set_microros_serial_transports(Serial);
  delay(2000);

  // Get the default memory allocator provided by rcl
  allocator = rcl_get_default_allocator();
  // Initialize rclc_support with default allocator
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  // Initialize a ROS node with the name "micro_ros_platformio_node"
  RCCHECK(rclc_node_init_default(&node, "micro_ros_platformio_node", "", &support));

  // Initialize a ROS publisher with the name "micro_ros_platformio_node_publisher" to publish Int32 messages
  RCCHECK(rclc_publisher_init_default(
    &publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "/meow"));

  RCCHECK(rclc_publisher_init_default(
    &mecanum_publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "/mecanum_vel"));
    
  // Initialize a timer with a period of 1 second which calls the function timer_callback() every time it expires
  const unsigned int timer_timeout = 1000;
  RCCHECK(rclc_timer_init_default(
    &timer,
    &support,
    RCL_MS_TO_NS(timer_timeout),
    timer_callback));

  // Initialize an executor that will manage the execution of all the ROS entities
  // Updated executor size to handle 3 entities (timer + 2 subscribers)
  RCCHECK(rclc_executor_init(&executor, &support.context, 3, &allocator));
  
  // Add our timer to the executor
  RCCHECK(rclc_executor_add_timer(&executor, &timer));

  // Initialize our message data to 0
  msg.data = 0;
  
  // Initialize mecanum message values
  mecanum_msg.front_left = 0;
  mecanum_msg.front_right = 0;
  mecanum_msg.rear_left = 0;
  mecanum_msg.rear_right = 0;

  // Initialize subscriber for Int32 messages
  RCCHECK(rclc_subscription_init_default(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "/bark"));

  // Initialize subscriber for MecanumCmd messages
  RCCHECK(rclc_subscription_init_default(
    &mecanum_subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(hazmat_msgs, msg, MecanumCmd),
    "/mecanum_cmd"));

  // Add subscribers to the executor with their respective callbacks
  RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &recv_msg, &subscription_callback, ON_NEW_DATA));
  RCCHECK(rclc_executor_add_subscription(&executor, &mecanum_subscriber, &mecanum_recv_msg, &mecanum_subscription_callback, ON_NEW_DATA));
}

void loop() {
  delay(100);
  // Execute pending tasks in the executor. This will handle all ROS communications.
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
}