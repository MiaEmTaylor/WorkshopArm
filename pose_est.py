# ------- IMPORTS --------------------------------------------------------
import cv2
import numpy as np

# ------- DICTIONARY -----------------------------------------------------
# telling ArUco which set of marker patterns to look for
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
J0, J1, J2, J3 = 0, 1, 2, 3 # redefining marker ids bc i will get confused.

# ------- VARS ------------------------------------------------------------
# each joint needs the ID it is connected to
connections = [(J0, J1), (J1, J2), (J2, J3)]

# ------- DETECTING AND LEBLING MARKERS -----------------------------------
# open the webcam
live = cv2.VideoCapture(0) # NOTE: change to differnt number for other camera
if not live.isOpened:
    print("Error: No live feed. Try changing live to 1.")
    exit()

while True: # capturing live frames
    success, frame = live.read()
    
    if not success:
        print("Error: Frames not captured.")
        break

# dysplaying cv feed
    cv2.imshow('Live Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # <-- q to quit
        break
live.release()
cv2.destroyAllWindows()

# detect markers in computer frame

# recive id numbers and cords


# ------- DETECT CENTER OF MARKER ------------------------------------------
# print the raw corners first before doing 
#                  math on them for laater
# helper function: two centers in, vector out
#   center = (average of all 4 ys and x values)
#   jnt_pt = center.marker_id


# ------- DRAWING THE SKELLY -----------------------------------------------
# pick a jnt_pt
# draw a line from base -> elbow -> wrist
# repeat the above until it connects all 
#               the lines in a sskeleton
# NEEDS TO BE VECTORS FOR LATER STEPS


# ------- CALCULATE ANGLES -------------------------------------------------
#TODO:  look up the dot product method for angle
# angle between two vectors dot product numpy


# ------- MAKE IT PRETTY --------------------------------------------------
# headders, print what the angles are and cords


# -------- LATER -----------------------------------------------------------

#TODO:  solvePnP, gives 3D rotation of each marker, needs camera calibration first!