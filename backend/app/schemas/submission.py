"""与提交任务相关的请求/响应模型。

为什么使用 Pydantic：
1. 在入口层提前做参数校验，减少无效请求进入业务逻辑。
2. 自动生成 OpenAPI 文档，便于前后端联调。
3. 明确字段类型，降低后续维护风险。
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreateSubmissionRequest(BaseModel):
    """创建评测任务请求体。"""

    problem_id: str = Field(..., description="题目 ID")
    language: Literal["cpp"] = Field("cpp", description="编程语言，Milestone 1 先仅支持 cpp")
    mode: Literal["review", "socratic"] = Field(
        "review",
        description="教学模式：review=代码审查，socratic=苏格拉底式引导",
    )
    source_code: str = Field(..., min_length=1, description="用户提交的源码")


class CreateSubmissionResponse(BaseModel):
    """创建任务响应体。"""

    submission_id: str
    stream_url: str
    created_at: datetime
