import cv2
import os
import torch
import numpy
import pybullet as p
import pybullet_data
import time
from ultralytics import YOLO

# --- 0. quick tests ---
print(cv2.aruco.DICT_6X6_250)

# --- 1. CONFIGURATION ---
image_path = "test_image.png"
video_path = "store-aisle-detection.mp4"
output_image = "output_result.png"
output_video = "output_detected_video.mp4"

print("--- Starting Environment Validation ---")
model = YOLO("yolo11n.pt") 

# --- 2. IMAGE DETECTION & SAVE ---
if os.path.exists(image_path):
    print("\n--- Processing Image ---")
    img_results = model(image_path)[0]
    img_results.save(filename=output_image)
    print(f"SUCCESS: Image saved to {output_image}")
else:
    print(f"SKIP: '{image_path}' not found.")

# --- 3. VIDEO DETECTION & SAVE ---
if os.path.exists(video_path):
    print("\n--- Processing Video ---")
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties for the saver
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Initialize VideoWriter (FourCC 'mp4v' is standard for .mp4)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run detection (stream=True saves memory)
        results = model(frame, stream=True)
        
        for r in results:
            annotated_frame = r.plot()
            
            # Write frame to the output file
            out.write(annotated_frame)
            
            # Show live preview
            cv2.imshow("Processing Video...", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"SUCCESS: Video saved to {output_video}")
else:
    print(f"SKIP: '{video_path}' not found.")

# --- 4. VAL PYTORCH & CUDA ---
print("\n--- Val PyTorch ---")
print(f"CUDA Available: {torch.cuda.is_available()}")

# --- 5. VAL PYBULLET (Simulation) ---
print("\n--- Val PyBullet ---")
try:
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("plane.urdf")
    p.loadURDF("r2d2.urdf", [0, 0, 1])
    for _ in range(60): 
        p.stepSimulation()
    p.disconnect()
    print("PyBullet simulation successful.")
except Exception as e:
    print(f"PyBullet failed: {e}")

print("\nAll tests finished! Check your folder for outputs.")

# --- 3. VAL PYTORCH ---
print("\n--- Val PyTorch ---")
print(f"CUDA Available: {torch.cuda.is_available()}")

# --- 4. VAL PYBULLET ---
print("\n--- Val PyBullet (Simulation) ---")
try:
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("plane.urdf")
    p.loadURDF("r2d2.urdf", [0, 0, 1])
    for _ in range(60): 
        p.stepSimulation()
    p.disconnect()
    print("PyBullet simulation successful.")
except Exception as e:
    print(f"PyBullet failed: {e}")

# --- 5. VAL NUMPY ---
print("\n--- Val NumPy ---")
print(f"NumPy Version: {numpy.__version__}")

print("\nAll tests finished!")
