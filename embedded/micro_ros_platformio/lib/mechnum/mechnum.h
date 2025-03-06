#ifndef mechnum_h
#define mechnum_h

#include <Arduino.h>

class mechnum 
{
    private:
        float speed_encoder;
        float dir;
        float power;
        int EN;
        int IN1;
        int IN2;
        int speed_imu;
        int EN1;
        int EN2;
        volatile int pulsecount;  // Make this variable volatile for ISRs

    public:
        void attach(int EN_Pin, int IN1_Pin, int IN2_Pin, int ENC1_Pin, int ENC2_Pin);
        float get_speed_enc();  // Modified to use internal pulsecount
        float get_speed_imu();
        void set_speed(int speed);
        void set_power(int power);
        void maintain_speed();
        static void enc_ISR0();  // Separate ISRs for each motor
        static void enc_ISR1();
        static void enc_ISR2();
        static void enc_ISR3();
};

#endif
