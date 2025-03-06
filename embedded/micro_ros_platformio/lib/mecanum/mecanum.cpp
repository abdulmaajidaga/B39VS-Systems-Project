#include "mecanum.h"
#include <Arduino.h>
#include <pwmWrite.h>
#include <I2Cdev.h>
#include <MPU6050.h>

// Global array of pointers to mecanum instances for ISR access
mecanum* mecanumPtr[4] = { nullptr, nullptr, nullptr, nullptr };

Pwm pwm = Pwm();
int instanceCounter = 0;

// Attach function to set up pins and interrupt
void mecanum::attach(int EN_Pin, int IN1_Pin, int IN2_Pin, int ENC1_Pin, int ENC2_Pin) {
    EN = EN_Pin;
    IN1 = IN1_Pin;
    IN2 = IN2_Pin;
    EN1 = ENC1_Pin;
    EN2 = ENC2_Pin;
    pulsecount = 0;  // Initialize pulse count

    pwm.attach(EN);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(EN1, INPUT_PULLUP);
    pinMode(EN2, INPUT_PULLUP);

    // Store instance pointer and attach ISRs based on instance count
    if (instanceCounter < 4) {
        mecanumPtr[instanceCounter] = this;
        switch (instanceCounter) {
            case 0:
                attachInterrupt(digitalPinToInterrupt(EN1), enc_ISR0, RISING);
                break;
            case 1:
                attachInterrupt(digitalPinToInterrupt(EN1), enc_ISR1, RISING);
                break;
            case 2:
                attachInterrupt(digitalPinToInterrupt(EN1), enc_ISR2, RISING);
                break;
            case 3:
                attachInterrupt(digitalPinToInterrupt(EN1), enc_ISR3, RISING);
                break;
        }
        instanceCounter++;
    }
}

// Separate ISRs for each motor
void mecanum::enc_ISR0() {
    if (digitalRead(mecanumPtr[0]->EN2) == HIGH)
        mecanumPtr[0]->pulsecount++;
    else
        mecanumPtr[0]->pulsecount--;
}

void mecanum::enc_ISR1() {
    if (digitalRead(mecanumPtr[1]->EN2) == HIGH)
        mecanumPtr[1]->pulsecount++;
    else
        mecanumPtr[1]->pulsecount--;
}

void mecanum::enc_ISR2() {
    if (digitalRead(mecanumPtr[2]->EN2) == HIGH)
        mecanumPtr[2]->pulsecount++;
    else
        mecanumPtr[2]->pulsecount--;
}

void mecanum::enc_ISR3() {
    if (digitalRead(mecanumPtr[3]->EN2) == HIGH)
        mecanumPtr[3]->pulsecount++;
    else
        mecanumPtr[3]->pulsecount--;
}

// Example speed calculation using encoder pulses
int32_t mecanum::get_speed_enc() {
    int pulsesPerRevolution = 150;  // Adjust based on your motor specs
    int32_t speed_encoder = (pulsecount / (int32_t)pulsesPerRevolution);  // Convert to RPM
    pulsecount = 0;  // Reset pulse count for the next cycle
    return int32_t(speed_encoder);
}

float mecanum::get_speed_imu() {
    return speed_imu;  // Placeholder
}

void mecanum::set_power(int powerr) {
    if (powerr >= 0) {
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        pwm.write(EN, powerr);
    } else {
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, HIGH);
        pwm.write(EN, -powerr);
    }
}

void mecanum::set_speed(int speed) {
    // To be implemented
}

void mecanum::maintain_speed() {
    // To be implemented
}
