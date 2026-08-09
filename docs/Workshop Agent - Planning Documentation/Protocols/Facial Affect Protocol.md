> Current status: Prototype stage — actively iterating. Lives in a separate repo (`facial_rec_prototype`, see `HOW_IT_WORKS.md` there for full build notes), not yet integrated into ArchArm.

---

## Overview

The Facial Affect Protocol handles reading a person's live emotional state from webcam video and turning it into something both a human and an agent can act on. It calibrates itself to one specific person's face, converts that into a continuous valence/arousal score, and feeds that score to LLM agents that reason about it in real time — closing the loop from "what does your face look like" to "what should be said or done about it."

Not currently part of ArchArm's kernel/protocol stack — this is the standalone prototype it would plug into a future Personality Protocol or Service Protocol integration.

---

## How It Works

### Pipeline

1. **Capture** — Live feed pulled from webcam via OpenCV (camera index hardcoded per-machine, see Limitations)
2. **Face tracking** — MediaPipe returns 478 tracked face points plus 52 pre-built "blendshape" scores (`browDownLeft`, `jawOpen`, `mouthSmileLeft`, etc.)
3. **Feature extraction** — raw blendshapes turned into a plain `{name: score} `dict, baseline-subtracted so a resting face reads as neutral
4. **Motion tracking** — a rolling tracker adds a second signal alongside the static reading: how fast each value is *changing*, not just where it sits, so a held expression and a passing twitch don't read the same
5. **Geometry/head pose** — a few measurements computed straight from the raw landmark coordinates rather than the blendshape vocabulary (eyebrow height difference, jaw clench, head pitch/yaw/roll relative to normal sitting posture)
6. **Personal classification** — a per-user Gaussian classifier weighted by how much each signal *normally* varies for that person, so a small-but-consistent cue counts more than a big-but-noisy one
7. **Continuous scoring** — level+motion vector run through a trained regression model to produce a single fast valence/arousal number, pooled from calibration data, an archived backup, and auto-labeled real session recordings
8. **Agent reasoning** — an LLM agent reads the live valence/arousal (and in one variant, transcribed speech) and decides what to say or do next

---

### Calibration

| Stage                 | What it does                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Photo-stimulus wizard | Shows OASIS-derived photos (real published valence/arousal ratings) in random order, records the natural reaction to each       |
| Live correction       | User can tell the system what they're actually feeling right now; blends into the profile weighted against existing data        |
| Session recording     | Captures real, unposed reactions (video + audio + per-frame face data) instead of staged photos, for more natural training data |
| Snapshot review       | Periodic photo + guess pairs saved during normal use; reviewed later, folded into calibration, then deleted                     |

Calibration data is per-person and stored locally — re-running the wizard is required if the feature vector shape changes (e.g. adding motion broke old calibration files).

---

### Generic Model Comparison

A pretrained third-party model (EmoNet, trained on thousands of *other* people's faces) runs alongside the personal calibration for comparison, and is used to auto-label session recordings for training data — throttled to run at most once every few seconds since it's slow on CPU.

---

### Agents

Three agent variants currently exist, all reading the same live valence/arousal signal:

- **Goal-directed agent** — has one tool (a short on-screen message) and a target expression state; commits to a quantified prediction of what will happen, scores itself against what actually happens, gets one corrective retry if its own self-audit fails
- **Voice + deception-signal agent** — listens, transcribes, and reasons about spoken content alongside facial readings; tracks mismatches between what's said and what the face shows as a loose heuristic, explicitly not a validated lie detector
- **Showcase agent** — no hidden goal, everything (mesh overlay, live graph, bar chart, compound detectors) on screen at once, for demoing

---

## Current Limitations

- Camera index is hardcoded per-machine, not auto-detected
- Calibration is single-user — the whole profile has to be redone for a new person
- EmoNet comparison runs at ~1fps on CPU, throttled to avoid dragging down the rest of the pipeline
- Deception-signal heuristic has no scientific validation behind it — verbal/facial mismatch only, not a real lie detector
- Trained regression model mixes trust levels: real OASIS-rated data (high trust) pooled with auto-labeled session data (low trust, noisier but higher volume)
- Lip-reading is only at the feasibility-check stage (do recorded mouth shapes look consistent per-word?) — no model built yet
- Not integrated with ArchArm's kernel/protocol routing — runs standalone

---

## Planned (not built)

- An actual lip-reading model, contingent on the feasibility check showing real signal
- Multi-person calibration profiles
- Integration point into a future Personality Protocol or Service Protocol, so ArchArm could consume this live affect signal instead of it only running as a standalone prototype
