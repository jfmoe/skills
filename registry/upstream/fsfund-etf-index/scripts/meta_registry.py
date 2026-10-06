#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill 元数据缓存：解析 get_udsp_2_api_out_in_param 响应。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from hj_client import fetch_skill_meta, skill_url

SKILL_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = SKILL_ROOT / ".cache"
CACHE_FILE = CACHE_DIR / "meta_registry.json"


def _cache_ttl_sec() -> int:
    raw = os.environ.get("HJ_META_CACHE_SEC", "3600").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 3600


def _block_rows(block: Any) -> list[dict[str, Any]]:
    if not isinstance(block, dict):
        return []
    rows = block.get("result")
    return rows if isinstance(rows, list) else []


def build_registry(raw: dict[str, Any]) -> dict[str, Any]:
    apis: dict[str, dict[str, Any]] = {}
    for row in _block_rows(raw.get("get_udsp_2_api_url")):
        path = str(row.get("PATH", "")).strip()
        if path:
            apis[path] = row

    inputs: dict[str, list[dict[str, Any]]] = {}
    for row in _block_rows(raw.get("get_udsp_2_api_input_param")):
        path = str(row.get("PATH", "")).strip()
        if path:
            inputs.setdefault(path, []).append(row)

    outputs: dict[str, list[dict[str, Any]]] = {}
    for row in _block_rows(raw.get("get_udsp_2_api_output_param")):
        path = str(row.get("PATH", "")).strip()
        if path:
            outputs.setdefault(path, []).append(row)

    required_groups: dict[str, dict[str, list[str]]] = {}
    for path, rows in inputs.items():
        groups: dict[str, list[str]] = {}
        for row in rows:
            group_id = str(row.get("REQUIRED_GROUP_ID", "") or "").strip()
            param = str(row.get("PARAM", "") or "").strip()
            if group_id and param:
                groups.setdefault(group_id, [])
                if param not in groups[group_id]:
                    groups[group_id].append(param)
        if groups:
            required_groups[path] = groups

    return {
        "skill_url": skill_url(),
        "fetched_at": int(time.time()),
        "apis": apis,
        "inputs": inputs,
        "outputs": outputs,
        "required_groups": required_groups,
    }


def save_registry(registry: dict[str, Any]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return CACHE_FILE


def load_registry() -> dict[str, Any] | None:
    if not CACHE_FILE.is_file():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def registry_is_fresh(registry: dict[str, Any]) -> bool:
    ttl = _cache_ttl_sec()
    if ttl == 0:
        return False
    fetched_at = int(registry.get("fetched_at") or 0)
    if fetched_at <= 0:
        return False
    if registry.get("skill_url") != skill_url():
        return False
    return (time.time() - fetched_at) <= ttl


def get_registry(*, force_refresh: bool = False) -> dict[str, Any]:
    if not force_refresh:
        cached = load_registry()
        if cached and registry_is_fresh(cached):
            return cached

    raw = fetch_skill_meta()
    registry = build_registry(raw)
    save_registry(registry)
    return registry


def resolve_api_path(registry: dict[str, Any], name: str) -> str:
    apis = registry.get("apis") or {}
    key = name.strip()
    if key in apis:
        return key
    upper = key.upper()
    if upper in apis:
        return upper
    lower = key.lower()
    for path, row in apis.items():
        if str(row.get("API_URL", "")).lower() == lower:
            return path
    raise SystemExit(f"未找到接口: {name}（先执行 list-apis 查看 PATH）")


def format_schema(registry: dict[str, Any], path: str) -> str:
    apis = registry.get("apis") or {}
    api = apis.get(path, {})
    lines: list[str] = [
        f"# {path}",
        f"定义来源: remote (skill_url={registry.get('skill_url')})",
        "",
    ]
    if api:
        lines.extend(
            [
                f"接口名称: {api.get('API_NAME', '')}",
                f"大类: {api.get('CATEGORY_NAME', '')}",
                f"描述: {api.get('API_MEMO', '')}",
                f"API_URL: {api.get('API_URL', '')}",
                "",
            ]
        )

    input_rows = registry.get("inputs", {}).get(path, [])
    lines.append("## 入参")
    if not input_rows:
        lines.append("（无入参记录）")
    else:
        lines.append("| 字段 | 名称 | 类型 | 样例 | 必填组 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in input_rows:
            lines.append(
                "| {param} | {name} | {typ} | {example} | {group} |".format(
                    param=row.get("PARAM", ""),
                    name=row.get("PARAM_NAME", ""),
                    typ=row.get("PARAM_TYPE", ""),
                    example=row.get("PARAM_EXAMPLE", ""),
                    group=row.get("REQUIRED_GROUP_ID", ""),
                )
            )

    groups = registry.get("required_groups", {}).get(path, {})
    if groups:
        lines.extend(["", "## 必填组规则", ""])
        for group_id, params in groups.items():
            joined = "、".join(params)
            lines.append(f"- **{group_id}**：以下入参至少填写一项 → {joined}")

    output_rows = registry.get("outputs", {}).get(path, [])
    lines.extend(["", "## 出参"])
    if not output_rows:
        lines.append("（无出参记录）")
    else:
        lines.append("| 字段 | 名称 | 类型 |")
        lines.append("| --- | --- | --- |")
        for row in output_rows:
            lines.append(
                "| {param} | {name} | {typ} |".format(
                    param=row.get("PARAM", ""),
                    name=row.get("PARAM_NAME", ""),
                    typ=row.get("PARAM_TYPE", ""),
                )
            )

    return "\n".join(lines)


def format_api_list(registry: dict[str, Any]) -> str:
    apis = registry.get("apis") or {}
    lines = [
        f"skill_url: {registry.get('skill_url')}",
        f"接口数量: {len(apis)}",
        "",
        "| PATH | 大类 | 接口名称 | 描述 |",
        "| --- | --- | --- | --- |",
    ]
    for path in sorted(apis):
        row = apis[path]
        memo = str(row.get("API_MEMO", "")).replace("\n", " ")
        if len(memo) > 80:
            memo = memo[:80] + "…"
        lines.append(
            "| {path} | {cat} | {name} | {memo} |".format(
                path=path,
                cat=row.get("CATEGORY_NAME", ""),
                name=row.get("API_NAME", ""),
                memo=memo,
            )
        )
    return "\n".join(lines)
