how are we going to do 6 fingers
	Gemini says: "Real-time pose detection for robotic arms and 6-fingered hands can be achieved using Python, OpenCV, and MediaPipe. MediaPipe identifies 21 3D hand landmarks (knuckles, fingertips) in real-time. While designed for 5 fingers, the framework can be extended to 6 by custom training or mapping existing landmarks to a 6-finger kinematic model, sending coordinates via Serial/ROS"
	Handling 6 Fingers: Standard Mediapipe detects 5 fingers. To handle a 6th, you must:
	Option A: Extend Keypoints: Develop a custom machine learning model or fine-tune MediaPipe's hand model to detect 24+ points instead of 21.
	Option B: Custom Logic: Detect the 6th finger's position relative to the 5th finger or by calculating the convex hull of the hand
do we need to train a model on out own?
what will we train our model on? 
[link to mediapipe hand model detector for open cv](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#models)
https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DsignhD3T0w8&ved=2ahUKEwjV9fGsp6KUAxVcGoYAHeTZBxcQkPEHegQIGRAB&usg=AOvVaw3gjYRk-Tii3QYqvuNxxaHg <- hand tracking with human hand tutorial with OpenCV and python

well need to compare both perceived location (from CV) of the joints to the servos enumerator returns to help it earn confidence score. well need to modify the models confidence classifier.


coco pose only handles these in the base mod:
    - nose
    - left_eye
    - right_eye
    - left_ear
    - right_ear
    - left_shoulder
    - right_shoulder
    - left_elbow
    - right_elbow
    - left_wrist
    - right_wrist
    - left_hip
    - right_hip
    - left_knee
    - right_knee
    - left_ankle
    - right_ankle


https://platform.ultralytics.com/eric-brille/datasets/humanfinderyolo26-3 < - human finder !

need to look into how to make our own data set. if we need to make a data set later rather than before the final that's okay, we can get the basic tracking set up ad sending data to the servos over serial or ssh for basic wrist elbow and base rotation and movement. we may need to sacrifice cool looking sleek design for the placement stickers for tracking rotation. this could help training significantly


to bring the hand to the docker we will likely need another sticker. 
