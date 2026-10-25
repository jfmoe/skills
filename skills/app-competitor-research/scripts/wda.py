#!/usr/bin/env python3
"""Call WebDriverAgent directly through an iPhone Use (PUA) session.

Usage:
    python3 -I wda.py shot <out.png>                 screenshot (device pixels)
    python3 -I wda.py get <endpoint>                 GET /session/<id><endpoint>
    python3 -I wda.py post <endpoint> '<json>'       POST /session/<id><endpoint>

Covers gestures PUA tools lack: /wda/touchAndHold {"x","y","duration"(s)},
/wda/doubleTap {"x","y"}, /actions (W3C pointer actions, durations in ms,
two touch pointers for pinch), /orientation {"orientation":"PORTRAIT"}.
Coordinates are device points, not screenshot pixels. Holds the same
operation.lock as PUA so calls never overlap a PUA action; fails fast if busy.
"""
import fcntl, json, sys, base64, urllib.request
from pathlib import Path
root = Path.home() / '.local/share/iphone-use'
def call(method, endpoint, payload=None, session=True):
    with (root / 'operation.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = json.loads((root / 'config.json').read_text())
        s = json.loads((root / 'session.json').read_text())
        base = f"http://127.0.0.1:{config['local_port']}"
        url = base + ('/session/' + s['session_id'] if session else '') + endpoint
        req = urllib.request.Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={'Content-Type': 'application/json'}, method=method)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=60) as r:
            return json.load(r)
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'shot':
        v = call('GET', '/screenshot', session=False)['value']
        Path(sys.argv[2]).write_bytes(base64.b64decode(v)); print('ok')
    elif cmd == 'post':
        print(json.dumps(call('POST', sys.argv[2], json.loads(sys.argv[3])))[:300])
    elif cmd == 'get':
        print(json.dumps(call('GET', sys.argv[2]))[:500])
