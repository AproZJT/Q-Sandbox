from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(code="UNAUTHORIZED", message="缺少认证令牌", status_code=401)

    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise AppError(code="INVALID_TOKEN", message="认证令牌无效", status_code=401) from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise AppError(code="INVALID_TOKEN", message="令牌类型无效", status_code=401)

    user_id = payload.get("sub")
    if user_id is None:
        raise AppError(code="INVALID_TOKEN", message="令牌内容无效", status_code=401)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise AppError(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

    return user


def require_roles(*roles: str):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in roles:
            raise AppError(code="FORBIDDEN", message="权限不足", status_code=403)
        return user

    return _checker
