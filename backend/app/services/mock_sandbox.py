"""Milestone 1 的沙箱 Mock 服务。

为什么现在先 Mock：
1. 先打通“提交 -> 事件流 -> LLM 流式”主链路，快速验证架构。
2. 降低初期复杂度，把容器安全细节留到 Milestone 2 专项实现。
3. 前端可以提前联调状态面板与日志面板，减少后续并行阻塞。
"""

import asyncio
from collections.abc import AsyncGenerator


async def run_mock_sandbox(source_code: str) -> AsyncGenerator[tuple[str, dict], None]:
    """模拟 C++ 沙箱执行过程，产出状态与输出事件。

    返回：
        (event_type, payload) 的异步事件流。
    """
    # 模拟排队
    yield "sandbox.queued", {"message": "任务已进入评测队列"}
    await asyncio.sleep(0.5)

    # 模拟执行启动
    yield "sandbox.running", {"message": "沙箱启动中"}
    await asyncio.sleep(0.8)

    # 模拟 stdout/stderr
    preview = source_code.strip().splitlines()[0][:40] if source_code.strip() else "<empty>"
    yield "sandbox.stdout", {"chunk": f"[mock] 编译通过，代码首行预览: {preview}"}
    await asyncio.sleep(0.6)

    yield "sandbox.stdout", {"chunk": "[mock] 程序输出: 42"}
    await asyncio.sleep(0.4)

    # 给一个轻微告警，便于前端调试 stderr 展示区域
    yield "sandbox.stderr", {"chunk": "[mock] warning: comparison between signed and unsigned integer"}
    await asyncio.sleep(0.5)

    # 模拟最终结果
    yield "sandbox.result", {
        "exit_code": 0,
        "time_ms": 186,
        "summary": "程序成功运行，输出为 42，存在潜在类型比较告警",
    }
