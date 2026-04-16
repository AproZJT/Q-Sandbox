"""结构化日志工具。

说明：
- 统一 JSON 日志格式，便于后续接 ELK/ClickHouse。
- 所有关键日志尽量携带 submission_id 与 stage。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """初始化基础日志配置。"""
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(level=log_level, format="%(message)s")


def log_event(*, level: int = logging.INFO, event: str, **fields: Any) -> None:
    """输出一条结构化 JSON 日志。"""
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logging.log(level, json.dumps(payload, ensure_ascii=False))
