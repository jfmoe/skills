"""Copy the interface documents of an unpacked upstream package into this provider.

Usage:
    python sync_upstream.py <unpacked htbr-etf-skill directory>

Only interfaces that ``references/availability.json`` records as served are copied, plus all
workflow documents and the interface catalogue with the rows of unserved interfaces dropped.
The text is kept as upstream wrote it except for the command prefix, which becomes this
skill's client. The summary lists documents that were added, changed or removed,
which is what a maintainer reviews after an upstream release.
"""

import json
import re
import sys
from pathlib import Path

PROVIDER = Path(__file__).resolve().parents[1]
UPSTREAM_COMMAND = 'python "<SKILL_DIR>/scripts/api_client.py" invoke'
COMMAND = "pixi run etf-htbr invoke"


def sync(source: Path, target: Path, names: set[str] | None) -> dict[str, list[str]]:
    target.mkdir(parents=True, exist_ok=True)
    changes: dict[str, list[str]] = {"added": [], "changed": [], "removed": [], "skipped": []}
    wanted = {}
    for path in sorted(source.glob("*.md")):
        if names is not None and path.stem not in names:
            changes["skipped"].append(path.stem)
            continue
        wanted[path.name] = path.read_text().replace(UPSTREAM_COMMAND, COMMAND)
    for name, text in wanted.items():
        current = target / name
        if not current.is_file():
            changes["added"].append(name)
        elif current.read_text() != text:
            changes["changed"].append(name)
        current.write_text(text)
    for path in sorted(target.glob("*.md")):
        if path.name not in wanted:
            path.unlink()
            changes["removed"].append(path.name)
    return changes


def served_catalog(text: str, served: set[str]) -> str:
    """The upstream catalogue without the table rows whose interfaces are all unserved."""
    kept = []
    for line in text.replace(UPSTREAM_COMMAND, COMMAND).splitlines():
        cells = line.split("|")
        names = re.findall(r"`([a-z0-9-]+)`", cells[2]) if len(cells) > 3 else []
        if names and not served.intersection(names):
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    upstream = Path(arguments[0]) / "references"
    availability = json.loads((PROVIDER / "references" / "availability.json").read_text())
    served = {name for name, entry in availability["interfaces"].items() if entry["status"] == 200}
    documented = {path.stem for path in (upstream / "apis").glob("*.md")}
    catalog = PROVIDER / "references" / "api-catalog.md"
    catalog_text = served_catalog((upstream / "api-catalog.md").read_text(), served)
    catalog_changed = not catalog.is_file() or catalog.read_text() != catalog_text
    catalog.write_text(catalog_text)
    report = {
        "catalog_changed": catalog_changed,
        "apis": sync(upstream / "apis", PROVIDER / "references" / "apis", served),
        "workflows": sync(upstream / "workflows", PROVIDER / "references" / "workflows", None),
        "documented_but_never_probed": sorted(documented - set(availability["interfaces"])),
        "probed_but_no_longer_documented": sorted(set(availability["interfaces"]) - documented),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
