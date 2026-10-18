# ------- HOLISTIC SPEED TEST ---------------------------------------------
# headless test for the brain laptop. no window, just prints numbers.
# runs mediapipe holistic on the webcam for a few seconds and reports
# how many frames per second it gets + how often it found face/body/hands.
#
# usage (from repo root, inside the uv venv):
#   python src/holistic_fps_test.py                 # camera 0, 20 sec, complexity 1
#   python src/holistic_fps_test.py --cam 0 --secs 30 --complexity 0

# ------- IMPORTS --------------------------------------------------------
import argparse
import time

import cv2
import mediapipe as mp

# ------- ARGS ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--cam", type=int, default=0, help="camera index (/dev/videoN)")
parser.add_argument("--secs", type=float, default=20, help="how long to run")
parser.add_argument("--complexity", type=int, default=1, choices=[0, 1, 2],
                    help="0 = fastest, 2 = most accurate")
parser.add_argument("--width", type=int, default=640)
parser.add_argument("--height", type=int, default=480)
args = parser.parse_args()

# ------- CAMERA ----------------------------------------------------------
live = cv2.VideoCapture(args.cam)
live.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
live.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
if not live.isOpened():
    raise SystemExit(f"could not open camera {args.cam}. try --cam 1")

# ------- RUN -------------------------------------------------------------
frames = 0
found = {"face": 0, "pose": 0, "left hand": 0, "right hand": 0}

with mp.solutions.holistic.Holistic(model_complexity=args.complexity) as holistic:
    print(f"running for {args.secs}s at {args.width}x{args.height}, "
          f"complexity {args.complexity}...")
    start = time.time()
    while time.time() - start < args.secs:
        ok, frame = live.read()
        if not ok:
            print("camera read failed, stopping")
            break

        # mediapipe wants RGB, opencv gives BGR
        results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frames += 1

        if results.face_landmarks:
            found["face"] += 1
        if results.pose_landmarks:
            found["pose"] += 1
        if results.left_hand_landmarks:
            found["left hand"] += 1
        if results.right_hand_landmarks:
            found["right hand"] += 1

    elapsed = time.time() - start

live.release()

# ------- REPORT ----------------------------------------------------------
print(f"\nframes: {frames} in {elapsed:.1f}s  ->  {frames / elapsed:.1f} FPS")
for part, count in found.items():
    pct = 100 * count / frames if frames else 0
    print(f"  {part:<11} seen in {pct:5.1f}% of frames")
