#!/usr/bin/env python3
"""Measure on-screen motion in a device recording.

Usage:
    uv run --with numpy python -I research/tools/analyze_motion.py <movie> [--csv out.csv] [--frames out-dir]

Decodes the movie to small grayscale frames with ffmpeg, then reports:
  - motion segments: runs of consecutive frames whose content changes,
    with start time, end time, duration and frame count;
  - flat frames: frames with almost no detail (blank white/black screens),
    which reveal loading gaps such as a white screen before an image appears.

With --frames, writes the first, middle and last frame of every motion
segment as JPEG for visual evidence.
"""

import argparse
import csv
import json
import pathlib
import subprocess

import numpy as np

W, H = 160, 120
MOTION_THRESHOLD = 1.0  # mean absolute gray difference (0-255) that counts as change
FLAT_STD = 4.0  # gray standard deviation below which a frame is treated as flat
GAP_FRAMES = 3  # still frames tolerated inside one motion segment


def frame_times(movie):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=best_effort_timestamp_time",
         "-of", "json", str(movie)], capture_output=True, check=True, text=True).stdout
    return [float(f["best_effort_timestamp_time"]) for f in json.loads(out)["frames"]]


def frames(movie):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(movie), "-vf", f"scale={W}:{H},format=gray", "-fps_mode", "passthrough",
         "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.int16)


def segments(diffs, times):
    moving = [i for i, d in enumerate(diffs, start=1) if d >= MOTION_THRESHOLD]
    result = []
    for i in moving:
        if result and i - result[-1][1] <= GAP_FRAMES + 1:
            result[-1][1] = i
        else:
            result.append([i, i])
    # A segment spans from the last still frame before it to its last changed frame.
    return [(s - 1, e, times[s - 1], times[e]) for s, e in result]


def export(movie, t, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", str(movie), "-frames:v", "1",
                    "-q:v", "3", str(path)], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("movie", type=pathlib.Path)
    parser.add_argument("--csv", type=pathlib.Path)
    parser.add_argument("--frames", type=pathlib.Path)
    parser.add_argument("--mark", type=float, action="append", default=[],
                        help="movie time (s) of an input action; reports delay to the next motion segment")
    args = parser.parse_args()

    gray = frames(args.movie)
    times = frame_times(args.movie)[: len(gray)]
    diffs = np.abs(gray[1:] - gray[:-1]).mean(axis=(1, 2))
    stds = gray.std(axis=(1, 2))
    means = gray.mean(axis=(1, 2))

    duration = times[-1] - times[0]
    print(f"{len(gray)} frames over {duration:.3f}s (avg {len(gray) / duration:.1f} fps)")
    gaps = np.diff(times)
    print(f"frame interval: median {np.median(gaps) * 1000:.1f}ms, max {gaps.max() * 1000:.1f}ms")

    segs = segments(diffs, times)
    print(f"\nmotion segments (threshold {MOTION_THRESHOLD}):")
    for k, (s, e, ts, te) in enumerate(segs, start=1):
        print(f"  #{k}: {ts:.3f}s -> {te:.3f}s  duration {(te - ts) * 1000:.0f}ms  frames {e - s}")
        if args.frames:
            args.frames.mkdir(parents=True, exist_ok=True)
            for tag, idx in (("start", s), ("mid", (s + e) // 2), ("end", e)):
                export(args.movie, times[idx], args.frames / f"seg{k:02d}-{tag}-{times[idx]:.3f}s.jpg")

    for mark in args.mark:
        later = [(ts, te) for _, _, ts, te in segs if te >= mark]
        if later:
            ts, te = later[0]
            print(f"mark {mark:.3f}s: change starts +{(ts - mark) * 1000:.0f}ms, settles +{(te - mark) * 1000:.0f}ms")
        else:
            print(f"mark {mark:.3f}s: no motion afterwards")

    flat = [i for i, v in enumerate(stds) if v < FLAT_STD]
    print(f"\nflat frames (std < {FLAT_STD}): {len(flat)}")
    if flat:
        runs = []
        for i in flat:
            if runs and i == runs[-1][1] + 1:
                runs[-1][1] = i
            else:
                runs.append([i, i])
        for s, e in runs:
            print(f"  {times[s]:.3f}s -> {times[e]:.3f}s  frames {e - s + 1}  mean gray {means[s]:.0f}")

    if args.csv:
        with args.csv.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["frame", "time_s", "diff_from_prev", "gray_std", "gray_mean"])
            for i in range(len(gray)):
                w.writerow([i, f"{times[i]:.4f}", f"{diffs[i - 1]:.3f}" if i else "", f"{stds[i]:.2f}", f"{means[i]:.1f}"])


if __name__ == "__main__":
    main()
