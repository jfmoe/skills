#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UDSP Skill 网关 HTTP 客户端（共享模块）。"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

DEFAULT_BASE = "https://app.fsfund.com/apps/cerdo/udsp-api/udsp/skill/v01/"
META_API = "get_udsp_2_api_out_in_param"
DEFAULT_SKILL_URL = "fsfund-etf-index"


def base_url() -> str:
    return os.environ.get("HJ_BASE_URL", DEFAULT_BASE).rstrip("/") + "/"


def skill_url() -> str:
    return os.environ.get("HJ_SKILL_URL", DEFAULT_SKILL_URL).strip()


def app_secret() -> str:
    secret = os.environ.get("HJ_APP_SECRET", "").strip()
    if not secret:
        raise SystemExit("缺少环境变量 HJ_APP_SECRET，请先配置后再调用。")
    return secret


def build_url(api_code: str) -> str:
    return base_url() + api_code


def post_json(api_code: str, body: dict[str, Any] | None = None) -> Any:
    url = build_url(api_code)
    payload = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    headers = {
        "hjAppSecret": app_secret(), 
        "Content-Type": "application/json;charset=UTF-8",
    }
    req = request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=120) as resp:
            resp.encoding = "utf-8"
            text = resp.read().decode("utf-8")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code}: {detail}") from e
    except error.URLError as e:
        raise SystemExit(f"请求失败: {e}") from e

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def api_data(api_code: str, put_data: dict[str, Any] | None = None) -> Any:
    return post_json(api_code, put_data)


def fetch_skill_meta() -> dict[str, Any]:
    """拉取本 Skill 绑定的接口列表与出入参。"""
    response = post_json(META_API, {"skill_url": skill_url()})
    code = str(response.get("code", ""))
    if code not in {"0000", "00000"}:
        raise SystemExit(f"元数据拉取失败: {response.get('message', response)}")
    data = response.get("data") or {}
    result = data.get("result")
    if not isinstance(result, dict):
        raise SystemExit("元数据响应缺少 data.result 对象")
    return result
