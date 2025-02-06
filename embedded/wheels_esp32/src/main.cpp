#include <Arduino.h>
#include "mechnum.h"

mechnum m1 ;
mechnum m2 ;
mechnum m3 ;
mechnum m4 ;
void setup() {
  m1.attach(17,8,18);
  m2.attach(9,11,10);
  m3.attach(4,6,5);
  m4.attach(16,15,7);

  //code when implemented
  Serial.begin(9600); 
  float m1s,m2s,m3s,m4s;
}

void loop() {
  m1.set_power(100,1);
  m2.set_power(100,1);
  m3.set_power(100,1);
  m4.set_power(100,1);

  // code when implemented 
  if (Serial.available()){
    // m1s = Serial.readBytesUntil()
  }
}
