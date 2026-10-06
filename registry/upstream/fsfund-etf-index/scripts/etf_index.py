#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fsfund-etf-index Skill CLI。

子命令:
  refresh-meta              拉取并缓存本 Skill 接口元数据
  list-apis [--json]        列出可用接口（PATH）
  schema <PATH>             查看某接口入参/出参
  call <PATH> [JSON_BODY]   调用业务接口

环境变量:
  HJ_APP_SECRET             应用密钥（必填）
  HJ_BASE_URL               网关前缀，默认 .../udsp/skill/v01/
  HJ_SKILL_URL              Skill 标识，默认 fsfund-etf-index
  HJ_META_CACHE_SEC         元数据缓存秒数，默认 3600；0 表示每次刷新
"""

from __future__ import annotations

import json
import sys
from typing import Any

from hj_client import api_data, fetch_skill_meta
from meta_registry import (
    build_registry,
    format_api_list,
    format_schema,
    get_registry,
    resolve_api_path,
    save_registry,
)


def cmd_refresh_meta() -> int:
    raw = fetch_skill_meta()
    registry = build_registry(raw)
    path = save_registry(registry)
    print(f"元数据已缓存: {path}")
    print(f"接口数量: {len(registry.get('apis', {}))}")
    return 0


def cmd_list_apis(use_json: bool) -> int:
    registry = get_registry()
    if use_json:
        apis = registry.get("apis") or {}
        payload = [
            {
                "path": path,
                "api_name": row.get("API_NAME"),
                "category": row.get("CATEGORY_NAME"),
                "api_memo": row.get("API_MEMO"),
                "api_url": row.get("API_URL"),
            }
            for path, row in sorted(apis.items())
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_api_list(registry))
    return 0


def cmd_schema(path_arg: str) -> int:
    registry = get_registry()
    path = resolve_api_path(registry, path_arg)
    print(format_schema(registry, path))
    return 0


def cmd_call(path_arg: str, body_json: str | None) -> int:
    registry = get_registry()
    path = resolve_api_path(registry, path_arg)
    body: dict[str, Any] = {}
    if body_json:
        body = json.loads(body_json)
    result = api_data(path, body)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def print_help() -> None:
    print(__doc__.strip())


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help", "help"}:
        print_help()
        return 0 if len(argv) >= 2 else 2

    cmd = argv[1]
    if cmd == "refresh-meta":
        return cmd_refresh_meta()
    if cmd == "list-apis":
        use_json = "--json" in argv[2:]
        return cmd_list_apis(use_json)
    if cmd == "schema":
        if len(argv) < 3:
            print("用法: etf_index.py schema <PATH>", file=sys.stderr)
            return 2
        return cmd_schema(argv[2])
    if cmd == "call":
        if len(argv) < 3:
            print("用法: etf_index.py call <PATH> [JSON_BODY]", file=sys.stderr)
            return 2
        body = argv[3] if len(argv) >= 4 else None
        return cmd_call(argv[2], body)

    print(f"未知子命令: {cmd}", file=sys.stderr)
    print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
