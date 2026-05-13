# --------- IMPORTS --------------------


# ------- VARS -------------------------
# establish vars
# each joint needs the ID it is connected to


# ------ DICTIONARY ---------------------
# telling ArUco which set of marker patterns to look for


# ------- DETECTING AND LEBLING MARKERS
# open the webcam and begin capturing live feed
# detect markers in computer frame
# recive id numbers and cords


# ------- DETECT CENTER OF MARKER ---------
# print the raw corners first before doing 
#                  math on them for laater
# helper function: two centers in, vector out
#   center = (average of all 4 ys and x values)
#   jnt_pt = center.marker_id


# ------- DRAWING THE SKELLY -----------
# pick a jnt_pt
# draw a line from base -> elbow -> wrist
# repeat the above until it connects all 
#               the lines in a sskeleton
# NEEDS TO BE VECTORS FOR LATER STEPS


# ------- CALCULATE ANGLES -------------
#TODO:  look up the dot product method for angle
# angle between two vectors dot product numpy

# ------- PRINT IT PRETTY --------------
# headders, print what the angles are and cords


# -------------------- LATER ------------------------

#TODO:  solvePnP, gives 3D rotation of each marker, needs camera calibration first!