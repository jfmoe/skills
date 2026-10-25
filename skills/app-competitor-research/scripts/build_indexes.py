#!/usr/bin/env python3
"""Build the fact index and the evidence index for one competitor directory.

Usage:
    python3 -I build_indexes.py research/<app>

Writes:
    <app>/INDEX.md               one line per fact: ID, device, topic, file
    <app>/screenshots/index.md   clickable evidence per fact ID, for humans

Fact rows are table rows whose first cell is a fact ID (e.g. RD-012) with
columns 编号 | 设备 | 主题 | 事实 | 路径. Evidence files are found by name:
any file under screenshots/ whose name starts with the fact ID.
"""

import collections
import pathlib
import re
import sys

ID = re.compile(r"^([A-Z]{2}-\d{3})")
ROW = re.compile(r"^\|\s*([A-Z]{2}-\d{3})\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|")


def fact_rows(app):
    for path in sorted(app.rglob("*.md")):
        rel = path.relative_to(app)
        if rel.parts[0] in ("screenshots", "sources", "recordings") or path.name == "INDEX.md":
            continue
        for line in path.read_text().splitlines():
            m = ROW.match(line)
            if m:
                yield m.group(1), m.group(2), m.group(3), str(rel)


def main():
    app = pathlib.Path(sys.argv[1])

    rows = sorted(set(fact_rows(app)), key=lambda r: (r[0][:2], r[0]))
    lines = ["# 事实索引", "", "由 `build_indexes.py` 生成，勿手改。按编号在对应文件中 grep 整行即可读到事实。", "",
             "| 编号 | 设备 | 主题 | 文件 |", "|---|---|---|---|"]
    lines += [f"| {i} | {d} | {t} | {f} |" for i, d, t, f in rows]
    (app / "INDEX.md").write_text("\n".join(lines) + "\n")

    shots = app / "screenshots"
    evidence = collections.defaultdict(list)
    for path in sorted(shots.rglob("*")):
        m = ID.match(path.name)
        if path.is_file() and m:
            evidence[m.group(1)].append(path.relative_to(shots))
    lines = ["# 证据索引", "", "由 `build_indexes.py` 生成，勿手改。文件名以事实编号开头。", ""]
    for prefix in sorted({k[:2] for k in evidence}):
        lines += [f"## {prefix}", ""]
        for fid in sorted(k for k in evidence if k.startswith(prefix)):
            links = "、".join(f"[{p.name[len(fid) + 1:] or p.name}]({p})" for p in evidence[fid])
            lines.append(f"- {fid}：{links}")
        lines.append("")
    (shots / "index.md").write_text("\n".join(lines))
    print(f"{len(rows)} facts, {sum(len(v) for v in evidence.values())} evidence files")


if __name__ == "__main__":
    main()
