# ------- KEYBOARD CONTROL ---------------------------------------------------
# Manual jog controller, no AI involved. Live camera window shows both the
# commanded angles and the real camera-measured ones.
#
# Controls:
#   left/right - shoulder
#   up/down    - elbow1
#   a/d        - elbow2  (only two axes on the arrow keys, elbow2 gets its
#                          own since there are three joints)
#   r          - reset to neutral (90/90/90)
#   q          - quit

import argparse

import cv2

from joint_angles import calculate_joint_angles
from servo_io import DummyServoLink, ServoLink

WINDOW_NAME = "Manual Control - arrows: shoulder/elbow1, a/d: elbow2, r: reset, q: quit"
STEP_DEG = 5

# Arrow key codes as reported by cv2.waitKey() & 0xFF on Linux/X11. If these
# don't respond on your setup, unrecognized key presses print their raw code
# to the console so they can be swapped in here.
KEY_LEFT, KEY_UP, KEY_RIGHT, KEY_DOWN = 81, 82, 83, 84


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


def clamp(v):
    return max(0.0, min(180.0, v))


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

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    cam = cv2.VideoCapture(args.camera)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cam_ok = cam.isOpened()
    if not cam_ok:
        print(f"Warning: could not open camera {args.camera} - jogging blind, no preview or measurement.")

    link = DummyServoLink() if args.dry_run else ServoLink(args.port)
    link.connect()

    angles = {"shoulder": 90.0, "elbow1": 90.0, "elbow2": 90.0}
    for joint, deg in angles.items():
        link.send_angle(joint, deg)

    print("Controls: left/right = shoulder, up/down = elbow1, a/d = elbow2, r = reset, q = quit")
    print(f"shoulder={angles['shoulder']:.0f} elbow1={angles['elbow1']:.0f} elbow2={angles['elbow2']:.0f}")

    try:
        while True:
            frame = None
            if cam_ok:
                for _ in range(3):
                    cam.grab()
                success, frame = cam.retrieve()
                if not success:
                    frame = None

            if frame is None:
                # cv2.waitKey needs a real window to receive key events, so
                # show a blank placeholder when there's no camera.
                import numpy as np
                frame = np.zeros((200, 640, 3), dtype="uint8")
                cv2.putText(frame, "no camera - jogging blind", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = detector.detectMarkers(gray)
                centers = marker_centers_by_id(corners, ids)
                measured = calculate_joint_angles(centers)
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                draw_skeleton(frame, centers)

                m_shoulder = measured["shoulder"]
                m_elbow = measured["elbow"]
                m_shoulder_s = "?" if m_shoulder is None else f"{m_shoulder:.0f}"
                m_elbow_s = "?" if m_elbow is None else f"{m_elbow:.0f}"
                cv2.putText(frame, f"measured   shoulder:{m_shoulder_s} elbow:{m_elbow_s}",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

            cv2.putText(frame, (f"commanded  shoulder:{angles['shoulder']:.0f} "
                                 f"elbow1:{angles['elbow1']:.0f} elbow2:{angles['elbow2']:.0f}"),
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(30) & 0xFF
            moved = False

            if key == KEY_LEFT:
                angles["shoulder"] = clamp(angles["shoulder"] - STEP_DEG)
                moved = True
            elif key == KEY_RIGHT:
                angles["shoulder"] = clamp(angles["shoulder"] + STEP_DEG)
                moved = True
            elif key == KEY_UP:
                angles["elbow1"] = clamp(angles["elbow1"] + STEP_DEG)
                moved = True
            elif key == KEY_DOWN:
                angles["elbow1"] = clamp(angles["elbow1"] - STEP_DEG)
                moved = True
            elif key == ord("a"):
                angles["elbow2"] = clamp(angles["elbow2"] - STEP_DEG)
                moved = True
            elif key == ord("d"):
                angles["elbow2"] = clamp(angles["elbow2"] + STEP_DEG)
                moved = True
            elif key == ord("r"):
                angles = {"shoulder": 90.0, "elbow1": 90.0, "elbow2": 90.0}
                moved = True
            elif key == ord("q"):
                break
            elif key != 255:
                print(f"(unrecognized key, raw code: {key})")

            if moved:
                for joint, deg in angles.items():
                    link.send_angle(joint, deg)
                print(f"shoulder={angles['shoulder']:.0f} elbow1={angles['elbow1']:.0f} elbow2={angles['elbow2']:.0f}")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        link.close()


if __name__ == "__main__":
    main()
