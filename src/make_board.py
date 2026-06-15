# ------- IMPORTS --------------------------------------------------------
import cv2
import numpy as np

ARUCO_DICT = cv2.aruco.DICT_4X4_50  # Dictionary ID
SQUARES_VERTICALLY = 3               # Number of squares vertically
SQUARES_HORIZONTALLY = 3             # Number of squares horizontally
SQUARE_LENGTH = 350                   # Square side length (in pixels)
MARKER_LENGTH = 210                   # ArUco marker side length (in pixels)
MARGIN_PX = 75                       # Margins size (in pixels)

IMG_SIZE = tuple(i * SQUARE_LENGTH + 2 * MARGIN_PX for i in (SQUARES_VERTICALLY, SQUARES_HORIZONTALLY))
OUTPUT_NAME = 'ChArUco_Marker.png'

board = cv2.aruco.CharucoBoard(
    (SQUARES_HORIZONTALLY, SQUARES_VERTICALLY),
    SQUARE_LENGTH / 150.0,   # convert px → inches for real-world scale
    MARKER_LENGTH / 150.0,
    cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
)

img = board.generateImage(IMG_SIZE, marginSize=MARGIN_PX, borderBits=1)
cv2.imwrite("charuco_board.png", img)