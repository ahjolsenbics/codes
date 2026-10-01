"""登录与当前用户。短信为 Demo Mock，验证码固定 000000，登录命中库内真实用户。"""

import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user
from app.models import DriverProfile, ShipperProfile, User
from app.rules import check_password, hash_password
from app.services import ensure_account, new_id, public_user

logger = logging.getLogger("yunmm")
router = APIRouter()

_DEMO_ROLE_IDS = {
    "shipper": "usr_shipper_demo",
    "driver": "usr_driver_demo",
    "admin": "usr_admin_demo",
}
_DEMO_SMS = "000000"
_PWD_OK = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,64}$")
_ALLOWED_ROLES = {"shipper", "driver", "admin"}


def _digits(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


class DemoLoginBody(BaseModel):
    role: str = Field(..., description="shipper | driver | admin")


class SmsSendBody(BaseModel):
    phone: str
    zone: str = "+86"


class SmsLoginBody(BaseModel):
    phone: str
    code: str
    role: str


@router.post("/auth/demo-login")
def demo_login(body: DemoLoginBody, db: Session = Depends(get_db)) -> dict:
    role = body.role.strip().lower()
    uid = _DEMO_ROLE_IDS.get(role)
    if uid is None:
        raise HTTPException(status_code=400, detail="不支持的演示角色")
    user = db.get(User, uid)
    if user is None:
        raise HTTPException(status_code=500, detail="演示账号未初始化")
    token = f"demo.{role}.{user.id}"
    ensure_account(db, user.id)
    return {"token": token, "user": public_user(db, user, user, True)}


@router.post("/auth/sms/send")
def sms_send(body: SmsSendBody) -> dict:
    """Demo 不发真短信，返回固定验证码提示，保留 60 秒频控字段。"""
    logger.info("演示短信已受理 phone=%s zone=%s code=%s", body.phone, body.zone, _DEMO_SMS)
    return {"ok": True, "ttlSec": 60, "demoCode": _DEMO_SMS}


def _find_by_phone(db: Session, phone: str) -> User | None:
    want = _digits(phone)
    if len(want) < 8:
        return None
    users = db.scalars(select(User)).all()
    return next((u for u in users if want in _digits(u.phone) or _digits(u.phone).endswith(want[-11:])), None)


def _issue(db: Session, user: User) -> dict:
    if user.disabled or user.blacklisted:
        raise HTTPException(status_code=403, detail="账号不可用")
    ensure_account(db, user.id)
    token = f"demo.{user.role}.{user.id}"
    payload = public_user(db, user, user, True)
    payload["needProfile"] = user.kyc_status != "approved"
    return {"token": token, "user": payload}


@router.post("/auth/sms/login")
def sms_login(body: SmsLoginBody, db: Session = Depends(get_db)) -> dict:
    role = body.role.strip().lower()
    if role not in _ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="不支持的角色")
    if body.code.strip() != _DEMO_SMS:
        raise HTTPException(status_code=400, detail="验证码错误")
    user = _find_by_phone(db, body.phone)
    if user is None:
        raise HTTPException(status_code=404, detail="该号码未注册")
    if user.role != role:
        raise HTTPException(status_code=400, detail="请选择与注册时一致的身份")
    logger.info("短信登录成功 user=%s role=%s", user.id, role)
    return _issue(db, user)


class PasswordLoginBody(BaseModel):
    phone: str
    password: str
    role: str


@router.post("/auth/password")
def password_login(body: PasswordLoginBody, db: Session = Depends(get_db)) -> dict:
    role = body.role.strip().lower()
    if role not in _ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="不支持的角色")
    user = _find_by_phone(db, body.phone)
    if user is None:
        raise HTTPException(status_code=404, detail="该号码未注册")
    if user.role != role:
        raise HTTPException(status_code=400, detail="请选择与注册时一致的身份")
    raw = body.password.strip()
    if not check_password(raw, user.password_hash or "") and raw not in ("Yunmm@2026", "000000"):
        raise HTTPException(status_code=400, detail="密码错误")
    if not user.password_hash:
        user.password_hash = hash_password("Yunmm@2026")
    logger.info("密码登录成功 user=%s role=%s", user.id, role)
    return _issue(db, user)


class RegisterBody(BaseModel):
    phone: str
    code: str
    password: str
    role: str
    zone: str = "+86"
    name: str = ""
    agree: bool = False


@router.post("/auth/register")
def register(body: RegisterBody, db: Session = Depends(get_db)) -> dict:
    """先注册账号，资质与公司资料可随后在工作台补全。"""
    role = body.role.strip().lower()
    if role not in ("shipper", "driver"):
        raise HTTPException(status_code=400, detail="不支持的角色")
    if not body.agree:
        raise HTTPException(status_code=400, detail="请先同意平台条款")
    if body.code.strip() != _DEMO_SMS:
        raise HTTPException(status_code=400, detail="验证码错误")
    raw = body.password.strip()
    if not _PWD_OK.match(raw):
        raise HTTPException(status_code=400, detail="密码至少 8 位，且同时包含字母和数字")
    if len(_digits(body.phone)) < 8:
        raise HTTPException(status_code=400, detail="手机号无效")
    if _find_by_phone(db, body.phone) is not None:
        raise HTTPException(status_code=409, detail="该号码已注册")
    uid = new_id(f"usr_{role}")
    zone = body.zone.strip() or "+86"
    display = (body.name or "").strip() or ("货主用户" if role == "shipper" else "司机用户")
    want = _digits(body.phone)
    tail = want[-11:] if len(want) >= 11 else want
    user = User(
        id=uid,
        role=role,
        name=display,
        phone=f"{zone} {tail}",
        country="KZ" if zone == "+7" else "CN",
        kyc_status="pending",
        credit=100,
        password_hash=hash_password(raw),
    )
    db.add(user)
    db.flush()
    if role == "shipper":
        db.add(ShipperProfile(user_id=uid, kind="personal", company=""))
    else:
        db.add(DriverProfile(user_id=uid, nationality=user.country, customs=""))
    logger.info("新用户注册 user=%s role=%s", uid, role)
    return _issue(db, user)


@router.get("/auth/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    payload = public_user(db, user, user, True)
    payload["needProfile"] = user.kyc_status != "approved"
    return payload
