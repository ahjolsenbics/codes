"""领域模型。状态与证件结构对齐开发大纲。"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(32), unique=True)
    country: Mapped[str] = mapped_column(String(8), default="CN")
    locale: Mapped[str] = mapped_column(String(12), default="zh-CN")
    kyc_status: Mapped[str] = mapped_column(String(20), default="pending")
    credit: Mapped[int] = mapped_column(Integer, default=100)
    blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    deposit_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(80), default="")
    chat_strikes: Mapped[int] = mapped_column(Integer, default=0)
    frozen_reason: Mapped[str] = mapped_column(String(120), default="")
    ops_role: Mapped[str] = mapped_column(String(20), default="")
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=True)
    quiet_hours: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    shipper: Mapped["ShipperProfile | None"] = relationship(back_populates="user", uselist=False)
    driver: Mapped["DriverProfile | None"] = relationship(back_populates="user", uselist=False)


class ShipperProfile(Base):
    __tablename__ = "shipper_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))  # enterprise / personal / forwarder
    company: Mapped[str] = mapped_column(String(120), default="")
    user: Mapped[User] = relationship(back_populates="shipper")


class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    nationality: Mapped[str] = mapped_column(String(8), default="CN")
    green_card_no: Mapped[str] = mapped_column(String(40), default="")
    green_card_expires: Mapped[str] = mapped_column(String(20), default="")
    customs: Mapped[str] = mapped_column(String(80), default="")
    user: Mapped[User] = relationship(back_populates="driver")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("driver_profiles.user_id"), index=True)
    plate: Mapped[str] = mapped_column(String(20))
    length_m: Mapped[float] = mapped_column(Float, default=13.0)
    tonnage: Mapped[float] = mapped_column(Float, default=30.0)
    body_type: Mapped[str] = mapped_column(String(24), default="van")
    energy: Mapped[str] = mapped_column(String(16), default="diesel")
    axles: Mapped[int] = mapped_column(Integer, default=6)
    vin: Mapped[str] = mapped_column(String(24), default="")
    brand: Mapped[str] = mapped_column(String(40), default="")
    inspect_expires: Mapped[str] = mapped_column(String(20), default="")
    insurance_expires: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(16), default="active")
    driver: Mapped[DriverProfile] = relationship(back_populates="vehicles")


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    expires_at: Mapped[str] = mapped_column(String(20), default="")
    note: Mapped[str] = mapped_column(String(200), default="")
    file_url: Mapped[str] = mapped_column(String(240), default="")
    extra_json: Mapped[str] = mapped_column(Text, default="")


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    shipper_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    origin: Mapped[str] = mapped_column(String(80))
    origin_country: Mapped[str] = mapped_column(String(8), default="CN")
    dest: Mapped[str] = mapped_column(String(80))
    dest_country: Mapped[str] = mapped_column(String(8), default="KZ")
    load_time: Mapped[str] = mapped_column(String(32))
    cargo_name: Mapped[str] = mapped_column(String(80))
    weight_t: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float] = mapped_column(Float, default=0)
    packing: Mapped[str] = mapped_column(String(40), default="pallet")
    cargo_class: Mapped[str] = mapped_column(String(40), default="general")
    truck_length: Mapped[float] = mapped_column(Float, default=13)
    truck_tonnage: Mapped[float] = mapped_column(Float, default=30)
    receiver_name: Mapped[str] = mapped_column(String(40), default="")
    receiver_phone: Mapped[str] = mapped_column(String(32), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    match_mode: Mapped[str] = mapped_column(String(16), default="bid")
    expect_price: Mapped[int] = mapped_column(Integer, default=0)
    floor_price: Mapped[int] = mapped_column(Integer, default=0)
    grab_price: Mapped[int] = mapped_column(Integer, default=0)
    bid_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(24), index=True)
    photos: Mapped[str] = mapped_column(String(200), default="3")
    photos_json: Mapped[str] = mapped_column(Text, default="[]")
    origin_lat: Mapped[float] = mapped_column(Float, default=0)
    origin_lng: Mapped[float] = mapped_column(Float, default=0)
    dest_lat: Mapped[float] = mapped_column(Float, default=0)
    dest_lng: Mapped[float] = mapped_column(Float, default=0)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    quotes: Mapped[list["Quote"]] = relationship(back_populates="load")
    invites: Mapped[list["AssignInvite"]] = relationship(back_populates="load")


class Quote(Base):
    __tablename__ = "quotes"
    __table_args__ = (UniqueConstraint("load_id", "driver_id", name="uq_quote_driver"),)

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    load_id: Mapped[str] = mapped_column(ForeignKey("loads.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    eta: Mapped[str] = mapped_column(String(40), default="")
    remark: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    load: Mapped[Load] = relationship(back_populates="quotes")


class AssignInvite(Base):
    __tablename__ = "assign_invites"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    load_id: Mapped[str] = mapped_column(ForeignKey("loads.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    load: Mapped[Load] = relationship(back_populates="invites")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    load_id: Mapped[str] = mapped_column(ForeignKey("loads.id"), index=True)
    shipper_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    vehicle_id: Mapped[str] = mapped_column(String(40), default="")
    match_mode: Mapped[str] = mapped_column(String(16))
    freight: Mapped[int] = mapped_column(Integer)
    deposit: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), index=True)
    track_index: Mapped[int] = mapped_column(Integer, default=0)
    grab_hold_id: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class StatusLog(Base):
    __tablename__ = "status_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(40), index=True)
    from_status: Mapped[str] = mapped_column(String(24), default="")
    to_status: Mapped[str] = mapped_column(String(24))
    actor_id: Mapped[str] = mapped_column(String(40))
    actor_role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Waybill(Base):
    __tablename__ = "waybills"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), unique=True)
    load_note: Mapped[str] = mapped_column(Text, default="")
    deliver_note: Mapped[str] = mapped_column(Text, default="")
    sign_photo: Mapped[str] = mapped_column(String(80), default="")
    signed: Mapped[bool] = mapped_column(Boolean, default=False)
    load_photo: Mapped[str] = mapped_column(String(240), default="")
    deliver_photo: Mapped[str] = mapped_column(String(240), default="")
    sign_data: Mapped[str] = mapped_column(Text, default="")


class TrackingPoint(Base):
    __tablename__ = "tracking_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(40), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    load_id: Mapped[str] = mapped_column(String(40), default="")
    order_id: Mapped[str] = mapped_column(String(40), default="")
    shipper_id: Mapped[str] = mapped_column(String(40), index=True)
    driver_id: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    sender_id: Mapped[str] = mapped_column(String(40))
    kind: Mapped[str] = mapped_column(String(16), default="text")
    body: Mapped[str] = mapped_column(Text)
    translated: Mapped[str] = mapped_column(Text, default="")
    risk: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DepositAccount(Base):
    __tablename__ = "deposit_accounts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    available: Mapped[int] = mapped_column(Integer, default=0)
    frozen: Mapped[int] = mapped_column(Integer, default=0)


class DepositLedger(Base):
    __tablename__ = "deposit_ledgers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(40), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(Integer)
    channel: Mapped[str] = mapped_column(String(20), default="")
    order_id: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(20), default="ok")
    note: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class CreditRecord(Base):
    __tablename__ = "credit_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(40), index=True)
    delta: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(80))
    order_id: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(40), index=True)
    from_user: Mapped[str] = mapped_column(String(40))
    to_user: Mapped[str] = mapped_column(String(40))
    stars: Mapped[int] = mapped_column(Integer)
    tags: Mapped[str] = mapped_column(String(120), default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Port(Base):
    __tablename__ = "ports"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name_zh: Mapped[str] = mapped_column(String(80))
    name_ru: Mapped[str] = mapped_column(String(80), default="")
    name_en: Mapped[str] = mapped_column(String(80), default="")
    country: Mapped[str] = mapped_column(String(8))
    corridor: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(24), default="smooth")
    wait_min: Mapped[int] = mapped_column(Integer, default=30)
    source: Mapped[str] = mapped_column(String(40), default="ops")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    lat: Mapped[float] = mapped_column(Float, default=0)
    lng: Mapped[float] = mapped_column(Float, default=0)


class PortReport(Base):
    __tablename__ = "port_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    port_id: Mapped[str] = mapped_column(String(40), index=True)
    driver_id: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(24))
    wait_min: Mapped[int] = mapped_column(Integer, default=0)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_url: Mapped[str] = mapped_column(String(240), default="")
    lat: Mapped[float] = mapped_column(Float, default=0)
    lng: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class EstimateLog(Base):
    __tablename__ = "estimate_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(80))
    dest: Mapped[str] = mapped_column(String(80))
    result_json: Mapped[str] = mapped_column(Text, default="")
    anon_key: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(40), index=True)
    opener_id: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    verdict: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    review_status: Mapped[str] = mapped_column(String(20), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Blacklist(Base):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(40), unique=True)
    reason: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class SysConfig(Base):
    __tablename__ = "sys_configs"

    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    value: Mapped[str] = mapped_column(String(80))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(String(12), default="zh-CN")
    audience: Mapped[str] = mapped_column(String(20), default="all")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class I18nEntry(Base):
    __tablename__ = "i18n_entries"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    zh: Mapped[str] = mapped_column(Text, default="")
    ru: Mapped[str] = mapped_column(Text, default="")
    en: Mapped[str] = mapped_column(Text, default="")
    kk: Mapped[str] = mapped_column(Text, default="")


class GrabHold(Base):
    """抢单后货主确认窗。超时自动成交，窗内取消算货主违约。"""

    __tablename__ = "grab_holds"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    load_id: Mapped[str] = mapped_column(String(40), index=True)
    driver_id: Mapped[str] = mapped_column(String(40), index=True)
    freight: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(40), index=True)
    kind: Mapped[str] = mapped_column(String(24), default="order")
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text, default="")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class EstimateCache(Base):
    __tablename__ = "estimate_caches"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    origin: Mapped[str] = mapped_column(String(80))
    dest: Mapped[str] = mapped_column(String(80))
    truck: Mapped[str] = mapped_column(String(40), default="")
    cargo: Mapped[str] = mapped_column(String(40), default="")
    result_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class LaneSubscribe(Base):
    __tablename__ = "lane_subs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    driver_id: Mapped[str] = mapped_column(String(40), index=True)
    origin: Mapped[str] = mapped_column(String(80))
    dest: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
