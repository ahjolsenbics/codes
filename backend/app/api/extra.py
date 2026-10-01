"""保证金、口岸、测算、资质、信用。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.deps import get_current_user, get_optional_user
from app.models import (
    Credential,
    CreditRecord,
    DepositAccount,
    DepositLedger,
    DriverProfile,
    EstimateLog,
    LaneSubscribe,
    Notification,
    Port,
    PortReport,
    Review,
    ShipperProfile,
    User,
    Vehicle,
)
from app.rules import (
    anon_estimate_count,
    confirm_pay,
    estimate_cached,
    green_card_light,
    green_card_ok,
    hash_password,
    start_pay,
)
from app.services import cfg_int, ensure_account, new_id, public_user

logger = logging.getLogger("yunmm")

router = APIRouter()


class TopupBody(BaseModel):
    amount: int = 200
    channel: str = "wechat"


class EstimateBody(BaseModel):
    origin: str
    dest: str
    truck: str = "13.5x32"
    cargo: str = "general"
    weight: float = 18


class PortReportBody(BaseModel):
    status: str
    waitMin: int = 60
    photoUrl: str = ""
    lat: float = 0
    lng: float = 0


class KycItemIn(BaseModel):
    kind: str
    fileUrl: str = ""
    expiresAt: str = ""
    extra: dict = Field(default_factory=dict)


class KycBody(BaseModel):
    kind: str = "enterprise"
    company: str = ""
    legalName: str = ""
    idNumber: str = ""
    items: list[KycItemIn] = Field(default_factory=list)


_SHIPPER_REQUIRED = {
    "enterprise": ("business_license", "operator_id"),
    "forwarder": ("business_license", "operator_id"),
    "personal": ("id_card_front",),
}
_DRIVER_REQUIRED = (
    "id_card",
    "id_card_hold",
    "license",
    "vehicle",
    "road_permit",
    "tir",
    "green_card",
    "truck_front",
    "truck_side",
    "truck_box",
)


def _cred_out(c: Credential) -> dict:
    extra: dict = {}
    if c.extra_json:
        try:
            extra = json.loads(c.extra_json)
        except json.JSONDecodeError:
            extra = {}
    return {
        "id": c.id,
        "kind": c.kind,
        "status": c.status,
        "expiresAt": c.expires_at,
        "note": c.note,
        "fileUrl": c.file_url,
        "extra": extra,
        "daysLeft": _days_left(c.expires_at),
    }


def _days_left(expires: str) -> int | None:
    if not expires:
        return None
    try:
        day = datetime.strptime(expires[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    return (day - datetime.now(timezone.utc).date()).days


def _vehicle_out(v: Vehicle) -> dict:
    return {
        "id": v.id,
        "plate": v.plate,
        "lengthM": v.length_m,
        "tonnage": v.tonnage,
        "bodyType": getattr(v, "body_type", "") or "van",
        "energy": getattr(v, "energy", "") or "diesel",
        "axles": getattr(v, "axles", 6) or 6,
        "vin": getattr(v, "vin", "") or "",
        "brand": getattr(v, "brand", "") or "",
        "inspectExpires": getattr(v, "inspect_expires", "") or "",
        "insuranceExpires": getattr(v, "insurance_expires", "") or "",
        "status": getattr(v, "status", "active") or "active",
    }


@router.get("/deposits/me")
def my_deposit(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    acc = ensure_account(db, user.id)
    ledgers = db.scalars(
        select(DepositLedger).where(DepositLedger.user_id == user.id).order_by(DepositLedger.id.desc())
    ).all()
    return {
        "available": acc.available,
        "frozen": acc.frozen,
        "exempt": user.deposit_exempt,
        "ledgers": [
            {
                "id": x.id,
                "kind": x.kind,
                "amount": x.amount,
                "channel": x.channel,
                "orderId": x.order_id,
                "status": getattr(x, "status", "ok") or "ok",
                "note": getattr(x, "note", "") or "",
                "at": x.created_at.isoformat() if x.created_at else None,
            }
            for x in ledgers
        ],
    }


@router.post("/deposits/topup")
def pay_deposit(body: TopupBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.deposit_exempt:
        return {"ok": True, "exempt": True, "status": "ok"}
    row = start_pay(db, user, body.amount, body.channel)
    return {
        "intentId": row.id,
        "status": "pending",
        "amount": row.amount,
        "channel": body.channel,
        "qr": f"yunmm://pay/{row.id}/{body.channel}/{row.amount}",
    }


class PayConfirmBody(BaseModel):
    intentId: int


@router.post("/deposits/confirm")
def pay_confirm(body: PayConfirmBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        return confirm_pay(db, user, body.intentId)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ports")
def list_ports(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Port)).all()
    ttl = cfg_int(db, "port_status_ttl_hours", settings.port_status_ttl_hours)
    items = []
    now = __import__("datetime").datetime.utcnow()
    for p in rows:
        updated = p.updated_at.replace(tzinfo=None) if p.updated_at and p.updated_at.tzinfo else p.updated_at
        stale = False
        if updated:
            stale = (now - updated).total_seconds() > ttl * 3600
        items.append(
            {
                "id": p.id,
                "nameZh": p.name_zh,
                "nameRu": p.name_ru,
                "nameEn": p.name_en,
                "country": p.country,
                "corridor": p.corridor,
                "status": "stale" if stale else p.status,
                "waitMin": p.wait_min,
                "source": p.source,
                "lat": p.lat,
                "lng": p.lng,
                "updatedAt": p.updated_at.isoformat() if p.updated_at else None,
                "ttlHours": ttl,
                "stale": stale,
            }
        )
    return {"items": items}


@router.get("/ports/{port_id}")
def port_detail(port_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    p = db.get(Port, port_id)
    if p is None:
        raise HTTPException(status_code=404, detail="口岸不存在")
    reports = db.scalars(select(PortReport).where(PortReport.port_id == port_id).order_by(PortReport.id.desc())).all()
    return {
        "id": p.id,
        "nameZh": p.name_zh,
        "status": p.status,
        "waitMin": p.wait_min,
        "source": p.source,
        "reports": [
            {"id": r.id, "status": r.status, "waitMin": r.wait_min, "approved": r.approved, "driverId": r.driver_id}
            for r in reports
        ],
    }


@router.post("/ports/{port_id}/report")
def report_port(
    port_id: str,
    body: PortReportBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可上报口岸")
    port = db.get(Port, port_id)
    if port is None:
        raise HTTPException(status_code=404, detail="口岸不存在")
    if body.lat and port.lat:
        dist = abs(body.lat - port.lat) + abs(body.lng - port.lng)
        if dist > 0.8:
            raise HTTPException(status_code=400, detail="定位不在口岸围栏内")
    db.add(
        PortReport(
            port_id=port_id,
            driver_id=user.id,
            status=body.status,
            wait_min=body.waitMin,
            approved=False,
            photo_url=body.photoUrl or "/covers/building.svg",
            lat=body.lat,
            lng=body.lng,
        )
    )
    return {"ok": True, "pendingReview": True}


@router.post("/estimate")
def estimate(
    body: EstimateBody,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> dict:
    anon = (request.headers.get("x-anon-key") or (request.client.host if request.client else "anon"))[:80]
    limit = cfg_int(db, "estimate_anon_limit", 2)
    if user is None and anon_estimate_count(db, anon) >= limit:
        return {"needLogin": True, "limit": limit}
    data = estimate_cached(db, body.origin, body.dest, body.truck, body.cargo, body.weight)
    db.add(
        EstimateLog(
            origin=body.origin,
            dest=body.dest,
            result_json=json.dumps(data, ensure_ascii=False),
            anon_key=user.id if user else anon,
        )
    )
    return data


@router.get("/kyc/me")
def my_kyc(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    creds = db.scalars(select(Credential).where(Credential.user_id == user.id)).all()
    shipper = db.get(ShipperProfile, user.id)
    driver = db.get(DriverProfile, user.id)
    return {
        "status": user.kyc_status,
        "role": user.role,
        "kind": shipper.kind if shipper else ("driver" if user.role == "driver" else "enterprise"),
        "company": shipper.company if shipper else "",
        "greenCardNo": driver.green_card_no if driver else "",
        "greenCardExpires": driver.green_card_expires if driver else "",
        "greenLight": green_card_light(driver.green_card_expires if driver else ""),
        "greenDays": _days_left(driver.green_card_expires if driver else ""),
        "frozen": bool(user.frozen_reason),
        "frozenReason": user.frozen_reason,
        "customs": driver.customs if driver else "",
        "portPoints": int(
            (db.scalar(select(func.count(PortReport.id)).where(PortReport.driver_id == user.id, PortReport.approved.is_(True))) or 0) * 8
        ),
        "rejectReason": next((c.note for c in creds if c.status == "rejected" and c.note), ""),
        "credentials": [
            {**_cred_out(c), "light": green_card_light(c.expires_at) if c.expires_at else "none"}
            for c in creds
        ],
    }


@router.post("/kyc/submit")
def submit_kyc(body: KycBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    items = {x.kind: x for x in body.items if x.kind}
    if user.role == "driver":
        required = _DRIVER_REQUIRED
        missing = [k for k in required if not (items.get(k) and items[k].fileUrl)]
        green = items.get("green_card")
        if green:
            extra = green.extra or {}
            if not extra.get("no") or not extra.get("expires") or not extra.get("customs"):
                missing.append("green_card_fields")
    else:
        kind = body.kind if body.kind in _SHIPPER_REQUIRED else "enterprise"
        required = _SHIPPER_REQUIRED[kind]
        missing = [k for k in required if not (items.get(k) and items[k].fileUrl)]
        if kind != "personal" and not body.company.strip():
            missing.append("company")
        if kind == "personal" and (not body.legalName.strip() or not body.idNumber.strip()):
            missing.append("id_profile")
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少必填材料: {','.join(missing)}")

    existing = {c.kind: c for c in db.scalars(select(Credential).where(Credential.user_id == user.id)).all()}
    for kind, item in items.items():
        row = existing.get(kind)
        extra_json = json.dumps(item.extra or {}, ensure_ascii=False)
        if row is None:
            row = Credential(id=new_id("crd"), user_id=user.id, kind=kind)
            db.add(row)
        row.file_url = item.fileUrl
        row.expires_at = item.expiresAt or (item.extra or {}).get("expires", "")
        row.extra_json = extra_json
        row.status = "pending"
        row.note = ""

    if user.role == "shipper":
        profile = db.get(ShipperProfile, user.id)
        kind = body.kind if body.kind in _SHIPPER_REQUIRED else "enterprise"
        if profile is None:
            profile = ShipperProfile(user_id=user.id, kind=kind, company=body.company.strip())
            db.add(profile)
        else:
            profile.kind = kind
            profile.company = body.company.strip() or profile.company
    else:
        profile = db.get(DriverProfile, user.id)
        green = items.get("green_card")
        extra = (green.extra if green else {}) or {}
        if profile is None:
            profile = DriverProfile(user_id=user.id)
            db.add(profile)
        if extra:
            profile.green_card_no = str(extra.get("no") or profile.green_card_no)
            profile.green_card_expires = str(extra.get("expires") or profile.green_card_expires)
            profile.customs = str(extra.get("customs") or profile.customs)

    user.kyc_status = "pending"
    logger.info("资质已提交审核 user=%s role=%s items=%s", user.id, user.role, list(items))
    return {"status": user.kyc_status}


@router.get("/users/{user_id}/credit")
def credit_page(user_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    recs = db.scalars(select(CreditRecord).where(CreditRecord.user_id == user_id).order_by(CreditRecord.id.desc())).all()
    reviews = db.scalars(select(Review).where(Review.to_user == user_id)).all()
    stars = [r.stars for r in reviews] or [5]
    credit = target.credit
    return {
        "user": public_user(db, target, user, True),
        "level": "A" if credit >= 120 else ("B" if credit >= 100 else "C"),
        "ontime": round(sum(1 for s in stars if s >= 4) / max(len(stars), 1), 2),
        "complaints": sum(1 for r in recs if r.reason in ("dispute_lose", "breach")),
        "records": [{"delta": r.delta, "reason": r.reason, "orderId": r.order_id} for r in recs],
        "reviews": [{"stars": r.stars, "tags": r.tags, "comment": r.comment} for r in reviews],
    }


class SettingsBody(BaseModel):
    password: str = ""
    notifyPush: bool | None = None
    notifySms: bool | None = None
    quietHours: bool | None = None


@router.post("/settings")
def save_settings(body: SettingsBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if body.password:
        if len(body.password) < 6:
            raise HTTPException(status_code=400, detail="密码至少 6 位")
        user.password_hash = hash_password(body.password)
    if body.notifyPush is not None:
        user.notify_push = body.notifyPush
    if body.notifySms is not None:
        user.notify_sms = body.notifySms
    if body.quietHours is not None:
        user.quiet_hours = body.quietHours
    return public_user(db, user, user, True)


@router.post("/account/cancel")
def cancel_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    user.disabled = True
    user.frozen_reason = "cancelled"
    return {"ok": True}


@router.get("/notifications")
def list_notes(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())).all()
    return {
        "unread": sum(1 for x in rows if not x.read),
        "items": [
            {
                "id": x.id,
                "kind": x.kind,
                "title": x.title,
                "body": x.body,
                "read": x.read,
                "at": x.created_at.isoformat() if x.created_at else None,
            }
            for x in rows[:40]
        ],
    }


@router.post("/notifications/read")
def read_notes(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    for x in db.scalars(select(Notification).where(Notification.user_id == user.id, Notification.read.is_(False))).all():
        x.read = True
    return {"ok": True}


class VehicleBody(BaseModel):
    plate: str
    lengthM: float = 13.5
    tonnage: float = 32
    bodyType: str = "van"
    energy: str = "diesel"
    axles: int = 6
    vin: str = ""
    brand: str = ""
    inspectExpires: str = "2027-06-30"
    insuranceExpires: str = "2026-12-31"


@router.get("/vehicles")
def my_vehicles(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可管理车辆")
    rows = db.scalars(select(Vehicle).where(Vehicle.driver_id == user.id)).all()
    return {"items": [_vehicle_out(v) for v in rows]}


@router.post("/vehicles")
def add_vehicle(body: VehicleBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可绑定车辆")
    v = Vehicle(
        id=new_id("veh"),
        driver_id=user.id,
        plate=body.plate,
        length_m=body.lengthM,
        tonnage=body.tonnage,
        body_type=body.bodyType,
        energy=body.energy,
        axles=body.axles or 6,
        vin=body.vin.strip(),
        brand=body.brand.strip(),
        inspect_expires=body.inspectExpires or "2027-06-30",
        insurance_expires=body.insuranceExpires or "2026-12-31",
        status="active",
    )
    db.add(v)
    db.flush()
    return _vehicle_out(v)


class LaneBody(BaseModel):
    origin: str
    dest: str


@router.get("/lanes")
def my_lanes(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(LaneSubscribe).where(LaneSubscribe.driver_id == user.id)).all()
    return {"items": [{"id": x.id, "origin": x.origin, "dest": x.dest} for x in rows]}


@router.post("/lanes")
def add_lane(body: LaneBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可订阅线路")
    row = LaneSubscribe(id=new_id("ln"), driver_id=user.id, origin=body.origin, dest=body.dest)
    db.add(row)
    return {"id": row.id}


@router.get("/users/{user_id}/phone")
def unlock_phone(user_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    unlock = cfg_int(db, "phone_unlock_credit", settings.phone_unlock_credit)
    if user.credit < unlock:
        raise HTTPException(status_code=403, detail=f"信用分需达到 {unlock} 才可查看完整号码")
    return {"phone": target.phone, "unlocked": True}
