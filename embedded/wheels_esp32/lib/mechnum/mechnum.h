#ifndef MECANUM_H
#define MECANUM_H

#include <Arduino.h>

class mecanum {
public:
  // Pin numbers (set during attach)
  int EN;    // PWM output pin for motor speed
  int IN1;   // Motor direction control
  int IN2;   // Motor direction control
  int EN1;   // Encoder pin (interrupt attached here)
  int EN2;   // Encoder pin (used for determining direction)
  
  // Encoder pulse count (volatile because updated in ISR)
  volatile int pulsecount;
  
  // (Optional) IMU speed reading
  float speed_imu;

  // Methods
  void attach(int EN_Pin, int IN1_Pin, int IN2_Pin, int ENC1_Pin, int ENC2_Pin);
  float get_speed_enc();
  float get_speed_imu();
  void set_power(int power);
  void set_speed(int speed);    // Placeholder for future PID control
  void maintain_speed();        // Placeholder for speed maintenance

private:
  // Common ISR for all instances. The argument will point to the current instance.
  static void IRAM_ATTR commonISR(void* arg);
};

#endif
