*Class Final Project — Alternative Final | Started May 4th*

> This is a subsection of the larger WorkshopArm project. Full project documentation lives separately — this covers only the class final prototype build.

---

## What This Was

For my alternative final, I built a computer vision prototype system for a robotic arm. The goal was live pose estimation using ArUco fiducial markers with a real-time overlay — a smaller, proof-of-concept version of the CV system I'm building for TSA/STLP competitions.

**Programming tie-in:** Python backend CV system (with some C++ dependencies for physics simulation tooling)  
**Game Design tie-in:** CV systems like this are used in VR/AR environments to track players and map real-world movement

**Tools used:** Python, OpenCV, ArUco, VSCode, GitHub, Obsidian

---

## Deliverables

- [Demo video](https://drive.google.com/file/d/1Hsy_CuNtfWNe-Sbw7fpa0IHy2qDAmw-A/view?usp=sharing)
- [Project files](https://drive.google.com/drive/folders/1rgKidUYaPM-dRBTdIIs-LXvj5q1wCQU5?usp=sharing)

> Note: Not every script in the files folder is fully mine — I used and modified public calibration scripts where needed. The main pose estimation script (`pose_est.py`) is my own work and is the core of the project.

---

## Plan (completed)

- [x] Figure out dependencies and get ArUco + OpenCV running
- [x] Write pseudocode for the main script
- [x] Write and run the marker generation script
- [x] Print out the 4 markers
- [x] Build the small prototype arm
- [x] Calibrate the camera
- [x] Attach markers to the arm
- [x] Finish pose estimation script
- [x] Test, record, update docs

*— checkpoint May 29th —*

- [x] Testing, bug fixes, documentation updates

---

## Weekly Notes

### Week 1

Getting the environment set up was the main challenge this week. Go Guardian (school content filter) was blocking installers for Python, NumPy, and OpenCV, so I had to move to an older desktop to get around that. It's slower but the installs worked fine there.

Ran into a few dependency issues — pip was outdated and needed to be updated, and I also had to install Visual Studio Build Tools for C++ because of PyBullet's requirements. Spent the rest of the week validating that everything was running, then started learning PyBullet and OnShape (a browser-based CAD tool I was going to use for the virtual arm).

OnShape turned out to be more complicated than I wanted to deal with for this scope, so I decided to shift the 3D work to home and use a text-based or simplified approach for the prototype at school. Since the system only needs to map major joints, I scaled down to a small physical arm instead of the full thing.

---

### Week 2

Planned out how to get useful data from the CV pipeline. Started by looking into YOLO for pose estimation — tested it but scrapped it pretty quickly. The results were inaccurate and the detections looked bad, not worth building on.

Switched to an ArUco fiducial marker approach instead. Wrote out pseudocode for the full pose estimation script including joint angle calculations. Also started putting together a command reference doc for the libraries I'm using.

**End of week goals I set:**
- Pseudocode done or near done ✓
- Print and detect markers to understand the output ✓
- Basics up to skeleton drawing done by Friday ✓
- Weekend: design and print/build the small arm

---

### Week 3

Got the prototype arm to school. Camera calibration was the big focus — ran into some distortion and fisheye issues that took a few days to work through.

By Wednesday most of it was resolved, though there were still some resolution and warping quirks. After looking into it more I realized the model was actually detecting the markers correctly despite the visual weirdness — the distortion only looks off when the camera is pressed flat, but the math processes fine as long as the marker is mostly centered. Good enough.

**Calibration output (sample):**
```
Marker IDs found: [[2] [0] [3] [1]] Rejected candidates: 18 Charuco corners found: 4 tvec: [[-0.08415096] [-0.12226047] [ 0.72450109]]

Resolution used: cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```
**Saturday:** Got live tracking and detection working. Added a visual overlay showing the markers and their tracking IDs. Then added lines connecting the tracked joint points — the arm mapping is working well.

Issues I hit during this phase:
- Had to switch file paths to Linux versions since I was on my personal machine
- The distortion correction API changed between versions — had to figure out the newer syntax
- A few logic bugs where things weren't inside the right loop, but those were easy catches once I walked through it

After that it was pretty straightforward. Really happy with how it came out.

