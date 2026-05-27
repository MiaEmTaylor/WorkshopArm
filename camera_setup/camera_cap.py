import cv2
import os
import time

def start_camera_and_capture(save_path, base_name, delay=2.0):
    """
    Displays live camera view and automatically captures frames.
    
    :param save_path: Directory to save the images.
    :param base_name: Prefix name for the captured files.
    :param delay: Time in seconds between each automatic capture.
    """
    # Initialize the camera (0 is usually the default built-in webcam)
    cap = cv2.VideoCapture(0)
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Create the destination directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print(f"Created directory: {save_path}")

    print("Camera feed active. Press 'q' to quit.")
    
    # Initialize timing and naming variables
    last_capture_time = time.time()
    img_counter = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame. Exiting...")
            break

        # Display the live camera feed in a window
        cv2.imshow('Live Camera View', frame)

        # Automatic capture logic
        current_time = time.time()
        if current_time - last_capture_time >= delay:
            # Generate exact file path (e.g., /path/to/my_image_001.jpg)
            img_filename = f"{base_name}_{img_counter:03d}.jpg"
            full_path = os.path.join(save_path, img_filename)
            
            # Save the frame
            cv2.imwrite(full_path, frame)
            print(f"Auto-captured: {full_path}")
            
            # Update counters/timers
            last_capture_time = current_time
            img_counter += 1

        # Check for the 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up and release the camera
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released. Program terminated.")

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Define your destination directory and base filename here
    TARGET_PATH = "./snaps"
    FILE_NAME = "board"
    AUTO_CAPTURE_DELAY = 0.9  # Takes a picture every 3 seconds

    start_camera_and_capture(
        save_path=TARGET_PATH, 
        base_name=FILE_NAME, 
        delay=AUTO_CAPTURE_DELAY
    )
