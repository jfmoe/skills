"""Minimal client for the Huatai-PineBridge ETF data gateway.

Usage:
    python htbr_client.py invoke <api_id> '<json payload>'

The API key comes from the HTBR_API_KEY environment variable and is exchanged for a
short-lived token, cached next to this provider so repeated commands reuse it. Exit code 0
means the gateway reported success; anything else prints the gateway's status and error.
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request

BASE_URL = os.environ.get("HTBR_BASE_URL", "https://esa.huatai-pb.com/api/v1").rstrip("/")
SKILL_ID = "htbr-etf-skill"
TIMEOUT = 120
TOKEN_MARGIN = 120
TOKEN_CACHE = Path(__file__).resolve().parents[1] / ".cache" / "token.json"


class GatewayError(Exception):
    def __init__(self, status: int, body: Any) -> None:
        self.status = status
        self.body = body
        detail = body.get("error") if isinstance(body, dict) else body
        super().__init__(f"HTTP {status}: {json.dumps(detail, ensure_ascii=False)[:500]}")

    @property
    def code(self) -> str:
        if isinstance(self.body, dict) and isinstance(self.body.get("error"), dict):
            return str(self.body["error"].get("code") or "")
        return ""


def _post(path: str, payload: dict, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    call = request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(call, timeout=TIMEOUT) as response:
            status, raw = response.status, response.read().decode("utf-8", "replace")
    except error.HTTPError as failure:
        status, raw = failure.code, failure.read().decode("utf-8", "replace")
    try:
        body = json.loads(raw)
    except ValueError:
        body = raw
    if status == 200 and isinstance(body, dict) and body.get("success"):
        return body
    raise GatewayError(status, body)


def _token(refresh: bool = False) -> str:
    if not refresh and TOKEN_CACHE.is_file():
        cached = json.loads(TOKEN_CACHE.read_text())
        if cached.get("base_url") == BASE_URL and time.time() < cached["expires_at"] - TOKEN_MARGIN:
            return cached["access_token"]
    key = os.environ.get("HTBR_API_KEY")
    if not key:
        raise SystemExit("HTBR_API_KEY is not set")
    data = _post(
        "/auth/token",
        {
            "apiKey": key,
            "skillId": SKILL_ID,
            "nonce": str(uuid.uuid4()),
            "timestamp": int(time.time()),
        },
    )["data"]
    TOKEN_CACHE.parent.mkdir(exist_ok=True)
    TOKEN_CACHE.touch(mode=0o600, exist_ok=True)
    TOKEN_CACHE.write_text(
        json.dumps(
            {
                "base_url": BASE_URL,
                "access_token": data["accessToken"],
                "expires_at": time.time() + int(data.get("expiresIn") or 0),
            }
        )
    )
    return data["accessToken"]


def invoke(api_id: str, payload: dict) -> dict:
    """Call one business interface and return the gateway's full response."""
    path = f"/business/{api_id}:invoke"
    try:
        return _post(path, payload, _token())
    except GatewayError as failure:
        if failure.status != 401 or failure.code not in ("TOKEN_EXPIRED", "TOKEN_INVALID"):
            raise
        return _post(path, payload, _token(refresh=True))


def main(arguments: list[str]) -> int:
    if len(arguments) != 3 or arguments[0] != "invoke":
        print(__doc__, file=sys.stderr)
        return 2
    try:
        response = invoke(arguments[1], json.loads(arguments[2]))
    except GatewayError as failure:
        print(str(failure), file=sys.stderr)
        return 1
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
