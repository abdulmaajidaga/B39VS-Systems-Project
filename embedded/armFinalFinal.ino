#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define I2C_SDA 20 
#define I2C_SCL 19 

#define SERVO1_MIN 120   // Servo 1 range (0-270°)
#define SERVO1_MAX 470  

#define SERVO2_MIN 120   // Servo 2 range (0-270°)
#define SERVO2_MAX 470  

#define SERVO3_NEUTRAL 340  // Stop (90° equivalent)
#define SERVO3_CW 470       // Full-speed Clockwise (180° equivalent)
#define SERVO3_CCW 210      // Full-speed Counterclockwise (0° equivalent)

#define SERVO4_MIN 120   // Servo 4 range (0-270°)
#define SERVO4_MAX 470  

#define ANALOG1_PIN 3
#define ANALOG2_PIN 12
#define ANALOG3_PIN 13
#define ANALOG4_PIN 14

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

int currentAngle3 = 90;  // Store the last angle for Servo 3

void setup() {
    Wire.begin(I2C_SDA, I2C_SCL);
    pwm.begin();
    pwm.setPWMFreq(50);
    Serial.begin(115200);
    Serial.println("Enter four angles (Servo1: 10-114, Servo2: 0-270, Servo3: 0-180, Servo4: 0-196) separated by space:");
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        if (input.length() > 0) {
            int angle1, angle2, angle3, angle4;
            int result = sscanf(input.c_str(), "%d %d %d %d", &angle1, &angle2, &angle3, &angle4);

            if (result == 4) { // Ensure four numbers are received
                if (angle1 >= 15 && angle1 <= 152 && angle2 >= 0 && angle2 <= 270 &&
                    angle3 >= 0 && angle3 <= 360 && angle4 >= 0 && angle4 <= 196) {
                    
                    int pulse1 = map(angle1, 0, 270, SERVO1_MIN, SERVO1_MAX);
                    int pulse2 = map(angle2, 0, 270, SERVO2_MIN, SERVO2_MAX);
                    int pulse4 = map(angle4, 0, 270, SERVO4_MIN, SERVO4_MAX);

                    // Servo 3 Handling (Continuous Rotation Simulated as Position)
                    moveToAngle3(angle3);

                    pwm.setPWM(0, 0, pulse1);
                    pwm.setPWM(1, 0, pulse2);
                    pwm.setPWM(3, 0, pulse4);

                    Serial.printf("Servo1: %d°, Servo2: %d°, Servo3: %d°, Servo4: %d°\n", angle1, angle2, angle3, angle4);
                } else {
                    Serial.println("Invalid input! Servo1: 15-152, Servo2: 0-270, Servo3: 0-360, Servo4: 0-196.");
                }
            } else {
                Serial.println("Please enter four numbers separated by space (e.g., '90 180 90 90').");
            }
        }
    }

    // Read analog values from the 4 sensors
    int analogValue1 = analogRead(ANALOG1_PIN);
    int analogValue2 = analogRead(ANALOG2_PIN);
    int analogValue3 = analogRead(ANALOG3_PIN);
    int analogValue4 = analogRead(ANALOG4_PIN);

    // Map analog readings to degrees
    int mappedanal1 = map(analogValue1, 250, 2203, 0, 195);
    int mappedanal2 = map(analogValue2, 250, 2203, 0, 195);
    int mappedanal3 = map(analogValue3, 343, 3006, 0, 180);
    int mappedanal4 = map(analogValue4, 250, 2203, 0, 195);

    // Print the analog values to Serial Monitor
    Serial.printf("Analog1: %d°, Analog2: %d°, Analog3: %d°, Analog4: %d°\n", mappedanal1, mappedanal2, mappedanal3, mappedanal4);

    delay(500); // Small delay to avoid serial flooding
}

void moveToAngle3(int targetAngle) {
    int angleDifference = targetAngle - currentAngle3;
    int moveDuration = map(abs(angleDifference), 0, 360, 0, 1000); // Adjust time based on servo speed

    if (angleDifference > 0) {
        pwm.setPWM(2, 0, SERVO3_CW); // Rotate forward
    } 
    else if (angleDifference < 0) {
        pwm.setPWM(2, 0, SERVO3_CCW); // Rotate backward
    }
  
    delay(moveDuration); // Wait for estimated movement duration
    pwm.setPWM(2, 0, SERVO3_NEUTRAL); // Stop servo

    currentAngle3 = targetAngle; // Update position estimate
}