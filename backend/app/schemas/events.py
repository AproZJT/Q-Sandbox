"""SSE 事件统一数据模型。

为什么定义统一 envelope：
1. 前端只需实现一套解析逻辑，按 type 分发渲染即可。
2. 便于后续做断线重连（结合 Last-Event-ID）。
3. 事件可直接落日志，支持按 submission_id 追踪全链路。
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    """统一事件结构。"""

    submission_id: str = Field(..., description="任务唯一 ID")
    event_id: int = Field(..., description="事件序号，单个 submission 内递增")
    ts: str = Field(..., description="事件生成时间（ISO8601）")
    type: str = Field(..., description="事件类型，例如 llm.delta")
    payload: dict[str, Any] = Field(default_factory=dict, description="事件载荷")


class EventFactory:
    """用于生成递增事件，避免在业务代码里重复拼装字段。"""

    def __init__(self, submission_id: str) -> None:
        self.submission_id = submission_id
        self._counter = 0

    def build(self, event_type: str, payload: dict[str, Any] | None = None) -> EventEnvelope:
        self._counter += 1
        return EventEnvelope(
            submission_id=self.submission_id,
            event_id=self._counter,
            ts=datetime.now(timezone.utc).isoformat(),
            type=event_type,
            payload=payload or {},
        )
