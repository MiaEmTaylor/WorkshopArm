### April - May 2026

- Software/concept routing architecture + early concepts, see [[Main Documentation]]
- Developed start of [[Workshop Agent - Planning Documentation/Protocols/Digit Docking Protocol|Digit Docking Protocol]] and [[Digit Docking Mechanism]]
- Computer vision pose estimation prototype, see [[WorkshopArm CV Prototype Docs]]

---
### June 2026

- Cleaning up Documentation (used Claude to reword messy documentation)
- 

---
### July 2026

- Early iterations of the facial emotion classifier

---
### August 2026 (1st-10th)

- Made the digit assembly blueprint — decided on finger scale/dimensions: 164mm tip-to-palm, split into base (66mm), middle (44mm), and upper (54mm) segments, 37mm diameter, with head/cuff/skirt/tip detailing (20mm/12mm/10mm/10mm)
- Finalized parts that need to be bought, including but not limited to: N20 motor, bolt actuator hardware
- Decided to put the tether joint on the upper two joints to improve grip strength
- Worked on finger dimensions and built a 3D model prototype
- Edited, cleaned, strengthened, and retrained — basically rebuilt — the facial recognition system for CV
- Changed the facial emotion classifier to a valence/arousal-based system, now also passing facial markers
- Built session recording (video + audio + per-frame face data, with offline transcription) to capture real, unposed reactions instead of just staged calibration photos
- Added a generic pretrained model (EmoNet) running alongside the personal calibration, to compare against and help auto-label session recordings
- Trained a pooled valence/arousal regression model (affect_model.json) from calibration + archived data + auto-labeled sessions, with a held-out accuracy check separate from training
- Ran a sanity check on whether recorded mouth shapes are consistent enough per-word to be worth building a lip-reader on top of (open question, not yet a feature)
- Built and iterated on an AI agent experiment that reads live facial affect and reasons about how to move it toward a target state, including a self-scored prediction ledger and a suppressed-smile detector as a second success signal
- Built a second, voice-enabled agent variant that listens, transcribes, and reasons about spoken content alongside facial readings
- Reorganized the codebase into folders by role (apps/core/modeling/data/logs/assets) for maintainability
- Reconciled two out-of-sync local copies of the project (one had newer drawings/docs, the other matched GitHub's reorganized structure), merged them into one, pushed to GitHub, and flattened the local folder path to `/home/mia_mousie/ARCHLOGIC/ArchArm`
- Added motion.py, tracking how fast facial signals are changing over time, not just their static level
- Added per-photo calibration diagnostics logging to trace category confusion back to specific images
- Built a third "showcase" agent combining all the readings/agent reasoning for demoing
- Wrote HOW_IT_WORKS.md documenting the full pipeline, and cut dated version-checkpoint branches on GitHub

---
### October 2026

**Oct 15–16**
- Reviewed the TSA Robotics System Design rules + rating form against where the project is; found the gaps (no moving robot yet, need the competitive robotics/outreach link, safety plan)
- Pulled the STLP Level 1 (2026) and Level 2 (2025) project rubrics and the Georgetown College Robot Use rubric; put all three in one rubric doc
- Made the big planner/question list; dropped ArUco markers for good
- Cooling decided: no liquid, springs + passive heatsinks + thermistors, fan only if testing needs it
- Decided the interaction signals (gestures, gaze, distance, speed, voice words/tone, pressure, explicit input, context) and the handshake initializer
- Reorganized protocols: removed Router and Security (security goes in every protocol), added GPT, IK, Signal Fusion, Handshake, Marionette, Telemetry
- Planned the multi-person vision pipeline (YOLO-pose for everyone, Holistic on User 1, tracker) and the attention cycle (max 2 people)
- Finger roles: pointer laser, swappable middle finger, pressure sensors on fingers + palm

**Oct 18**
- Sourced the electronics: ESP32 (hand board), N20s, TB6612, TMC2209, AS5600 encoders + TCA9548A, ADS1015, thermistors, pressure sensors
- Inventoried parts at home and things to harvest (Xbox brick, laptops, hoverboard, walkie-talkies)
- Picked the old HP laptop (i3-8145U, 12GB, Void Linux) as the brain instead of a Pi; fixed its clock (reset to 2018) and set up chrony
- Added `src/holistic_fps_test.py` to test how fast vision runs on the laptop

**Oct 19**
- Mr. Camenisch said TSA can buy parts with an itemized estimate
- Picked motors: NEMA 17 (shoulder rotation), NEMA 17 pancake (wrist rotation), 12V worm gear motor (shoulder lift), 270° high-torque servo (elbow), XL4016s for servo power
- Strength math: servos can't match human strength at 1.9× scale; human-level moved to Future Improvements

**Oct 21–22**
- Sized bearings for the 1.9× arm (lazy susans for shoulder + wrist rotation, 608s for the elbow)
- Cleaned up the cart and made the Parts Master List (buying soon / have / buying later)

**Oct 22–23**
- Answered the design questions: 2 cameras, "just talk" voice sample (voiceprint only), handshake grip (ceiling 22 lbs, 3 s release), Signal Fusion priority + confidence, recognition (face + voice), affect (EmoNet → personal calibration)
- Split Handshake into Puppeteer (boss), Handshake (who) and Learning (feedback)
- Wrote a basic page for every protocol and updated the protocol architecture
