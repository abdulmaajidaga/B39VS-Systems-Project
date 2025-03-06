#include "mechnum.h"
#include <Arduino.h>
#include <pwmWrite.h>
#include <I2Cdev.h>
#include <MPU6050.h>

// Global array of pointers to mechnum instances for ISR access
mechnum* mechnumPtr[4] = { nullptr, nullptr, nullptr, nullptr };

Pwm pwm = Pwm();
int instanceCounter = 0;

// Attach function to set up pins and interrupt
void mechnum::attach(int EN_Pin, int IN1_Pin, int IN2_Pin, int ENC1_Pin, int ENC2_Pin) {
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
        mechnumPtr[instanceCounter] = this;
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
void mechnum::enc_ISR0() {
    if (digitalRead(mechnumPtr[0]->EN2) == HIGH)
        mechnumPtr[0]->pulsecount++;
    else
        mechnumPtr[0]->pulsecount--;
}

void mechnum::enc_ISR1() {
    if (digitalRead(mechnumPtr[1]->EN2) == HIGH)
        mechnumPtr[1]->pulsecount++;
    else
        mechnumPtr[1]->pulsecount--;
}

void mechnum::enc_ISR2() {
    if (digitalRead(mechnumPtr[2]->EN2) == HIGH)
        mechnumPtr[2]->pulsecount++;
    else
        mechnumPtr[2]->pulsecount--;
}

void mechnum::enc_ISR3() {
    if (digitalRead(mechnumPtr[3]->EN2) == HIGH)
        mechnumPtr[3]->pulsecount++;
    else
        mechnumPtr[3]->pulsecount--;
}

// Example speed calculation using encoder pulses
float mechnum::get_speed_enc() {
    int pulsesPerRevolution = 150;  // Adjust based on your motor specs
    float speed_encoder = (pulsecount / (float)pulsesPerRevolution);  // Convert to RPM
    pulsecount = 0;  // Reset pulse count for the next cycle
    return speed_encoder;
}

float mechnum::get_speed_imu() {
    return speed_imu;  // Placeholder
}

void mechnum::set_power(int powerr) {
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

void mechnum::set_speed(int speed) {
    // To be implemented
}

void mechnum::maintain_speed() {
    // To be implemented
}
