#include "mechnum.h"
#include <Arduino.h>
#include <pwmWrite.h>
#include <I2Cdev.h>
#include <MPU6050.h>

Pwm pwm = Pwm();

void mechnum::attach(int EN_Pin ,int IN1_Pin ,int IN2_Pin ,int ENC1_Pin ,int ENC2_Pin){
    EN = EN_Pin;
    IN1 = IN1_Pin;
    IN2 = IN2_Pin;
    EN1 = ENC1_Pin;
    EN2 = ENC2_Pin;

    pwm.attach(EN);
    pinMode(IN1 ,OUTPUT);
    pinMode(IN2 ,OUTPUT);
    pinMode(EN1,INPUT_PULLUP);
    pinMode(EN2,INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(EN1), enc1_ISR, RISING);
    
}
void IRAM_ATTR enc1_ISR() { 
    if (digitalRead(EN2) == HIGH) pulseCount1++; // Forward
    else pulseCount1--; // Backward
  }
float mechnum::get_speed_enc(volatile int &pulsecount) {
    //TODO : USE ENCODERS TO GET SPEED MESUREMENT 
    int pulsesPerRevolution = 150; // Adjust based on your motor specs
    float speed_encoder = (pulseCount / (float)pulsesPerRevolution); // Convert to RPM
    pulseCount = 0; // Reset pulse count for next cycle
    return speed_encoder;
}
float mechnum::get_speed_imu() {
    //TODO : USE IMU SPEED 
    return speed_imu;
}
void mechnum::set_speed(int speed) {
    //TODO : USE get_speed and set_power to set_speed
    // PID ??
}

void mechnum::maintain_speed() {
    //TODO: PID maintiain feedback look
    
}

void mechnum::set_power(int powerr) {
    if (powerr >= 0) {
        digitalWrite(IN1,HIGH);
        digitalWrite(IN2,LOW);
        pwm.write(EN,powerr);
    } else {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,HIGH);
        pwm.write(EN,-powerr);
    }
}