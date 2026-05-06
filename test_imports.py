"""
Val OpenCV
"""

import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()

"""
Val YOLO
"""

from ultralytics import YOLO

# Load a model
model = YOLO("yolo26n-pose.pt")  # load an official model
model = YOLO("path/to/best.pt")  # load a custom model

# Validate the model
metrics = model.val()  # no arguments needed, dataset and settings remembered
metrics.box.map  # map50-95
metrics.box.map50  # map50
metrics.box.map75  # map75
metrics.box.maps  # a list containing mAP50-95 for each category
metrics.box.image_metrics  # per-image metrics dictionary for box with precision, recall, F1, TP, FP, and FN
metrics.pose.map  # map50-95(P)
metrics.pose.map50  # map50(P)
metrics.pose.map75  # map75(P)
metrics.pose.maps  # a list containing mAP50-95(P) for each category
metrics.pose.image_metrics  # per-image metrics dictionary for pose with precision, recall, F1, TP, FP, and FN

"""
Val numpy
"""
import numpy
numpy.test()



"""
Val pybullet
"""
import pybullet as p
import time
import pybullet_data

# 1. Connect to PyBullet (GUI mode shows a window, DIRECT mode does not)
physicsClient = p.connect(p.GUI)

# 2. Add search path for URDF files (like planes and robots)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# 3. Set gravity
p.setGravity(0, 0, -9.81)

# 4. Load a floor plane and a robot
planeId = p.loadURDF("plane.urdf")
startPos = [0, 0, 1]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
boxId = p.loadURDF("r2d2.urdf", startPos, startOrientation)

# 5. Run simulation loop
for i in range(10000):
    p.stepSimulation()
    time.sleep(1./240.) # 240 Hz

# 6. Disconnect
p.disconnect()


"""
Val PyTorch
"""
import torch
x = torch.rand(5, 3)
print(x)

print(torch.cuda.is_available())

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
