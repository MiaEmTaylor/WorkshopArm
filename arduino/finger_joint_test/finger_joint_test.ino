/*
  finger_joint_test.ino

  Cardboard test finger — 3 joints:
    Joint 1 (base)   -> servo
    Joint 2 (middle) -> servo
    Joint 3 (tip)    -> tether only, no electronics (string/thread pulled
                         by hand or mechanically linked to a servo above)
  Tip -> small DC motor that spins the fingertip

  Wiring (change pin numbers below if you wire it differently):
    Servo 1 signal wire -> pin 9
    Servo 2 signal wire -> pin 10
    Servo power (red)   -> 5V (use external supply if using more than 1-2 servos)
    Servo ground (brown/black) -> GND (shared with Arduino GND)

    Tip motor -> through a transistor or motor driver, NOT directly to a pin.
    Motor driver/transistor control pin -> pin 3 (PWM)
    Motor power -> external supply matched to the motor's voltage
    Motor ground -> shared GND with Arduino

  This sketch just gives you three simple test functions you can call
  independently from setup()/loop() so you can check each joint and the
  motor work before combining them into real motion.
*/

#include <Servo.h>

Servo servoBase;   // Joint 1
Servo servoMiddle; // Joint 2

const int SERVO_BASE_PIN   = 9;
const int SERVO_MIDDLE_PIN = 10;
const int TIP_MOTOR_PIN    = 3; // must be a PWM pin (marked ~ on the board)

const int SERVO_MIN_ANGLE = 0;
const int SERVO_MAX_ANGLE = 90; // adjust once you see how far the cardboard joint can bend

void setup() {
  servoBase.attach(SERVO_BASE_PIN);
  servoMiddle.attach(SERVO_MIDDLE_PIN);
  pinMode(TIP_MOTOR_PIN, OUTPUT);

  // start everything at rest
  servoBase.write(SERVO_MIN_ANGLE);
  servoMiddle.write(SERVO_MIN_ANGLE);
  analogWrite(TIP_MOTOR_PIN, 0);
}

void loop() {
  testBaseJoint();
  delay(1000);

  testMiddleJoint();
  delay(1000);

  testTipMotor();
  delay(1000);
}

// Sweeps joint 1 from min to max and back
void testBaseJoint() {
  for (int angle = SERVO_MIN_ANGLE; angle <= SERVO_MAX_ANGLE; angle++) {
    servoBase.write(angle);
    delay(15);
  }
  for (int angle = SERVO_MAX_ANGLE; angle >= SERVO_MIN_ANGLE; angle--) {
    servoBase.write(angle);
    delay(15);
  }
}

// Sweeps joint 2 from min to max and back
void testMiddleJoint() {
  for (int angle = SERVO_MIN_ANGLE; angle <= SERVO_MAX_ANGLE; angle++) {
    servoMiddle.write(angle);
    delay(15);
  }
  for (int angle = SERVO_MAX_ANGLE; angle >= SERVO_MIN_ANGLE; angle--) {
    servoMiddle.write(angle);
    delay(15);
  }
}

// Spins the tip motor briefly at a moderate speed, then stops it
void testTipMotor() {
  analogWrite(TIP_MOTOR_PIN, 150); // speed 0-255
  delay(1500);
  analogWrite(TIP_MOTOR_PIN, 0);   // stop
}
