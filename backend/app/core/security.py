"""Step 2 安全防护：请求限流 + JWT + 密码哈希。"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


@dataclass
class RequestWindow:
    """单个客户端在时间窗口内的请求记录。"""

    timestamps: deque[float] = field(default_factory=deque)


class InMemoryRateLimiter:
    """轻量内存限流器（按客户端 IP）。

    说明：
    - 适合 Milestone 阶段单实例运行。
    - 后续多实例部署建议迁移到 Redis 令牌桶。
    """

    def __init__(self) -> None:
        self._buckets: dict[str, RequestWindow] = {}

    def allow(self, client_key: str) -> bool:
        now = time.time()
        window_sec = settings.RATE_LIMIT_WINDOW_SECONDS
        max_requests = settings.RATE_LIMIT_MAX_REQUESTS

        bucket = self._buckets.setdefault(client_key, RequestWindow())

        # 清理窗口外请求记录
        while bucket.timestamps and bucket.timestamps[0] <= now - window_sec:
            bucket.timestamps.popleft()

        if len(bucket.timestamps) >= max_requests:
            return False

        bucket.timestamps.append(now)
        return True

    def prune_stale(self) -> None:
        """清理长期不活跃客户端，避免字典无限增长。"""
        now = time.time()
        idle_sec = settings.RATE_LIMIT_WINDOW_SECONDS * 3
        stale_keys = []

        for key, bucket in self._buckets.items():
            if not bucket.timestamps:
                stale_keys.append(key)
                continue
            if bucket.timestamps[-1] <= now - idle_sec:
                stale_keys.append(key)

        for key in stale_keys:
            self._buckets.pop(key, None)


rate_limiter = InMemoryRateLimiter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "role": role,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
