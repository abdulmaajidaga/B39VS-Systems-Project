#include <Arduino.h>
#include "mechnum.h"

mechnum m1 ;
mechnum m2 ;
mechnum m3 ;
mechnum m4 ;
int m1s = 0,m2s = 0,m3s = 0,m4s = 0;

void setup() {
  m1.attach(17,8,18);
  m2.attach(11,10,9);
  m3.attach(4,6,5);
  m4.attach(16,15,7);

  //code when implemented
  Serial.begin(115200); 
  
}

void loop() {
  m1.set_power(m1s,1);
  m2.set_power(m2s,1);
  m3.set_power(m3s,1);
  m4.set_power(m4s,1);

  // code when implemented 
  if (Serial.available()){
    String speeds = Serial.readString();
    m1s = speeds.substring(0,2).toInt();
    m2s = speeds.substring(2,4).toInt();
    m3s = speeds.substring(4,6).toInt();
    m4s = speeds.substring(6,8).toInt();
    Serial.println(speeds);;
  }
}
