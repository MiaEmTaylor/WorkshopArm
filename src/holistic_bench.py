# ------- HOLISTIC BENCHMARK ----------------------------------------------
# runs a bunch of mediapipe holistic speed tests on the brain laptop and
# writes a report folder. uses video files instead of webcams so the camera
# can't slow things down, and plays 2 videos at once to fake 2 cameras.
#
# default tests (each --secs long, ~20 sec):
#   1 camera:  complexity 0 / 1 / 2, 320 wide, face detail on
#   2 cameras: sequential (one loop takes turns), threads, processes
# --full runs every combination instead (48 tests, ~20 min).
#
# usage (from repo root, inside the venv):
#   python src/holistic_bench.py
#   python src/holistic_bench.py --secs 10 --no-video
#   python src/holistic_bench.py --full
#
# output: reports/<date>_<hostname>/
#   summary.md     speed table + laptop info (rewritten after every test)
#   snaps/*.jpg    3 frames per camera per test with the tracking dots drawn
#   tracking.mp4   ~10 sec of both videos side by side with the dots on

# ------- IMPORTS --------------------------------------------------------
import argparse
import multiprocessing
import platform
import queue
import socket
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp

# ------- SETTINGS --------------------------------------------------------
REPO = Path(__file__).parent.parent
SAMPLES = REPO / "data" / "samples"
VIDEOS = [SAMPLES / "classroom.mp4", SAMPLES / "people-detection.mp4"]
CAM_NAMES = ["cam1", "cam2"]
SNAP_AT = (0.25, 0.5, 0.75)  # take snapshots at these points in each test

# what the results object calls each body part
PARTS = {"face": "face_landmarks", "pose": "pose_landmarks",
         "left hand": "left_hand_landmarks", "right hand": "right_hand_landmarks"}

holistic_api = mp.solutions.holistic
draw = mp.solutions.drawing_utils
styles = mp.solutions.drawing_styles


# ------- DRAWING ---------------------------------------------------------
def annotate(frame, results, label=""):
    """copy of the frame with the tracking dots + lines drawn on"""
    out = frame.copy()
    if results.face_landmarks:
        draw.draw_landmarks(out, results.face_landmarks, holistic_api.FACEMESH_CONTOURS,
                            None, styles.get_default_face_mesh_contours_style())
    if results.pose_landmarks:
        draw.draw_landmarks(out, results.pose_landmarks, holistic_api.POSE_CONNECTIONS,
                            styles.get_default_pose_landmarks_style())
    for hand in (results.left_hand_landmarks, results.right_hand_landmarks):
        if hand:
            draw.draw_landmarks(out, hand, holistic_api.HAND_CONNECTIONS,
                                styles.get_default_hand_landmarks_style(),
                                styles.get_default_hand_connections_style())
    if label:
        cv2.putText(out, label, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(out, label, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return out


# ------- ONE FAKE CAMERA -------------------------------------------------
class Stream:
    """a looping video + its own holistic model, counting how it does"""

    def __init__(self, video, cfg, name, snap_dir=None):
        self.cap = cv2.VideoCapture(str(video))
        if not self.cap.isOpened():
            raise SystemExit(f"could not open {video}")
        self.cfg = cfg
        self.name = name
        self.snap_dir = snap_dir
        self.holistic = holistic_api.Holistic(model_complexity=cfg["complexity"],
                                              refine_face_landmarks=cfg["face"])
        self.frames = 0
        self.busy = 0.0  # seconds spent inside holistic.process
        self.found = dict.fromkeys(PARTS, 0)
        self.snaps = 0

    def read(self):
        ok, frame = self.cap.read()
        if not ok:  # video ended, start it over
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.cap.read()
        h, w = frame.shape[:2]
        if w != self.cfg["width"]:  # shrink, keeping the shape
            frame = cv2.resize(frame, (self.cfg["width"], round(h * self.cfg["width"] / w)))
        return frame

    def step(self, snap=False):
        frame = self.read()
        t = time.monotonic()
        # mediapipe wants RGB, opencv gives BGR
        results = self.holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.busy += time.monotonic() - t
        self.frames += 1
        for part, attr in PARTS.items():
            if getattr(results, attr):
                self.found[part] += 1
        if snap and self.snap_dir:
            self.snaps += 1
            path = self.snap_dir / f"{self.cfg['name']}_{self.name}_{self.snaps}.jpg"
            cv2.imwrite(str(path), annotate(frame, results, f"{self.cfg['name']} {self.name}"),
                        [cv2.IMWRITE_JPEG_QUALITY, 85])
        return frame, results

    def stats(self, elapsed):
        n = max(self.frames, 1)
        return {"name": self.name, "frames": self.frames, "fps": self.frames / elapsed,
                "ms": 1000 * self.busy / n,
                "found": {part: 100 * count / n for part, count in self.found.items()}}

    def close(self):
        self.holistic.close()
        self.cap.release()


def run_loop(streams, secs):
    """process a frame from each stream in turn until time is up"""
    start = time.monotonic()
    marks = [start + f * secs for f in SNAP_AT]
    while (now := time.monotonic()) < start + secs:
        snap = bool(marks) and now >= marks[0]
        if snap:
            marks.pop(0)
        for s in streams:
            s.step(snap)
    return time.monotonic() - start


# ------- THE 3 WAYS TO RUN 2 CAMERAS -------------------------------------
# workers load their model first, then wait at the barrier so loading
# time doesn't count and every camera starts at the same moment
def stream_worker(video, cfg, name, secs, snap_dir, barrier, report):
    s = Stream(video, cfg, name, snap_dir)
    barrier.wait()
    report.put(s.stats(run_loop([s], secs)))
    s.close()


def run_test(cfg, secs, snap_dir):
    jobs = list(zip(VIDEOS, CAM_NAMES))[:cfg["streams"]]

    if cfg["mode"] == "procs":  # separate python programs, one per camera
        ctx = multiprocessing.get_context("spawn")
        barrier, report = ctx.Barrier(len(jobs)), ctx.Queue()
        procs = [ctx.Process(target=stream_worker,
                             args=(video, cfg, name, secs, snap_dir, barrier, report))
                 for video, name in jobs]
        for p in procs:
            p.start()
        stats = [report.get(timeout=secs + 120) for _ in procs]
        for p in procs:
            p.join()

    elif cfg["mode"] == "threads":  # one program, one thread per camera
        barrier, report = threading.Barrier(len(jobs)), queue.Queue()
        threads = [threading.Thread(target=stream_worker,
                                    args=(video, cfg, name, secs, snap_dir, barrier, report))
                   for video, name in jobs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        stats = [report.get() for _ in threads]

    else:  # "seq": one loop takes turns between cameras (also used for 1 camera)
        streams = [Stream(video, cfg, name, snap_dir) for video, name in jobs]
        elapsed = run_loop(streams, secs)
        stats = [s.stats(elapsed) for s in streams]
        for s in streams:
            s.close()

    return sorted(stats, key=lambda s: s["name"])


# ------- TEST LIST -------------------------------------------------------
def make_tests(full):
    base = {"streams": 1, "mode": "seq", "complexity": 1, "width": 640, "face": False}
    if full:  # every combination
        tests = [{"streams": streams, "mode": mode, "complexity": c, "width": w, "face": face}
                 for streams, mode in [(1, "seq"), (2, "seq"), (2, "threads"), (2, "procs")]
                 for c in (0, 1, 2) for w in (640, 320) for face in (False, True)]
    else:  # change one thing at a time from the base
        tests = [{**base, "complexity": 0}, base, {**base, "complexity": 2},
                 {**base, "width": 320}, {**base, "face": True}]
        tests += [{**base, "streams": 2, "mode": mode} for mode in ("seq", "threads", "procs")]

    for t in tests:
        mode = "" if t["streams"] == 1 else f"_{t['mode']}"
        face = "_face" if t["face"] else ""
        t["name"] = f"{t['streams']}cam{mode}_c{t['complexity']}_w{t['width']}{face}"
    return tests


# ------- TRACKING VIDEO --------------------------------------------------
def make_video(path, secs=10):
    """both videos side by side with the dots drawn, complexity 1, face detail on"""
    cfg = {"name": "video", "complexity": 1, "width": 640, "face": True}
    streams = [Stream(video, cfg, name) for video, name in zip(VIDEOS, CAM_NAMES)]
    fps = streams[0].cap.get(cv2.CAP_PROP_FPS) or 15
    writer = None
    for _ in range(int(secs * fps)):
        frames = [annotate(*s.step(), s.name) for s in streams]
        h = frames[0].shape[0]
        frames = [f if f.shape[0] == h else cv2.resize(f, (round(f.shape[1] * h / f.shape[0]), h))
                  for f in frames]
        both = cv2.hconcat(frames)
        if writer is None:
            writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps,
                                     (both.shape[1], both.shape[0]))
        writer.write(both)
    writer.release()
    for s in streams:
        s.close()


# ------- REPORT ----------------------------------------------------------
def read_file(path, default="?"):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return default


def laptop_info():
    cpu = next((line.split(":", 1)[1].strip() for line in read_file("/proc/cpuinfo", "").splitlines()
                if line.startswith("model name")), platform.processor())
    power = {"1": "plugged in", "0": "on battery"}.get(
        read_file("/sys/class/power_supply/ACAD/online"), "?")
    return {"laptop": socket.gethostname(), "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cpu": cpu, "power": power,
            "battery": read_file("/sys/class/power_supply/BAT1/capacity") + "%",
            "cpu governor": read_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
            "python": platform.python_version(), "mediapipe": mp.__version__,
            "opencv": cv2.__version__}


def write_summary(path, info, secs, tests, results):
    how = {"seq": "sequential", "threads": "threads", "procs": "processes"}
    lines = ["# Holistic benchmark", ""]
    lines += [f"- **{k}:** {v}" for k, v in info.items()]
    lines += [f"- **seconds per test:** {secs}", "",
              "| test | cams | how | complexity | width | face detail | FPS per cam | total FPS "
              "| ms per frame | face | pose | L hand | R hand |",
              "|" + "---|" * 13]
    for t, stats in zip(tests, results):
        per_cam = " / ".join(f"{s['fps']:.1f}" for s in stats)
        total = sum(s["fps"] for s in stats)
        ms = sum(s["ms"] for s in stats) / len(stats)
        found = [sum(s["found"][part] for s in stats) / len(stats) for part in PARTS]
        lines.append(f"| {t['name']} | {t['streams']} | {how[t['mode']] if t['streams'] > 1 else '-'} "
                     f"| {t['complexity']} | {t['width']} | {'on' if t['face'] else 'off'} "
                     f"| {per_cam} | {total:.1f} | {ms:.0f} | "
                     + " | ".join(f"{f:.0f}%" for f in found) + " |")
    lines += ["", "## What the columns mean", "",
              "- **FPS per cam:** frames per second each fake camera got (cam1 / cam2).",
              "- **total FPS:** all cameras added up, i.e. how much work the laptop did.",
              "- **ms per frame:** average time inside `holistic.process` for one frame. "
              "Higher with 2 cams means they were fighting over the CPU.",
              "- **face / pose / hands:** % of frames where holistic found that part. "
              "Holistic only tracks one person per camera, so this is about that person.",
              "- **how:** sequential = one loop taking turns, threads = one program with a thread "
              "per camera, processes = a separate python program per camera.",
              "", "Snapshots with the tracking dots are in `snaps/`. "
              "`tracking.mp4` (if there) is both cameras at complexity 1 with face detail on.",
              "", "Videos: `classroom.mp4` (cam1) and `people-detection.mp4` (cam2) from "
              "[Intel sample-videos](https://github.com/intel-iot-devkit/sample-videos), CC-BY 4.0."]
    path.write_text("\n".join(lines) + "\n")


# ------- RUN -------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secs", type=float, default=20, help="how long each test runs")
    parser.add_argument("--full", action="store_true", help="every combination (~20 min)")
    parser.add_argument("--no-video", action="store_true", help="skip tracking.mp4")
    args = parser.parse_args()

    for video in VIDEOS:
        if not video.exists():
            raise SystemExit(f"missing {video}, did you git pull?")

    info = laptop_info()
    out = REPO / "reports" / f"{datetime.now():%Y-%m-%d_%H%M}_{info['laptop']}"
    snap_dir = out / "snaps"
    snap_dir.mkdir(parents=True, exist_ok=True)

    tests = make_tests(args.full)
    print(f"{len(tests)} tests x {args.secs:g}s, {info['power']}, report -> {out}\n")
    results = []
    for i, t in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] {t['name']:<28}", end="", flush=True)
        stats = run_test(t, args.secs, snap_dir)
        results.append(stats)
        print(" / ".join(f"{s['fps']:5.1f}" for s in stats), "FPS")
        # rewrite every time so a crash halfway still leaves a report
        write_summary(out / "summary.md", info, args.secs, tests[:i], results)

    if not args.no_video:
        print("\nmaking tracking.mp4 ...")
        make_video(out / "tracking.mp4")

    rel = out.relative_to(REPO)
    print(f"\ndone. report is in {rel}/summary.md")
    print(f"to put it on github:\n  git add {rel} && git commit -m 'Add holistic benchmark "
          f"report' && git push")


if __name__ == "__main__":
    main()
