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

    public:
    void attach(int EN_Pin ,int IN1_Pin ,int IN2_Pin);
    float get_speed_enc();
    float get_speed_imu();
    void set_speed(float speed);
    void set_power(float power ,bool dir);
    void maintain_speed();
};

#endif
