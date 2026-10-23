# Overview
Aiden needs a physical part. an arm. a workshop tool. an agent that handles everything from screwing parts in, to opening jars, to adding personality to your home system. 
# Protocol Architecture
Security isn't its own protocol, it's built into every protocol. Every protocol hands its readings to Signal Fusion, and Civil can override all of them.

## Control

### Puppeteer Protocol
The boss. Makes the general decisions about what the arm should do and directs Marionette (e.g. "touch user's hand"). Uses Handshake's info about who it's working with.
### Marionette Protocol
Low-level motor control + most of the actual arm and hand control. Takes general direction from Puppeteer, works out and runs the movement. Talks to IK. Reads the joint encoders and handles joint end limits.
### IK Protocol
Inverse kinematics. Turns a target position into joint angles for Marionette.
### Civil Protocol
Operational safety enforcement. Overrides everything, including Puppeteer. Force limits (handshake grip ceiling 22 lbs), speed limits, distance rules, e-stop, strain/overload. Built for competent adults: safe without being useless.
### [[Digit Docking Protocol]]
Manages finger attachment swapping and tool configuration. Handles the docking sensors.

## Sensing

### Vision Protocol
Computer vision pipeline. Two cameras: Room/Person (behind the arm, wide view of people) and Workshop/Arm (above the work area, angled down at the arm and table). YOLO-pose for everyone, MediaPipe Holistic for User 1, tracker keeps person IDs. Runs the attention cycle: detects User 1, can change with context, splits between max 2 people when unsure.
### [[Facial Affect Protocol]]
Reads a person's live emotional state as valence/arousal + confidence. EmoNet for new people (low confidence), personal calibration for known people (high confidence), built up automatically over time. Used as a comfort monitor, readiness check, personality cue, feedback signal and conversation context. Code lives in its own repo for now.
### Echo Arch
Full audio system. Mic input, voice words (speech-to-text), voice tone, voiceprints, speaker detection (whose mouth is open = "possibly speaking"), audio output.
### Signal Fusion Protocol
Combines the output of every other protocol (and all finger/palm sensor data) into one clean data packet. Priority rules on top, confidence weighting underneath.
Priority: Civil > task context > explicit input > voice words > pressure > gestures > gaze > face/affect.

## People

### Handshake Protocol
Everything about WHO. Runs the initializer (explain, handshake, photo, grip, "just talk" voice sample, name), recognizes returning people (face + voice, guest mode when unsure), and keeps each person's profile: grip, voiceprint, affect calibration, habits, preferences and reactions. Adjusts speed, distance, handoff style and personality tone per person.
### Learning Protocol
Feedback over time across all users: successes and the dramatic corrections/reactions that show up often. Scores all data for the learned model. Safety settings can only auto-adjust toward safer.
### Service Protocol
Human interaction and command parsing: explicit input, commands, task context. Heavier implementation than standard ArchLogic.
### Personality Protocol
Handles persona, voice generation, personality-fitted motion suggestions, and thought process generation.
### GPT Protocol
Routes selected tasks to OpenAI.

## System

### Recovery Protocol
System diagnostics / health monitoring + power control. Temperature (thermistors), cooling, strain/current.
### Audit Protocol
Full system logging and event history. Safety records are kept permanently.
### Telemetry Protocol
Readings + visual display of the cameras and tracking on a monitor.
