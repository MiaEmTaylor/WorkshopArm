> Current status: Planned, not built.

## Overview
Low-level motor control + most of the actual arm and hand control. Takes general direction from Puppeteer and works out and runs the movement.

## Does
- Turns goals into movement, using [[IK Protocol|IK]]
- Runs the motors: steppers (TMC2209), worm motor (BTS7960), servos (PCA9685), N20s (TB6612)
- Reads the 6 AS5600 joint encoders; feedback loop runs on the laptop
- Handles joint end limits
- Ramps speed up/down to cut current spikes

## Talks to
Puppeteer, IK, Civil, Recovery, Uno + ESP32 boards over USB.

## Open
- Serial message format between the laptop and the boards
