"""FastAPI 应用主入口。

为什么单独保留 main.py：
1. 便于 uvicorn 直接启动（uvicorn app.main:app --reload）。
2. 统一集中放置中间件（如 CORS），避免分散导致环境不一致。
3. 后续接入日志、追踪、异常处理时有稳定入口。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.submission import router as submission_router
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging


setup_logging()

app = FastAPI(
    title="Q-Sandbox",
    version="0.1.0",
    description="轻量版编程练习后端",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submission_router, prefix="/api/v1", tags=["submission"])
register_exception_handlers(app)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
