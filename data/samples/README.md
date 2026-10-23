# Sample videos

Test clips for the speed tests (`src/holistic_bench.py`, `src/holistic_fps_test.py`),
used as fake cameras so the webcam can't slow the numbers down.

| file | what's in it | used as |
|---|---|---|
| `classroom.mp4` | 4 people in a classroom, ~33 sec | cam1 |
| `people-detection.mp4` | people walking through a room, ~50 sec | cam2 |

Both are from Intel's [sample-videos](https://github.com/intel-iot-devkit/sample-videos)
repo, licensed [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Shrunk to 640x360 at 15 FPS with no audio to keep them small in git.
