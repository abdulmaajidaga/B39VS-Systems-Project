#ifndef mechnum_h
#define mechnum_h
class mechnum 
{
    private:
    //var for lib func
    float speed_encoder ;
    float dir;
    float power;
    int EN ;
    int IN1;
    int IN2;
    int speed_imu;
    int EN1;
    int EN2;
    int pulsecount;

    public:
    void attach(int EN_Pin ,int IN1_Pin ,int IN2_Pin ,int ENC1_Pin ,int ENC2_Pin);
    float get_speed_enc();
    float get_speed_imu();
    void set_speed(int speed);
    void set_power(int power);
    void maintain_speed();
    void IRAM_ATTR enc1_ISR();
};

#endif
