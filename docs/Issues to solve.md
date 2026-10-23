# Issues to Solve

## Resolved
**do we need to train a model on our own?**
Switched to ArUco fiducial markers — no custom model needed for current phase.

**what will we train our model on?**
Same as above — not applicable for ArUco approach.

**coco pose only handles these in the base mod: [list]**
Not using COCO pose — ArUco approach replaced this entirely.

**to bring the hand to the docker we will likely need another sticker.**
Yes — this is ID4. Planned in Vision Protocol.

## Still Open

**how are we going to do 6 fingers**
Gemini says: "Real-time pose detection for robotic arms and 6-fingered hands can be achieved using Python, OpenCV, and MediaPipe. MediaPipe identifies 21 3D hand landmarks (knuckles, fingertips) in real-time. While designed for 5 fingers, the framework can be extended to 6 by custom training or mapping existing landmarks to a 6-finger kinematic model, sending coordinates via Serial/ROS"
Handling 6 Fingers: Standard Mediapipe detects 5 fingers. To handle a 6th, you must:
Option A: Extend Keypoints: Develop a custom machine learning model or fine-tune MediaPipe's hand model to detect 24+ points instead of 21.
Option B: Custom Logic: Detect the 6th finger's position relative to the 5th finger or by calculating the convex hull of the hand

**well need to compare both perceived location (from CV) of the joints to the servos enumerator returns to help it earn confidence score. well need to modify the models confidence classifier.**

**need to look into how to make our own data set. if we need to make a data set later rather than before the final that's okay, we can get the basic tracking set up ad sending data to the servos over serial or ssh for basic wrist elbow and base rotation and movement. we may need to sacrifice cool looking sleek design for the placement stickers for tracking rotation. this could help training significantly**

## Machine reads scary and unsafe rather than intimidating and charming
Exaggerate the first 20% of a reach so the human knows where it's going.
CV-vs-encoder reconciliation problem becomes a feature: put "wrist position: 71% confidence" on the overlay. A system that admits uncertainty is trusted more.

### A — judge-side
Peak-end rule. They remember the highest-intensity moment and the last moment. Design both deliberately. Your USB-A-right-side-up gag is an excellent ending — it's funny, it's humanizing, and it's genuinely hard.
Give the judge a job. Hand them the jar. Let them struggle with it for three seconds, then let the arm do it. Participation inflates ratings (IKEA effect) and it converts spectators into witnesses.
Stage a failure and recover. Service recovery paradox: a visible failure followed by a clean recovery rates higher than a flawless run. Also, your Recovery Protocol suddenly has a demo.
Name your own limitations first. "The deception-signal heuristic is unvalidated and is not a lie detector." Saying that before a judge asks kills the gotcha and reads as maturity. Withholding it and getting caught is a scored disaster.