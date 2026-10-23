# Holistic benchmark

- **laptop:** the-cake-is-a-lie
- **date:** 2026-10-22 23:19
- **cpu:** Intel(R) Core(TM) i3-8145U CPU @ 2.10GHz
- **power:** plugged in
- **battery:** 14%
- **cpu governor:** powersave
- **python:** 3.11.17
- **mediapipe:** 0.10.21
- **opencv:** 4.11.0
- **seconds per test:** 10.0

| test | cams | how | complexity | width | face detail | FPS per cam | total FPS | ms per frame | face | pose | L hand | R hand |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1cam_c0_w640 | 1 | - | 0 | 640 | off | 17.2 | 17.2 | 58 | 57% | 99% | 82% | 99% |
| 1cam_c1_w640 | 1 | - | 1 | 640 | off | 15.1 | 15.1 | 66 | 63% | 100% | 72% | 100% |
| 1cam_c2_w640 | 1 | - | 2 | 640 | off | 6.8 | 6.8 | 146 | 57% | 100% | 42% | 100% |
| 1cam_c1_w320 | 1 | - | 1 | 320 | off | 15.8 | 15.8 | 62 | 12% | 100% | 75% | 98% |
| 1cam_c1_w640_face | 1 | - | 1 | 640 | on | 15.0 | 15.0 | 66 | 87% | 100% | 71% | 100% |
| 2cam_seq_c1_w640 | 2 | sequential | 1 | 640 | off | 8.5 / 8.5 | 17.0 | 58 | 29% | 84% | 27% | 52% |
| 2cam_threads_c1_w640 | 2 | threads | 1 | 640 | off | 11.4 / 17.1 | 28.5 | 72 | 33% | 70% | 32% | 51% |
| 2cam_procs_c1_w640 | 2 | processes | 1 | 640 | off | 11.4 / 17.1 | 28.5 | 72 | 33% | 70% | 32% | 51% |

## What the columns mean

- **FPS per cam:** frames per second each fake camera got (cam1 / cam2).
- **total FPS:** all cameras added up, i.e. how much work the laptop did.
- **ms per frame:** average time inside `holistic.process` for one frame. Higher with 2 cams means they were fighting over the CPU.
- **face / pose / hands:** % of frames where holistic found that part. Holistic only tracks one person per camera, so this is about that person.
- **how:** sequential = one loop taking turns, threads = one program with a thread per camera, processes = a separate python program per camera.

Snapshots with the tracking dots are in `snaps/`. `tracking.mp4` (if there) is both cameras at complexity 1 with face detail on.

Videos: `classroom.mp4` (cam1) and `people-detection.mp4` (cam2) from [Intel sample-videos](https://github.com/intel-iot-devkit/sample-videos), CC-BY 4.0.
