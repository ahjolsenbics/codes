"""管理后台：看板、审核、保证金、纠纷、黑名单、配置、审计。"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import require_admin
from app.models import (
    Announcement,
    AuditLog,
    Blacklist,
    Credential,
    DepositAccount,
    DepositLedger,
    Dispute,
    DriverProfile,
    EstimateLog,
    I18nEntry,
    Load,
    Order,
    Port,
    PortReport,
    ShipperProfile,
    SysConfig,
    User,
)
from app.rules import notify, refund_pay
from app.services import add_credit, new_id, unfreeze_deposit

logger = logging.getLogger("yunmm")
router = APIRouter()


def _audit(db: Session, admin: User, action: str, target: str = "") -> None:
    db.add(AuditLog(actor_id=admin.id, action=action, target=target))


def _name(db: Session, user_id: str) -> str:
    user = db.get(User, user_id)
    return user.name if user else user_id


def _company(db: Session, user_id: str) -> str:
    shipper = db.get(ShipperProfile, user_id)
    return shipper.company if shipper else ""


@router.get("/admin/dashboard")
def dashboard(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    users = db.scalar(select(func.count(User.id))) or 0
    approved = db.scalar(select(func.count(User.id)).where(User.kyc_status == "approved")) or 0
    kyc_pending = db.scalar(select(func.count(User.id)).where(User.kyc_status == "pending")) or 0
    loads = db.scalar(select(func.count(Load.id))) or 0
    loads_pending = db.scalar(select(func.count(Load.id)).where(Load.status == "pending_review")) or 0
    orders = db.scalar(select(func.count(Order.id))) or 0
    done = db.scalar(select(func.count(Order.id)).where(Order.status == "completed")) or 0
    disputes = db.scalar(select(func.count(Dispute.id))) or 0
    disputes_open = db.scalar(select(func.count(Dispute.id)).where(Dispute.status == "open")) or 0
    estimates = db.scalar(select(func.count(EstimateLog.id))) or 0
    ledger_sum = db.scalar(select(func.coalesce(func.sum(DepositLedger.amount), 0)).where(DepositLedger.kind == "pay")) or 0
    by_country = db.execute(select(User.country, func.count(User.id)).group_by(User.country)).all()
    by_status = db.execute(select(Order.status, func.count(Order.id)).group_by(Order.status)).all()
    series = []
    from datetime import datetime, timedelta, timezone

    today = datetime.now(timezone.utc).date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(days=1)
        n = db.scalar(select(func.count(Order.id)).where(Order.created_at >= start, Order.created_at < end)) or 0
        series.append({"day": day.isoformat()[5:], "orders": n})
    pending_pay = db.scalar(select(func.count(DepositLedger.id)).where(DepositLedger.status == "pending")) or 0
    kyc_queue = [
        {"id": u.id, "name": u.name, "role": u.role, "kycStatus": u.kyc_status}
        for u in db.scalars(select(User).where(User.kyc_status == "pending").limit(8)).all()
    ]
    load_queue = [
        {
            "id": x.id,
            "origin": x.origin,
            "dest": x.dest,
            "originCountry": x.origin_country,
            "destCountry": x.dest_country,
            "cargoName": x.cargo_name,
            "weightT": x.weight_t,
            "matchMode": x.match_mode,
            "status": x.status,
        }
        for x in db.scalars(select(Load).where(Load.status == "pending_review").limit(8)).all()
    ]
    live_orders = []
    for o in db.scalars(
        select(Order).where(Order.status.in_(("in_transit", "wait_load", "loading", "wait_confirm"))).limit(8)
    ).all():
        load = db.get(Load, o.load_id)
        live_orders.append(
            {
                "id": o.id,
                "status": o.status,
                "freight": o.freight,
                "shipperName": _name(db, o.shipper_id),
                "driverName": _name(db, o.driver_id),
                "lane": f"{load.origin} → {load.dest}" if load else o.id,
            }
        )
    return {
        "users": users,
        "kycPassRate": round(approved / users, 3) if users else 0,
        "kycPending": kyc_pending,
        "loads": loads,
        "loadsPending": loads_pending,
        "orders": orders,
        "dealRate": round(done / orders, 3) if orders else 0,
        "depositIn": int(ledger_sum),
        "disputeRate": round(disputes / orders, 3) if orders else 0,
        "disputesOpen": disputes_open,
        "estimates": estimates,
        "pendingPay": int(pending_pay),
        "usersByCountry": sorted(
            [{"country": c or "CN", "count": n} for c, n in by_country],
            key=lambda x: -x["count"],
        ),
        "ordersByStatus": [{"status": s, "count": n} for s, n in by_status],
        "series": series,
        "operator": admin.name,
        "opsRole": admin.ops_role or "super",
        "kycQueue": kyc_queue,
        "loadQueue": load_queue,
        "liveOrders": live_orders,
    }


@router.get("/admin/users")
def users(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(User)).all()
    return {
        "items": [
            {
                "id": u.id,
                "role": u.role,
                "name": u.name,
                "phone": u.phone,
                "country": u.country,
                "kycStatus": u.kyc_status,
                "credit": u.credit,
                "blacklisted": u.blacklisted,
                "disabled": u.disabled,
                "company": _company(db, u.id),
            }
            for u in rows
        ]
    }


class FlagBody(BaseModel):
    disabled: bool | None = None


@router.post("/admin/users/{user_id}")
def patch_user(
    user_id: str,
    body: FlagBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.disabled is not None:
        u.disabled = body.disabled
    _audit(db, admin, "user.patch", user_id)
    return {"ok": True, "disabled": u.disabled}


@router.get("/admin/kyc")
def kyc_queue(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    users = db.scalars(select(User).where(User.kyc_status.in_(["pending", "rejected"]))).all()
    creds = db.scalars(select(Credential)).all()
    by_user: dict[str, list[dict]] = {}
    for c in creds:
        extra = {}
        if c.extra_json:
            try:
                extra = json.loads(c.extra_json)
            except json.JSONDecodeError:
                extra = {}
        by_user.setdefault(c.user_id, []).append(
            {
                "id": c.id,
                "kind": c.kind,
                "status": c.status,
                "expiresAt": c.expires_at,
                "note": c.note,
                "fileUrl": c.file_url,
                "extra": extra,
            }
        )
    items = []
    for u in users:
        shipper = db.get(ShipperProfile, u.id)
        driver = db.get(DriverProfile, u.id)
        items.append(
            {
                "id": u.id,
                "name": u.name,
                "role": u.role,
                "phone": u.phone,
                "kycStatus": u.kyc_status,
                "company": shipper.company if shipper else "",
                "kind": shipper.kind if shipper else "",
                "greenCardNo": driver.green_card_no if driver else "",
                "greenCardExpires": driver.green_card_expires if driver else "",
                "customs": driver.customs if driver else "",
                "credentials": by_user.get(u.id, []),
            }
        )
    items.sort(key=lambda x: (0 if x["kycStatus"] == "pending" else 1, 0 if x["id"] == "usr_shipper_11" else 1, x["name"]))
    return {"users": items, "credentials": [c for rows in by_user.values() for c in rows]}


class ReviewBody(BaseModel):
    passFlag: bool
    reason: str = ""


@router.post("/admin/kyc/{user_id}")
def review_kyc(
    user_id: str,
    body: ReviewBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not body.passFlag and not body.reason.strip():
        raise HTTPException(status_code=400, detail="驳回必须填写原因")
    u.kyc_status = "approved" if body.passFlag else "rejected"
    for c in db.scalars(select(Credential).where(Credential.user_id == user_id)).all():
        c.status = u.kyc_status
        c.note = body.reason
    _audit(db, admin, "kyc.review", user_id)
    logger.info("资质审核完成 admin=%s user=%s status=%s", admin.id, user_id, u.kyc_status)
    return {"status": u.kyc_status}


@router.get("/admin/loads")
def admin_loads(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Load).order_by(Load.created_at.desc())).all()
    return {
        "items": [
            {
                "id": x.id,
                "origin": x.origin,
                "dest": x.dest,
                "status": x.status,
                "matchMode": x.match_mode,
                "shipperId": x.shipper_id,
                "cargoName": x.cargo_name,
                "weightT": x.weight_t,
                "originCountry": x.origin_country,
                "destCountry": x.dest_country,
                "company": _company(db, x.shipper_id),
                "expectPrice": x.expect_price,
                "grabPrice": x.grab_price,
            }
            for x in rows
        ]
    }


class LoadReviewBody(BaseModel):
    approve: bool
    reason: str = ""


@router.post("/admin/loads/{load_id}/review")
def review_load(
    load_id: str,
    body: LoadReviewBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    load = db.get(Load, load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="货源不存在")
    load.status = "published" if body.approve else "rejected"
    _audit(db, admin, "load.review", load_id)
    return {"status": load.status}


@router.get("/admin/orders")
def admin_orders(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Order).order_by(Order.created_at.desc())).all()
    return {
        "items": [
            {
                "id": o.id,
                "status": o.status,
                "freight": o.freight,
                "shipperId": o.shipper_id,
                "driverId": o.driver_id,
                "shipperName": _name(db, o.shipper_id),
                "driverName": _name(db, o.driver_id),
                "lane": (lambda load: f"{load.origin} → {load.dest}" if load else o.id)(db.get(Load, o.load_id)),
                "matchMode": o.match_mode,
            }
            for o in rows
        ]
    }


@router.get("/admin/deposits")
def admin_deposits(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    accs = db.scalars(select(DepositAccount)).all()
    ledgers = db.scalars(select(DepositLedger).order_by(DepositLedger.id.desc()).limit(80)).all()
    return {
        "accounts": [
            {"userId": a.user_id, "name": _name(db, a.user_id), "available": a.available, "frozen": a.frozen}
            for a in accs
        ],
        "ledgers": [
            {
                "id": x.id,
                "userId": x.user_id,
                "name": _name(db, x.user_id),
                "kind": x.kind,
                "amount": x.amount,
                "channel": x.channel,
                "orderId": x.order_id,
                "status": getattr(x, "status", "ok") or "ok",
                "note": getattr(x, "note", "") or "",
            }
            for x in ledgers
        ],
        "pending": [
            {
                "id": x.id,
                "userId": x.user_id,
                "name": _name(db, x.user_id),
                "amount": x.amount,
                "channel": x.channel,
                "status": x.status,
            }
            for x in ledgers
            if getattr(x, "status", "ok") == "pending"
        ],
    }


@router.get("/admin/disputes")
def admin_disputes(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Dispute)).all()
    return {
        "items": [
            {
                "id": d.id,
                "orderId": d.order_id,
                "openerId": d.opener_id,
                "reason": d.reason,
                "status": d.status,
                "verdict": d.verdict,
                "evidence": json.loads(d.evidence_json or "[]") if getattr(d, "evidence_json", "") else [],
                "reviewStatus": getattr(d, "review_status", "") or "",
            }
            for d in rows
        ]
    }


class DisputeBody(BaseModel):
    liableUserId: str
    verdict: str
    deduct: bool = True


@router.post("/admin/disputes/{dispute_id}/rule")
def rule_dispute(
    dispute_id: str,
    body: DisputeBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    d = db.get(Dispute, dispute_id)
    if d is None:
        raise HTTPException(status_code=404, detail="纠纷不存在")
    d.status = "ruled"
    d.verdict = body.verdict
    liable = db.get(User, body.liableUserId)
    order = db.get(Order, d.order_id)
    if liable and order:
        unfreeze_deposit(db, liable, order.deposit, order.id, deduct=body.deduct)
        add_credit(db, liable, -10, "dispute_lose", order.id)
        order.status = "executed"
    _audit(db, admin, "dispute.rule", dispute_id)
    return {"status": d.status}


@router.get("/admin/blacklist")
def admin_blacklist(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Blacklist)).all()
    return {"items": [{"userId": b.user_id, "name": _name(db, b.user_id), "reason": b.reason} for b in rows]}


class BlackBody(BaseModel):
    userId: str
    reason: str


@router.post("/admin/blacklist")
def add_black(body: BlackBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    u = db.get(User, body.userId)
    if u is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    u.blacklisted = True
    if db.scalar(select(Blacklist).where(Blacklist.user_id == body.userId)) is None:
        db.add(Blacklist(user_id=body.userId, reason=body.reason))
    _audit(db, admin, "blacklist.add", body.userId)
    return {"ok": True}


@router.get("/admin/ports")
def admin_ports(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    ports = db.scalars(select(Port)).all()
    reports = db.scalars(select(PortReport).where(PortReport.approved.is_(False))).all()
    return {
        "ports": [
            {
                "id": p.id,
                "nameZh": p.name_zh,
                "nameEn": p.name_en,
                "nameRu": p.name_ru,
                "status": p.status,
                "waitMin": p.wait_min,
                "country": p.country,
            }
            for p in ports
        ],
        "reports": [
            {"id": r.id, "portId": r.port_id, "status": r.status, "waitMin": r.wait_min, "driverId": r.driver_id}
            for r in reports
        ],
    }


class PortBody(BaseModel):
    status: str
    waitMin: int


@router.post("/admin/ports/{port_id}")
def set_port(port_id: str, body: PortBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    p = db.get(Port, port_id)
    if p is None:
        raise HTTPException(status_code=404, detail="口岸不存在")
    p.status = body.status
    p.wait_min = body.waitMin
    _audit(db, admin, "port.update", port_id)
    return {"status": p.status}


@router.post("/admin/ports/reports/{report_id}")
def approve_report(
    report_id: int,
    body: ReviewBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    r = db.get(PortReport, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="上报不存在")
    r.approved = body.passFlag
    if body.passFlag:
        p = db.get(Port, r.port_id)
        if p:
            p.status = r.status
            p.wait_min = r.wait_min
            p.source = "driver"
            from datetime import datetime

            p.updated_at = datetime.utcnow()
        driver = db.get(User, r.driver_id)
        if driver:
            add_credit(db, driver, 2, "port_report")
            notify(db, driver.id, "port", "口岸上报已采纳", "+2 信用积分")
    _audit(db, admin, "port.report", str(report_id))
    return {"approved": r.approved}


@router.get("/admin/config")
def get_config(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(SysConfig)).all()
    return {"items": {r.key: r.value for r in rows}}


class ConfigBody(BaseModel):
    items: dict[str, str]


@router.put("/admin/config")
def put_config(body: ConfigBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    for k, v in body.items.items():
        row = db.get(SysConfig, k)
        if row:
            row.value = str(v)
        else:
            db.add(SysConfig(key=k, value=str(v)))
    _audit(db, admin, "config.update")
    return {"ok": True}


@router.get("/admin/i18n")
def i18n_admin(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(I18nEntry)).all()
    items = [{"key": r.key, "zh": r.zh, "ru": r.ru, "en": r.en, "kk": r.kk} for r in rows]
    missing = [x["key"] for x in items if not x["ru"] or not x["en"] or not x["kk"]]
    return {"items": items, "missing": missing, "missingCount": len(missing)}


@router.get("/admin/announcements")
def anns(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Announcement)).all()
    return {"items": [{"id": a.id, "title": a.title, "body": a.body, "locale": a.locale, "audience": getattr(a, "audience", "all") or "all"} for a in rows]}


class AnnBody(BaseModel):
    title: str
    body: str
    locale: str = "zh-CN"
    audience: str = "all"


@router.post("/admin/announcements")
def create_ann(body: AnnBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    row = Announcement(id=new_id("ann"), title=body.title, body=body.body, locale=body.locale, audience=body.audience)
    db.add(row)
    _audit(db, admin, "ann.create", row.id)
    from app.models import User as U

    q = select(U)
    if body.audience in ("shipper", "driver"):
        q = q.where(U.role == body.audience)
    for u in db.scalars(q).all():
        notify(db, u.id, "ann", body.title, body.body)
    return {"id": row.id}


@router.get("/admin/audit")
def audit(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all()
    return {
        "items": [
            {"id": x.id, "actorId": x.actor_id, "action": x.action, "target": x.target, "at": x.created_at.isoformat() if x.created_at else None}
            for x in rows
        ]
    }


@router.get("/admin/dashboard.csv")
def dashboard_csv(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> PlainTextResponse:
    data = dashboard(admin, db)
    lines = ["metric,value", f"users,{data['users']}", f"orders,{data['orders']}", f"depositIn,{data['depositIn']}", f"disputesOpen,{data['disputesOpen']}"]
    for x in data.get("series") or []:
        lines.append(f"day_{x['day']},{x['orders']}")
    return PlainTextResponse("\n".join(lines), media_type="text/csv")


class EvidenceBody(BaseModel):
    note: str = ""
    url: str = ""


@router.post("/admin/disputes/{dispute_id}/evidence")
def add_evidence(
    dispute_id: str,
    body: EvidenceBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    d = db.get(Dispute, dispute_id)
    if d is None:
        raise HTTPException(status_code=404, detail="纠纷不存在")
    items = json.loads(d.evidence_json or "[]")
    items.append({"note": body.note, "url": body.url, "by": admin.name})
    d.evidence_json = json.dumps(items, ensure_ascii=False)
    return {"ok": True, "evidence": items}


@router.post("/admin/disputes/{dispute_id}/review")
def review_dispute(dispute_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    if (admin.ops_role or "super") not in ("super",):
        raise HTTPException(status_code=403, detail="仅超管可复核")
    d = db.get(Dispute, dispute_id)
    if d is None:
        raise HTTPException(status_code=404, detail="纠纷不存在")
    d.review_status = "reviewed"
    _audit(db, admin, "dispute.review", dispute_id)
    return {"ok": True}


class RefundBody(BaseModel):
    ledgerId: int


@router.post("/admin/deposits/refund")
def refund(body: RefundBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    try:
        return refund_pay(db, body.ledgerId, admin)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/admin/deposits/{ledger_id}/kaspi")
def kaspi_confirm(ledger_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    from app.rules import confirm_pay

    row = db.get(DepositLedger, ledger_id)
    if row is None:
        raise HTTPException(status_code=404, detail="流水不存在")
    user = db.get(User, row.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    try:
        return confirm_pay(db, user, ledger_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/i18n.csv")
def i18n_csv(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> PlainTextResponse:
    rows = db.scalars(select(I18nEntry)).all()
    lines = ["key,zh,ru,en,kk"]
    missing = 0
    for r in rows:
        if not r.ru or not r.en:
            missing += 1
        def q(v: str) -> str:
            return '"' + (v or "").replace('"', '""') + '"'
        lines.append(",".join([q(r.key), q(r.zh), q(r.ru), q(r.en), q(r.kk)]))
    return PlainTextResponse("\n".join(lines), media_type="text/csv")


class I18nImportBody(BaseModel):
    items: list[dict]


@router.post("/admin/i18n/import")
def i18n_import(body: I18nImportBody, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    n = 0
    for item in body.items:
        key = str(item.get("key") or "")
        if not key:
            continue
        row = db.get(I18nEntry, key)
        if row is None:
            row = I18nEntry(key=key)
            db.add(row)
        row.zh = str(item.get("zh") or row.zh)
        row.ru = str(item.get("ru") or row.ru)
        row.en = str(item.get("en") or row.en)
        row.kk = str(item.get("kk") or row.kk)
        n += 1
    _audit(db, admin, "i18n.import")
    return {"ok": True, "count": n}


@router.get("/admin/i18n/missing")
def i18n_missing(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(I18nEntry)).all()
    missing = [r.key for r in rows if not r.ru or not r.en or not r.kk]
    return {"items": missing, "count": len(missing)}
