# ------- IMPORTS --------------------------------------------------------
import argparse
import cv2
import numpy as np
import json
from pathlib import Path

from joint_angles import calculate_joint_angles
from servo_io import ServoLink, DummyServoLink

DATA_DIR = Path(__file__).parent.parent / "data"

# ------- ARGS --------------------------------------------------------------
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--port", type=str, default=None, help="Serial port for the Arduino, e.g. /dev/ttyACM0")
arg_parser.add_argument("--dry-run", action="store_true", help="Use DummyServoLink instead of real hardware")
arg_parser.add_argument("--camera", type=int, default=1, help="OpenCV camera index")
args = arg_parser.parse_args()

link = DummyServoLink() if args.dry_run else ServoLink(args.port)
link.connect()

# ------- DICTIONARY -----------------------------------------------------
# telling ArUco which set of marker patterns to look for
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()  # Marker detection parameters
detector = cv2.aruco.ArucoDetector(dictionary, parameters)  # newer OpenCV wraps detection in this class
J0, J1, J2, J3 = 0, 1, 2, 3 # redefining marker ids bc i will get confused.

# ------- VARS ------------------------------------------------------------
# each joint needs the ID it is connected to
connections = [(J0, J1), (J1, J2), (J2, J3)]

calibration_path = DATA_DIR / 'calibration.json'
matrix_coefficients, distortion_coefficients = None, None
if calibration_path.exists():
    with open(calibration_path, 'r') as f:
        json_data = json.load(f)
    matrix_coefficients = np.array(json_data['mtx'])
    distortion_coefficients = np.array(json_data['dist'])
else:
    print(f"Warning: {calibration_path} not found - using raw (non-undistorted) frames.")

# ------- DETECT CENTER OF MARKER ------------------------------------------
def marker_center(marker_corners):
    pts = marker_corners.reshape(4, 2)
    return pts.mean(axis=0)

def marker_centers_by_id(corners, ids):
    if ids is None:
        return {}
    return {int(marker_id): marker_center(marker_corners)
            for marker_id, marker_corners in zip(ids.ravel(), corners)}

def vector_between_centers(start_center, end_center):
    return end_center - start_center

# ------- DETECTING AND LEBLING MARKERS -----------------------------------
# open the webcam
live = cv2.VideoCapture(args.camera)
if not live.isOpened():
    print(f"Error: No live feed on camera {args.camera}. Try --camera with a different index.")
    exit()

while True: # capturing live frames
    success, frame = live.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale
    
    if not success:
        print("Error: Frames not captured.")
        break
    
    # Load and undistort image (kinda)
    if matrix_coefficients is not None:
        h, w = gray.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix_coefficients, distortion_coefficients, (w,h), 1, (w,h))
        gray_undist = cv2.undistort(gray, matrix_coefficients, distortion_coefficients, None, newcameramtx)
    else:
        gray_undist = gray

    # detect markers in computer frame
    corners, ids, rejected = detector.detectMarkers(gray_undist)

    # recive id numbers and cords
    print(f"Marker IDs found: {ids if ids is not None else 'None'}")
    print(f"Marker corners found: {corners}")

    # dysplaying cv feed with overlay
    centers = marker_centers_by_id(corners, ids)
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)  # draws boxes around markers and labels them with their id
    for center in centers.values(): # draws a green dot at the center of each marker
        cv2.circle(frame, tuple(center.astype(int)), 5, (0, 255, 0), -1)

    
    # ------- DRAWING THE SKELLY -----------------------------------------------
    # pick a jnt_pt
    # draw a line from base -> elbow -> wrist
    # repeat the above until it connects all 
    #               the lines in a sskeleton
    # NEEDS TO BE VECTORS FOR LATER STEPS
    for start_id, end_id in connections: # for each connection, if the centers of the start and end markers are detected, draw a line between them
        if start_id in centers and end_id in centers:
            start_center = centers[start_id]
            end_center = centers[end_id]
            cv2.line(frame, tuple(start_center.astype(int)), tuple(end_center.astype(int)), (255, 0, 0), 2)

    # ------- CALCULATE ANGLES AND DRIVE SERVOS -------------------------------
    angles = calculate_joint_angles(centers)
    shoulder_angle = angles["shoulder"]
    elbow_angle = angles["elbow"]

    if shoulder_angle is not None:
        link.send_angle("shoulder", shoulder_angle)
        cv2.putText(frame, f"shoulder: {shoulder_angle:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if elbow_angle is not None:
        # one CV elbow reading, both elbow servos driven to it
        link.send_angle("elbow1", elbow_angle)
        link.send_angle("elbow2", elbow_angle)
        cv2.putText(frame, f"elbow: {elbow_angle:.1f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    print(f"Shoulder: {shoulder_angle}, Elbow: {elbow_angle}")

    cv2.imshow('Live Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # <-- q to quit
        break                                                             
        
# close feed
live.release()
cv2.destroyAllWindows()
link.close()


# -------- LATER -----------------------------------------------------------

#TODO:  solvePnP, gives 3D rotation of each marker, needs camera calibration first!
