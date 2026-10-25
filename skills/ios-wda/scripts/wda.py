#!/usr/bin/env python3
"""Drive a physical iPhone/iPad through WebDriverAgent (WDA). Coordinates are points.

Service:
  devices | teams | apps [KEYWORD]        paired devices / signing team IDs / installed apps
  setup [--udid U] [--team T] [--bundle-id B] [--ref TAG]
                                          save config, fetch WDA source, build and sign (idempotent)
  start | stop | status | doctor          run the USB forward and runner; report readiness
                                          (other commands restart a dropped service by themselves)

Observe:
  shot [PATH] [--scale S] [--crop X,Y,W,H]   screenshot; image px = points x S
  tree [-i] | find TEXT | wait TEXT [--timeout S] | app | alert

Act (prints ok ... t=<epoch sent>; add --wait TEXT, --find TEXT, --tree or --shot [PATH] to observe):
  tap X Y | tap --text T | doubletap X Y | hold X Y [SEC] | swipe X1 Y1 X2 Y2 [--ms N] [--hold-ms N]
  pinch CX CY FROM TO [--ms N] | type TEXT | home | activate ID | terminate ID
  orient portrait|landscape | alert --tap BUTTON | sleep SEC
  do 'STEP' 'STEP' ... [observe options]   several steps in one call, stops at the first failure
  record SEC OUT.mp4 [--pct 25] | settings JSON
  get EP | post EP JSON | delete EP   [--root] [--out FILE]  any WDA endpoint, raw

State: $WDA_HOME (default ~/.local/share/ios-wda).
"""
import argparse
import base64
import contextlib
import fcntl
import http.client
import json
import os
import plistlib
import re
import shlex
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOME = Path(os.environ.get("WDA_HOME", Path.home() / ".local/share/ios-wda"))
CONFIG, SOURCE, DERIVED, LOGS = HOME / "config.json", HOME / "WebDriverAgent", HOME / "derived_data", HOME / "logs"
REPOSITORY = "https://github.com/appium/WebDriverAgent.git"
DEFAULT_REF = "v16.15.3"
DEVICE_PORT, DEVICE_MJPEG_PORT = 8100, 9100
DEFAULTS = {"ref": DEFAULT_REF, "port": 8100, "mjpeg_port": 9100}
USBMUXD = "/var/run/usbmuxd"
ALWAYS_LIST = {"TextField", "SecureTextField", "SearchField", "TextView", "Alert", "Sheet", "Switch"}
INTERACTIVE = {"Button", "Cell", "Link", "TextField", "SecureTextField", "SearchField", "TextView", "Switch",
               "Slider", "Tab", "SegmentedControl", "MenuItem", "Alert", "Sheet", "Key"}


def die(message):
    sys.exit(f"error: {message}")


def config():
    if not CONFIG.is_file():
        die("not configured; run: setup --udid U --team T --bundle-id B (see references/setup.md)")
    return {**DEFAULTS, **json.loads(CONFIG.read_text())}


def pid_alive(name):
    path = HOME / f"{name}.pid"
    if not path.is_file():
        return None
    pid = int(path.read_text())
    try:
        os.kill(pid, 0)
        return pid
    except ProcessLookupError:
        path.unlink()
        return None


# ---------------------------------------------------------------- usbmuxd forward
# usbmuxd is the macOS daemon that tunnels TCP to a device port over USB or Wi-Fi pairing.

def _recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("usbmuxd closed the connection")
        data += chunk
    return data


def _mux(sock, message):
    payload = plistlib.dumps({**message, "ClientVersionString": "ios-wda", "ProgName": "ios-wda"})
    sock.sendall(struct.pack("<IIII", 16 + len(payload), 1, 8, 1) + payload)
    length = struct.unpack("<I", _recv_exact(sock, 16)[:4])[0]
    return plistlib.loads(_recv_exact(sock, length - 16))


def mux_device_id(udid):
    want = udid.replace("-", "").lower()
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(USBMUXD)
        listed = _mux(s, {"MessageType": "ListDevices"}).get("DeviceList", [])
    matches = [d for d in listed if d["Properties"].get("SerialNumber", "").replace("-", "").lower() == want]
    # A Wi-Fi-paired device is listed twice; prefer the cable.
    matches.sort(key=lambda d: d["Properties"].get("ConnectionType") != "USB")
    return matches[0]["DeviceID"] if matches else None


def mux_connect(udid, port):
    device_id = mux_device_id(udid)
    if device_id is None:
        raise ConnectionError("device not visible to usbmuxd (unplugged, untrusted, or asleep)")
    s = socket.socket(socket.AF_UNIX)
    s.connect(USBMUXD)
    result = _mux(s, {"MessageType": "Connect", "DeviceID": device_id, "PortNumber": socket.htons(port)})
    if result.get("Number") != 0:
        s.close()
        raise ConnectionError(f"device port {port} refused")
    return s


def _pipe(src, dst):
    try:
        while chunk := src.recv(65536):
            dst.sendall(chunk)
    except OSError:
        pass
    finally:
        for sock in (src, dst):
            with contextlib.suppress(OSError):
                sock.shutdown(socket.SHUT_RDWR)


def serve_forward(udid, mappings):
    def accept_loop(server, device_port):
        while True:
            client, _ = server.accept()
            try:
                remote = mux_connect(udid, device_port)
            except Exception as e:
                print(f"forward {device_port}: {e}", flush=True)
                client.close()
                continue
            for a, b in ((client, remote), (remote, client)):
                threading.Thread(target=_pipe, args=(a, b), daemon=True).start()

    for local_port, device_port in mappings:
        server = socket.create_server(("127.0.0.1", local_port))
        threading.Thread(target=accept_loop, args=(server, device_port), daemon=True).start()
        print(f"forward 127.0.0.1:{local_port} -> device:{device_port}", flush=True)
    signal.sigwait({signal.SIGINT, signal.SIGTERM})


# ---------------------------------------------------------------- service

def run(argv, timeout=60):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def list_devices():
    with tempfile.NamedTemporaryFile(suffix=".json") as out:
        code, _, err = run(["xcrun", "devicectl", "list", "devices", "--json-output", out.name, "--timeout", "10"])
        if code:
            die(err.strip())
        devices = json.loads(Path(out.name).read_text())["result"]["devices"]
    return [d for d in devices if d.get("hardwareProperties", {}).get("reality") == "physical"]


def cmd_devices(_):
    for d in list_devices():
        hw, props = d["hardwareProperties"], d.get("deviceProperties", {})
        print(" | ".join(str(x) for x in (props.get("name"), hw.get("udid"), hw.get("marketingName"),
                                           props.get("osVersionNumber"), d.get("connectionProperties", {}).get("tunnelState"),
                                           "devmode=" + str(props.get("developerModeStatus")))))


def cmd_teams(_):
    _, out, _ = run(["security", "find-certificate", "-a", "-c", "Apple Development", "-p"])
    seen = set()
    for pem in re.findall(r"-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----", out, re.S):
        info = subprocess.run(["openssl", "x509", "-noout", "-subject", "-enddate", "-nameopt", "multiline,utf8"],
                              input=pem, capture_output=True, text=True).stdout
        team = re.search(r"organizationalUnitName\s*=\s*(\w+)", info)
        if team and team.group(1) not in seen:
            seen.add(team.group(1))
            org = re.search(r"organizationName\s*=\s*(.+)", info)
            end = re.search(r"notAfter=(.+)", info)
            print(f"{team.group(1)} | {org.group(1).strip() if org else ''} | cert expires {end.group(1) if end else '?'}")
    if not seen:
        print("no Apple Development certificate; sign in to Xcode > Settings > Accounts (setup can also create one)")


def xcodebuild(c, action):
    return ["xcodebuild", "-project", str(SOURCE / "WebDriverAgent.xcodeproj"), "-scheme", "WebDriverAgentRunner",
            "-destination", f"id={c['udid']}", "-derivedDataPath", str(DERIVED), "-allowProvisioningUpdates",
            f"DEVELOPMENT_TEAM={c['team_id']}", "CODE_SIGN_STYLE=Automatic",
            f"PRODUCT_BUNDLE_IDENTIFIER={c['bundle_id']}", action]


def cmd_setup(a):
    saved = json.loads(CONFIG.read_text()) if CONFIG.is_file() else {}
    for key, value in (("udid", a.udid), ("team_id", a.team), ("bundle_id", a.bundle_id), ("ref", a.ref),
                       ("port", a.port), ("mjpeg_port", a.mjpeg_port)):
        if value is not None:
            saved[key] = value
    missing = [k for k in ("udid", "team_id", "bundle_id") if not saved.get(k)]
    if missing:
        die(f"missing {', '.join(missing)}; find them with: devices, teams")
    HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(saved, indent=1) + "\n")
    c = config()

    _, tag, _ = run(["git", "-C", str(SOURCE), "describe", "--tags", "--exact-match"]) if SOURCE.is_dir() else (1, "", "")
    if tag.strip() != c["ref"]:
        shutil.rmtree(SOURCE, ignore_errors=True)
        code, _, err = run(["git", "clone", "--depth", "1", "--branch", c["ref"], REPOSITORY, str(SOURCE)], timeout=600)
        if code:
            die(err.strip())
        print(f"fetched WDA {c['ref']}")

    LOGS.mkdir(parents=True, exist_ok=True)
    log = LOGS / "build.log"
    with log.open("w") as f:
        code = subprocess.run(xcodebuild(c, "build-for-testing"), stdout=f, stderr=subprocess.STDOUT).returncode
    if code:
        errors = [line for line in log.read_text().splitlines() if "error" in line.lower()][-8:]
        die("build failed:\n" + "\n".join(errors) + f"\nfull log: {log}; causes: references/setup.md")
    (HOME / "build.json").write_text(json.dumps({k: c[k] for k in ("udid", "team_id", "bundle_id", "ref")}))
    print(f"built and signed WDA {c['ref']} for {c['udid']}; next: start")


def wda_status(port, timeout=3):
    try:
        with OPENER.open(f"http://127.0.0.1:{port}/status", timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return None


def spawn(name, argv):
    LOGS.mkdir(parents=True, exist_ok=True)
    log = (LOGS / f"{name}.log").open("w")
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    (HOME / f"{name}.pid").write_text(str(p.pid))


def ensure_ready(timeout):
    """Start whatever is missing (forward, runner) and wait until WDA answers."""
    c = config()
    if not pid_alive("forward"):
        spawn("forward", [sys.executable, "-I", __file__, "_forward"])
        time.sleep(1)
        if not pid_alive("forward"):
            die("forward exited:\n" + (LOGS / "forward.log").read_text()[-600:] +
                "\nport in use? pick others: setup --port N --mjpeg-port M")
    if not wda_status(c["port"]):
        if not (HOME / "build.json").is_file():
            die("no build; run: setup")
        if not pid_alive("runner"):
            spawn("runner", xcodebuild(c, "test-without-building"))
        deadline = time.time() + timeout
        while not wda_status(c["port"]):
            if not pid_alive("runner") or time.time() > deadline:
                tail = (LOGS / "runner.log").read_text().splitlines()[-12:]
                hint = "runner still running but not serving: stop, then start" if pid_alive("runner") else "runner exited"
                die("runner not ready (" + hint + "); log tail:\n" + "\n".join(tail) +
                    "\ncauses: references/setup.md#故障表")
            time.sleep(2)


def cmd_start(a):
    ensure_ready(a.timeout)
    cmd_status(a)


def cmd_stop(_):
    for name in ("runner", "forward"):
        pid = pid_alive(name)
        if pid:
            os.killpg(pid, signal.SIGTERM)
            (HOME / f"{name}.pid").unlink(missing_ok=True)
            print(f"stopped {name}")


def cmd_status(_):
    c = config()
    st = wda_status(c["port"])
    if not st:
        print(f"not ready (forward={'up' if pid_alive('forward') else 'down'}, "
              f"runner={'up' if pid_alive('runner') else 'down'}); run: start")
        return
    v = st["value"]
    win = s("GET", "/window/size")["value"]
    app = request("GET", "/wda/activeAppInfo")["value"].get("bundleId")
    locked = request("GET", "/wda/locked")["value"]
    print(f"ready | {v.get('device')} {v.get('os', {}).get('name')} {v.get('os', {}).get('version')} | "
          f"wda {v.get('build', {}).get('version')} | app {app} | {win['width']}x{win['height']} pt | "
          f"{'LOCKED' if locked else 'unlocked'}")


def cmd_doctor(_):
    code, out, _ = run(["xcodebuild", "-version"])
    print("xcode:", out.split("\n")[0] if code == 0 else "missing; install full Xcode and launch it once")
    if not CONFIG.is_file():
        print("config: missing; run setup")
        return
    c = config()
    print("config:", " ".join(f"{k}={c[k]}" for k in ("udid", "team_id", "bundle_id", "ref", "port", "mjpeg_port")))
    print("build:", "ok" if (HOME / "build.json").is_file() else "missing; run setup")
    try:
        print("usb:", "visible" if mux_device_id(c["udid"]) is not None else "not visible; plug in, unlock, trust")
    except OSError as e:
        print("usb: error", e)
    for tool in ("git", "ffmpeg"):
        print(f"{tool}:", "ok" if shutil.which(tool) else f"missing (needed by {'setup' if tool == 'git' else 'record'})")
    print("forward:", "up" if pid_alive("forward") else "down (see logs/forward.log)",
          "| runner:", "up" if pid_alive("runner") else "down")
    st = wda_status(c["port"])
    if not st:
        print("wda: not ready")
    else:
        version = st["value"].get("build", {}).get("version")
        external = "" if pid_alive("runner") else "; runner started elsewhere: usable, but stop cannot stop it"
        mismatch = "" if c["ref"].lstrip("v") == version else f"; version differs from ref {c['ref']}"
        print(f"wda: ready {version}{external}{mismatch}")


# ---------------------------------------------------------------- WDA client

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
_session = None
_last_post = 0.0  # epoch of the latest POST: the moment an action was sent


class InvalidSession(Exception):
    pass


def _send(method, path, payload, timeout):
    global _last_post
    data = json.dumps(payload).encode() if payload is not None else None
    if method != "GET":
        _last_post = time.time()
    req = urllib.request.Request(f"http://127.0.0.1:{config()['port']}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with OPENER.open(req, timeout=timeout) as r:
        return json.load(r)


def device_context():
    """One-line hint on why an action failed: a locked device or another app in front."""
    try:
        if _send("GET", "/wda/locked", None, 3)["value"]:
            return "device LOCKED: ask the user to unlock"
        return "foreground " + str(_send("GET", "/wda/activeAppInfo", None, 3)["value"].get("bundleId"))
    except Exception:
        return "device state unknown"


def request(method, path, payload=None, timeout=60, recovered=False):
    try:
        return _send(method, path, payload, timeout)
    except urllib.error.HTTPError as e:
        body = json.loads(e.read() or b"{}")
        value = body.get("value", body)
        message = value.get("message", value) if isinstance(value, dict) else value
        if isinstance(value, dict) and value.get("error") == "invalid session id":
            raise InvalidSession
        die(f"WDA {e.code} {path}: {str(message)[:300]} | {device_context()}")
    except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError) as e:
        reason = getattr(e, "reason", e)
        # Refused means the local forward is not listening, so nothing reached the device.
        delivered = method != "GET" and not isinstance(reason, ConnectionRefusedError)
        if recovered or not (HOME / "build.json").is_file():
            die(f"WDA unreachable ({reason}); run: doctor")
        print(f"WDA unreachable ({reason}); restarting service", file=sys.stderr)
        ensure_ready(90)
        if delivered:
            die(f"service restarted, but {method} {path} may or may not have reached the device; "
                "observe the screen before repeating it")
        return request(method, path, payload, timeout, recovered=True)


def session_id():
    """Reuse the active session so other WDA clients keep theirs."""
    global _session
    if _session is None:
        _session = request("GET", "/status").get("sessionId")
        if not _session:
            caps = {"shouldWaitForQuiescence": False, "waitForIdleTimeout": 0, "shouldTerminateApp": False}
            _session = request("POST", "/session", {"capabilities": {"alwaysMatch": caps}})["sessionId"]
            s("POST", "/appium/settings", {"settings": {"waitForIdleTimeout": 0, "animationCoolOffTimeout": 0,
                                                        "snapshotMaxDepth": 50}})
    return _session


def s(method, endpoint, payload=None, timeout=60):
    global _session
    try:
        return request(method, f"/session/{session_id()}{endpoint}", payload, timeout)
    except InvalidSession:
        # The session ended (runner restarted); WDA rejected the call, so sending it again is safe.
        _session = None
        return request(method, f"/session/{session_id()}{endpoint}", payload, timeout)


@contextlib.contextmanager
def operation_lock(timeout=30):
    HOME.mkdir(parents=True, exist_ok=True)
    with (HOME / "operation.lock").open("a") as f:
        deadline = time.time() + timeout
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() > deadline:
                    die(f"device busy: another wda.py call held the lock for {timeout}s")
                time.sleep(0.2)
        yield


def touch(*fingers):
    actions = [{"type": "pointer", "id": f"f{i}", "parameters": {"pointerType": "touch"}, "actions": steps}
               for i, steps in enumerate(fingers)]
    s("POST", "/actions", {"actions": actions})


def stroke(x1, y1, x2, y2, ms, hold_ms=0):
    return [{"type": "pointerMove", "duration": 0, "x": x1, "y": y1}, {"type": "pointerDown", "button": 0},
            {"type": "pause", "duration": hold_ms},
            {"type": "pointerMove", "duration": ms, "x": x2, "y": y2}, {"type": "pointerUp", "button": 0}]


def elements(include_offscreen=False):
    raw = s("GET", "/source?format=xml&excluded_attributes=visible,accessible")["value"]
    win = s("GET", "/window/size")["value"]
    found, seen = [], set()
    for node in ET.fromstring(raw).iter():
        a = node.attrib
        kind = a.get("type", "").removeprefix("XCUIElementType")
        if kind in ("Application", "Window") or "x" not in a:
            continue
        text = a.get("label") or a.get("name") or ""
        value = a.get("value") or ""
        if not (text or value or kind in ALWAYS_LIST):
            continue
        x, y, w, h = (float(a[k]) for k in ("x", "y", "width", "height"))
        if not include_offscreen and not (w > 0 and h > 0 and x < win["width"] and y < win["height"]
                                          and x + w > 0 and y + h > 0):
            continue
        n = {"type": kind, "text": text, "value": "" if value == text else value,
             "x": round(x + w / 2), "y": round(y + h / 2), "w": round(w), "h": round(h),
             "enabled": a.get("enabled") != "false"}
        key = tuple(n.values())
        if key not in seen:
            seen.add(key)
            found.append(n)
    return found


def show(nodes):
    if not nodes:
        print("(no matching element)")
    for n in nodes:
        value = f" ={n['value']!r}" if n["value"] else ""
        print(f"{n['type']} {n['text']!r}{value} @{n['x']},{n['y']} {n['w']}x{n['h']}{'' if n['enabled'] else ' disabled'}")


def match(nodes, text):
    """Exact text before substring; within each, enabled interactive elements first, then tree order."""
    exact = [n for n in nodes if n["text"] == text]
    partial = [n for n in nodes if n not in exact and (text in n["text"] or text in n["value"])]
    rank = lambda n: (not n["enabled"], n["type"] not in INTERACTIVE)
    return sorted(exact, key=rank) + sorted(partial, key=rank)


def screenshot(path, scale=1.0, crop=None):
    win = s("GET", "/window/size")["value"]
    png = base64.b64decode(request("GET", "/screenshot")["value"])
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        tmp.write(png)
        tmp.flush()
        out_w, out_h = win["width"] * scale, win["height"] * scale
        if crop:
            # sips resamples before cropping when both are in one call, so crop in its own pass.
            # It also reads an offset of 0 as "unset" and centers the crop; 1 px is close enough.
            cx, cy, cw, ch = crop
            px = struct.unpack(">I", png[16:20])[0] / win["width"]
            subprocess.run(["sips", "-c", str(round(ch * px)), str(round(cw * px)), "--cropOffset",
                            str(max(1, round(cy * px))), str(max(1, round(cx * px))), tmp.name],
                           check=True, capture_output=True)
            out_w, out_h = cw * scale, ch * scale
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "75", "-Z",
                        str(round(max(out_w, out_h))), tmp.name, "--out", path], check=True, capture_output=True)
    origin = f", origin {crop[0]:g},{crop[1]:g}" if crop else ""
    print(f"{path} {round(out_w)}x{round(out_h)} px = points x {scale:g}{origin}")


def record(seconds, out, pct):
    c = config()
    keys = ("mjpegServerFramerate", "mjpegScalingFactor", "mjpegServerScreenshotQuality")
    saved = {k: v for k, v in s("GET", "/appium/settings")["value"].items() if k in keys}
    # 60 is only a cap; the device delivers what it can capture (about 20 fps on an iPad Pro).
    s("POST", "/appium/settings", {"settings": dict(zip(keys, (60, pct, 40)))})
    stream = OPENER.open(f"http://127.0.0.1:{c['mjpeg_port']}/", timeout=10)
    frames_dir = Path(tempfile.mkdtemp(prefix="wda-rec-"))
    buf, frames = b"", []
    start, start_epoch = time.monotonic(), time.time()
    try:
        while time.monotonic() - start < seconds:
            chunk = stream.read1(1 << 16)
            if not chunk:
                break
            buf += chunk
            while (i := buf.find(b"\xff\xd8")) >= 0 and (j := buf.find(b"\xff\xd9", i + 2)) >= 0:
                path = frames_dir / f"{len(frames):06d}.jpg"
                path.write_bytes(buf[i:j + 2])
                frames.append((path, time.monotonic() - start))
                buf = buf[j + 2:]
    finally:
        stream.close()
        s("POST", "/appium/settings", {"settings": saved})
    if len(frames) < 2:
        die("no frames received; check status")
    listing = frames_dir / "frames.txt"
    with listing.open("w") as f:
        for (path, t), (_, t_next) in zip(frames, frames[1:] + [(None, frames[-1][1] + 1 / 30)]):
            f.write(f"file '{path}'\nduration {t_next - t:.4f}\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-fps_mode", "vfr",
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True)
    shutil.rmtree(frames_dir)
    span = frames[-1][1] - frames[0][1]
    # An action logged with time.time() sits at (epoch - movie_t0_epoch) seconds into the movie.
    print(f"{out} {len(frames)} frames / {span:.2f}s ({(len(frames) - 1) / span:.1f} fps) "
          f"movie_t0_epoch={start_epoch + frames[0][1]:.3f}")


def wait_for(text, timeout):
    deadline = time.time() + timeout
    while not (hits := match(elements(), text)):
        if time.time() > deadline:
            die(f"{text!r} not visible after {timeout:g}s")
        time.sleep(0.5)
    show(hits[:3])


def act(a):
    if a.cmd == "tap":
        if a.text:
            hits = match(elements(), a.text)
            if not hits:
                die(f"no visible element matching {a.text!r}; try: find, or tap by coordinates from shot")
            a.x, a.y = hits[0]["x"], hits[0]["y"]
            label = f" {hits[0]['type']} {hits[0]['text']!r}"
        elif a.y is None:
            die("tap needs X Y or --text")
        else:
            label = ""
        touch([{"type": "pointerMove", "duration": 0, "x": a.x, "y": a.y}, {"type": "pointerDown", "button": 0},
               {"type": "pause", "duration": 60}, {"type": "pointerUp", "button": 0}])
        return f"tap{label} @{a.x:g},{a.y:g}"
    if a.cmd == "doubletap":
        s("POST", "/wda/doubleTap", {"x": a.x, "y": a.y})
    elif a.cmd == "hold":
        s("POST", "/wda/touchAndHold", {"x": a.x, "y": a.y, "duration": a.seconds})
    elif a.cmd == "swipe":
        touch(stroke(a.x1, a.y1, a.x2, a.y2, a.ms, a.hold_ms))
    elif a.cmd == "pinch":
        r0, r1 = a.start / 2, a.end / 2
        touch(stroke(a.cx - r0, a.cy, a.cx - r1, a.cy, a.ms), stroke(a.cx + r0, a.cy, a.cx + r1, a.cy, a.ms))
    elif a.cmd == "type":
        s("POST", "/wda/keys", {"value": list(a.text)})
    elif a.cmd == "home":
        request("POST", "/wda/homescreen", {})
    elif a.cmd in ("activate", "terminate"):
        s("POST", f"/wda/apps/{a.cmd}", {"bundleId": a.bundle_id})
    elif a.cmd == "orient":
        s("POST", "/orientation", {"orientation": a.orientation.upper()})
    elif a.cmd == "alert" and a.tap:
        s("POST", "/alert/accept", {"name": a.tap})
    return a.cmd


SERVICE = ("devices", "teams", "setup", "start", "stop", "status", "doctor", "apps")
NOT_IN_BATCH = SERVICE + ("record", "do", "_forward")
ACTS = ("tap", "doubletap", "hold", "swipe", "pinch", "type", "home", "activate", "terminate", "orient", "alert")


def build_parser():
    p = argparse.ArgumentParser(prog="wda", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="command")
    for name in ("devices", "teams", "stop", "status", "doctor", "app", "_forward"):
        sub.add_parser(name)
    sub.add_parser("apps").add_argument("keyword", nargs="?", help="match app name or bundle ID, any case")
    c = sub.add_parser("setup")
    for flag in ("--udid", "--team", "--bundle-id", "--ref"):
        c.add_argument(flag)
    c.add_argument("--port", type=int)
    c.add_argument("--mjpeg-port", type=int)
    sub.add_parser("start").add_argument("--timeout", type=int, default=120)

    c = sub.add_parser("shot")
    c.add_argument("path", nargs="?", default="/tmp/wda-shot.jpg")
    c.add_argument("--scale", type=float, default=1)
    c.add_argument("--crop", help="X,Y,W,H in points")
    sub.add_parser("tree").add_argument("-i", "--interactive", action="store_true")
    sub.add_parser("find").add_argument("text")
    c = sub.add_parser("wait")
    c.add_argument("text")
    c.add_argument("--timeout", type=float, default=10)
    sub.add_parser("sleep").add_argument("seconds", type=float)

    def observe_options(parser):
        parser.add_argument("--shot", nargs="?", const="/tmp/wda-shot.jpg", help="screenshot afterwards")
        parser.add_argument("--scale", type=float, default=1, help="scale for --shot")
        parser.add_argument("--tree", action="store_true", help="print visible elements afterwards")
        parser.add_argument("--find", metavar="TEXT", help="print only elements matching TEXT afterwards")
        parser.add_argument("--wait", metavar="TEXT", help="afterwards, wait up to 10s until TEXT is visible")
        parser.add_argument("--settle", type=float, default=0.6, help="seconds before --shot/--tree/--find")
        return parser

    act = {name: observe_options(sub.add_parser(name)) for name in ACTS}
    act["tap"].add_argument("x", nargs="?", type=float)
    act["tap"].add_argument("y", nargs="?", type=float)
    act["tap"].add_argument("--text")
    for name in ("doubletap", "hold"):
        act[name].add_argument("x", type=float)
        act[name].add_argument("y", type=float)
    act["hold"].add_argument("seconds", nargs="?", type=float, default=1.0)
    for k in ("x1", "y1", "x2", "y2"):
        act["swipe"].add_argument(k, type=float)
    act["swipe"].add_argument("--ms", type=int, default=300)
    act["swipe"].add_argument("--hold-ms", type=int, default=0)
    act["pinch"].add_argument("cx", type=float)
    act["pinch"].add_argument("cy", type=float)
    act["pinch"].add_argument("start", type=float, help="finger gap at start, points (fingers move horizontally)")
    act["pinch"].add_argument("end", type=float, help="finger gap at end; larger than start zooms in")
    act["pinch"].add_argument("--ms", type=int, default=400)
    act["type"].add_argument("text")
    act["activate"].add_argument("bundle_id")
    act["terminate"].add_argument("bundle_id")
    act["orient"].add_argument("orientation", choices=["portrait", "landscape"])
    act["alert"].add_argument("--tap")
    c = observe_options(sub.add_parser("do", help="run several steps in one call; stops at the first failure"))
    c.add_argument("steps", nargs="+", help="each step is one quoted command line, e.g. 'tap --text 搜索'")

    c = sub.add_parser("record")
    c.add_argument("seconds", type=float)
    c.add_argument("out")
    c.add_argument("--pct", type=int, default=25, help="frame size as a percent of screen pixels")
    sub.add_parser("settings").add_argument("json")
    for name in ("get", "post", "delete"):
        c = sub.add_parser(name)
        c.add_argument("endpoint")
        if name == "post":
            c.add_argument("json")
        c.add_argument("--root", action="store_true", help="path from the server root, not the session")
        c.add_argument("--out", help="write the full value to a file instead of printing 4000 chars")
    return p


def cmd_apps(a):
    with tempfile.NamedTemporaryFile(suffix=".json") as out:
        code, _, err = run(["xcrun", "devicectl", "device", "info", "apps", "--device", config()["udid"],
                            "--include-default-apps", "--json-output", out.name])
        if code:
            die(err.strip().splitlines()[-1] if err.strip() else "devicectl failed")
        apps = json.loads(Path(out.name).read_text())["result"]["apps"]
    key = (a.keyword or "").lower()
    rows = sorted((x["name"], x["bundleIdentifier"]) for x in apps
                  if key in x["name"].lower() or key in x["bundleIdentifier"].lower())
    for name, bundle in rows:
        print(f"{bundle} | {name}")
    if not rows:
        print("(no matching app)")


def observe(a):
    if a.wait:
        wait_for(a.wait, 10)
    elif a.shot or a.tree or a.find:
        time.sleep(a.settle)
    if a.find:
        show(match(elements(), a.find))
    if a.tree:
        show(elements())
    if a.shot:
        screenshot(a.shot, a.scale)


def execute(a, parser):
    if a.cmd in ACTS and not (a.cmd == "alert" and not a.tap):
        print(f"ok {act(a)} t={_last_post:.3f}")
        observe(a)
    elif a.cmd == "do":
        for n, line in enumerate(a.steps, 1):
            try:
                step = parser.parse_args(shlex.split(line))
                if step.cmd in NOT_IN_BATCH:
                    die(f"{step.cmd} cannot run inside do")
                execute(step, parser)
            except SystemExit as e:
                done = f"{n - 1} of them done"
                die(f"step {n}/{len(a.steps)} {line!r} failed ({done}): {str(e.code).removeprefix('error: ')}")
        observe(a)
    elif a.cmd == "sleep":
        time.sleep(a.seconds)
    elif a.cmd == "shot":
        screenshot(a.path, a.scale, [float(v) for v in a.crop.split(",")] if a.crop else None)
    elif a.cmd == "tree":
        nodes = elements()
        show([n for n in nodes if n["type"] in INTERACTIVE] if a.interactive else nodes)
    elif a.cmd == "find":
        show(match(elements(True), a.text))
    elif a.cmd == "wait":
        wait_for(a.text, a.timeout)
    elif a.cmd == "app":
        info = request("GET", "/wda/activeAppInfo")["value"]
        print(info.get("bundleId"), "pid", info.get("pid"))
    elif a.cmd == "alert":
        text = s("GET", "/alert/text")["value"]
        print(text, "| buttons:", " / ".join(s("GET", "/wda/alert/buttons")["value"]))
    elif a.cmd == "record":
        record(a.seconds, a.out, a.pct)
    elif a.cmd == "settings":
        print(json.dumps(s("POST", "/appium/settings", {"settings": json.loads(a.json)})["value"]))
    elif a.cmd in ("get", "post", "delete"):
        call = request if a.root else s
        value = call(a.cmd.upper(), a.endpoint, json.loads(a.json) if a.cmd == "post" else None).get("value")
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        if a.out:
            Path(a.out).write_text(text)
            print(f"{a.out} {len(text)} chars")
        else:
            print(text[:4000] + (f"\n... truncated {len(text) - 4000} chars; use --out" if len(text) > 4000 else ""))


def main():
    parser = build_parser()
    a = parser.parse_args()
    if a.cmd == "_forward":
        c = config()
        serve_forward(c["udid"], [(c["port"], DEVICE_PORT), (c["mjpeg_port"], DEVICE_MJPEG_PORT)])
    elif a.cmd in SERVICE:
        globals()["cmd_" + a.cmd](a)
    else:
        with contextlib.nullcontext() if a.cmd == "record" else operation_lock():
            execute(a, parser)


if __name__ == "__main__":
    main()
