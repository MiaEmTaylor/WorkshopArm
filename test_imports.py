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
Val YOLO imports and load mods
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