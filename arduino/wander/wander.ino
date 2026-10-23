/*
  wander.ino

  Fully standalone - no serial connection, no laptop, no Python needed
  after flashing. Picks a new random pose across the full 0-180 degree
  range on each of the three joints, moves there smoothly and slowly
  (eased in/out, not constant speed), holds briefly, then picks a new
  random pose and does it again - forever.

  Still needs POWER from somewhere once it's off the laptop (a USB power
  bank, a wall adapter, whatever you're using) - only the data/command
  connection is unnecessary now, not electricity.

  Wiring (same as arm_control.ino):
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

float posShoulder = 90;
float posElbow1 = 90;
float posElbow2 = 90;

const float DEG_PER_STEP = 1.0;   // small step size = smooth motion
const int STEP_DELAY_MS = 40;     // slow
const int HOLD_MS = 2000;         // pause at each pose before picking the next

void setup() {
  servoShoulder.attach(SHOULDER_PIN);
  servoElbow1.attach(ELBOW1_PIN);
  servoElbow2.attach(ELBOW2_PIN);

  servoShoulder.write((int)posShoulder);
  servoElbow1.write((int)posElbow1);
  servoElbow2.write((int)posElbow2);

  // A0 is left unconnected on purpose - the floating voltage there reads
  // as noise, giving a different random seed each boot instead of always
  // wandering the same fixed sequence.
  randomSeed(analogRead(A0));
  delay(1000);
}

float easeStep(float from, float to, float frac) {
  float eased = frac * frac * (3.0 - 2.0 * frac);  // smoothstep: eases in and out, no abrupt start/stop
  return from + (to - from) * eased;
}

void moveTo(float targetShoulder, float targetElbow1, float targetElbow2) {
  float startShoulder = posShoulder;
  float startElbow1 = posElbow1;
  float startElbow2 = posElbow2;

  float maxDist = max(abs(targetShoulder - startShoulder),
                   max(abs(targetElbow1 - startElbow1), abs(targetElbow2 - startElbow2)));
  int steps = max(1, (int)(maxDist / DEG_PER_STEP));

  for (int i = 1; i <= steps; i++) {
    float frac = (float)i / steps;
    posShoulder = easeStep(startShoulder, targetShoulder, frac);
    posElbow1 = easeStep(startElbow1, targetElbow1, frac);
    posElbow2 = easeStep(startElbow2, targetElbow2, frac);

    servoShoulder.write((int)posShoulder);
    servoElbow1.write((int)posElbow1);
    servoElbow2.write((int)posElbow2);

    delay(STEP_DELAY_MS);
  }
}

void loop() {
  float targetShoulder = random(0, 181);
  float targetElbow1 = random(0, 181);
  float targetElbow2 = random(0, 181);

  moveTo(targetShoulder, targetElbow1, targetElbow2);
  delay(HOLD_MS);
}
