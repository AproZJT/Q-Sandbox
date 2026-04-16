"""统一错误响应模型。"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """统一错误体，便于前后端稳定解析。"""

    code: str = Field(..., description="业务错误码")
    message: str = Field(..., description="面向用户的错误描述")
    detail: str | None = Field(default=None, description="可选调试细节")
