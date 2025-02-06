#include "mechnum.h"
#include <Arduino.h>
#include <pwmWrite.h>
#include <I2Cdev.h>
#include <MPU6050.h>

Pwm pwm = Pwm();

void mechnum::attach(int EN_Pin ,int IN1_Pin ,int IN2_Pin){
    EN = EN_Pin;
    IN1 = IN1_Pin;
    IN2 = IN2_Pin;
    pwm.attach(EN);
    pinMode(IN1 ,OUTPUT);
    pinMode(IN2 ,OUTPUT);
}

float mechnum::get_speed_enc() {
    //TODO : USE ENCODERS TO GET SPEED MESUREMENT 
    return speed_encoder;
}
float mechnum::get_speed_imu() {
    //TODO : USE IMU SPEED 
    return speed_imu;
}
void mechnum::set_speed(float speed) {
    //TODO : USE get_speed and set_power to set_speed
    // PID ??
}

void mechnum::maintain_speed() {
    //TODO: PID maintiain feedback look
    
}

void mechnum::set_power(float powerr ,bool dirr) {
    //TODO : ADD PWM SPEED MODULATION FOR SPEED CONTROL
    dir = dirr;
    power = powerr ;

    if (dir) {
        digitalWrite(IN1,HIGH);
        digitalWrite(IN2,LOW);
        pwm.write(EN,power);
    }
    else {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,HIGH);
        pwm.write(EN,power);
    }
}