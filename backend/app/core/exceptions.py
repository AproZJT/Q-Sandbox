"""全局异常处理。

目标：
1. 将 FastAPI 默认错误转为统一 ErrorResponse。
2. 统一返回格式，降低前端分支复杂度。
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.error import ErrorResponse


class AppError(Exception):
    """业务级异常，支持稳定错误码返回。"""

    def __init__(self, *, code: str, message: str, status_code: int = 400, detail: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppError)
    async def app_exception_handler(_: Request, exc: AppError) -> JSONResponse:
        body = ErrorResponse(code=exc.code, message=exc.message, detail=exc.detail)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = f"HTTP_{exc.status_code}"
        message = str(exc.detail) if exc.detail else "请求处理失败"
        body = ErrorResponse(code=code, message=message)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        body = ErrorResponse(code="VALIDATION_ERROR", message="请求参数不合法", detail=str(exc))
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unknown_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        body = ErrorResponse(code="INTERNAL_ERROR", message="服务器内部错误", detail=str(exc))
        return JSONResponse(status_code=500, content=body.model_dump())
