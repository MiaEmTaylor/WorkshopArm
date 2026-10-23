/*
  servo_sweep_test.ino

  No serial, no Python, nothing else. Just sweeps all three servos
  0 -> 180 -> 0 forever. Upload this from the Arduino IDE and watch.

  Wiring (same as arm_control.ino):
    Shoulder servo signal -> pin 2
    Elbow1   servo signal -> pin 3
    Elbow2   servo signal -> pin 4
    Servo power (red)          -> external supply, NOT the Arduino 5V pin
    Servo ground (brown/black) -> shared GND with Arduino
*/

#include <Servo.h>

Servo servoShoulder;
Servo servoElbow1;
Servo servoElbow2;

void setup() {
  servoShoulder.attach(2);
  servoElbow1.attach(3);
  servoElbow2.attach(4);
}

void sweep(Servo &s) {
  for (int angle = 0; angle <= 180; angle += 1) {
    s.write(angle);
    delay(15);
  }
  for (int angle = 180; angle >= 0; angle -= 1) {
    s.write(angle);
    delay(15);
  }
}

void loop() {
  // one servo at a time - lower peak current draw than all three together
  sweep(servoShoulder);
  delay(500);
  sweep(servoElbow1);
  delay(500);
  sweep(servoElbow2);
  delay(500);
}
