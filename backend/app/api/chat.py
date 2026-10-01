"""会话、消息、中俄 Mock 翻译、敏感词。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user
from app.models import Conversation, Load, Message, Order, User
from app.services import add_credit, new_id, scan_sensitive, translate_text

router = APIRouter()


class OpenBody(BaseModel):
    loadId: str | None = None
    orderId: str | None = None
    peerId: str | None = None


class SendBody(BaseModel):
    body: str
    kind: str = "text"


@router.get("/conversations")
def list_conv(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(
        select(Conversation).where(or_(Conversation.shipper_id == user.id, Conversation.driver_id == user.id))
    ).all()
    items = []
    for c in rows:
        last = db.scalars(
            select(Message).where(Message.conversation_id == c.id).order_by(Message.id.desc())
        ).first()
        peer_id = c.driver_id if user.id == c.shipper_id else c.shipper_id
        peer = db.get(User, peer_id) if peer_id else None
        load = db.get(Load, c.load_id) if c.load_id else None
        items.append(
            {
                "id": c.id,
                "loadId": c.load_id,
                "orderId": c.order_id,
                "peerId": peer_id,
                "peerName": peer.name if peer else "对方",
                "lane": f"{load.origin} → {load.dest}" if load else "",
                "last": None
                if last is None
                else {
                    "body": last.body,
                    "kind": last.kind,
                    "senderId": last.sender_id,
                    "at": last.created_at.isoformat() if last.created_at else None,
                },
            }
        )
    return {"items": items}


@router.post("/conversations/open")
def open_conv(body: OpenBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    shipper_id = user.id if user.role == "shipper" else body.peerId
    driver_id = user.id if user.role == "driver" else body.peerId
    if body.loadId:
        load = db.get(Load, body.loadId)
        if load is None:
            raise HTTPException(status_code=404, detail="货源不存在")
        shipper_id = load.shipper_id
        if user.role == "driver":
            driver_id = user.id
    existing = db.scalar(
        select(Conversation).where(
            Conversation.shipper_id == shipper_id,
            Conversation.driver_id == driver_id,
            Conversation.load_id == (body.loadId or ""),
        )
    )
    if existing:
        return {"id": existing.id}
    conv = Conversation(
        id=new_id("cv"),
        load_id=body.loadId or "",
        order_id=body.orderId or "",
        shipper_id=shipper_id or "",
        driver_id=driver_id or "",
    )
    db.add(conv)
    db.flush()
    return {"id": conv.id}


@router.get("/conversations/{cid}/messages")
def messages(cid: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    conv = db.get(Conversation, cid)
    if conv is None or (user.role != "admin" and user.id not in (conv.shipper_id, conv.driver_id)):
        raise HTTPException(status_code=404, detail="会话不存在")
    rows = db.scalars(select(Message).where(Message.conversation_id == cid).order_by(Message.id)).all()
    now = __import__("datetime").datetime.utcnow()
    for m in rows:
        if m.sender_id != user.id and m.read_at is None:
            m.read_at = now
    return {
        "items": [
            {
                "id": m.id,
                "senderId": m.sender_id,
                "kind": m.kind,
                "body": m.body,
                "translated": m.translated,
                "risk": m.risk,
                "readAt": m.read_at.isoformat() if m.read_at else None,
                "at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in rows
        ]
    }


@router.post("/conversations/{cid}/messages")
def send(cid: str, body: SendBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    conv = db.get(Conversation, cid)
    if conv is None or user.id not in (conv.shipper_id, conv.driver_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    risk = scan_sensitive(body.body)
    text = body.body
    if risk:
        text = "【联系方式已隐藏】请在成交后查看脱敏号码"
        user.chat_strikes = (user.chat_strikes or 0) + 1
        add_credit(db, user, -2, "sensitive")
        if user.chat_strikes >= 3:
            add_credit(db, user, -8, "breach")
    trans = translate_text(body.body, user.locale)
    msg = Message(
        conversation_id=cid,
        sender_id=user.id,
        kind=body.kind,
        body=text,
        translated=trans,
        risk=risk,
    )
    db.add(msg)
    db.flush()
    return {"id": msg.id, "body": msg.body, "translated": msg.translated, "risk": msg.risk}
