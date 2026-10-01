"""货源发布、浏览、竞价/抢单/指派。"""

from datetime import timedelta
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.deps import get_current_user
from app.models import AssignInvite, DriverProfile, GrabHold, Load, Quote, ShipperProfile, User, Vehicle, utcnow
from app.rules import city_ll, green_card_ok, green_card_light, notify
from app.services import (
    cancel_grab,
    cfg_int,
    choose_quote,
    confirm_grab,
    grab_load,
    new_id,
    public_user,
    respond_invite,
    serialize_load,
)

router = APIRouter()


class PublishBody(BaseModel):
    origin: str
    dest: str
    originCountry: str = "CN"
    destCountry: str = "KZ"
    loadTime: str
    cargoName: str
    weightT: float
    volumeM3: float = 0
    packing: str = "pallet"
    cargoClass: str = "general"
    truckLength: float = 13.5
    truckTonnage: float = 32
    receiverName: str = ""
    receiverPhone: str = ""
    remark: str = ""
    matchMode: str = "bid"
    expectPrice: int = 0
    floorPrice: int = 0
    grabPrice: int = 0
    inviteDriverIds: list[str] = Field(default_factory=list)
    photos: list[str] = Field(default_factory=list)
    draft: bool = False
    deadlineHours: int | None = None


class QuoteBody(BaseModel):
    amount: int
    eta: str = ""
    remark: str = ""


class AssignBody(BaseModel):
    driverIds: list[str]
    message: str = ""


class ChooseBody(BaseModel):
    quoteId: str


def _quote_count(db: Session, load_id: str) -> int:
    return db.scalar(select(func.count(Quote.id)).where(Quote.load_id == load_id, Quote.status == "active")) or 0


def _lowest_quote(db: Session, load_id: str) -> int | None:
    raw = db.scalar(select(func.min(Quote.amount)).where(Quote.load_id == load_id, Quote.status == "active"))
    return int(raw) if raw is not None else None


def _dump_load(db: Session, load: Load) -> dict:
    return serialize_load(load, _quote_count(db, load.id), _lowest_quote(db, load.id))


@router.get("/loads")
def list_marketplace(
    mode: str | None = None,
    corridor: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    q = select(Load).where(Load.status.in_(["published", "matching"]))
    if mode:
        q = q.where(Load.match_mode == mode)
    if corridor == "CN-KZ":
        q = q.where(Load.dest_country == "KZ")
    rows = db.scalars(q.order_by(Load.created_at.desc())).all()
    return {"items": [_dump_load(db, x) for x in rows]}


@router.get("/loads/mine")
def my_loads(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "shipper":
        raise HTTPException(status_code=403, detail="仅货主可查看我的货源")
    rows = db.scalars(select(Load).where(Load.shipper_id == user.id).order_by(Load.created_at.desc())).all()
    return {"items": [_dump_load(db, x) for x in rows]}


@router.post("/loads")
def publish(body: PublishBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "shipper":
        raise HTTPException(status_code=403, detail="仅货主可发布货源")
    if user.kyc_status != "approved":
        raise HTTPException(status_code=403, detail="未认证不可发单")
    if user.blacklisted:
        raise HTTPException(status_code=403, detail="黑名单用户禁止发单")
    o_lat, o_lng = city_ll(body.origin)
    d_lat, d_lng = city_ll(body.dest)
    hours = body.deadlineHours or cfg_int(db, "bid_close_hours", settings.bid_close_hours)
    load = Load(
        id=new_id("lod"),
        shipper_id=user.id,
        origin=body.origin,
        dest=body.dest,
        origin_country=body.originCountry,
        dest_country=body.destCountry,
        load_time=body.loadTime,
        cargo_name=body.cargoName,
        weight_t=body.weightT,
        volume_m3=body.volumeM3,
        packing=body.packing,
        cargo_class=body.cargoClass,
        truck_length=body.truckLength,
        truck_tonnage=body.truckTonnage,
        receiver_name=body.receiverName,
        receiver_phone=body.receiverPhone,
        remark=body.remark,
        match_mode=body.matchMode,
        expect_price=body.expectPrice,
        floor_price=body.floorPrice,
        grab_price=body.grabPrice,
        bid_deadline=utcnow() + timedelta(hours=hours),
        status="draft" if body.draft else "pending_review",
        photos_json=json.dumps((body.photos or [])[:9], ensure_ascii=False),
        origin_lat=o_lat,
        origin_lng=o_lng,
        dest_lat=d_lat,
        dest_lng=d_lng,
        is_draft=body.draft,
    )
    db.add(load)
    db.flush()
    max_n = cfg_int(db, "assign_max_drivers", settings.assign_max_drivers)
    if body.matchMode == "assign":
        hours = cfg_int(db, "assign_invite_hours", settings.assign_invite_hours)
        for did in body.inviteDriverIds[:max_n]:
            db.add(
                AssignInvite(
                    id=new_id("inv"),
                    load_id=load.id,
                    driver_id=did,
                    status="pending",
                    expires_at=utcnow() + timedelta(hours=hours),
                )
            )
    return _dump_load(db, load)


@router.get("/loads/{load_id}")
def load_detail(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    load = db.get(Load, load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="货源不存在")
    shipper = db.get(User, load.shipper_id)
    dealt = load.status in ("dealt", "wait_load", "loading", "in_transit", "wait_confirm", "completed")
    data = _dump_load(db, load)
    data["shipper"] = public_user(db, shipper, user, dealt) if shipper else None
    if data["shipper"]:
        profile = db.get(ShipperProfile, load.shipper_id)
        if profile:
            data["shipper"]["company"] = profile.company
    data["quotes"] = []
    if user.role == "shipper" and user.id == load.shipper_id:
        quotes = db.scalars(select(Quote).where(Quote.load_id == load.id)).all()
        data["quotes"] = []
        for q in quotes:
            drv = db.get(User, q.driver_id)
            card = public_user(db, drv, user, False) if drv else None
            if card:
                veh = db.scalar(select(Vehicle).where(Vehicle.driver_id == q.driver_id))
                card["vehicles"] = (
                    [
                        {
                            "lengthM": veh.length_m,
                            "tonnage": veh.tonnage,
                            "plate": veh.plate,
                            "brand": veh.brand,
                            "bodyType": veh.body_type,
                        }
                    ]
                    if veh
                    else []
                )
            data["quotes"].append(
                {
                    "id": q.id,
                    "driverId": q.driver_id,
                    "amount": q.amount,
                    "eta": q.eta,
                    "remark": q.remark,
                    "status": q.status,
                    "driver": card,
                }
            )
    data["invites"] = [
        {"id": i.id, "driverId": i.driver_id, "status": i.status}
        for i in db.scalars(select(AssignInvite).where(AssignInvite.load_id == load.id)).all()
    ]
    holds = db.scalars(select(GrabHold).where(GrabHold.load_id == load.id).order_by(GrabHold.created_at.desc())).all()
    data["holds"] = [
        {
            "id": h.id,
            "driverId": h.driver_id,
            "freight": h.freight,
            "status": h.status,
            "expiresAt": h.expires_at.isoformat() if h.expires_at else None,
            "driver": public_user(db, db.get(User, h.driver_id), user, False) if db.get(User, h.driver_id) else None,
        }
        for h in holds
    ]
    return data


@router.post("/loads/{load_id}/quotes")
def place_quote(
    load_id: str,
    body: QuoteBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可报价")
    if user.kyc_status != "approved" or user.blacklisted:
        raise HTTPException(status_code=403, detail="资质未通过或已拉黑")
    ok, reason = green_card_ok(db, user)
    if not ok:
        raise HTTPException(status_code=403, detail=reason)
    load = db.get(Load, load_id)
    if load is None or load.match_mode != "bid" or load.status not in ("published", "matching"):
        raise HTTPException(status_code=400, detail="当前不可报价")
    existing = db.scalar(select(Quote).where(Quote.load_id == load_id, Quote.driver_id == user.id))
    if existing:
        existing.amount = body.amount
        existing.eta = body.eta
        existing.remark = body.remark
        existing.status = "active"
        q = existing
    else:
        q = Quote(
            id=new_id("quo"),
            load_id=load_id,
            driver_id=user.id,
            amount=body.amount,
            eta=body.eta,
            remark=body.remark,
        )
        db.add(q)
    load.status = "matching"
    db.flush()
    return {"id": q.id, "amount": q.amount, "status": q.status}


@router.post("/loads/{load_id}/grab")
def grab(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="仅司机可抢单")
    load = db.get(Load, load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="货源不存在")
    try:
        hold = grab_load(db, load, user)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "holdId": hold.id,
        "status": hold.status,
        "expiresAt": hold.expires_at.isoformat() if hold.expires_at else None,
        "orderId": None,
    }


@router.post("/loads/{load_id}/grab/confirm")
def grab_confirm(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    hold = db.scalar(
        select(GrabHold).where(GrabHold.load_id == load_id, GrabHold.status == "pending").order_by(GrabHold.created_at.desc())
    )
    if hold is None:
        raise HTTPException(status_code=404, detail="没有待确认的抢单")
    try:
        order = confirm_grab(db, hold, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"orderId": order.id, "status": order.status}


@router.post("/loads/{load_id}/grab/cancel")
def grab_cancel(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    hold = db.scalar(
        select(GrabHold).where(GrabHold.load_id == load_id, GrabHold.status == "pending").order_by(GrabHold.created_at.desc())
    )
    if hold is None:
        raise HTTPException(status_code=404, detail="没有待确认的抢单")
    try:
        cancel_grab(db, hold, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "status": hold.status}


@router.post("/loads/{load_id}/assign")
def assign(
    load_id: str,
    body: AssignBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    load = db.get(Load, load_id)
    if load is None or load.shipper_id != user.id:
        raise HTTPException(status_code=404, detail="货源不存在")
    max_n = cfg_int(db, "assign_max_drivers", settings.assign_max_drivers)
    hours = cfg_int(db, "assign_invite_hours", settings.assign_invite_hours)
    created = []
    for did in body.driverIds[:max_n]:
        inv = AssignInvite(
            id=new_id("inv"),
            load_id=load.id,
            driver_id=did,
            message=body.message,
            expires_at=utcnow() + timedelta(hours=hours),
        )
        db.add(inv)
        notify(db, did, "assign", "收到货主指派", f"{load.origin} → {load.dest}")
        created.append(did)
    load.match_mode = "assign"
    load.status = "matching"
    return {"invited": created}


@router.post("/loads/{load_id}/choose")
def choose(
    load_id: str,
    body: ChooseBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    load = db.get(Load, load_id)
    quote = db.get(Quote, body.quoteId)
    if load is None or quote is None or load.shipper_id != user.id:
        raise HTTPException(status_code=404, detail="货源或报价不存在")
    try:
        order = choose_quote(db, load, quote, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"orderId": order.id, "status": order.status}


@router.get("/invites")
def my_invites(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AssignInvite).where(AssignInvite.driver_id == user.id)).all()
    items = []
    for inv in rows:
        load = db.get(Load, inv.load_id)
        items.append(
            {
                "id": inv.id,
                "status": inv.status,
                "message": inv.message,
                "expiresAt": inv.expires_at.isoformat() if inv.expires_at else None,
                "load": _dump_load(db, load) if load else None,
            }
        )
    return {"items": items}


class InviteReply(BaseModel):
    accept: bool


@router.post("/invites/{invite_id}/reply")
def reply_invite(
    invite_id: str,
    body: InviteReply,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    inv = db.get(AssignInvite, invite_id)
    if inv is None or inv.driver_id != user.id:
        raise HTTPException(status_code=404, detail="邀请不存在")
    try:
        order = respond_invite(db, inv, user, body.accept)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"inviteStatus": inv.status, "orderId": order.id if order else None}


@router.post("/loads/{load_id}/offline")
def offline_load(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    load = db.get(Load, load_id)
    if load is None or load.shipper_id != user.id:
        raise HTTPException(status_code=404, detail="货源不存在")
    if load.status not in ("published", "matching", "pending_review", "draft"):
        raise HTTPException(status_code=400, detail="当前状态不可下架")
    load.status = "cancelled"
    for q in load.quotes:
        if q.status == "active":
            q.status = "expired"
    for h in db.scalars(select(GrabHold).where(GrabHold.load_id == load.id, GrabHold.status == "pending")).all():
        h.status = "cancelled"
    return {"ok": True, "status": load.status}


@router.post("/loads/{load_id}/copy")
def copy_load(load_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    src = db.get(Load, load_id)
    if src is None or src.shipper_id != user.id:
        raise HTTPException(status_code=404, detail="货源不存在")
    copy = Load(
        id=new_id("lod"),
        shipper_id=user.id,
        origin=src.origin,
        dest=src.dest,
        origin_country=src.origin_country,
        dest_country=src.dest_country,
        load_time=src.load_time,
        cargo_name=src.cargo_name,
        weight_t=src.weight_t,
        volume_m3=src.volume_m3,
        packing=src.packing,
        cargo_class=src.cargo_class,
        truck_length=src.truck_length,
        truck_tonnage=src.truck_tonnage,
        receiver_name=src.receiver_name,
        receiver_phone=src.receiver_phone,
        remark=src.remark,
        match_mode=src.match_mode,
        expect_price=src.expect_price,
        floor_price=src.floor_price,
        grab_price=src.grab_price,
        bid_deadline=utcnow() + timedelta(hours=cfg_int(db, "bid_close_hours", settings.bid_close_hours)),
        status="pending_review",
        photos_json=src.photos_json,
        origin_lat=src.origin_lat,
        origin_lng=src.origin_lng,
        dest_lat=src.dest_lat,
        dest_lng=src.dest_lng,
        is_draft=False,
    )
    db.add(copy)
    db.flush()
    return _dump_load(db, copy)


@router.get("/drivers")
def list_drivers(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(User).where(User.role == "driver", User.kyc_status == "approved", User.blacklisted.is_(False))).all()
    items = []
    for d in rows:
        profile = db.get(DriverProfile, d.id)
        vehicles = db.scalars(select(Vehicle).where(Vehicle.driver_id == d.id)).all()
        items.append(
            {
                **public_user(db, d, user, False),
                "greenCardExpires": profile.green_card_expires if profile else "",
                "greenLight": green_card_light(profile.green_card_expires if profile else ""),
                "customs": profile.customs if profile else "",
                "vehicles": [
                    {
                        "id": v.id,
                        "plate": v.plate,
                        "lengthM": v.length_m,
                        "tonnage": v.tonnage,
                        "brand": getattr(v, "brand", "") or "",
                        "bodyType": getattr(v, "body_type", "") or "van",
                    }
                    for v in vehicles
                ],
            }
        )
    return {"items": items}


@router.get("/holds")
def my_holds(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    q = select(GrabHold)
    if user.role == "driver":
        q = q.where(GrabHold.driver_id == user.id)
    elif user.role == "shipper":
        load_ids = [x.id for x in db.scalars(select(Load).where(Load.shipper_id == user.id)).all()]
        q = q.where(GrabHold.load_id.in_(load_ids or ["__none__"]))
    rows = db.scalars(q.order_by(GrabHold.created_at.desc())).all()
    items = []
    for h in rows:
        load = db.get(Load, h.load_id)
        items.append(
            {
                "id": h.id,
                "status": h.status,
                "freight": h.freight,
                "expiresAt": h.expires_at.isoformat() if h.expires_at else None,
                "load": _dump_load(db, load) if load else None,
                "driver": public_user(db, db.get(User, h.driver_id), user, False) if db.get(User, h.driver_id) else None,
            }
        )
    return {"items": items}
