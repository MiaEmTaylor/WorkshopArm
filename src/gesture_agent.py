# ------- GESTURE AGENT ------------------------------------------------------
# Reads the arm's current camera-tracked position, takes a short text
# description of what's happening, and asks OpenAI to design a gesture as
# an ordered list of full-arm POSES (all three joints at once). The code
# then smoothly moves through those poses in order. One API call per
# situation - no per-step back-and-forth, which was slow and finicky.
#
# Same tool-calling pattern as facial_rec_prototype/apps/profile_agent.py:
# one forced tool call per turn, structured JSON out.

import argparse
import json
import queue
import threading
import time
from pathlib import Path

import cv2
from dotenv import load_dotenv
from openai import OpenAI

from joint_angles import calculate_joint_angles
from servo_io import DummyServoLink, ServoLink

# OPENAI_API_KEY lives in the sibling facial_rec_prototype project's .env,
# not in this repo - same key profile_agent.py uses.
ENV_PATH = Path(__file__).parent.parent.parent / "facial_rec_prototype" / ".env"
load_dotenv(ENV_PATH, override=True)

OPENAI_MODEL = "gpt-4o"
WINDOW_NAME = "Gesture Agent - Live Feed"
JOINTS = ["shoulder", "elbow1", "elbow2"]

# Small step + short settle reads as smooth continuous motion instead of
# visible jumps, and asks less torque/current of the servo at once than one
# big jump - all three joints have confirmed working power.
MICRO_STEP_DEG = 2
MICRO_STEP_SETTLE_SECONDS = 0.06
HOLD_SECONDS = 0.4  # pause at each pose before moving to the next

WANDER_SITUATION = (
    "Nothing in particular is happening - nobody gave you a specific situation. Explore some natural, "
    "idle movement on your own (a curious look around, a small stretch, anything that reads as alive "
    "rather than frozen). Keep it gentle and slow."
)
WANDER_PAUSE_SECONDS = 3.0  # gap between one idle gesture finishing and the next being composed

POSE_TOOL = {
    "type": "function",
    "function": {
        "name": "perform_gesture",
        "description": "Compose a gesture as an ordered sequence of full-arm poses to move through.",
        "strict": True,
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "What gesture you're doing and why it fits the situation. One or two "
                                    "sentences.",
                },
                "poses": {
                    "type": "array",
                    "description": "3-8 poses, moved through in order, each held briefly. E.g. an extend "
                                    "pose, then several alternating weave poses for a wave, then optionally "
                                    "a return-to-neutral pose.",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "shoulder": {"type": "number", "description": "Target angle, 0-180 degrees."},
                            "elbow1": {"type": "number", "description": "Target angle, 0-180 degrees."},
                            "elbow2": {"type": "number", "description": "Target angle, 0-180 degrees."},
                        },
                        "required": ["shoulder", "elbow1", "elbow2"],
                    },
                },
            },
            "required": ["reasoning", "poses"],
        },
    },
}

SYSTEM_PROMPT = (
    "You control a real robot arm with three actuated servos: shoulder, elbow1, elbow2 (0-180 degrees each). "
    "There is no gripper and no object detection beyond tracking the arm's own position.\n\n"
    "Given a situation, design a gesture (a wave, a nod, offering a handshake, anything human-like that "
    "fits) as an ordered list of POSES - each pose is a target angle for all three servos at once. The arm "
    "moves smoothly through each pose in order, briefly holding at each before the next.\n\n"
    "A proper wave: an EXTEND pose (reach out - a real, clear change from the starting position, not a "
    "small nudge), then several WEAVE poses that alternate a WIDE range on elbow1 and/or elbow2 (e.g. 50 "
    "and 130 - not a narrow 40-to-50 wiggle), repeated 3-4 times, optionally ending on a neutral pose "
    "(shoulder=90, elbow1=90, elbow2=90).\n\n"
    "Use big, real angle differences between poses - the servos have real mechanical slop, so subtle "
    "differences won't read as motion at all. If nothing about the situation calls for a gesture, return "
    "a single neutral pose."
)


def marker_center(marker_corners):
    pts = marker_corners.reshape(4, 2)
    return pts.mean(axis=0)


def marker_centers_by_id(corners, ids):
    if ids is None:
        return {}
    return {int(marker_id): marker_center(marker_corners)
            for marker_id, marker_corners in zip(ids.ravel(), corners)}


# J0 base -> J1 shoulder -> J2 elbow -> J3 wrist, same chain as pose_est.py
SKELETON_CONNECTIONS = [(0, 1), (1, 2), (2, 3)]


def draw_skeleton(frame, centers):
    for start_id, end_id in SKELETON_CONNECTIONS:
        if start_id in centers and end_id in centers:
            cv2.line(frame, tuple(centers[start_id].astype(int)), tuple(centers[end_id].astype(int)),
                      (255, 0, 0), 2)


def read_current_angles(cam, detector):
    """Flushes any stale buffered frames (cv2.VideoCapture can otherwise
    hand back a several-frames-old picture) then grabs the current one.
    Shows it live (with overlay) and returns
    {"shoulder": deg or None, "elbow": deg or None}."""
    for _ in range(3):
        cam.grab()
    success, frame = cam.retrieve()
    if not success:
        return {"shoulder": None, "elbow": None}
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    centers = marker_centers_by_id(corners, ids)
    angles = calculate_joint_angles(centers)

    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    draw_skeleton(frame, centers)
    if angles["shoulder"] is not None:
        cv2.putText(frame, f"shoulder: {angles['shoulder']:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if angles["elbow"] is not None:
        cv2.putText(frame, f"elbow: {angles['elbow']:.1f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow(WINDOW_NAME, frame)
    cv2.waitKey(1)
    return angles


def _ease(frac):
    """Smoothstep: zero velocity at both ends of the move instead of a
    constant speed that starts/stops abruptly - that abrupt start/stop is
    what reads as a 'jerk', not the step size itself."""
    return frac * frac * (3 - 2 * frac)


def execute_pose(link, cam, detector, cam_ok, pose, last_commanded):
    """Smoothly moves all three joints from their last commanded angles to
    `pose` at once (not one joint fully, then the next), so it reads as one
    natural, eased movement instead of a sequence of single-joint twitches."""
    start = {j: last_commanded.get(j, 90.0) for j in JOINTS}
    target = {j: pose[j] for j in JOINTS}
    steps = max(1, int(max(abs(target[j] - start[j]) for j in JOINTS) / MICRO_STEP_DEG))

    for i in range(1, steps + 1):
        frac = _ease(i / steps)
        for j in JOINTS:
            angle = start[j] if steps == 1 else start[j] + (target[j] - start[j]) * frac
            link.send_angle(j, angle)
        time.sleep(MICRO_STEP_SETTLE_SECONDS)
        if cam_ok:
            read_current_angles(cam, detector)  # live preview only, not fed back into reasoning

    for j in JOINTS:
        last_commanded[j] = target[j]


def run_turn(client, link, cam, detector, cam_ok, situation, last_commanded):
    angles = read_current_angles(cam, detector) if cam_ok else {"shoulder": None, "elbow": None}
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Situation: {situation if situation else '(nothing reported)'}\n"
            f"Starting position: shoulder={angles['shoulder']}, elbow={angles['elbow']}"
        )},
    ]

    resp = client.chat.completions.create(
        model=OPENAI_MODEL, messages=conversation,
        tools=[POSE_TOOL], tool_choice={"type": "function", "function": {"name": "perform_gesture"}},
    )
    call = resp.choices[0].message.tool_calls[0]
    result = json.loads(call.function.arguments)
    print(f"  {result['reasoning']}")

    for i, pose in enumerate(result["poses"]):
        print(f"  pose {i + 1}/{len(result['poses'])}: {pose}")
        execute_pose(link, cam, detector, cam_ok, pose, last_commanded)
        time.sleep(HOLD_SECONDS)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=1, help="OpenCV camera index")
    parser.add_argument("--port", type=str, default=None, help="Serial port for the Arduino, e.g. /dev/ttyACM0")
    parser.add_argument("--dry-run", action="store_true", help="Use DummyServoLink instead of real hardware")
    parser.add_argument("--wander", type=float, default=None,
                         help="Instead of waiting for typed input, move on its own for this many seconds "
                              "(idle/exploratory gestures, no situation needed). Press 'q' to stop early.")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.dry_run and not args.port:
        raise SystemExit("--port is required unless --dry-run is set")

    client = OpenAI()  # reads OPENAI_API_KEY from the environment

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    cam = cv2.VideoCapture(args.camera)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cam_ok = cam.isOpened()
    if not cam_ok:
        print(f"Warning: could not open camera {args.camera} - position will be reported as unknown.")

    link = DummyServoLink() if args.dry_run else ServoLink(args.port)
    link.connect()

    # Tracks each servo's last commanded angle across turns, since nothing
    # else remembers it - starts at a guessed neutral 90 until the first
    # real move for that joint.
    last_commanded = {"shoulder": 90.0, "elbow1": 90.0, "elbow2": 90.0}

    try:
        if args.wander is not None:
            print(f"Wandering on its own for {args.wander:.0f}s - press 'q' in the window to stop early.")
            end = time.time() + args.wander
            while time.time() < end:
                run_turn(client, link, cam, detector, cam_ok, WANDER_SITUATION, last_commanded)
                stop_early = False
                pause_end = time.time() + WANDER_PAUSE_SECONDS
                while time.time() < pause_end:
                    if cam_ok:
                        read_current_angles(cam, detector)  # live preview
                    if cv2.waitKey(30) & 0xFF == ord('q'):
                        stop_early = True
                        break
                if stop_early:
                    break
            print("Done wandering.")
            return

        # input() blocks, so it runs on its own thread - the main thread
        # keeps the camera window live (with 'q' to quit too) while waiting.
        situations = queue.Queue()

        def input_loop():
            while True:
                s = input("\nWhat's happening right now? (blank to skip, 'quit' to stop): ").strip()
                situations.put(s)
                if s.lower() == "quit":
                    return

        threading.Thread(target=input_loop, daemon=True).start()

        while True:
            try:
                situation = situations.get(timeout=0.03)
            except queue.Empty:
                if cam_ok:
                    read_current_angles(cam, detector)  # just for the live preview
                elif cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                continue

            if situation.lower() == "quit":
                break
            run_turn(client, link, cam, detector, cam_ok, situation, last_commanded)
    finally:
        cam.release()
        cv2.destroyAllWindows()
        link.close()


if __name__ == "__main__":
    main()
