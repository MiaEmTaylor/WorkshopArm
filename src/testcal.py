import cv2
import numpy as np
import json

# Config
ARUCO_DICT = cv2.aruco.DICT_4X4_50
SQUARES_HORIZONTALLY = 3
SQUARES_VERTICALLY = 3
SQUARE_LENGTH = 0.0635
MARKER_LENGTH = 0.0381

# Load calibration
with open('./calibration.json', 'r') as f:
    json_data = json.load(f)
mtx = np.array(json_data['mtx'])
dst = np.array(json_data['dist'])

# Load and undistort image (kinda)
image = cv2.imread('./snaps/IMG_20260527_095053.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
h, w = image.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dst, (w,h), 1, (w,h))
image = cv2.undistort(image, mtx, dst, None, newcameramtx)

# Setup detector
dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
board = cv2.aruco.CharucoBoard((SQUARES_HORIZONTALLY, SQUARES_VERTICALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, params)

# Detect
marker_corners, marker_ids, rejectedCandidates = detector.detectMarkers(image)
print(f"Marker IDs found: {marker_ids}")
print(f"Rejected candidates: {len(rejectedCandidates)}")

if marker_ids is not None and len(marker_ids) > 0:
    ret, charucoCorners, charucoIds = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, image, board)
    print(f"Charuco corners found: {ret}")
    
    if charucoCorners is not None and charucoIds is not None and len(charucoCorners) > 3:
        retval, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(
            charucoCorners, charucoIds, board, mtx, dst, np.empty(1), np.empty(1)
        )
        if retval:
            print(f"tvec: {tvec}")
        else:
            print("est failed")
    else:
        print("Not enough corners")
else:
    print("No markers found")

cv2.imshow("image", image)
cv2.waitKey(0)