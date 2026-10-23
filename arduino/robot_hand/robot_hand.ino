/*
  5-Finger Tendon Robot Hand
  Board:   Arduino Uno
  Servos:  5x micro servos (SG90 / MG90S style), one per finger
  Build:   Coroplast hand, straw guides, string tendons tied to servo horns

  Works two ways (set USE_PCA9685 below):
    0 = servos plugged straight into Uno pins 3, 5, 6, 9, 10
    1 = servos on a PCA9685 16-channel servo driver board, channels 0-4

  Control it from the Serial Monitor (115200 baud, "Newline" line ending).
  Type "help" for the list of commands.
*/

// ======================= CONFIG =======================

#define USE_PCA9685 0   // 1 if you're using a PCA9685 driver board

const uint8_t NUM_FINGERS = 5;
const char* NAMES[NUM_FINGERS] = {"thumb", "index", "middle", "ring", "pinky"};

const uint8_t PINS[NUM_FINGERS]     = {3, 5, 6, 9, 10};  // Uno pins (direct mode)
const uint8_t CHANNELS[NUM_FINGERS] = {0, 1, 2, 3, 4};   // PCA9685 channels

// CALIBRATE THESE for your hand (use the "a" command to find the numbers).
// openAngle   = servo angle where the finger is straight and the string is just slack
// closedAngle = servo angle where the finger is fully curled
// If a finger moves backwards, swap its two numbers.
int openAngle[NUM_FINGERS]   = { 10,  10,  10,  10,  10};
int closedAngle[NUM_FINGERS] = {150, 170, 170, 170, 170};

float speedDegPerStep = 3.0;          // how far each servo moves per 15 ms step
const unsigned long STEP_MS = 15;

// =======================================================

#if USE_PCA9685
  #include <Wire.h>
  #include <Adafruit_PWMServoDriver.h>
  Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);
  const int SERVO_MIN_US = 500;       // pulse width for 0 degrees
  const int SERVO_MAX_US = 2400;      // pulse width for 180 degrees
#else
  #include <Servo.h>
  Servo servos[NUM_FINGERS];
#endif

float currentAngle[NUM_FINGERS];
int   targetAngle[NUM_FINGERS];
bool  relaxed = false;
unsigned long lastStep = 0;

// ---------- low-level servo output ----------

void writeServo(uint8_t i, int angle) {
  angle = constrain(angle, 0, 180);
#if USE_PCA9685
  long us = map(angle, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  uint16_t ticks = (uint16_t)(us * 4096L / 20000L);   // 50 Hz = 20 ms period
  pwm.setPWM(CHANNELS[i], 0, ticks);
#else
  servos[i].write(angle);
#endif
}

void relaxAll() {
  // Stop sending pulses so servos don't buzz/heat while holding against the string
  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
#if USE_PCA9685
    pwm.setPWM(CHANNELS[i], 0, 0);
#else
    servos[i].detach();
#endif
  }
  relaxed = true;
}

void wakeAll() {
  if (!relaxed) return;
  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
#if USE_PCA9685
    writeServo(i, (int)currentAngle[i]);
#else
    servos[i].write((int)currentAngle[i]);
    servos[i].attach(PINS[i]);
#endif
  }
  relaxed = false;
}

// ---------- finger control ----------

// bend: 0 = fully open, 100 = fully closed
int bendToAngle(uint8_t i, int bend) {
  bend = constrain(bend, 0, 100);
  return map(bend, 0, 100, openAngle[i], closedAngle[i]);
}

void setFinger(uint8_t i, int bend) {
  wakeAll();
  targetAngle[i] = bendToAngle(i, bend);
}

void setHand(const int bends[NUM_FINGERS]) {
  for (uint8_t i = 0; i < NUM_FINGERS; i++) setFinger(i, bends[i]);
}

bool atTarget() {
  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
    if (abs(currentAngle[i] - targetAngle[i]) > 0.5) return false;
  }
  return true;
}

// Moves every servo a little toward its target. Call often.
void updateServos() {
  if (relaxed || millis() - lastStep < STEP_MS) return;
  lastStep = millis();

  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
    float diff = targetAngle[i] - currentAngle[i];
    if (abs(diff) <= speedDegPerStep) currentAngle[i] = targetAngle[i];
    else currentAngle[i] += (diff > 0 ? speedDegPerStep : -speedDegPerStep);
    writeServo(i, (int)currentAngle[i]);
  }
}

// Used by the demo sequences: wait for the move to finish, then hold a bit
void waitMove(unsigned long holdMs) {
  while (!atTarget()) updateServos();
  unsigned long start = millis();
  while (millis() - start < holdMs) updateServos();
}

// ---------- gestures (thumb, index, middle, ring, pinky) ----------

const int G_OPEN[]   = {  0,   0,   0,   0,   0};
const int G_FIST[]   = {100, 100, 100, 100, 100};
const int G_POINT[]  = {100,   0, 100, 100, 100};
const int G_PEACE[]  = {100,   0,   0, 100, 100};
const int G_THUMBS[] = {  0, 100, 100, 100, 100};
const int G_ROCK[]   = {100,   0, 100, 100,   0};
const int G_LOVE[]   = {  0,   0, 100, 100,   0};
const int G_OK[]     = {100, 100,   0,   0,   0};
const int G_CALL[]   = {  0, 100, 100, 100,   0};

void countToFive() {
  const int steps[6][NUM_FINGERS] = {
    {100, 100, 100, 100, 100},
    {100,   0, 100, 100, 100},
    {100,   0,   0, 100, 100},
    {100,   0,   0,   0, 100},
    {100,   0,   0,   0,   0},
    {  0,   0,   0,   0,   0},
  };
  for (uint8_t s = 0; s < 6; s++) { setHand(steps[s]); waitMove(600); }
}

void wave() {
  // Fingers curl one after another, pinky to thumb, then back
  setHand(G_OPEN); waitMove(200);
  for (int i = NUM_FINGERS - 1; i >= 0; i--) { setFinger(i, 100); waitMove(80); }
  for (int i = 0; i < NUM_FINGERS; i++)      { setFinger(i, 0);   waitMove(80); }
}

void demo() {
  const int* moves[] = {G_FIST, G_OPEN, G_POINT, G_PEACE, G_THUMBS, G_ROCK, G_OK, G_OPEN};
  for (uint8_t m = 0; m < sizeof(moves) / sizeof(moves[0]); m++) {
    setHand(moves[m]);
    waitMove(800);
  }
  countToFive();
  wave(); wave();
}

// ---------- serial commands ----------

void printHelp() {
  Serial.println(F("\n--- Robot Hand Commands ---"));
  Serial.println(F("open | fist | point | peace | thumbs | rock | love | ok | call"));
  Serial.println(F("count | wave | demo"));
  Serial.println(F("f <1-5> <0-100>   bend one finger (0=open, 100=closed)"));
  Serial.println(F("a <1-5> <0-180>   raw servo angle (for calibration)"));
  Serial.println(F("speed <1-20>      movement speed"));
  Serial.println(F("relax             stop holding (servos go limp, no buzzing)"));
  Serial.println(F("status            show finger angles"));
  Serial.println(F("Fingers: 1=thumb 2=index 3=middle 4=ring 5=pinky"));
}

void printStatus() {
  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
    Serial.print(i + 1); Serial.print(F(" "));
    Serial.print(NAMES[i]); Serial.print(F(": angle "));
    Serial.print((int)currentAngle[i]);
    Serial.print(F("  (open ")); Serial.print(openAngle[i]);
    Serial.print(F(", closed ")); Serial.print(closedAngle[i]);
    Serial.println(F(")"));
  }
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  if (cmd.length() == 0) return;

  int sp1 = cmd.indexOf(' ');
  String word = (sp1 < 0) ? cmd : cmd.substring(0, sp1);
  String rest = (sp1 < 0) ? "" : cmd.substring(sp1 + 1);
  rest.trim();
  int sp2 = rest.indexOf(' ');
  int arg1 = rest.toInt();
  int arg2 = (sp2 < 0) ? -1 : rest.substring(sp2 + 1).toInt();

  if      (word == "open")   setHand(G_OPEN);
  else if (word == "fist" || word == "close") setHand(G_FIST);
  else if (word == "point")  setHand(G_POINT);
  else if (word == "peace")  setHand(G_PEACE);
  else if (word == "thumbs") setHand(G_THUMBS);
  else if (word == "rock")   setHand(G_ROCK);
  else if (word == "love")   setHand(G_LOVE);
  else if (word == "ok")     setHand(G_OK);
  else if (word == "call")   setHand(G_CALL);
  else if (word == "count")  countToFive();
  else if (word == "wave")   wave();
  else if (word == "demo")   demo();
  else if (word == "relax")  { relaxAll(); Serial.println(F("Servos relaxed. Any move command wakes them.")); }
  else if (word == "status") printStatus();
  else if (word == "help")   printHelp();
  else if (word == "speed") {
    speedDegPerStep = constrain(arg1, 1, 20);
    Serial.print(F("Speed = ")); Serial.println(speedDegPerStep);
  }
  else if (word == "f" && arg1 >= 1 && arg1 <= 5 && arg2 >= 0) {
    setFinger(arg1 - 1, arg2);
  }
  else if (word == "a" && arg1 >= 1 && arg1 <= 5 && arg2 >= 0) {
    wakeAll();
    targetAngle[arg1 - 1] = constrain(arg2, 0, 180);
    Serial.print(NAMES[arg1 - 1]); Serial.print(F(" -> ")); Serial.println(targetAngle[arg1 - 1]);
  }
  else {
    Serial.print(F("Unknown command: ")); Serial.println(cmd);
    Serial.println(F("Type 'help'"));
    return;
  }
  Serial.println(F("ok"));
}

// ---------- setup / loop ----------

void setup() {
  Serial.begin(115200);

#if USE_PCA9685
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50);
  delay(10);
#endif

  // Start every finger open
  for (uint8_t i = 0; i < NUM_FINGERS; i++) {
    currentAngle[i] = openAngle[i];
    targetAngle[i]  = openAngle[i];
#if USE_PCA9685
    writeServo(i, openAngle[i]);
#else
    servos[i].write(openAngle[i]);   // set position before attach = no startup jump
    servos[i].attach(PINS[i]);
#endif
    delay(150);                       // stagger so all 5 don't draw a current spike at once
  }

  Serial.println(F("Robot hand ready."));
  printHelp();
}

void loop() {
  if (Serial.available()) {
    handleCommand(Serial.readStringUntil('\n'));
  }
  updateServos();
}
