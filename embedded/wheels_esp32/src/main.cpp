#include <Arduino.h>
#include "mechnum.h"

mechnum m1;
mechnum m2;
mechnum m3;
mechnum m4;
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
#define ENC1_A 35
#define ENC1_B 36

#define ENC2_A 47
#define ENC2_B 48

#define ENC3_A 41
#define ENC3_B 42

#define ENC4_A 14
#define ENC4_B 13

// Encoder pulse counters
volatile int pulseCount1 = 0, pulseCount2 = 0, pulseCount3 = 0, pulseCount4 = 0;

// Function to calculate RPM (adjusted for your motor's encoder PPR)
float calculateRPM(volatile int &pulseCount) {
  int pulsesPerRevolution = 150; // Adjust based on your motor specs
  float rpm = (pulseCount / (float)pulsesPerRevolution); // Convert to RPM
  pulseCount = 0; // Reset pulse count for next cycle
    
  return rpm;

}

void stopMotors() {
  digitalWrite(ENA1, LOW); digitalWrite(ENB1, LOW);
  digitalWrite(ENA2, LOW); digitalWrite(ENB2, LOW);
}

// Interrupt service routines (ISR) for encoders
void IRAM_ATTR enc1_ISR() { 
  if (digitalRead(ENC1_B) == HIGH) pulseCount1++; // Forward
  else pulseCount1--; // Backward
}
void IRAM_ATTR enc2_ISR() { 
  if (digitalRead(ENC2_B) == HIGH) pulseCount2++; 
  else pulseCount2--; 
}
void IRAM_ATTR enc3_ISR() { 
  if (digitalRead(ENC3_B) == HIGH) pulseCount3++; 
  else pulseCount3--; 
}
void IRAM_ATTR enc4_ISR() { 
  if (digitalRead(ENC4_B) == HIGH) pulseCount4++; 
  else pulseCount4--; 
}

void setup() {
  // Initialise all motor pins
  m1.attach(ENA1,IN1_1,IN2_1);
  m2.attach(ENB1,IN4_2,IN3_2);
  m3.attach(ENA2,IN1_3,IN2_3);
  m4.attach(ENB2,IN4_4,IN3_4);

  // Set encoder pins as inputs
  pinMode(ENC1_A, INPUT_PULLUP); pinMode(ENC1_B, INPUT_PULLUP);
  pinMode(ENC2_A, INPUT_PULLUP); pinMode(ENC2_B, INPUT_PULLUP);
  pinMode(ENC3_A, INPUT_PULLUP); pinMode(ENC3_B, INPUT_PULLUP);
  pinMode(ENC4_A, INPUT_PULLUP); pinMode(ENC4_B, INPUT_PULLUP);

  // Attach interrupts for encoder readings
  attachInterrupt(digitalPinToInterrupt(ENC1_A), enc1_ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC2_A), enc2_ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC3_A), enc3_ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC4_A), enc4_ISR, RISING);

  Serial.begin(115200);

  stopMotors();
}

void loop() {
  m1.set_power(m1s);
  m2.set_power(m2s);
  m3.set_power(m3s);
  m4.set_power(m4s);

  // code when implemented 
  if (Serial.available()){
    String speeds = Serial.readString();
    m1s = speeds.substring(0,4).toInt();
    m2s = speeds.substring(4,8).toInt();
    m3s = speeds.substring(8,12).toInt();
    m4s = speeds.substring(12,16).toInt();
    
    // Output encoder values
    // Serial.print(m1s); Serial.print(" | ");
    // Serial.print(m2s); Serial.print(" | ");
    // Serial.print(m3s); Serial.print(" | ");
    // Serial.println(m4s);
    Serial.print(calculateRPM(pulseCount1)); Serial.print("|");
    Serial.print(calculateRPM(pulseCount2)); Serial.print("|");
    Serial.print(calculateRPM(pulseCount3)); Serial.print("|");
    Serial.println(calculateRPM(pulseCount4));
  }
}

