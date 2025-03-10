#include "mechnum.h"
#include <Arduino.h>
#include <pwmWrite.h>
#include <I2Cdev.h>
#include <MPU6050.h>

// Create a global PWM object (ensure the pwmWrite library is compatible with your ESP32 setup)
Pwm pwm = Pwm();

void mecanum::attach(int EN_Pin, int IN1_Pin, int IN2_Pin, int ENC1_Pin, int ENC2_Pin) {
  // Save pin assignments
  EN = EN_Pin;
  IN1 = IN1_Pin;
  IN2 = IN2_Pin;
  EN1 = ENC1_Pin;
  EN2 = ENC2_Pin;
  
  // Initialize pulse counter
  pulsecount = 0;
  
  // Initialize motor control pins
  pwm.attach(EN);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  // Set encoder pins as inputs (using pullups)
  pinMode(ENC1_Pin, INPUT_PULLUP);
  pinMode(ENC2_Pin, INPUT_PULLUP);
  
  // Register the common ISR for this motor.
  // attachInterruptArg passes 'this' as an argument so the ISR knows which instance to update.
  attachInterruptArg(digitalPinToInterrupt(ENC1_Pin), mecanum::commonISR, this, RISING);
}

void IRAM_ATTR mecanum::commonISR(void* arg) {
  // Cast the argument back to a mecanum instance
  mecanum* instance = (mecanum*) arg;
  // Use the second encoder pin (EN2) to determine direction
  if (digitalRead(instance->EN2) == HIGH) {
    instance->pulsecount++;
  } else {
    instance->pulsecount--;
  }
}

float mecanum::get_speed_enc() {
  // Atomically read and reset pulsecount
  noInterrupts();
  int pulses = pulsecount;
  pulsecount = 0;
  interrupts();
  
  // Calculate speed in RPM (adjust pulsesPerRevolution as needed)
  int pulsesPerRevolution = 150;
  float rpm = (pulses / (float)pulsesPerRevolution) * 60;  // pulses per second * 60 = RPM
  return rpm;
}

float mecanum::get_speed_imu() {
  // Placeholder: return IMU-based speed if implemented
  return speed_imu;
}

void mecanum::set_power(int power) {
  // Constrain power to valid range
  power = constrain(power, -255, 255);
  if (power >= 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    pwm.write(EN, power);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    pwm.write(EN, -power);
  }
}

void mecanum::set_speed(int speed) {
  // Placeholder for PID control to set motor speed
}

void mecanum::maintain_speed() {
  // Placeholder for speed maintenance logic
}
