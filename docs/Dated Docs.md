### April - May 2026

- Software/concept routing architecture + early concepts, see [[Main Documentation]]
- Developed start of [[Workshop Agent - Planning Documentation/Protocols/Digit Docking Protocol|Digit Docking Protocol]] and [[Digit Docking Mechanism]]
- Computer vision pose estimation prototype, see [[WorkshopArm CV Prototype Docs]]

---
### June 2026

- Cleaning up Documentation (used Claude to reword messy documentation)
- 

---
### July 2026

- Early iterations of the facial emotion classifier

---
### August 2026 (1st-10th)

- Made the digit assembly blueprint — decided on finger scale/dimensions: 164mm tip-to-palm, split into base (66mm), middle (44mm), and upper (54mm) segments, 37mm diameter, with head/cuff/skirt/tip detailing (20mm/12mm/10mm/10mm)
- Finalized parts that need to be bought, including but not limited to: N20 motor, bolt actuator hardware
- Decided to put the tether joint on the upper two joints to improve grip strength
- Worked on finger dimensions and built a 3D model prototype
- Edited, cleaned, strengthened, and retrained — basically rebuilt — the facial recognition system for CV
- Changed the facial emotion classifier to a valence/arousal-based system, now also passing facial markers
- Built session recording (video + audio + per-frame face data, with offline transcription) to capture real, unposed reactions instead of just staged calibration photos
- Added a generic pretrained model (EmoNet) running alongside the personal calibration, to compare against and help auto-label session recordings
- Trained a pooled valence/arousal regression model (affect_model.json) from calibration + archived data + auto-labeled sessions, with a held-out accuracy check separate from training
- Ran a sanity check on whether recorded mouth shapes are consistent enough per-word to be worth building a lip-reader on top of (open question, not yet a feature)
- Built and iterated on an AI agent experiment that reads live facial affect and reasons about how to move it toward a target state, including a self-scored prediction ledger and a suppressed-smile detector as a second success signal
- Built a second, voice-enabled agent variant that listens, transcribes, and reasons about spoken content alongside facial readings
- Reorganized the codebase into folders by role (apps/core/modeling/data/logs/assets) for maintainability
- Reconciled two out-of-sync local copies of the project (one had newer drawings/docs, the other matched GitHub's reorganized structure), merged them into one, pushed to GitHub, and flattened the local folder path to `/home/mia_mousie/ARCHLOGIC/ArchArm`
- Added motion.py, tracking how fast facial signals are changing over time, not just their static level
- Added per-photo calibration diagnostics logging to trace category confusion back to specific images
- Built a third "showcase" agent combining all the readings/agent reasoning for demoing
- Wrote HOW_IT_WORKS.md documenting the full pipeline, and cut dated version-checkpoint branches on GitHub