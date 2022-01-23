#include "AccelStepper.h"

AccelStepper motor(8,4,2,5,3);
//int incomingByte = 0;

void setup() {
Serial.begin(9600); // set the baud rate
}
void loop() {
char inByte =' ';
if (Serial.available() > 0) {
  String(inByte) = Serial.readString(); 
  if (inByte == "Z\r\n"){
    Serial.print("Z A\r\n");
    delay(1);
    Serial.print("Z D\r\n");
    }
  if (inByte == "SUI\r\n"){
    Serial.print("SUI  -    "+String(random(1,10))+".002 g  \r\n");
    }
 // Serial.print("ES");
}
}
