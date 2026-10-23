> Current status: Planned. The old ArUco marker prototype is retired (history in [[WorkshopArm CV Prototype Docs]]).

## Overview
Computer vision pipeline. Watches the people and the workspace. The arm's own joint positions come from the AS5600 encoders, not from cameras.

## Cameras
1. **Room/Person** — behind the arm, wide view of people (~15–20 FPS)
2. **Workshop/Arm** — ~4 ft above the work area on the bar the arm hangs from, angled down at the arm and table (~10–15 FPS)

Wrist camera = Future Improvement.

## Does
- YOLO-pose on everyone (on Intel graphics via OpenVINO): position, distance, movement speed, safety
- Tracker (ByteTrack) keeps person IDs between frames
- MediaPipe Holistic on User 1's crop: face, hands, gaze
- Holistic on bystanders now and then (rotating or triggered)
- Mouth tracking for Echo Arch's speaker detection

## Attention cycle
- Repeating cycle to find User 1 (the person the arm is focused on)
- User 1 can change based on context
- If unsure, attention splits between max 2 people

## Talks to
Signal Fusion, Facial Affect, Echo Arch, Handshake, Civil, Telemetry.

## Open
- Room/Person camera behind the arm may get blocked by the arm — test placement
- Real speed on the laptop (`src/holistic_fps_test.py`)
