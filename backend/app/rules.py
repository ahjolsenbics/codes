"""演示规则：抢单确认窗、流单、口岸过期、绿卡冻结、测算缓存、通知。"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    AssignInvite,
    Blacklist,
    CreditRecord,
    DepositLedger,
    DriverProfile,
    EstimateCache,
    EstimateLog,
    GrabHold,
    Load,
    Notification,
    Order,
    Port,
    Quote,
    Review,
    User,
    utcnow,
)

logger = logging.getLogger("yunmm")
_last_tick = 0.0

CITY_COORDS: dict[str, tuple[float, float]] = {
    "乌鲁木齐": (43.8256, 87.6168),
    "昌吉": (44.0144, 87.3082),
    "石河子": (44.3054, 86.0804),
    "奎屯": (44.4265, 84.9032),
    "伊宁": (43.9167, 81.3167),
    "霍尔果斯": (44.2143, 80.4189),
    "喀什": (39.4704, 75.9898),
    "阿拉山口": (45.1700, 82.5700),
    "阿拉木图": (43.2380, 76.8512),
    "阿斯塔纳": (51.1694, 71.4491),
    "塔什干": (41.2995, 69.2401),
    "奥什": (40.5283, 72.7985),
    "比什凯克": (42.8746, 74.5698),
    "奇姆肯特": (42.3419, 69.5901),
    "莫斯科": (55.7558, 37.6173),
    "新西伯利亚": (55.0084, 82.9357),
}

# 乌鲁木齐 G30 → 霍尔果斯 → AH5 阿拉木图，节点按公路走廊铺开
TRACK_ROUTE = [
    (43.8256, 87.6168),
    (44.0130, 87.3120),
    (44.1570, 86.8900),
    (44.3054, 86.0804),
    (44.4265, 84.9032),
    (44.4300, 84.6800),
    (44.6000, 82.8900),
    (44.8500, 82.0500),
    (44.2000, 80.8500),
    (44.2143, 80.4189),
    (44.2700, 80.0000),
    (44.1600, 79.4700),
    (44.0500, 79.2000),
    (43.8800, 78.4000),
    (43.7200, 78.0000),
    (43.8800, 77.0600),
    (43.5000, 76.9500),
    (43.2380, 76.8512),
]

ROUTE_STOPS = [
    "乌鲁木齐经济技术开发区",
    "昌吉西枢纽",
    "呼图壁服务区",
    "石河子货运场",
    "奎屯互通",
    "乌苏收费站",
    "精河服务区",
    "博乐过境",
    "霍城集结区",
    "霍尔果斯口岸 Horogos",
    "热肯特 Zharkent",
    "琼扎",
    "萨雷奥泽克",
    "库恩格伊山口",
    "卡普恰盖 Kapchagay",
    "阿拉木图北环",
    "阿拉木图物流园",
    "阿拉木图交货点",
]

PHRASE_ZH_RU = {
    "您好": "Здравствуйте",
    "你好": "Здравствуйте",
    "已装货": "Погрузка завершена",
    "已出发": "Выехали",
    "到达口岸": "Прибыли на КПП",
    "已送达": "Доставлено",
    "请确认收货": "Подтвердите получение",
    "在路上": "В пути",
    "堵车": "Пробка",
    "排队": "Очередь",
    "霍尔果斯": "Хоргос",
    "阿拉木图": "Алматы",
    "运费": "Фрахт",
    "保证金": "Депозит",
    "运单": "Накладная",
    "卸货": "Разгрузка",
    "装货": "Погрузка",
    "明天": "завтра",
    "今天": "сегодня",
    "小时": "часов",
    "分钟": "минут",
    "谢谢": "Спасибо",
    "好的": "Хорошо",
    "收到": "Принято",
    "位置": "Местоположение",
    "车牌": "Номер авто",
    "吨": "тонн",
}

PHRASE_RU_ZH = {v: k for k, v in PHRASE_ZH_RU.items()}


def hash_password(raw: str) -> str:
    return hashlib.sha256(f"yunmm|{raw}".encode()).hexdigest()


def check_password(raw: str, stored: str) -> bool:
    if not stored:
        return False
    return hash_password(raw) == stored


def city_ll(name: str) -> tuple[float, float]:
    return CITY_COORDS.get(name or "", (43.8256, 87.6168))


def notify(db: Session, user_id: str, kind: str, title: str, body: str = "") -> None:
    from app.services import new_id

    user = db.get(User, user_id)
    if user is not None and not user.notify_push:
        return
    db.add(Notification(id=new_id("nt"), user_id=user_id, kind=kind, title=title, body=body))


def green_card_ok(db: Session, driver: User) -> tuple[bool, str]:
    profile = db.get(DriverProfile, driver.id)
    if profile is None:
        return True, ""
    exp = (profile.green_card_expires or "").strip()
    if not exp:
        return True, ""
    try:
        day = datetime.strptime(exp[:10], "%Y-%m-%d").date()
    except ValueError:
        return True, ""
    left = (day - utcnow().date()).days
    if left < 0:
        driver.frozen_reason = "green_card_expired"
        return False, "绿卡已过期，接单已冻结"
    return True, ""


def green_card_light(expires: str) -> str:
    if not expires:
        return "none"
    try:
        day = datetime.strptime(expires[:10], "%Y-%m-%d").date()
    except ValueError:
        return "none"
    left = (day - utcnow().date()).days
    if left < 0:
        return "expired"
    if left <= 1:
        return "d1"
    if left <= 7:
        return "d7"
    if left <= 30:
        return "d30"
    return "ok"


def naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def tick_rules(db: Session) -> dict:
    """请求间隙跑规则，避免另起调度进程。"""
    global _last_tick
    now_ts = time.time()
    if now_ts - _last_tick < 8:
        return {"skipped": True}
    _last_tick = now_ts
    from app.services import add_credit, cfg_int, deal_load

    now = utcnow()
    now_naive = now.replace(tzinfo=None) if now.tzinfo else now
    done: dict[str, int] = {"holds": 0, "expired": 0, "invites": 0, "reviews": 0, "ports": 0, "black": 0}

    hold_sec = cfg_int(db, "grab_confirm_seconds", settings.grab_confirm_seconds)
    if hold_sec < 60:
        hold_sec = 1800
    pick_h = cfg_int(db, "shipper_pick_hours", settings.shipper_pick_hours)
    ttl_h = cfg_int(db, "port_status_ttl_hours", settings.port_status_ttl_hours)

    holds = db.scalars(select(GrabHold).where(GrabHold.status == "pending")).all()
    for hold in holds:
        exp = naive(hold.expires_at)
        if exp and exp > now_naive:
            continue
        load = db.get(Load, hold.load_id)
        driver = db.get(User, hold.driver_id)
        if load is None or driver is None or load.status not in ("published", "matching"):
            hold.status = "expired"
            continue
        shipper = db.get(User, load.shipper_id)
        if shipper is None:
            hold.status = "expired"
            continue
        try:
            order = deal_load(db, load, driver, shipper, hold.freight, driver, "grab")
            order.grab_hold_id = hold.id
            hold.status = "auto"
            notify(db, shipper.id, "order", "抢单超时自动成交", f"{load.origin} → {load.dest}")
            notify(db, driver.id, "order", "货主超时未确认，订单已自动成交", load.id)
            done["holds"] += 1
        except ValueError:
            hold.status = "expired"

    for load in db.scalars(select(Load).where(Load.status.in_(["published", "matching"]), Load.match_mode == "bid")).all():
        deadline = naive(load.bid_deadline)
        if deadline is None:
            continue
        if now_naive < deadline + timedelta(hours=pick_h):
            continue
        load.status = "expired"
        for q in load.quotes:
            if q.status == "active":
                q.status = "expired"
        notify(db, load.shipper_id, "load", "竞价已流单", f"{load.origin} → {load.dest} 超时未选司机")
        done["expired"] += 1

    for inv in db.scalars(select(AssignInvite).where(AssignInvite.status == "pending")).all():
        exp = naive(inv.expires_at)
        if exp and exp < now_naive:
            inv.status = "expired"
            done["invites"] += 1

    week_ago = now_naive - timedelta(days=7)
    completed = db.scalars(select(Order).where(Order.status == "completed")).all()
    for order in completed:
        created = naive(order.created_at)
        if created and created > week_ago:
            continue
        for uid, peer in ((order.shipper_id, order.driver_id), (order.driver_id, order.shipper_id)):
            existed = db.scalar(select(Review).where(Review.order_id == order.id, Review.from_user == uid))
            if existed:
                continue
            db.add(
                Review(
                    order_id=order.id,
                    from_user=uid,
                    to_user=peer,
                    stars=5,
                    tags="on_time,auto",
                    comment="超时默认好评",
                )
            )
            done["reviews"] += 1

    stale_before = now_naive - timedelta(hours=ttl_h)
    for port in db.scalars(select(Port)).all():
        updated = naive(port.updated_at)
        if updated and updated < stale_before and port.status != "stale":
            port.status = "stale"
            done["ports"] += 1

    for driver in db.scalars(select(User).where(User.role == "driver")).all():
        ok, reason = green_card_ok(db, driver)
        if not ok:
            driver.frozen_reason = reason

    strikes = db.execute(
        select(CreditRecord.user_id, func.count(CreditRecord.id))
        .where(CreditRecord.reason.in_(["dispute_lose", "breach", "sensitive"]))
        .group_by(CreditRecord.user_id)
    ).all()
    for uid, n in strikes:
        if n < 3:
            continue
        user = db.get(User, uid)
        if user is None or user.blacklisted:
            continue
        user.blacklisted = True
        if db.scalar(select(Blacklist).where(Blacklist.user_id == uid)) is None:
            db.add(Blacklist(user_id=uid, reason="违约满 3 次自动拉黑"))
        notify(db, uid, "risk", "账号已进入黑名单", "累计违约达到 3 次")
        done["black"] += 1

    logger.info("规则扫描 %s", done)
    return done


def translate_text(text: str, source_locale: str) -> str:
    raw = text or ""
    table = PHRASE_ZH_RU if source_locale.startswith("zh") else PHRASE_RU_ZH
    out = raw
    for src, dst in table.items():
        if src in out:
            out = out.replace(src, dst)
    if out != raw:
        return out
    if source_locale.startswith("zh"):
        return f"【俄文对照】{raw}"
    if source_locale.startswith("ru"):
        return f"【中文对照】{raw}"
    return raw


def estimate_cached(db: Session, origin: str, dest: str, truck: str, cargo: str, weight: float = 18) -> dict:
    from app.services import cfg, estimate_quote, new_id

    days = int(cfg(db, "estimate_cache_days", "7") or "7")
    key = f"{origin}|{dest}|{truck}|{cargo}|{weight}"
    row = db.get(EstimateCache, key)
    now = utcnow().replace(tzinfo=None)
    if row:
        created = naive(row.created_at)
        if created and created > now - timedelta(days=days):
            try:
                data = json.loads(row.result_json)
                data["cached"] = True
                return data
            except json.JSONDecodeError:
                pass
    data = estimate_quote(origin, dest, truck, cargo, db, weight)
    data["cached"] = False
    payload = json.dumps(data, ensure_ascii=False)
    if row is None:
        db.add(
            EstimateCache(
                id=key,
                origin=origin,
                dest=dest,
                truck=truck,
                cargo=cargo,
                result_json=payload,
            )
        )
    else:
        row.result_json = payload
        row.created_at = utcnow()
    return data


def anon_estimate_count(db: Session, anon_key: str) -> int:
    since = utcnow().replace(tzinfo=None) - timedelta(days=1)
    return (
        db.scalar(
            select(func.count(EstimateLog.id)).where(
                EstimateLog.anon_key == anon_key,
                EstimateLog.created_at >= since,
            )
        )
        or 0
    )


def gps_point(index: int) -> tuple[float, float, str]:
    i = max(0, min(index, len(TRACK_ROUTE) - 1))
    lat, lng = TRACK_ROUTE[i]
    lat += random.uniform(-0.004, 0.004)
    lng += random.uniform(-0.006, 0.006)
    stop = ROUTE_STOPS[i] if i < len(ROUTE_STOPS) else "在途"
    return round(lat, 5), round(lng, 5), stop


def start_pay(db: Session, user: User, amount: int, channel: str) -> DepositLedger:
    row = DepositLedger(
        user_id=user.id,
        kind="pay",
        amount=amount,
        channel=channel,
        status="pending",
        note="等待支付确认",
    )
    db.add(row)
    db.flush()
    return row


def confirm_pay(db: Session, user: User, ledger_id: int) -> dict:
    from app.services import ensure_account

    row = db.get(DepositLedger, ledger_id)
    if row is None or row.user_id != user.id:
        raise ValueError("支付单不存在")
    if row.status == "ok":
        acc = ensure_account(db, user.id)
        return {"available": acc.available, "frozen": acc.frozen, "status": "ok"}
    if row.status != "pending":
        raise ValueError("支付单不可确认")
    acc = ensure_account(db, user.id)
    acc.available += row.amount
    row.status = "ok"
    row.note = "已到账"
    notify(db, user.id, "pay", "保证金已到账", f"{row.channel} +{row.amount}")
    return {"available": acc.available, "frozen": acc.frozen, "status": "ok"}


def refund_pay(db: Session, ledger_id: int, admin: User) -> dict:
    from app.services import ensure_account

    row = db.get(DepositLedger, ledger_id)
    if row is None:
        raise ValueError("流水不存在")
    if row.status == "refunded":
        return {"ok": True}
    acc = ensure_account(db, row.user_id)
    if row.status == "ok":
        take = min(acc.available, row.amount)
        acc.available -= take
    row.status = "refunded"
    row.note = f"原路退款 by {admin.name}"
    notify(db, row.user_id, "pay", "保证金已退款", f"{row.channel} {row.amount}")
    return {"ok": True, "status": "refunded"}
