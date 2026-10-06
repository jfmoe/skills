#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容入口：直接调用业务接口。推荐改用 etf_index.py call。"""

from __future__ import annotations

import json
import sys
from typing import Any

from hj_client import api_data


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "用法: python api_client.py <PATH> [JSON_BODY]\n"
            "推荐: python etf_index.py call <PATH> [JSON_BODY]",
            file=sys.stderr,
        )
        return 2
    api_code = argv[1]
    put_data: dict[str, Any] = {}
    if len(argv) >= 3:
        put_data = json.loads(argv[2])
    result = api_data(api_code, put_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
