/*
  arm_control.ino

  Three-joint arm: shoulder, elbow1, elbow2, one hobby servo each.
  Reads plain text lines from serial: "<JOINT>:<ANGLE>\n"
    e.g. "SHOULDER:90.0\n"
  9600 baud. Matches servo_io.py on the Python side.

  Wiring:
    Shoulder servo signal -> pin 2
    Elbow1   servo signal -> pin 3
    Elbow2   servo signal -> pin 4
    Servo power (red)          -> external supply, NOT the Arduino 5V pin
    Servo ground (brown/black) -> shared GND with Arduino
*/

#include <Servo.h>

const int SHOULDER_PIN = 2;
const int ELBOW1_PIN = 3;
const int ELBOW2_PIN = 4;

Servo servoShoulder;
Servo servoElbow1;
Servo servoElbow2;

String inputLine = "";

void setup() {
  Serial.begin(9600);
  servoShoulder.attach(SHOULDER_PIN);
  servoElbow1.attach(ELBOW1_PIN);
  servoElbow2.attach(ELBOW2_PIN);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(inputLine);
      inputLine = "";
    } else {
      inputLine += c;
    }
  }
}

void handleLine(String line) {
  line.trim();
  int sep = line.indexOf(':');
  if (sep < 0) return;

  String joint = line.substring(0, sep);
  joint.toUpperCase();
  int deg = (int)line.substring(sep + 1).toFloat();
  deg = constrain(deg, 0, 180);

  if (joint == "SHOULDER") {
    servoShoulder.write(deg);
  } else if (joint == "ELBOW1") {
    servoElbow1.write(deg);
  } else if (joint == "ELBOW2") {
    servoElbow2.write(deg);
  }
}
