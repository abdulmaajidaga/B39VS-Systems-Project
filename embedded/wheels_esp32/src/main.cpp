#include <Arduino.h>
#include "mechnum.h"

mechnum m1;
mechnum m2;
mechnum m3;
mechnum m4;
int m1s = 0, m2s = 0, m3s = 0, m4s = 0;

#define ENA1 17
#define IN1_1 8
#define IN2_1 18

#define ENB1 11
#define IN3_2 9
#define IN4_2 10

#define ENA2 4
#define IN1_3 6
#define IN2_3 5

#define ENB2 16
#define IN3_4 7
#define IN4_4 15

#define ENC1_A 40
#define ENC1_B 39

#define ENC2_A 41
#define ENC2_B 42

#define ENC3_A 38
#define ENC3_B 37

#define ENC4_A 35
#define ENC4_B 36

void setup() {
    m1.attach(ENA1, IN1_1, IN2_1, ENC1_A, ENC1_B);
    m2.attach(ENB1, IN4_2, IN3_2, ENC2_A, ENC2_B);
    m3.attach(ENA2, IN1_3, IN2_3, ENC3_A, ENC3_B);
    m4.attach(ENB2, IN4_4, IN3_4, ENC4_A, ENC4_B);
    Serial.begin(9600);
}

void loop() {
    m1.set_power(m1s);
    m2.set_power(m2s);
    m3.set_power(m3s);
    m4.set_power(m4s);

    if (Serial.available()) {
        String speeds = Serial.readString();
        m1s = speeds.substring(0, 4).toInt();
        m2s = speeds.substring(4, 8).toInt();
        m3s = speeds.substring(8, 12).toInt();
        m4s = speeds.substring(12, 16).toInt();
        
        Serial.print(m1.get_speed_enc()); Serial.print("|");
        Serial.print(m2.get_speed_enc()); Serial.print("|");
        Serial.print(m3.get_speed_enc()); Serial.print("|");
        Serial.println(m4.get_speed_enc());
    }
}
