
int weight = 0;

void setup() {
Serial.begin(19200); // set the baud rate
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
    weight += 1;
    Serial.print("SUI  -    "+String(weight/1000.0,3)+" g  \r\n");
    }
 // Serial.print("ES");
}
}
