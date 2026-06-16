> Current status: Prototype complete — live CV tracking working. Planning arm movement control phase. See [[WorkshopArm CV Prototype Docs]] for full build notes.

---

## Overview

The Vision Protocol handles the computer vision pipeline for WorkshopArm. In its current prototype form, it tracks the position of the arm's major joints in real time using ArUco fiducial markers and an OpenCV detection pipeline, producing a live overlay with joint centers and skeleton lines connecting them.

---

## How It Works

### Markers
Four ArUco markers (DICT_4X4_50) are physically attached to the arm at each major joint. Each marker has a hardcoded ID mapped to a joint:

| Marker ID | Joint |
|-----------|-------|
| 0 | J0 — Base |
| 1 | J1 — Shoulder |
| 2 | J2 — Elbow |
| 3 | J3 — Wrist |

---

### Pipeline

1. **Capture** — Live feed pulled from webcam via OpenCV
2. **Undistort** — Frame corrected using calibration data loaded from `calibration.json` (camera matrix + distortion coefficients)
3. **Grayscale conversion** — Frame converted to grayscale for marker detection
4. **Marker detection** — ArUco detector scans the frame and returns corner coordinates and IDs for any found markers
5. **Center calculation** — Center point of each detected marker is computed by averaging its four corners
6. **Overlay** — Detected markers are boxed and labeled, green dots drawn at each joint center
7. **Skeleton drawing** — Lines drawn between connected joint centers following the chain: J0 → J1 → J2 → J3

---

### Connections

```python
connections = [(J0, J1), (J1, J2), (J2, J3)]
```

If both endpoints of a connection are detected in the current frame, a line is drawn. If a marker drops out, that segment just doesn't render — nothing breaks.

---

### Camera Calibration

Calibration is handled separately via a ChArUco board calibration script. Output is saved to `calibration.json` and loaded at runtime. This corrects for lens distortion before detection runs.

Required capture resolution:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

---

## Current Limitations

- Angle calculation between joints not yet implemented (dot product method, NumPy — stubbed in code)
- `solvePnP` for full 3D rotation per marker not yet implemented — currently 2D center tracking only
- No filtering applied to joint positions (Kalman filter planned for smoother output)
- Camera index hardcoded — needs to be changed per machine

---

## Planned (not built)

- Joint angle output via dot product method
- `solvePnP` for 3D pose per marker
- Kalman filtering for smooth servo-ready output
- Serial/SSH data output to servos

---

## Next Phase — Arm Movement Control

### Goal
Move J3 (arm tip) to track and touch ID4 (a free-placed target marker, not a joint).

### Order of Operations

1. **solvePnP** — get full 3D pose (tvec + rvec) for all joint markers. Must be stable before anything else.
2. **Joint angles** — dot product method between 3D joint vectors. Define rotation axes per joint (J0=base rotate, J1=shoulder flex, J2=elbow flex, J3=wrist rotate+deviate). Already stubbed.
3. **New marker setup** — print ID4+, expand dictionary, recalibrate, update `calibration.json`
4. **Movement loop** — compute 3D error between J3 and ID4, map to servo targets via IK, send over serial (PySerial), repeat every frame
5. **Kalman filter** — smooth output before it hits the Arduino

### Arduino Side (planned)
Receive target angles → drive servos → report back actual positions for confidence scoring.