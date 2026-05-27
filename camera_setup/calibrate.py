import cv2
import numpy as np
import os
import json

ARUCO_DICT = cv2.aruco.DICT_4X4_50
SQUARES_VERTICALLY = 3
SQUARES_HORIZONTALLY = 3
SQUARE_LENGTH = 0.0635
MARKER_LENGTH = 0.0381

def get_calibration_parameters(img_dir):
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_HORIZONTALLY, SQUARES_VERTICALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, params)

    image_files = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.endswith(".jpg")]
    if not image_files:
        raise ValueError(f"No jpg files found in {img_dir}")

    all_charuco_corners = []
    all_charuco_ids = []
    imgSize = None

    for image_file in image_files:
        image = cv2.imread(image_file)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        imgSize = image.shape
        marker_corners, marker_ids, _ = detector.detectMarkers(image)

        if marker_ids is not None and len(marker_ids) > 0:
            ret, charucoCorners, charucoIds = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, image, board)
            if charucoCorners is not None and charucoIds is not None and len(charucoCorners) > 3:
                all_charuco_corners.append(charucoCorners)
                all_charuco_ids.append(charucoIds)
                print(f"OK: {image_file} ({len(charucoCorners)} corners)")
            else:
                print(f"Not enough corners: {image_file}")
        else:
            print(f"No markers detected: {image_file}")

    if not all_charuco_corners:
        raise ValueError("No valid charuco corners found in any image")

    print(f"Calibrating with {len(all_charuco_corners)} images...")

    _, mtx, dist, _, _ = cv2.aruco.calibrateCameraCharuco(
        all_charuco_corners, all_charuco_ids, board, imgSize, None, None,
        flags=cv2.CALIB_RATIONAL_MODEL
    )
    return mtx, dist

SENSOR = 'monochrome'
LENS = 'kowa_f12mm_F1.8'
OUTPUT_JSON = 'calibration.json'

mtx, dist = get_calibration_parameters(img_dir='./snaps/')
data = {"sensor": SENSOR, "lens": LENS, "mtx": mtx.tolist(), "dist": dist.tolist()}
with open(OUTPUT_JSON, 'w') as json_file:
    json.dump(data, json_file, indent=4)
print(f'Data has been saved to {OUTPUT_JSON}')