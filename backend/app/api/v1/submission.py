"""Submission 核心路由：创建任务 + SSE 事件流（支持事件缓存与续传）。

本版增强点：
1. 每个 submission 维护内存事件缓存。
2. SSE 支持 last_event_id 续传（跳过已接收事件）。
3. 沙箱与 LLM 流程只执行一次，重连不会重复跑任务。
4. 增加内存回收策略：TTL 清理 + 总量上限清理，避免内存无限增长。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Query, Request
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import log_event
from app.core.metrics import metrics
from app.core.security import rate_limiter
from app.schemas.events import EventEnvelope, EventFactory
from app.schemas.submission import CreateSubmissionRequest, CreateSubmissionResponse
from app.services.llm_service import LLMService
from app.services.sandbox_service import run_sandbox

router = APIRouter()

# 内存态 submission 存储。
# 说明：
# - Milestone 阶段先用内存实现最小可运行方案。
# - 后续可平滑替换到 Redis / DB，接口协议不变。
SUBMISSIONS: dict[str, dict] = {}


llm_service = LLMService()


def _format_sse(envelope: EventEnvelope) -> dict[str, str]:
    """将统一事件模型转换为 SSE 标准字段。"""
    return {
        "id": str(envelope.event_id),
        "event": envelope.type,
        "data": envelope.model_dump_json(),
    }


def _append_event(submission: dict, envelope: EventEnvelope) -> None:
    """把事件安全地追加到 submission 缓存。"""
    submission["events"].append(envelope)
    submission["updated_at"] = datetime.now(timezone.utc)


def _safe_cancel_task(task: asyncio.Task | None) -> None:
    """安全取消后台任务，避免回收时残留运行中的 pipeline。"""
    if task is None:
        return
    if not task.done():
        task.cancel()


def _prune_submissions() -> None:
    """执行内存回收：先 TTL 清理，再按总量上限裁剪。

    回收策略：
    1) TTL：仅清理“已完成且最后更新时间超过阈值”的任务。
    2) 上限：当总量超限时，优先删除最老的已完成任务；
       若仍超限，再删除最老任务（极端保护，避免 OOM）。
    """
    now = datetime.now(timezone.utc)
    expire_before = now - timedelta(minutes=settings.SUBMISSION_TTL_MINUTES)

    # 1) TTL 清理（仅 completed）
    ttl_delete_ids: list[str] = []
    for sid, item in SUBMISSIONS.items():
        updated_at: datetime = item.get("updated_at", item.get("created_at", now))
        if item.get("completed") and updated_at < expire_before:
            ttl_delete_ids.append(sid)

    for sid in ttl_delete_ids:
        task = SUBMISSIONS[sid].get("task")
        _safe_cancel_task(task)
        del SUBMISSIONS[sid]

    # 2) 总量上限保护
    if len(SUBMISSIONS) <= settings.MAX_SUBMISSIONS_IN_MEMORY:
        return

    # 按更新时间排序，越旧越先删
    ordered = sorted(
        SUBMISSIONS.items(),
        key=lambda kv: kv[1].get("updated_at", kv[1].get("created_at", now)),
    )

    # 2.1 优先删除已完成任务
    for sid, item in ordered:
        if len(SUBMISSIONS) <= settings.MAX_SUBMISSIONS_IN_MEMORY:
            break
        if item.get("completed"):
            _safe_cancel_task(item.get("task"))
            del SUBMISSIONS[sid]

    # 2.2 极端保护：若仍超限，删除最老任务（包含未完成）
    if len(SUBMISSIONS) > settings.MAX_SUBMISSIONS_IN_MEMORY:
        ordered = sorted(
            SUBMISSIONS.items(),
            key=lambda kv: kv[1].get("updated_at", kv[1].get("created_at", now)),
        )
        for sid, item in ordered:
            if len(SUBMISSIONS) <= settings.MAX_SUBMISSIONS_IN_MEMORY:
                break
            _safe_cancel_task(item.get("task"))
            del SUBMISSIONS[sid]


async def _run_submission_pipeline(submission_id: str) -> None:
    """后台执行一次完整评测流程，并把事件写入缓存。"""
    submission = SUBMISSIONS.get(submission_id)
    if not submission:
        metrics.inc("pipeline_missing_submission")
        log_event(event="pipeline_missing_submission", submission_id=submission_id)
        return

    factory = EventFactory(submission_id=submission_id)

    try:
        log_event(event="pipeline_started", submission_id=submission_id)
        metrics.inc("pipeline_started")

        accepted = factory.build("submission.accepted", {"message": "任务创建成功"})
        _append_event(submission, accepted)

        await asyncio.sleep(0.1)

        sandbox_summary = ""
        async for event_type, payload in run_sandbox(submission["source_code"]):
            envelope = factory.build(event_type, payload)
            _append_event(submission, envelope)
            if event_type == "sandbox.result":
                sandbox_summary = str(payload.get("summary", "无"))

        llm_start = factory.build("llm.start", {"message": "开始生成 AI 点评"})
        _append_event(submission, llm_start)

        async for delta in llm_service.stream_review(
            mode=submission["mode"],
            problem_id=submission["problem_id"],
            source_code=submission["source_code"],
            sandbox_summary=sandbox_summary,
        ):
            delta_event = factory.build("llm.delta", {"delta": delta})
            _append_event(submission, delta_event)

        llm_end = factory.build("llm.end", {"message": "AI 点评生成结束"})
        _append_event(submission, llm_end)

        done = factory.build("done", {"message": "任务全流程完成"})
        _append_event(submission, done)

        metrics.inc("pipeline_success")
        log_event(event="pipeline_success", submission_id=submission_id)

    except Exception as exc:  # noqa: BLE001 - 统一转业务 error 事件
        error_event = factory.build(
            "error",
            {
                "stage": "pipeline",
                "message": "任务执行失败",
                "detail": str(exc),
            },
        )
        _append_event(submission, error_event)
        metrics.inc("pipeline_error")
        log_event(event="pipeline_error", submission_id=submission_id, detail=str(exc))
    finally:
        submission["completed"] = True
        submission["updated_at"] = datetime.now(timezone.utc)
        log_event(event="pipeline_finished", submission_id=submission_id)


@router.post("/submissions", response_model=CreateSubmissionResponse)
async def create_submission(request: Request, payload: CreateSubmissionRequest) -> CreateSubmissionResponse:
    """创建 submission，先不执行任务，等待首次 SSE 订阅触发。"""
    _prune_submissions()
    rate_limiter.prune_stale()

    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        metrics.inc("submission_rate_limited")
        log_event(event="submission_rate_limited", client_ip=client_ip)
        raise AppError(
            code="RATE_LIMITED",
            message="请求过于频繁，请稍后再试",
            status_code=429,
        )

    allowed_languages = {lang.strip() for lang in settings.ALLOWED_LANGUAGES.split(",") if lang.strip()}
    if payload.language not in allowed_languages:
        metrics.inc("submission_unsupported_language")
        log_event(event="submission_unsupported_language", language=payload.language)
        raise AppError(
            code="UNSUPPORTED_LANGUAGE",
            message=f"当前仅支持语言: {', '.join(sorted(allowed_languages))}",
            status_code=400,
        )

    if len(payload.source_code) > settings.MAX_SOURCE_CODE_LENGTH:
        metrics.inc("submission_payload_too_large")
        log_event(event="submission_payload_too_large", size=len(payload.source_code))
        raise AppError(
            code="PAYLOAD_TOO_LARGE",
            message=f"source_code 超长，最大允许 {settings.MAX_SOURCE_CODE_LENGTH} 字符",
            status_code=413,
        )

    submission_id = str(uuid4())
    created_at = datetime.now(timezone.utc)

    SUBMISSIONS[submission_id] = {
        "submission_id": submission_id,
        "problem_id": payload.problem_id,
        "language": payload.language,
        "mode": payload.mode,
        "source_code": payload.source_code,
        "created_at": created_at,
        "updated_at": created_at,
        "events": [],
        "started": False,
        "completed": False,
        "task": None,
    }

    metrics.inc("submission_created")
    log_event(event="submission_created", submission_id=submission_id, mode=payload.mode, language=payload.language)

    return CreateSubmissionResponse(
        submission_id=submission_id,
        stream_url=f"/api/v1/submissions/{submission_id}/events",
        created_at=created_at,
    )


@router.get("/submissions/{submission_id}/events")
async def stream_submission_events(
    submission_id: str,
    last_event_id: int | None = Query(default=None, description="续传起点：仅返回 event_id > 该值的事件"),
) -> EventSourceResponse:
    """统一事件流：支持缓存重放与断线续传。"""
    _prune_submissions()

    submission = SUBMISSIONS.get(submission_id)
    if not submission:
        metrics.inc("submission_not_found")
        log_event(event="submission_not_found", submission_id=submission_id)
        raise AppError(code="SUBMISSION_NOT_FOUND", message="submission_id 不存在或已过期", status_code=404)

    # 首次订阅时启动后台任务。
    if not submission["started"]:
        submission["started"] = True
        submission["updated_at"] = datetime.now(timezone.utc)
        submission["task"] = asyncio.create_task(_run_submission_pipeline(submission_id))
        metrics.inc("submission_stream_started")
        log_event(event="submission_stream_started", submission_id=submission_id)

    async def event_generator() -> AsyncGenerator[dict, None]:
        # 计算续传起点：跳过 <= last_event_id 的缓存事件。
        next_index = 0
        if last_event_id is not None:
            for i, item in enumerate(submission["events"]):
                if item.event_id > last_event_id:
                    next_index = i
                    break
            else:
                next_index = len(submission["events"])

        while True:
            events: list[EventEnvelope] = submission["events"]

            # 先把当前可见的缓存事件全部推给前端。
            while next_index < len(events):
                yield _format_sse(events[next_index])
                next_index += 1
                submission["updated_at"] = datetime.now(timezone.utc)

            # 若流程已结束且没有新事件，结束 SSE。
            if submission["completed"] and next_index >= len(events):
                break

            # 等待后台任务继续产生日志事件。
            await asyncio.sleep(0.08)

    return EventSourceResponse(event_generator())
