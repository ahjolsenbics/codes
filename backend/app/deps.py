"""请求上下文：解析演示 Token，绑定数据库用户。"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import User


def parse_user(authorization: str | None, db: Session) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.removeprefix("Bearer ").strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "demo":
        raise HTTPException(status_code=401, detail="无效令牌")
    user = db.get(User, parts[2])
    if user is None or user.disabled:
        raise HTTPException(status_code=401, detail="用户不可用")
    if user.role != parts[1]:
        raise HTTPException(status_code=401, detail="角色不匹配")
    return user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    return parse_user(authorization, db)


def get_optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return parse_user(authorization, db)
    except HTTPException:
        return None


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def require_ops(*roles: str):
    def _inner(user: User = Depends(require_admin)) -> User:
        if not roles:
            return user
        current = user.ops_role or "super"
        if current == "super" or current in roles:
            return user
        raise HTTPException(status_code=403, detail="权限不足")

    return _inner
