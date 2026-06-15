import cv2
import os
from ultralytics import YOLO

image_path = "arm2.jpg"
output_image = "output_arm2.jpg"

print("\n------- Processing Image -------")
model = YOLO('yolo11n-pose.pt') # Load pre-trained pose model

img_results = model(image_path)
target_indices = [5,7,9,6,8,10]
for result in img_results:
    keypoints = result.keypoints.xy.cpu().numpy()

for person_kpts in keypoints:
    filtered_kpts = person_kpts[target_indices]
    print("\n------- filtered keypoints are shoulder, elbow, and wrist -------\n", filtered_kpts)

annotated_frame = result.plot()
cv2.imwrite(output_image, annotated_frame)
print(f"Image saved to {output_image}")