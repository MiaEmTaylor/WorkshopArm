# ------- POINT CONTROL -------------------------------------------------------
# Click anywhere in the live camera window and the arm tries to point its
# wrist marker (J3) there, continuously, in real time.
#
# No inverse kinematics or camera-to-arm calibration - instead it
# auto-calibrates on startup: nudges shoulder, elbow1, and elbow2 - each
# independently, not mirrored - a known amount and watches how the wrist
# marker moves on screen in response. That gives a simple local "pixels
# moved per degree" model (a 2x3 Jacobian, one column per joint). Every
# frame after that, it solves the minimum-norm correction across all three
# joints that should reduce the gap between the wrist marker and your last
# click - classic proportional visual servoing, not true 3D pointing.
#
# Three joints for a 2D (x,y) target is redundant on purpose: when one
# joint saturates at 0 or 180 and can't contribute any more, the solve
# naturally leans on whichever other joints still have room, instead of
# getting stuck. If the target genuinely can't be reached (all three maxed
# out in the needed direction, or a joint has no visible effect at all),
# stall detection notices the distance to target has stopped improving and
# says so instead of silently spinning forever.

import argparse
import time
from collections import deque

import cv2
import numpy as np

JOINTS = ["shoulder", "elbow1", "elbow2"]

CALIBRATION_STEP_DEG = 15
SETTLE_SECONDS = 0.6
CONTROL_GAIN = 0.6      # fraction of the estimated correction applied each frame
MAX_STEP_DEG = 6        # per-frame clamp so it doesn't lurch
ARRIVED_PIXELS = 15
STALL_HISTORY_FRAMES = 20   # how many recent frames to judge "not improving" over
STALL_IMPROVEMENT_PIXELS = 5  # must close at least this many pixels over that window
WINDOW_NAME = "Point Control - click anywhere to aim the arm there, q to quit"

SKELETON_CONNECTIONS = [(0, 1), (1, 2), (2, 3)]


def marker_center(marker_corners):
    pts = marker_corners.reshape(4, 2)
    return pts.mean(axis=0)


def marker_centers_by_id(corners, ids):
    if ids is None:
        return {}
    return {int(marker_id): marker_center(marker_corners)
            for marker_id, marker_corners in zip(ids.ravel(), corners)}


def draw_skeleton(frame, centers):
    for start_id, end_id in SKELETON_CONNECTIONS:
        if start_id in centers and end_id in centers:
            cv2.line(frame, tuple(centers[start_id].astype(int)), tuple(centers[end_id].astype(int)),
                      (255, 0, 0), 2)


def grab(cam, detector):
    for _ in range(3):
        cam.grab()
    ok, frame = cam.retrieve()
    if not ok:
        return None, {}
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    return frame, marker_centers_by_id(corners, ids)


def wrist_pos(cam, detector):
    for _ in range(5):
        _, centers = grab(cam, detector)
        if 3 in centers:
            return centers[3]
        time.sleep(0.1)
    return None


def calibrate(link, cam, detector, angles):
    """Nudges each joint independently, watches how the wrist marker (J3)
    moves on screen, builds {joint: (dx, dy) per degree}."""
    jacobian = {}
    for joint in JOINTS:
        before = wrist_pos(cam, detector)
        if before is None:
            print(f"Can't see the wrist marker (J3) to calibrate {joint} - is it in frame?")
            jacobian[joint] = np.array([0.0, 0.0])
            continue

        delta = CALIBRATION_STEP_DEG
        new_angle = min(180.0, angles[joint] + delta)
        if new_angle == angles[joint]:
            delta = -delta
            new_angle = max(0.0, angles[joint] + delta)

        link.send_angle(joint, new_angle)
        time.sleep(SETTLE_SECONDS)
        after = wrist_pos(cam, detector)
        link.send_angle(joint, angles[joint])  # back to where it started
        time.sleep(SETTLE_SECONDS)

        if after is None:
            print(f"Lost the wrist marker while calibrating {joint}.")
            jacobian[joint] = np.array([0.0, 0.0])
            continue
        jacobian[joint] = (after - before) / delta
        print(f"calibrated {joint}: moves the tip {jacobian[joint]} px per degree")

    return jacobian


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=1, help="OpenCV camera index")
    parser.add_argument("--port", type=str, default=None, help="Serial port for the Arduino, e.g. /dev/ttyACM0")
    parser.add_argument("--dry-run", action="store_true", help="Use DummyServoLink instead of real hardware")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.dry_run and not args.port:
        raise SystemExit("--port is required unless --dry-run is set")

    # Imported late so this file can still be parsed/tested without pyserial etc.
    from servo_io import DummyServoLink, ServoLink

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    cam = cv2.VideoCapture(args.camera)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cam.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    link = DummyServoLink() if args.dry_run else ServoLink(args.port)
    link.connect()

    angles = {j: 90.0 for j in JOINTS}
    for j in JOINTS:
        link.send_angle(j, angles[j])
    time.sleep(1.0)

    print("Calibrating - this moves the arm a bit on its own first, stand back.")
    jacobian = calibrate(link, cam, detector, angles)
    J = np.stack([jacobian[j] for j in JOINTS], axis=1)  # 2x3, one column per joint

    target = {"pos": None}
    dist_history = deque(maxlen=STALL_HISTORY_FRAMES)
    stalled = False

    def on_click(event, x, y, flags, userdata):
        nonlocal stalled
        if event == cv2.EVENT_LBUTTONDOWN:
            target["pos"] = np.array([float(x), float(y)])
            dist_history.clear()
            stalled = False
            print(f"target set: {x},{y}")

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_click)
    print("Click anywhere in the window to aim the arm there. Press q to quit.")

    try:
        while True:
            frame, centers = grab(cam, detector)
            if frame is None:
                if cv2.waitKey(30) & 0xFF == ord("q"):
                    break
                continue

            draw_skeleton(frame, centers)
            for c in centers.values():
                cv2.circle(frame, tuple(c.astype(int)), 5, (0, 255, 0), -1)
            if target["pos"] is not None:
                cv2.circle(frame, tuple(target["pos"].astype(int)), 10, (0, 0, 255), 2)

            wrist = centers.get(3)
            if wrist is not None and target["pos"] is not None:
                error = target["pos"] - wrist
                dist = float(np.linalg.norm(error))
                cv2.line(frame, tuple(wrist.astype(int)), tuple(target["pos"].astype(int)), (0, 0, 255), 1)

                if dist <= ARRIVED_PIXELS:
                    dist_history.clear()
                    stalled = False
                elif stalled:
                    pass  # already told the user it can't get closer - don't keep spamming moves
                else:
                    dist_history.append(dist)
                    if (len(dist_history) == STALL_HISTORY_FRAMES
                            and dist_history[0] - min(dist_history) < STALL_IMPROVEMENT_PIXELS):
                        stalled = True
                        print(f"Can't get any closer to that point - stuck about {dist:.0f}px away. "
                              f"All reachable joints are maxed out or have no more effect here. "
                              f"Click a different point to try again.")
                    else:
                        try:
                            delta, *_ = np.linalg.lstsq(J, error, rcond=None)
                        except np.linalg.LinAlgError:
                            delta = np.zeros(len(JOINTS))
                        delta = np.clip(delta * CONTROL_GAIN, -MAX_STEP_DEG, MAX_STEP_DEG)

                        for j, d in zip(JOINTS, delta):
                            angles[j] = float(np.clip(angles[j] + d, 0, 180))
                            link.send_angle(j, angles[j])

            status = "STUCK - click elsewhere" if stalled else "click to aim, q to quit"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 0, 255) if stalled else (255, 255, 255), 2)
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()
        link.close()


if __name__ == "__main__":
    main()
