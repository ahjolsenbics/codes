"""健康检查与公开配置（不含密钥）。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models import Load, Port, User
from app.services import serialize_load_public

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.env,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/meta/config")
def public_config() -> dict:
    """前端展示用的规则默认值，真正时长压缩只影响 Demo 运行。"""
    return {
        "bidCloseHours": settings.bid_close_hours,
        "shipperPickHours": settings.shipper_pick_hours,
        "grabConfirmSeconds": settings.grab_confirm_seconds,
        "assignInviteHours": settings.assign_invite_hours,
        "assignMaxDrivers": settings.assign_max_drivers,
        "depositCny": settings.deposit_cny,
        "lateHours": settings.late_hours,
        "portStatusTtlHours": settings.port_status_ttl_hours,
        "driverActiveOrderLimit": settings.driver_active_order_limit,
        "phoneUnlockCredit": settings.phone_unlock_credit,
        "creditInitial": settings.credit_initial,
        "supportedLocales": ["zh-CN", "ru-RU", "en-US"],
        "reservedLocales": ["kk-KZ"],
    }


@router.get("/public/market")
def public_market(db: Session = Depends(get_db)) -> dict:
    """展示页用货盘。数字按运营中平台量级演示，列表来自 Demo 库。"""
    loads = db.scalars(select(Load).order_by(Load.created_at.desc()).limit(16)).all()
    ports = db.scalars(select(Port)).all()
    users = db.scalar(select(func.count(User.id))) or 0
    return {
        "tagline": "China — Kazakhstan — Russia road freight exchange",
        "index": 1864,
        "loadsLive": 12847,
        "trucksLive": 3216,
        "participantsLive": 8904,
        "tendersLive": 24,
        "loadsToday": 186,
        "trucksToday": 42,
        "demoUsers": users,
        "items": [serialize_load_public(x) for x in loads],
        "ports": [
            {
                "id": p.id,
                "nameZh": p.name_zh,
                "nameEn": p.name_en,
                "nameRu": p.name_ru,
                "status": p.status,
                "waitMin": p.wait_min,
                "country": p.country,
                "corridor": p.corridor,
            }
            for p in ports
        ],
        "corridors": [
            {
                "from": "乌鲁木齐",
                "to": "阿拉木图",
                "km": 860,
                "rateLow": 16,
                "rateHigh": 22,
                "rateKind": "km",
                "waitPort": "khorgos",
                "waitHours": 3,
                "waitMin": 180,
            },
            {
                "from": "霍尔果斯",
                "to": "阿拉木图",
                "km": 350,
                "rateLow": 14,
                "rateHigh": 18,
                "rateKind": "km",
                "waitStatus": "smooth",
            },
            {
                "from": "喀什",
                "to": "奥什",
                "km": 420,
                "rateLow": 17,
                "rateHigh": 21,
                "rateKind": "km",
                "waitStatus": "slow",
            },
            {
                "from": "阿拉山口",
                "to": "多斯特克",
                "km": 12,
                "rateKind": "shuttle",
                "waitPort": "alashankou",
                "waitHours": 1.5,
                "waitMin": 90,
            },
        ],
    }
