// Author Teemu Mäntykallio, 2017-04-07

// Define pins
#define EN_PIN    6  // LOW: Driver enabled. HIGH: Driver disabled
#define STEP_PIN  5 // Step on rising edge
#define RX_PIN    3  // SoftwareSerial pins
#define TX_PIN    2  //

#include <TMC2208Stepper.h>
#include <AccelStepper.h>

AccelStepper stepper(AccelStepper::DRIVER, 5, 6); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

// Create driver that uses SoftwareSerial for communication
TMC2208Stepper driver = TMC2208Stepper(RX_PIN, TX_PIN);

int motor_speed;
const byte numChars = 32;
char receivedChars[numChars];   // an array to store the received data
boolean newData = false;
int dataNumber = 0;             // new for this version
boolean isInit =false;

void setup() {
  Serial.begin(19200);
  driver.beginSerial(115200);
  // Push at the start of setting up the driver resets the register to default
  driver.push();
  // Prepare pins
  pinMode(EN_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  driver.pdn_disable(true);     // Use PDN/UART pin for communication
  driver.I_scale_analog(false); // Use internal voltage reference
  driver.rms_current(50);      // Set driver current = 500mA, 0.5 multiplier for hold current and RSENSE = 0.11.
  driver.toff(2);               // Enable driver in software

  digitalWrite(EN_PIN, LOW);    // Enable driver in hardware
  stepper.setMaxSpeed(5000);
  stepper.setSpeed(0);  
  uint16_t current=driver.rms_current();
 // Serial.println(current);
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
    stepper.runSpeed();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
 // if (Serial.available() > 0) {
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();
        if (rc=='Z'){Serial.write('D');}
        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}


void showNewData() {
    if (newData == true) {
     //motor_speed = serial_reader();             // new for this version 
   //  Serial.println(atoi(receivedChars));
     stepper.setSpeed(map(atoi(receivedChars),0,140, 0, 500));
     newData = false;
    }
}
