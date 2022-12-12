// Include the Arduino Encoder Library
#include <Encoder.h>

// Include the Arduino Stepper Library
#include <Stepper.h>

#define P_I 3.14159

//set up conveyor motor pins
const int conv1 = 8;
const int conv2 = 9;
const int convEn = 10;



void setup() {
  // Conveyor
  pinMode(conv1, OUTPUT);
  pinMode(conv2, OUTPUT);
  pinMode(convEn, OUTPUT);
  // Set initial Conveyor rotation direction
  digitalWrite(conv1, LOW);
  digitalWrite(conv2, HIGH);
}

void loop() {
  conveyorRun();
  delay(10000);
  conveyorReverse();
  delay(5000);

}

void conveyorStop() {
  analogWrite(convEn, 0);
  delay(20);
}

void conveyorRun() {
  analogWrite(convEn, 255); // Send PWM signal to L298N Enable pin
  digitalWrite(conv1, HIGH);
  digitalWrite(conv2, LOW);
  delay(20);
}

void conveyorReverse() {
  analogWrite(convEn, 255); // Send PWM signal to L298N Enable pin
  digitalWrite(conv1, LOW);
  digitalWrite(conv2, HIGH);
  delay(20);
}




