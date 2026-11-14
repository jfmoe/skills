"""Call every interface in a payload file once and record which ones the gateway serves.

Usage:
    python probe.py <payloads.tsv> <response directory> <availability.json>

Each payload line is ``api_id<TAB>json payload``; lines starting with ``#`` are skipped. Raw
responses go to the response directory, one file per interface. The availability file gets
one entry per interface: HTTP status, gateway error code, and the number of records returned.
A rejected key or an exhausted quota stops the run without writing the availability file,
because every later interface would look unserved. Every call counts against the daily quota,
so run it only when checking for upstream changes.
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

import htbr_client


def record_count(data: object) -> int | None:
    """Rows in a response: the list itself, or the first list the data object holds."""
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return next((len(value) for value in data.values() if isinstance(value, list)), None)
    return None


def main(arguments: list[str]) -> int:
    if len(arguments) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    payloads, responses, availability = (Path(argument) for argument in arguments)
    responses.mkdir(parents=True, exist_ok=True)
    result = {}
    for line in payloads.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        api_id, payload = line.split("\t")
        started = time.time()
        try:
            status, body = 200, htbr_client.invoke(api_id, json.loads(payload))
        except htbr_client.GatewayError as failure:
            if failure.status in (401, 429):
                print(f"stopped at {api_id}: {failure}", file=sys.stderr)
                return 1
            status, body = failure.status, failure.body
        except OSError as failure:  # timeouts and network errors
            status, body = 0, {"error": {"code": type(failure).__name__, "message": str(failure)}}
        (responses / f"{api_id}.json").write_text(json.dumps(body, ensure_ascii=False, indent=1))
        error = body.get("error") if isinstance(body, dict) else None
        result[api_id] = {
            "status": status,
            "error": error.get("code") if isinstance(error, dict) else None,
            "records": record_count(body.get("data")) if isinstance(body, dict) else None,
            "seconds": round(time.time() - started, 1),
        }
        print(api_id, result[api_id])
        time.sleep(3)  # upstream asks for at least three seconds between calls
    availability.write_text(
        json.dumps(
            {"checked_on": date.today().isoformat(), "interfaces": dict(sorted(result.items()))},
            ensure_ascii=False,
            indent=1,
        )
        + "\n"
    )
    served = sum(entry["status"] == 200 for entry in result.values())
    unknown = [name for name, entry in result.items() if entry["status"] not in (200, 404)]
    print(f"{served} of {len(result)} interfaces served; undetermined: {unknown}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
