"""订单、运单、轨迹、评价。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user
from app.models import Load, Order, Review, StatusLog, TrackingPoint, User, Waybill
from app.rules import ROUTE_STOPS, TRACK_ROUTE
from app.services import advance_tracking, public_user, serialize_load, transit_order

router = APIRouter()


class ActionBody(BaseModel):
    action: str


class ReviewBody(BaseModel):
    stars: int = 5
    tags: str = "on_time"
    comment: str = ""


def _can_see(order: Order, user: User) -> bool:
    return user.role == "admin" or user.id in (order.shipper_id, order.driver_id)


def _dump_order(db: Session, order: Order, viewer: User) -> dict:
    load = db.get(Load, order.load_id)
    shipper = db.get(User, order.shipper_id)
    driver = db.get(User, order.driver_id)
    dealt = True
    waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
    logs = db.scalars(select(StatusLog).where(StatusLog.order_id == order.id).order_by(StatusLog.id)).all()
    points = db.scalars(
        select(TrackingPoint).where(TrackingPoint.order_id == order.id).order_by(TrackingPoint.id)
    ).all()
    return {
        "id": order.id,
        "status": order.status,
        "matchMode": order.match_mode,
        "freight": order.freight,
        "deposit": order.deposit,
        "trackIndex": order.track_index,
        "load": serialize_load(load) if load else None,
        "shipper": public_user(db, shipper, viewer, dealt) if shipper else None,
        "driver": public_user(db, driver, viewer, dealt) if driver else None,
        "waybill": None
        if waybill is None
        else {
            "id": waybill.id,
            "loadNote": waybill.load_note,
            "deliverNote": waybill.deliver_note,
            "signed": waybill.signed,
            "signPhoto": waybill.sign_photo,
            "loadPhoto": waybill.load_photo,
            "deliverPhoto": waybill.deliver_photo,
            "signData": waybill.sign_data,
        },
        "timeline": [
            {
                "from": x.from_status,
                "to": x.to_status,
                "actorId": x.actor_id,
                "actorRole": x.actor_role,
                "at": x.created_at.isoformat() if x.created_at else None,
            }
            for x in logs
        ],
        "track": [{"lat": p.lat, "lng": p.lng, "at": p.created_at.isoformat() if p.created_at else None} for p in points],
        "route": [{"lat": lat, "lng": lng, "name": ROUTE_STOPS[i] if i < len(ROUTE_STOPS) else ""} for i, (lat, lng) in enumerate(TRACK_ROUTE)],
        "reviewed": bool(db.scalar(select(Review).where(Review.order_id == order.id, Review.from_user == viewer.id))),
    }


@router.get("/orders")
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    q = select(Order)
    if user.role == "shipper":
        q = q.where(Order.shipper_id == user.id)
    elif user.role == "driver":
        q = q.where(Order.driver_id == user.id)
    rows = db.scalars(q.order_by(Order.created_at.desc())).all()
    return {"items": [_dump_order(db, o, user) for o in rows]}


@router.get("/orders/{order_id}")
def order_detail(order_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    order = db.get(Order, order_id)
    if order is None or not _can_see(order, user):
        raise HTTPException(status_code=404, detail="订单不存在")
    return _dump_order(db, order, user)


@router.post("/orders/{order_id}/actions")
def order_action(
    order_id: str,
    body: ActionBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = db.get(Order, order_id)
    if order is None or not _can_see(order, user):
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        transit_order(db, order, user, body.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if body.action == "arrive":
        waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
        if waybill:
            waybill.deliver_note = "arrived"
            if not waybill.deliver_photo:
                waybill.deliver_photo = "/covers/building.svg"
    if body.action == "start_load":
        waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
        if waybill and not waybill.load_photo:
            waybill.load_photo = "/covers/machine.svg"
    if body.action == "confirm_receive":
        waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
        if waybill:
            waybill.signed = True
    return _dump_order(db, order, user)


@router.post("/orders/{order_id}/track/simulate")
def simulate_track(order_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    order = db.get(Order, order_id)
    if order is None or not _can_see(order, user):
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        points = advance_tracking(db, order)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "trackIndex": order.track_index,
        "track": [{"lat": p.lat, "lng": p.lng} for p in points],
    }


@router.post("/orders/{order_id}/reviews")
def review_order(
    order_id: str,
    body: ReviewBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = db.get(Order, order_id)
    if order is None or order.status != "completed" or not _can_see(order, user):
        raise HTTPException(status_code=400, detail="仅已完成订单可评价")
    target = order.driver_id if user.id == order.shipper_id else order.shipper_id
    existed = db.scalar(select(Review).where(Review.order_id == order_id, Review.from_user == user.id))
    if existed:
        raise HTTPException(status_code=400, detail="已评价不可修改")
    db.add(
        Review(
            order_id=order_id,
            from_user=user.id,
            to_user=target,
            stars=body.stars,
            tags=body.tags,
            comment=body.comment,
        )
    )
    other = db.get(User, target)
    if other:
        from app.services import add_credit

        add_credit(db, other, 1 if body.stars >= 4 else 0, "review", order_id)
    return {"ok": True}


class SignBody(BaseModel):
    signData: str = ""
    comment: str = ""
    photoUrl: str = ""


@router.post("/orders/{order_id}/waybill/sign")
def sign_waybill(
    order_id: str,
    body: SignBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = db.get(Order, order_id)
    if order is None or not _can_see(order, user):
        raise HTTPException(status_code=404, detail="订单不存在")
    if user.id != order.shipper_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="仅货主可签收")
    if order.status not in ("wait_confirm", "completed"):
        raise HTTPException(status_code=400, detail="当前状态不可签收")
    waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
    if waybill is None:
        raise HTTPException(status_code=404, detail="运单不存在")
    waybill.signed = True
    waybill.sign_data = body.signData
    waybill.deliver_note = body.comment or waybill.deliver_note or "signed"
    if body.photoUrl:
        waybill.deliver_photo = body.photoUrl
    if order.status == "wait_confirm":
        from app.services import transit_order as _tr

        _tr(db, order, user, "confirm_receive")
    return _dump_order(db, order, user)


class PhotoBody(BaseModel):
    kind: str = "load"
    url: str


@router.post("/orders/{order_id}/photos")
def order_photo(
    order_id: str,
    body: PhotoBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = db.get(Order, order_id)
    if order is None or not _can_see(order, user):
        raise HTTPException(status_code=404, detail="订单不存在")
    waybill = db.scalar(select(Waybill).where(Waybill.order_id == order.id))
    if waybill is None:
        raise HTTPException(status_code=404, detail="运单不存在")
    if body.kind == "deliver":
        waybill.deliver_photo = body.url
    else:
        waybill.load_photo = body.url
    return _dump_order(db, order, user)
