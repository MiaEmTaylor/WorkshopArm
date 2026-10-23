# ------- SERVO CALIBRATION --------------------------------------------------
# Commands one joint through a sequence of angles, holds each for ~2s,
# records the CV-measured angle each frame, writes data/servo_log.csv,
# then prints a mean/max error summary per commanded position.
#
# No hardware:
#   python src/calibrate_servo.py --dry-run
# With hardware:
#   python src/calibrate_servo.py --joint elbow --port /dev/ttyACM0

import argparse
import csv
import json
import time
from pathlib import Path

import cv2
import numpy as np

from joint_angles import calculate_joint_angles
from servo_io import DummyServoLink, ServoLink

DATA_DIR = Path(__file__).parent.parent / "data"
LOG_PATH = DATA_DIR / "servo_log.csv"
LOG_FIELDS = ["timestamp", "joint", "commanded_deg", "measured_deg", "error_deg", "markers_visible"]

DEFAULT_SEQUENCE = [30.0, 60.0, 90.0, 120.0]
HOLD_SECONDS = 2.0

MARKERS_NEEDED = {
    "shoulder": (0, 1, 2),
    "elbow": (1, 2, 3),
}

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)  # newer OpenCV wraps detection in this class


def marker_center(marker_corners):
    pts = marker_corners.reshape(4, 2)
    return pts.mean(axis=0)


def marker_centers_by_id(corners, ids):
    if ids is None:
        return {}
    return {int(marker_id): marker_center(marker_corners)
            for marker_id, marker_corners in zip(ids.ravel(), corners)}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=1,
                         help="OpenCV camera index (default: 1, matches pose_est.py)")
    parser.add_argument("--port", type=str, default=None,
                         help="Serial port for the Arduino, e.g. /dev/ttyACM0. Required unless --dry-run.")
    parser.add_argument("--joint", choices=["shoulder", "elbow"], default="shoulder",
                         help="Which joint to calibrate (default: shoulder)")
    parser.add_argument("--dry-run", action="store_true",
                         help="Use DummyServoLink instead of real hardware")
    parser.add_argument("--sequence", type=float, nargs="+", default=DEFAULT_SEQUENCE,
                         help="Angles to command in degrees (default: 30 60 90 120)")
    return parser.parse_args()


def hold_and_measure(cam_ok, cam, mtx, dist, joint, commanded, rows):
    needed = MARKERS_NEEDED[joint]
    start = time.time()

    if not cam_ok:
        # No camera to sample - still record the commanded step so the CSV
        # stays valid, just with nothing measured.
        time.sleep(HOLD_SECONDS)
        rows.append({
            "timestamp": time.time(),
            "joint": joint,
            "commanded_deg": commanded,
            "measured_deg": None,
            "error_deg": None,
            "markers_visible": False,
        })
        return

    while time.time() - start < HOLD_SECONDS:
        success, frame = cam.read()
        if not success:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if mtx is not None:
            h, w = gray.shape[:2]
            newcameramtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
            gray = cv2.undistort(gray, mtx, dist, None, newcameramtx)

        corners, ids, _ = detector.detectMarkers(gray)
        centers = marker_centers_by_id(corners, ids)

        angles = calculate_joint_angles(centers)
        measured = angles[joint]
        markers_visible = all(m in centers for m in needed)
        error = None if measured is None else abs(measured - commanded)

        rows.append({
            "timestamp": time.time(),
            "joint": joint,
            "commanded_deg": commanded,
            "measured_deg": measured,
            "error_deg": error,
            "markers_visible": markers_visible,
        })


def print_summary(rows):
    by_commanded = {}
    for row in rows:
        by_commanded.setdefault(row["commanded_deg"], []).append(row["error_deg"])

    print("\nSummary (mean / max absolute error per commanded position):")
    for commanded, errors in sorted(by_commanded.items()):
        valid = [e for e in errors if e is not None]
        if not valid:
            print(f"  {commanded:>6.1f} deg: no measurements (markers never visible)")
            continue
        print(f"  {commanded:>6.1f} deg: mean={np.mean(valid):.2f} deg, max={np.max(valid):.2f} deg")


def main():
    args = parse_args()

    if not args.dry_run and not args.port:
        raise SystemExit("--port is required unless --dry-run is set")

    link = DummyServoLink() if args.dry_run else ServoLink(args.port)
    link.connect()

    cam = cv2.VideoCapture(args.camera)
    cam_ok = cam.isOpened()
    if not cam_ok:
        print(f"Warning: could not open camera {args.camera} - logging commanded angles only, no CV measurements.")

    calib_path = DATA_DIR / "calibration.json"
    mtx, dist = None, None
    if calib_path.exists():
        with open(calib_path) as f:
            calib = json.load(f)
        mtx = np.array(calib["mtx"])
        dist = np.array(calib["dist"])
    else:
        print(f"Warning: {calib_path} not found - detecting markers on raw (non-undistorted) frames.")

    rows = []
    try:
        for commanded in args.sequence:
            link.send_angle(args.joint, commanded)
            hold_and_measure(cam_ok, cam, mtx, dist, args.joint, commanded, rows)
    finally:
        cam.release()
        link.close()

    with open(LOG_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {LOG_PATH}")
    print_summary(rows)


if __name__ == "__main__":
    main()
