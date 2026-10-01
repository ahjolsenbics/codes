"""核心业务：状态机、撮合、保证金、信用、测算、翻译、防跳单。"""

from __future__ import annotations

import logging
import re
import threading
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    AssignInvite,
    Conversation,
    CreditRecord,
    DepositAccount,
    DepositLedger,
    GrabHold,
    Load,
    Message,
    Order,
    Quote,
    StatusLog,
    SysConfig,
    TrackingPoint,
    User,
    Waybill,
    utcnow,
)
from app.rules import TRACK_ROUTE, city_ll, gps_point, green_card_ok, notify

logger = logging.getLogger("yunmm")
_grab_lock = threading.Lock()

ORDER_FLOW = [
    "dealt",
    "wait_load",
    "loading",
    "in_transit",
    "wait_confirm",
    "completed",
]

DRIVER_ACTIONS = {
    "start_load": ("wait_load", "loading"),
    "start_transit": ("loading", "in_transit"),
    "arrive": ("in_transit", "wait_confirm"),
}
SHIPPER_ACTIONS = {
    "confirm_receive": ("wait_confirm", "completed"),
}

PHRASE_ZH_RU = {
    "您好": "Здравствуйте",
    "已装货": "Погрузка завершена",
    "已出发": "Выехали",
    "到达口岸": "Прибыли на КПП",
    "已送达": "Доставлено",
    "请确认收货": "Подтвердите получение",
}


def cfg(db: Session, key: str, default: str) -> str:
    row = db.get(SysConfig, key)
    return row.value if row else default


def cfg_int(db: Session, key: str, default: int) -> int:
    return int(cfg(db, key, str(default)))


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def public_user(db: Session, user: User, viewer: User | None, dealt: bool) -> dict:
    """成交前隐藏号码；成交后脱敏；信用达门槛解锁完整号码。"""
    unlock = cfg_int(db, "phone_unlock_credit", settings.phone_unlock_credit)
    phone = user.phone
    if viewer is not None and viewer.id == user.id:
        phone = user.phone
    elif not dealt:
        phone = ""
    elif viewer is None or viewer.credit < unlock:
        phone = _mask(phone)
    return {
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "phone": phone,
        "country": user.country,
        "locale": user.locale,
        "kycStatus": user.kyc_status,
        "credit": user.credit,
        "blacklisted": user.blacklisted,
        "depositExempt": user.deposit_exempt,
        "frozenReason": user.frozen_reason,
        "notifyPush": user.notify_push,
        "notifySms": user.notify_sms,
        "quietHours": user.quiet_hours,
        "opsRole": user.ops_role,
    }


def _mask(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return "****"
    return f"{digits[:3]}****{digits[-4:]}"


# Demo 货盘封面：本地 SVG，避免外网图挂掉后页面空白。
_COVERS = (
    ("机械", "/covers/machine.svg"),
    ("电子", "/covers/electronics.svg"),
    ("建材", "/covers/building.svg"),
    ("食品", "/covers/food.svg"),
    ("汽", "/covers/auto.svg"),
    ("纺", "/covers/textile.svg"),
    ("化", "/covers/chemical.svg"),
    ("果", "/covers/food.svg"),
    ("钢", "/covers/building.svg"),
)


def _cover(name: str) -> str:
    text = name or ""
    for key, url in _COVERS:
        if key in text:
            return url
    return "/covers/general.svg"


def serialize_load(load: Load, quote_count: int = 0, lowest_quote: int | None = None) -> dict:
    return {
        "id": load.id,
        "shipperId": load.shipper_id,
        "origin": load.origin,
        "originCountry": load.origin_country,
        "dest": load.dest,
        "destCountry": load.dest_country,
        "loadTime": load.load_time,
        "cargoName": load.cargo_name,
        "weightT": load.weight_t,
        "volumeM3": load.volume_m3,
        "packing": load.packing,
        "cargoClass": load.cargo_class,
        "truckLength": load.truck_length,
        "truckTonnage": load.truck_tonnage,
        "receiverName": load.receiver_name,
        "receiverPhone": load.receiver_phone,
        "remark": load.remark,
        "matchMode": load.match_mode,
        "expectPrice": load.expect_price,
        "floorPrice": load.floor_price,
        "grabPrice": load.grab_price,
        "bidDeadline": load.bid_deadline.isoformat() if load.bid_deadline else None,
        "status": load.status,
        "quoteCount": quote_count,
        "lowestQuote": lowest_quote,
        "cover": _cover(load.cargo_name),
        "photos": _photos(load),
        "originLat": load.origin_lat,
        "originLng": load.origin_lng,
        "destLat": load.dest_lat,
        "destLng": load.dest_lng,
        "draft": bool(load.is_draft),
        "createdAt": load.created_at.isoformat() if load.created_at else None,
    }


def serialize_load_public(load: Load, quote_count: int = 0, lowest_quote: int | None = None) -> dict:
    """未登录市场只给线路与货类，不含电话、公司、底价、收货人。"""
    data = serialize_load(load, quote_count, lowest_quote)
    for key in ("receiverPhone", "receiverName", "remark", "shipperId", "floorPrice"):
        data.pop(key, None)
    data["expectPrice"] = None
    data["grabPrice"] = None
    data["lowestQuote"] = None
    data["quoteCount"] = 0
    data["company"] = ""
    return data


def _photos(load: Load) -> list[str]:
    raw = getattr(load, "photos_json", "") or ""
    if raw.startswith("["):
        try:
            import json

            data = json.loads(raw)
            if isinstance(data, list):
                return [str(x) for x in data][:9]
        except Exception:
            return []
    return []


def ensure_account(db: Session, user_id: str) -> DepositAccount:
    acc = db.get(DepositAccount, user_id)
    if acc is None:
        acc = DepositAccount(user_id=user_id, available=0, frozen=0)
        db.add(acc)
        db.flush()
    return acc


def ledger(
    db: Session,
    user_id: str,
    kind: str,
    amount: int,
    channel: str = "",
    order_id: str = "",
    status: str = "ok",
    note: str = "",
) -> DepositLedger:
    row = DepositLedger(
        user_id=user_id,
        kind=kind,
        amount=amount,
        channel=channel,
        order_id=order_id,
        status=status,
        note=note,
    )
    db.add(row)
    db.flush()
    return row


def topup(db: Session, user: User, amount: int, channel: str) -> DepositAccount:
    acc = ensure_account(db, user.id)
    acc.available += amount
    ledger(db, user.id, "pay", amount, channel)
    logger.info("保证金缴纳 user=%s amount=%s channel=%s", user.id, amount, channel)
    return acc


def freeze_deposit(db: Session, user: User, amount: int, order_id: str) -> None:
    if user.deposit_exempt:
        return
    acc = ensure_account(db, user.id)
    if acc.available < amount:
        raise ValueError("保证金可用余额不足")
    acc.available -= amount
    acc.frozen += amount
    ledger(db, user.id, "freeze", amount, order_id=order_id)
    logger.info("保证金冻结 user=%s order=%s amount=%s", user.id, order_id, amount)


def unfreeze_deposit(db: Session, user: User, amount: int, order_id: str, deduct: bool = False) -> None:
    if user.deposit_exempt:
        return
    acc = ensure_account(db, user.id)
    take = min(acc.frozen, amount)
    acc.frozen -= take
    if deduct:
        ledger(db, user.id, "deduct", take, order_id=order_id)
        logger.info("保证金扣除 user=%s order=%s amount=%s", user.id, order_id, take)
    else:
        acc.available += take
        ledger(db, user.id, "unfreeze", take, order_id=order_id)
        logger.info("保证金解冻 user=%s order=%s amount=%s", user.id, order_id, take)


def add_credit(db: Session, user: User, delta: int, reason: str, order_id: str = "") -> None:
    user.credit = max(0, user.credit + delta)
    db.add(CreditRecord(user_id=user.id, delta=delta, reason=reason, order_id=order_id))
    logger.info("信用变化 user=%s delta=%s reason=%s credit=%s", user.id, delta, reason, user.credit)


def log_status(db: Session, order: Order, previous: str, actor: User) -> None:
    db.add(
        StatusLog(
            order_id=order.id,
            from_status=previous,
            to_status=order.status,
            actor_id=actor.id,
            actor_role=actor.role,
        )
    )
    conv = db.scalar(
        select(Conversation).where(
            Conversation.order_id == order.id,
        )
    )
    if conv:
        db.add(
            Message(
                conversation_id=conv.id,
                sender_id="system",
                kind="system",
                body=f"order.status.{order.status}",
            )
        )


def active_driver_orders(db: Session, driver_id: str) -> int:
    return db.scalar(
        select(func.count(Order.id)).where(
            Order.driver_id == driver_id,
            Order.status.in_(["dealt", "wait_load", "loading", "in_transit", "wait_confirm", "dispute"]),
        )
    ) or 0


def deal_load(
    db: Session,
    load: Load,
    driver: User,
    shipper: User,
    freight: int,
    actor: User,
    mode: str,
) -> Order:
    limit = cfg_int(db, "driver_active_order_limit", settings.driver_active_order_limit)
    if active_driver_orders(db, driver.id) >= limit:
        raise ValueError("司机进行中订单已达上限")
    if driver.blacklisted or shipper.blacklisted:
        raise ValueError("黑名单用户禁止交易")
    ok, reason = green_card_ok(db, driver)
    if not ok:
        raise ValueError(reason)
    deposit = cfg_int(db, "deposit_cny", settings.deposit_cny)
    order = Order(
        id=new_id("ord"),
        load_id=load.id,
        shipper_id=shipper.id,
        driver_id=driver.id,
        match_mode=mode,
        freight=freight,
        deposit=deposit,
        status="wait_load",
    )
    db.add(order)
    db.flush()
    db.add(
        Waybill(
            id=new_id("wb"),
            order_id=order.id,
            load_note="",
        )
    )
    conv = Conversation(
        id=new_id("cv"),
        load_id=load.id,
        order_id=order.id,
        shipper_id=shipper.id,
        driver_id=driver.id,
    )
    db.add(conv)
    db.flush()
    freeze_deposit(db, shipper, deposit, order.id)
    freeze_deposit(db, driver, deposit, order.id)
    load.status = "dealt"
    for q in list(load.quotes):
        if q.driver_id != driver.id:
            q.status = "expired"
        else:
            q.status = "won"
    for inv in list(load.invites):
        if inv.driver_id != driver.id and inv.status == "pending":
            inv.status = "expired"
    log_status(db, order, "dealt", actor)
    db.add(
        Message(
            conversation_id=conv.id,
            sender_id="system",
            kind="system",
            body="order.created",
        )
    )
    notify(db, shipper.id, "order", "订单已成交", f"{load.origin} → {load.dest}")
    notify(db, driver.id, "order", "订单已成交", f"{load.origin} → {load.dest}")
    logger.info(
        "订单成交 order=%s load=%s shipper=%s driver=%s freight=%s",
        order.id,
        load.id,
        shipper.id,
        driver.id,
        freight,
    )
    return order


def choose_quote(db: Session, load: Load, quote: Quote, actor: User) -> Order:
    if load.match_mode != "bid" or load.status not in ("published", "matching"):
        raise ValueError("当前货源不可选司机")
    if quote.status != "active":
        raise ValueError("报价已失效")
    driver = db.get(User, quote.driver_id)
    shipper = db.get(User, load.shipper_id)
    assert driver and shipper
    return deal_load(db, load, driver, shipper, quote.amount, actor, "bid")


def grab_load(db: Session, load: Load, driver: User) -> GrabHold:
    with _grab_lock:
        db.refresh(load)
        if load.match_mode != "grab" or load.status not in ("published", "matching"):
            raise ValueError("当前货源不可抢单")
        existing = db.scalar(select(Order).where(Order.load_id == load.id))
        if existing:
            raise ValueError("货源已被抢走")
        held = db.scalar(select(GrabHold).where(GrabHold.load_id == load.id, GrabHold.status == "pending"))
        if held:
            raise ValueError("已有司机抢单待货主确认")
        ok, reason = green_card_ok(db, driver)
        if not ok:
            raise ValueError(reason)
        if driver.blacklisted:
            raise ValueError("黑名单用户禁止交易")
        seconds = cfg_int(db, "grab_confirm_seconds", settings.grab_confirm_seconds)
        if seconds < 60:
            seconds = 1800
        hold = GrabHold(
            id=new_id("gh"),
            load_id=load.id,
            driver_id=driver.id,
            freight=load.grab_price or load.expect_price or 18000,
            status="pending",
            expires_at=utcnow() + timedelta(seconds=seconds),
        )
        db.add(hold)
        load.status = "matching"
        notify(db, load.shipper_id, "grab", "司机已抢单，请在 30 分钟内确认", load.id)
        notify(db, driver.id, "grab", "抢单成功，等待货主确认", load.id)
        logger.info("抢单进入确认窗 hold=%s load=%s driver=%s", hold.id, load.id, driver.id)
        return hold


def confirm_grab(db: Session, hold: GrabHold, actor: User) -> Order:
    if hold.status != "pending":
        raise ValueError("确认窗已关闭")
    load = db.get(Load, hold.load_id)
    driver = db.get(User, hold.driver_id)
    if load is None or driver is None:
        raise ValueError("抢单已失效")
    shipper = db.get(User, load.shipper_id)
    assert shipper
    if actor.id not in (shipper.id, "usr_admin_demo") and actor.role != "admin":
        raise ValueError("仅货主可确认抢单")
    order = deal_load(db, load, driver, shipper, hold.freight, actor, "grab")
    order.grab_hold_id = hold.id
    hold.status = "confirmed"
    return order


def cancel_grab(db: Session, hold: GrabHold, actor: User) -> None:
    if hold.status != "pending":
        raise ValueError("确认窗已关闭")
    load = db.get(Load, hold.load_id)
    shipper = db.get(User, load.shipper_id) if load else None
    if actor.role != "admin" and shipper and actor.id != shipper.id:
        raise ValueError("仅货主可取消")
    hold.status = "cancelled"
    if load:
        load.status = "published"
    if shipper:
        add_credit(db, shipper, -5, "breach", load.id if load else "")
        notify(db, hold.driver_id, "grab", "货主取消抢单，已记违约", hold.load_id)


def respond_invite(db: Session, invite: AssignInvite, driver: User, accept: bool) -> Order | None:
    if invite.status != "pending":
        raise ValueError("邀请已失效")
    exp = invite.expires_at
    if exp.tzinfo is not None:
        exp = exp.replace(tzinfo=None)
    if exp < datetime.utcnow():
        invite.status = "expired"
        raise ValueError("邀请已超时")
    if not accept:
        invite.status = "rejected"
        return None
    load = db.get(Load, invite.load_id)
    assert load
    shipper = db.get(User, load.shipper_id)
    assert shipper
    invite.status = "accepted"
    freight = load.expect_price or load.grab_price or 18000
    return deal_load(db, load, driver, shipper, freight, driver, "assign")


def transit_order(db: Session, order: Order, actor: User, action: str) -> Order:
    table = DRIVER_ACTIONS if actor.role == "driver" else SHIPPER_ACTIONS
    pair = table.get(action)
    if pair is None:
        raise ValueError("不允许的状态操作")
    expect, nxt = pair
    if order.status != expect:
        raise ValueError("订单状态不匹配")
    if action == "start_transit":
        seed_tracking(db, order)
    previous = order.status
    order.status = nxt
    load = db.get(Load, order.load_id)
    if load:
        load.status = nxt if nxt != "wait_load" else "dealt"
        if nxt == "completed":
            load.status = "completed"
    log_status(db, order, previous, actor)
    if nxt == "completed":
        shipper = db.get(User, order.shipper_id)
        driver = db.get(User, order.driver_id)
        if shipper:
            unfreeze_deposit(db, shipper, order.deposit, order.id)
            add_credit(db, shipper, 2, "complete_order", order.id)
        if driver:
            unfreeze_deposit(db, driver, order.deposit, order.id)
            add_credit(db, driver, 2, "complete_order", order.id)
    logger.info("订单状态 order=%s %s -> %s actor=%s", order.id, previous, nxt, actor.id)
    return order


def seed_tracking(db: Session, order: Order) -> None:
    if db.scalar(select(func.count(TrackingPoint.id)).where(TrackingPoint.order_id == order.id)):
        return
    lat, lng, _stop = gps_point(0)
    db.add(TrackingPoint(order_id=order.id, lat=lat, lng=lng))
    order.track_index = 0


def advance_tracking(db: Session, order: Order) -> list[TrackingPoint]:
    if order.status != "in_transit":
        raise ValueError("仅运输中可模拟轨迹")
    nxt = min(order.track_index + 1, len(TRACK_ROUTE) - 1)
    order.track_index = nxt
    lat, lng, stop = gps_point(nxt)
    db.add(TrackingPoint(order_id=order.id, lat=lat, lng=lng))
    db.flush()
    logger.info("模拟轨迹 order=%s idx=%s lat=%s lng=%s stop=%s", order.id, nxt, lat, lng, stop)
    return list(
        db.scalars(select(TrackingPoint).where(TrackingPoint.order_id == order.id).order_by(TrackingPoint.id)).all()
    )


def translate_text(text: str, source_locale: str) -> str:
    from app.rules import translate_text as _tr

    return _tr(text, source_locale)


def scan_sensitive(text: str) -> bool:
    if re.search(r"1\d{10}|weixin|wechat|wx|qq\s*\d+|whatsapp", text, re.I):
        return True
    return False


def estimate_quote(origin: str, dest: str, truck: str, cargo: str, db: Session | None = None, weight: float = 18) -> dict:
    """运费 = 国内段 + 口岸段 + 境外段，再乘车型/货类系数。"""
    corridors = {
        ("乌鲁木齐", "阿拉木图"): (670, 38, 270, 18, "khorgos"),
        ("乌鲁木齐", "塔什干"): (1180, 42, 430, 17, "irkeshtam"),
        ("霍尔果斯", "阿拉木图"): (40, 28, 282, 16, "khorgos"),
        ("喀什", "奥什"): (210, 36, 174, 19, "irkeshtam"),
        ("奎屯", "阿斯塔纳"): (520, 40, 1280, 17, "alashankou"),
        ("伊宁", "阿拉木图"): (90, 32, 310, 16, "khorgos"),
    }
    key = (origin, dest)
    cn, port, kz, price, gate = corridors.get(key, (620, 36, 280, 16, "khorgos"))
    if db is not None:
        price = float(cfg(db, "rate_base_cnkz", str(price)))
        t175 = float(cfg(db, "truck_factor_175", "1.15"))
        reefer = float(cfg(db, "cargo_factor_reefer", "1.35"))
    else:
        t175, reefer = 1.15, 1.35
    truck_k = t175 if "17" in truck else 1.0
    cargo_k = reefer if cargo in ("hazard", "reefer") else 1.0
    w = float(weight or 18)
    weight_k = 1.0 + max(0.0, (w - 18.0) * 0.012)
    km = cn + port + kz
    mid = int(km * price * truck_k * cargo_k * weight_k)
    low = int(mid * 0.88)
    high = int(mid * 1.12)
    o_lat, o_lng = city_ll(origin)
    d_lat, d_lng = city_ll(dest)
    return {
        "totalKm": km,
        "domesticKm": cn,
        "portKm": port,
        "abroadKm": kz,
        "borderKm": port,
        "foreignKm": kz,
        "hours": round(km / 52 + 5.5, 1),
        "driveHours": round(km / 52 + 5.5, 1),
        "portWaitHours": round(port / 12 + 3.2, 1),
        "feeLow": low,
        "feeHigh": high,
        "note": "reference_not_quote",
        "port": gate,
        "ports": [gate],
        "formula": f"{cn}×国内 + {port}×口岸 + {kz}×境外 × {price} × 车型{truck_k} × 货类{cargo_k}",
        "originLat": o_lat,
        "originLng": o_lng,
        "destLat": d_lat,
        "destLng": d_lng,
    }
