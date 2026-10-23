# Holistic benchmark

- **laptop:** the-cake-is-a-lie
- **date:** 2026-10-22 22:33
- **cpu:** Intel(R) Core(TM) i3-8145U CPU @ 2.10GHz
- **power:** on battery
- **battery:** 50%
- **cpu governor:** powersave
- **python:** 3.11.17
- **mediapipe:** 0.10.21
- **opencv:** 4.11.0
- **seconds per test:** 20

| test | cams | how | complexity | width | face detail | FPS per cam | total FPS | ms per frame | face | pose | L hand | R hand |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1cam_c0_w640 | 1 | - | 0 | 640 | off | 28.6 | 28.6 | 35 | 56% | 97% | 63% | 55% |
| 1cam_c1_w640 | 1 | - | 1 | 640 | off | 24.3 | 24.3 | 41 | 75% | 100% | 80% | 84% |
| 1cam_c2_w640 | 1 | - | 2 | 640 | off | 11.5 | 11.5 | 87 | 59% | 100% | 79% | 100% |
| 1cam_c1_w320 | 1 | - | 1 | 320 | off | 23.2 | 23.2 | 43 | 25% | 100% | 77% | 79% |
| 1cam_c1_w640_face | 1 | - | 1 | 640 | on | 22.7 | 22.7 | 44 | 86% | 100% | 78% | 82% |
| 2cam_seq_c1_w640 | 2 | sequential | 1 | 640 | off | 14.4 / 14.4 | 28.7 | 34 | 33% | 72% | 34% | 41% |
| 2cam_threads_c1_w640 | 2 | threads | 1 | 640 | off | 15.5 / 24.3 | 39.8 | 52 | 35% | 69% | 36% | 41% |
| 2cam_procs_c1_w640 | 2 | processes | 1 | 640 | off | 15.5 / 24.2 | 39.8 | 52 | 35% | 69% | 36% | 41% |

## What the columns mean

- **FPS per cam:** frames per second each fake camera got (cam1 / cam2).
- **total FPS:** all cameras added up, i.e. how much work the laptop did.
- **ms per frame:** average time inside `holistic.process` for one frame. Higher with 2 cams means they were fighting over the CPU.
- **face / pose / hands:** % of frames where holistic found that part. Holistic only tracks one person per camera, so this is about that person.
- **how:** sequential = one loop taking turns, threads = one program with a thread per camera, processes = a separate python program per camera.

Snapshots with the tracking dots are in `snaps/`. `tracking.mp4` (if there) is both cameras at complexity 1 with face detail on.

Videos: `classroom.mp4` (cam1) and `people-detection.mp4` (cam2) from [Intel sample-videos](https://github.com/intel-iot-devkit/sample-videos), CC-BY 4.0.
