#!/usr/bin/env python3
"""Record a device screen from WebDriverAgent's MJPEG stream into a movie.

Usage:
    python3 -I research/tools/record_mjpeg.py <seconds> <out.mp4> [--fps-setting 60] [--scale 25]

Unlike USB screen capture through AVFoundation, which switches the device's
USB configuration and drops the XCTest connection WDA runs on, the MJPEG
stream rides the existing usbmux connection. Frame rate is lower and depends
on the device, so every frame keeps its real arrival time: the output movie
uses variable frame durations and analyze_motion.py reads those timestamps.

Requires a READY iPhone Use session (reads its config and session files).
"""

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import urllib.request

STATE = pathlib.Path(os.environ.get("IPHONE_USE_STATE_DIR", pathlib.Path.home() / ".local/share/iphone-use"))


def wda_settings(settings):
    config = json.loads((STATE / "config.json").read_text())
    session = json.loads((STATE / "session.json").read_text())
    url = f"http://127.0.0.1:{config['local_port']}/session/{session['session_id']}/appium/settings"
    req = urllib.request.Request(url, data=json.dumps({"settings": settings}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30).read()
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("seconds", type=float)
    parser.add_argument("out", type=pathlib.Path)
    parser.add_argument("--fps-setting", type=int, default=60, help="WDA mjpegServerFramerate")
    parser.add_argument("--scale", type=int, default=25, help="WDA mjpegScalingFactor (percent)")
    args = parser.parse_args()

    config = wda_settings({"mjpegServerFramerate": args.fps_setting, "mjpegScalingFactor": args.scale,
                           "mjpegServerScreenshotQuality": 40})
    stream = STATE / "runtime/forward/screen-stream.mjs"
    proc = subprocess.Popen(["node", str(stream), config["udid"], str(config.get("mjpeg_device_port", 9100))],
                            stdout=subprocess.PIPE)
    frames_dir = pathlib.Path(tempfile.mkdtemp(prefix="mjpeg-"))
    buf, frames, start = b"", [], time.monotonic()
    start_epoch = time.time() - (time.monotonic() - start)
    print(f"recording {args.seconds}s", flush=True)
    try:
        while time.monotonic() - start < args.seconds:
            chunk = proc.stdout.read1(1 << 16)
            if not chunk:
                break
            buf += chunk
            while True:
                s = buf.find(b"\xff\xd8")
                e = buf.find(b"\xff\xd9", s + 2) if s >= 0 else -1
                if s < 0 or e < 0:
                    break
                t = time.monotonic() - start
                path = frames_dir / f"{len(frames):06d}.jpg"
                path.write_bytes(buf[s:e + 2])
                frames.append((path, t))
                buf = buf[e + 2:]
    finally:
        proc.terminate()

    if len(frames) < 2:
        raise SystemExit("no frames received; is the iPhone Use session READY?")
    listing = frames_dir / "frames.txt"
    with listing.open("w") as f:
        for (path, t), (_, t_next) in zip(frames, frames[1:] + [(None, frames[-1][1] + 1 / 30)]):
            f.write(f"file '{path}'\nduration {t_next - t:.4f}\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-fps_mode", "vfr", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(args.out)], check=True)
    shutil.rmtree(frames_dir)
    span = frames[-1][1] - frames[0][1]
    print(f"{len(frames)} frames over {span:.2f}s ({(len(frames) - 1) / span:.1f} fps) -> {args.out}")
    # The movie starts at the first frame: an action logged with time.time()
    # sits at (action_epoch - movie_t0_epoch) seconds; pass that to analyze_motion.py --mark.
    print(f"movie_t0_epoch={start_epoch + frames[0][1]:.3f}")


if __name__ == "__main__":
    main()
