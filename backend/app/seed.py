"""写入多样化 Demo 数据，保证看板与主流程可演示。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Announcement,
    AssignInvite,
    Blacklist,
    Conversation,
    Credential,
    CreditRecord,
    DepositAccount,
    DepositLedger,
    Dispute,
    DriverProfile,
    EstimateCache,
    I18nEntry,
    LaneSubscribe,
    Load,
    Message,
    Notification,
    Order,
    Port,
    PortReport,
    Quote,
    Review,
    ShipperProfile,
    StatusLog,
    SysConfig,
    TrackingPoint,
    User,
    Vehicle,
    Waybill,
    utcnow,
)
from app.rules import city_ll
from app.services import TRACK_ROUTE

logger = logging.getLogger("yunmm")

# 演示账号用人名/公司名，避免 Demo Shipper 这种课程作业观感。
# (姓名, 公司, 主体类型, 国家) — 货主以外籍为主，演示账号赵建军/待审张倩保留。
_SHIPPERS = [
    ("赵建军", "新疆丝路跨境物流有限公司", "enterprise", "CN"),
    ("古丽娜·阿赫梅托娃", "阿拉木图通达货代", "forwarder", "KZ"),
    ("买买提·艾力", "喀什西域进出口有限公司", "enterprise", "CN"),
    ("安娜·库兹涅佐娃", "新西伯利亚欧亚物流", "enterprise", "RU"),
    ("阿斯卡尔·叶先诺夫", "阿斯塔纳公路运贸", "enterprise", "KZ"),
    ("马拉特·伊萨耶夫", "奇姆肯特仓配", "personal", "KZ"),
    ("奥莉加·斯米尔诺娃", "莫斯科东方专线", "forwarder", "RU"),
    ("努尔苏丹·卡里莫夫", "比什凯克口岸物流", "enterprise", "KG"),
    ("叶卡捷琳娜·诺维科娃", "叶卡捷琳堡接货中心", "enterprise", "RU"),
    ("阿依古丽·萨德科娃", "阿拉木图果蔬冷链", "personal", "KZ"),
    ("张倩", "待审货代工作室", "forwarder", "CN"),
]
# 11 名司机里仅保留 1 名汉族（约 9%）。库内存中文音译，界面按语言切换。
_DRIVERS = [
    ("努尔兰·别科夫", "KZ", "霍尔果斯海关"),
    ("叶尔博拉特·努尔拉诺夫", "KZ", "霍尔果斯海关"),
    ("伊万·索科洛夫", "RU", "满洲里海关"),
    ("艾达尔·别科夫", "KZ", "阿拉山口海关"),
    ("努尔兰·卡西莫夫", "KZ", "霍尔果斯海关"),
    ("谢尔盖·奥尔洛夫", "RU", "满洲里海关"),
    ("达尼亚尔·斯马古洛夫", "KZ", "喀什海关"),
    ("阿列克谢·彼得罗夫", "RU", "满洲里海关"),
    ("吴斌", "CN", "伊尔克什坦海关"),
    ("巴克特詹·托列乌奥夫", "KZ", "多斯特克海关"),
    ("德米特里·沃尔科夫", "RU", "乌鲁木齐海关"),
]
_KYC_FILES = {
    "biz": "/kyc/biz.svg",
    "auth": "/kyc/auth.svg",
    "agent": "/kyc/agent.svg",
    "id_card": "/kyc/id.svg",
    "license": "/kyc/license.svg",
    "drive": "/kyc/license.svg",
    "vehicle": "/kyc/vehicle.svg",
    "green_card": "/kyc/green.svg",
    "green": "/kyc/green.svg",
    "road_permit": "/kyc/permit.svg",
    "tir": "/kyc/green.svg",
    "truck_photo": "/kyc/vehicle.svg",
    "business_license": "/kyc/biz.svg",
    "operator_id": "/kyc/agent.svg",
}


def _phone_shipper(country: str, i: int) -> str:
    if i == 1:
        return "+86 13800001001"
    if country == "KZ":
        return f"+7 7270001{i:03d}"
    if country == "RU":
        return f"+7 4950001{i:03d}"
    if country == "KG":
        return f"+996 555001{i:03d}"
    return f"+86 13800001{i:03d}"


def _kyc_file(kind: str) -> str:
    return _KYC_FILES.get(kind, "/kyc/id.svg")


def _kyc_file_ok(url: str) -> bool:
    """货盘封面或缺失的 /files 上传都不能当证件图。"""
    if not url:
        return False
    if url.startswith("/covers/"):
        return False
    if url.startswith("/kyc/"):
        return True
    if url.startswith("/files/"):
        from app.core.storage import upload_root

        name = url.rstrip("/").rsplit("/", 1)[-1]
        path = upload_root() / name
        if not path.is_file():
            return False
        # 过小的占位 PNG 在运营台经常空白，改走证件 SVG
        return path.stat().st_size >= 8 * 1024
    return True
_BRANDS = ["解放 J6P", "东风天龙", "陕汽德龙 X6000", "HOWO T7H", "欧曼 EST"]


def _plate_for(nation: str, i: int) -> str:
    if nation == "KZ":
        return f"0{i % 9 + 1} KG {400 + i:03d}"
    if nation == "RU":
        return f"А {400 + i} 77"
    prefixes = "ABCDEFGHJK"
    return f"新A·{prefixes[i % len(prefixes)]}{800 + i:04d}"


_RECEIVERS = {
    "阿拉木图": ("阿克托雷·仓库", "+7 777 120 4401"),
    "塔什干": ("Рахимов 收货", "+998 90 112 3344"),
    "奥什": ("Ош 货站 阿地力", "+996 555 201 118"),
    "比什凯克": ("Бишкек 物流园", "+996 312 445 020"),
    "阿斯塔纳": ("Астана 冷库值班", "+7 717 265 0911"),
    "奇姆肯特": ("Шымкент 建材仓", "+7 725 234 1180"),
    "塔拉兹": ("Тараз 接货点", "+7 726 245 3302"),
    "新西伯利亚": ("Новосибирск 仓 彼得罗娃", "+7 383 201 4408"),
    "莫斯科": ("Москва 仓 Петрова", "+7 495 120 8831"),
    "多斯特克": ("Достык 换装场", "+7 723 412 0091"),
    "塔尔迪库尔干": ("Талдыкорган 站台", "+7 728 245 1170"),
    "纳рын": ("Нарын 接货", "+996 3522 50112"),
    "安集延": ("Андижан 货场", "+998 74 223 0911"),
    "圣彼得堡": ("СПб 仓 伊万诺夫", "+7 812 320 4410"),
    "喀山": ("Казань 物流园", "+7 843 210 1188"),
    "叶卡捷琳堡": ("Екб 货站", "+7 343 365 2201"),
    "鄂木斯克": ("Омск 接货点", "+7 381 245 0912"),
}
_REMARK_BY_CARGO = {
    "机械零件": "防潮，装卸需叉车，不可叠压",
    "日用百货": "纸箱托盘，禁抛摔",
    "棉纱": "防潮防污，车厢需干燥",
    "电子产品": "防震防静电，禁止重压",
    "建材": "超长件提前沟通，绑扎加固",
    "冷链食品": "全程不断电，厢温 -18℃",
    "汽车配件": "原厂木箱，禁倒置",
    "家具": "直立摆放，禁压顶",
    "钢材": "超长捆扎，装卸需吊具",
    "水果": "通风保鲜，禁与气味货混装",
    "家电": "原厂纸箱直立，禁止倒置",
    "轮胎": "立放码垛，防油污",
    "纺织品": "防潮防霉，车厢保持干燥",
}


def seed_if_empty(db: Session) -> None:
    count = db.scalar(select(func.count(User.id))) or 0
    try:
        if not count:
            _seed(db)
            db.commit()
            logger.info("Demo 数据已写入 users=%s", db.scalar(select(func.count(User.id))))
        polish_demo_identities(db)
        enrich_demo_surfaces(db)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Demo 数据写入失败，已回滚")
        raise


def _seed(db: Session) -> None:
    now = utcnow()
    configs = {
        "bid_close_hours": str(settings.bid_close_hours),
        "shipper_pick_hours": str(settings.shipper_pick_hours),
        "grab_confirm_seconds": str(settings.grab_confirm_seconds),
        "assign_invite_hours": str(settings.assign_invite_hours),
        "assign_max_drivers": str(settings.assign_max_drivers),
        "deposit_cny": str(settings.deposit_cny),
        "late_hours": str(settings.late_hours),
        "port_status_ttl_hours": str(settings.port_status_ttl_hours),
        "driver_active_order_limit": str(settings.driver_active_order_limit),
        "phone_unlock_credit": str(settings.phone_unlock_credit),
        "credit_initial": str(settings.credit_initial),
    }
    for k, v in configs.items():
        db.add(SysConfig(key=k, value=v))

    admin = User(
        id="usr_admin_demo",
        role="admin",
        name="王敏",
        phone="+86 13800001000",
        locale="zh-CN",
        kyc_status="approved",
        credit=100,
    )
    db.add(admin)

    # Postgres 强制外键；SQLite 默认不检查。用户必须先 flush，再写资质/账户。
    shippers: list[User] = []
    shipper_meta: list[tuple[str, str, str, int]] = []
    for i, (name, company, kind, nation) in enumerate(_SHIPPERS, start=1):
        uid = "usr_shipper_demo" if i == 1 else f"usr_shipper_{i:02d}"
        u = User(
            id=uid,
            role="shipper",
            name=name,
            phone=_phone_shipper(nation, i),
            country=nation,
            kyc_status="approved" if i < 10 else "pending",
            credit=100 + i,
        )
        db.add(u)
        shippers.append(u)
        shipper_meta.append((uid, kind, company, i))

    drivers: list[User] = []
    driver_meta: list[tuple[str, str, str, int, bool]] = []
    for i, (name, nation, customs) in enumerate(_DRIVERS, start=1):
        uid = "usr_driver_demo" if i == 1 else f"usr_driver_{i:02d}"
        exempt = nation == "RU"
        u = User(
            id=uid,
            role="driver",
            name=name,
            phone="+86 13900001001" if i == 1 else (f"+7 7010001{i:03d}" if nation != "CN" else f"+86 13900001{i:03d}"),
            country=nation,
            kyc_status="approved" if i < 10 else "rejected",
            credit=118 if i == 1 else 90 + i * 2,
            deposit_exempt=exempt,
        )
        db.add(u)
        drivers.append(u)
        driver_meta.append((uid, nation, customs, i, exempt))

    db.flush()

    for uid, kind, company, i in shipper_meta:
        db.add(ShipperProfile(user_id=uid, kind=kind, company=company))
        db.add(DepositAccount(user_id=uid, available=5000 if i < 9 else 0, frozen=200 if i == 1 else 0))

    for uid, nation, customs, i, exempt in driver_meta:
        db.add(
            DriverProfile(
                user_id=uid,
                nationality=nation,
                green_card_no=f"GC-{i:04d}",
                green_card_expires="2027-06-30",
                customs=customs,
            )
        )
        db.add(DepositAccount(user_id=uid, available=0 if exempt else 3000, frozen=200 if i == 1 else 0))

    db.flush()

    for uid, nation, customs, i, exempt in driver_meta:
        db.add(
            Vehicle(
                id=f"veh_{i:02d}",
                driver_id=uid,
                plate=_plate_for(nation, i),
                length_m=13.5 if i % 2 else 17.5,
                tonnage=32 if i % 2 else 40,
                body_type="reefer" if i % 5 == 0 else "van",
                energy="diesel",
                axles=6 if i % 2 else 8,
                vin=f"LFW{i:04d}XJ{1000 + i}",
                brand=_BRANDS[i % len(_BRANDS)],
                inspect_expires="2027-03-31",
                insurance_expires="2026-12-18",
                status="active",
            )
        )
        for kind in ("id_card", "license", "vehicle", "road_permit", "tir", "green_card", "truck_photo"):
            db.add(
                Credential(
                    id=f"crd_{i:02d}_{kind}",
                    user_id=uid,
                    kind=kind,
                    status="approved" if i < 10 else "pending",
                    expires_at="2027-06-30" if kind == "green_card" else "",
                    file_url=_kyc_file(kind),
                )
            )

    db.add(
        Blacklist(
            user_id="usr_driver_11",
            reason="major_breach",
        )
    )
    drivers[-1].blacklisted = True
    drivers[-1].kyc_status = "rejected"

    ports = [
        ("khorgos", "霍尔果斯", "Хоргос", "Khorgos", "CN", "CN-KZ", "congested", 180, 44.2143, 80.4189),
        ("alashankou", "阿拉山口", "Алашанькоу", "Alashankou", "CN", "CN-KZ", "slow", 90, 45.168, 82.572),
        ("dostyk", "多斯特克", "Достык", "Dostyk", "KZ", "CN-KZ", "smooth", 40, 45.25, 82.48),
        ("manzhouli", "满洲里", "Маньчжурия", "Manzhouli", "CN", "CN-RU", "heavy", 240, 49.598, 117.43),
        ("khorgos_kz", "霍尔果斯（哈方）", "Нұржолы", "Nur Zholy", "KZ", "CN-KZ", "closed", 0, 44.20, 80.39),
        ("irkeshtam", "伊尔克什坦", "Иркештам", "Irkeshtam", "CN", "CN-KG", "unknown", 0, 39.68, 73.91),
    ]
    for pid, zh, ru, en, cty, cor, st, wait, lat, lng in ports:
        db.add(
            Port(
                id=pid,
                name_zh=zh,
                name_ru=ru,
                name_en=en,
                country=cty,
                corridor=cor,
                status=st,
                wait_min=wait,
                source="ops",
                updated_at=now - timedelta(minutes=40),
                lat=lat,
                lng=lng,
            )
        )
    db.flush()
    db.add(PortReport(port_id="khorgos", driver_id="usr_driver_demo", status="congested", wait_min=180, approved=True))

    routes = [
        ("乌鲁木齐", "CN", "阿拉木图", "KZ", "bid"),
        ("乌鲁木齐", "CN", "塔什干", "UZ", "grab"),
        ("喀什", "CN", "奥什", "KG", "assign"),
        ("霍尔果斯", "CN", "阿拉木图", "KZ", "bid"),
        ("乌鲁木齐", "CN", "比什凯克", "KG", "grab"),
        ("奎屯", "CN", "阿斯塔纳", "KZ", "bid"),
        ("库尔勒", "CN", "阿拉木图", "KZ", "bid"),
        ("昌吉", "CN", "奇姆肯特", "KZ", "grab"),
        ("石河子", "CN", "塔拉兹", "KZ", "bid"),
        ("哈密", "CN", "新西伯利亚", "RU", "bid"),
        ("乌鲁木齐", "CN", "莫斯科", "RU", "assign"),
        ("阿拉山口", "CN", "多斯特克", "KZ", "grab"),
        ("伊宁", "CN", "塔尔迪库尔干", "KZ", "bid"),
        ("阿克苏", "CN", "纳рын", "KG", "bid"),
        ("喀什", "CN", "安集延", "UZ", "grab"),
        ("乌鲁木齐", "CN", "阿拉木图", "KZ", "bid"),
        ("乌鲁木齐", "CN", "阿拉木图", "KZ", "grab"),
        ("霍尔果斯", "CN", "阿拉木图", "KZ", "assign"),
        ("乌鲁木齐", "CN", "比什凯克", "KG", "bid"),
        ("喀什", "CN", "奥什", "KG", "bid"),
        ("奎屯", "CN", "阿斯塔纳", "KZ", "grab"),
        ("乌鲁木齐", "CN", "阿拉木图", "KZ", "bid"),
    ]
    cargos = ["机械零件", "日用百货", "棉纱", "电子产品", "建材", "冷链食品", "汽车配件", "家具"]
    statuses_cycle = [
        "matching",
        "matching",
        "published",
        "pending_review",
        "matching",
        "dealt",
        "in_transit",
        "completed",
        "cancelled",
        "dispute",
        "matching",
        "matching",
        "published",
        "matching",
        "completed",
        "matching",
        "wait_load",
        "loading",
        "wait_confirm",
        "matching",
        "draft",
        "matching",
    ]

    loads: list[Load] = []
    for i, ((o, oc, d, dc, mode), st) in enumerate(zip(routes, statuses_cycle), start=1):
        lid = "lod_demo_cn_kz" if i == 1 else f"lod_{i:02d}"
        shipper = shippers[(i - 1) % 10]
        load = Load(
            id=lid,
            shipper_id=shipper.id,
            origin=o,
            origin_country=oc,
            dest=d,
            dest_country=dc,
            load_time=(now + timedelta(days=(i % 5) + 1)).strftime("%Y-%m-%d 08:00"),
            cargo_name=cargos[i % len(cargos)],
            weight_t=12 + (i % 18),
            volume_m3=40 + i,
            packing="pallet",
            cargo_class="reefer" if i % 7 == 0 else "general",
            truck_length=13.5 if i % 2 else 17.5,
            truck_tonnage=32 if i % 2 else 40,
            receiver_name=_RECEIVERS.get(d, (f"{d} 接货人", ""))[0],
            receiver_phone=_RECEIVERS.get(d, ("", f"+7 7770001{i:03d}"))[1],
            remark=_REMARK_BY_CARGO.get(cargos[i % len(cargos)], "按随车清单交接"),
            match_mode=mode,
            expect_price=16000 + i * 300,
            floor_price=14000 + i * 200,
            grab_price=17500 + i * 250,
            bid_deadline=now + timedelta(hours=20),
            status=st if st != "wait_load" else "dealt",
        )
        db.add(load)
        loads.append(load)

    db.flush()

    demo_load = loads[0]
    for j, drv in enumerate(drivers[:4], start=1):
        db.add(
            Quote(
                id=f"quo_demo_{j}",
                load_id=demo_load.id,
                driver_id=drv.id,
                amount=16800 + j * 400,
                eta="36h",
                remark="可走霍尔果斯，预计 36 小时",
                status="active",
            )
        )

    for i, load in enumerate(loads[1:8], start=2):
        if load.match_mode == "bid" and load.status == "matching":
            db.add(
                Quote(
                    id=f"quo_{i}_1",
                    load_id=load.id,
                    driver_id=drivers[i % 10].id,
                    amount=load.expect_price - 200,
                    status="active",
                )
            )
        if load.match_mode == "assign":
            db.add(
                AssignInvite(
                    id=f"inv_{i}",
                    load_id=load.id,
                    driver_id="usr_driver_demo",
                    message="优先走霍尔果斯，请 24 小时内确认",
                    status="pending",
                    expires_at=now + timedelta(hours=20),
                )
            )

    def add_order(oid: str, load: Load, driver: User, status: str, freight: int) -> Order:
        order = Order(
            id=oid,
            load_id=load.id,
            shipper_id=load.shipper_id,
            driver_id=driver.id,
            vehicle_id="veh_01",
            match_mode=load.match_mode,
            freight=freight,
            deposit=200,
            status=status,
            track_index=3 if status == "in_transit" else 0,
        )
        db.add(order)
        db.flush()
        db.add(Waybill(id=f"wb_{oid}", order_id=oid, signed=status == "completed"))
        db.add(
            Conversation(
                id=f"cv_{oid}",
                load_id=load.id,
                order_id=oid,
                shipper_id=load.shipper_id,
                driver_id=driver.id,
            )
        )
        db.add(
            StatusLog(
                order_id=oid,
                from_status="",
                to_status=status,
                actor_id="system",
                actor_role="system",
            )
        )
        if status in ("in_transit", "wait_confirm", "completed"):
            for idx, (lat, lng) in enumerate(TRACK_ROUTE[: 4 if status == "in_transit" else 6]):
                db.add(TrackingPoint(order_id=oid, lat=lat, lng=lng))
        return order

    # 运输中订单：主演示轨迹
    transit_load = next(x for x in loads if x.status == "in_transit")
    add_order("ord_transit_demo", transit_load, drivers[0], "in_transit", 18800)
    db.add(DepositLedger(user_id=transit_load.shipper_id, kind="freeze", amount=200, order_id="ord_transit_demo"))
    db.add(DepositLedger(user_id=drivers[0].id, kind="freeze", amount=200, order_id="ord_transit_demo"))

    completed = next(x for x in loads if x.status == "completed")
    add_order("ord_done_01", completed, drivers[1], "completed", 17200)
    db.add(Review(order_id="ord_done_01", from_user=completed.shipper_id, to_user=drivers[1].id, stars=5, tags="on_time", comment="准时到达，车况干净，配合卸货"))
    db.add(CreditRecord(user_id=drivers[1].id, delta=2, reason="complete_order", order_id="ord_done_01"))

    wait_load = next(x for x in loads if x.id == "lod_17")
    add_order("ord_wait_01", wait_load, drivers[0], "wait_load", 18100)

    loading = next(x for x in loads if x.status == "loading" or x.id == "lod_18")
    loading.status = "dealt"
    add_order("ord_loading_01", loading, drivers[2], "loading", 19000)

    wait_c = next(x for x in loads if x.id == "lod_19")
    add_order("ord_waitc_01", wait_c, drivers[3], "wait_confirm", 17600)

    dispute_load = next(x for x in loads if x.status == "dispute")
    add_order("ord_dispute_01", dispute_load, drivers[4], "dispute", 16500)
    db.add(
        Dispute(
            id="dsp_01",
            order_id="ord_dispute_01",
            opener_id=dispute_load.shipper_id,
            reason="货损，箱体进水",
            status="open",
        )
    )

    db.flush()

    db.add(
        Message(
            conversation_id="cv_ord_transit_demo",
            sender_id="usr_shipper_demo",
            kind="text",
            body="请注意口岸拥堵，霍尔果斯目前排队约 3 小时",
            translated="Обратите внимание на затор на КПП",
        )
    )
    db.add(
        Message(
            conversation_id="cv_ord_transit_demo",
            sender_id="usr_driver_demo",
            kind="text",
            body="已到达霍尔果斯",
            translated="Прибыли в Хоргос",
        )
    )

    db.add(Announcement(id="ann_01", title="Khorgos congestion", body="Expect 3h wait", locale="en-US"))
    db.add(Announcement(id="ann_02", title="霍尔果斯拥堵", body="预计等待 3 小时", locale="zh-CN"))
    db.add(I18nEntry(key="order.transporting", zh="运输中", ru="В пути", en="In transit", kk=""))
    db.add(I18nEntry(key="port.congested", zh="拥堵", ru="Затор", en="Congested", kk=""))
    db.add(CreditRecord(user_id="usr_driver_demo", delta=1, reason="on_time"))
    db.add(DepositLedger(user_id="usr_shipper_demo", kind="pay", amount=5000, channel="wechat"))
    db.add(DepositLedger(user_id="usr_driver_demo", kind="pay", amount=3000, channel="alipay"))


_EXTRA_PARTIES = [
    ("usr_shipper_kz12", "shipper", "萨乌列·努尔加利耶娃", "KZ", "阿拉木图仓配", "enterprise", "+7 7270002012"),
    ("usr_shipper_ru12", "shipper", "帕维尔·莫罗佐夫", "RU", "新西伯利亚接货中心", "enterprise", "+7 4950002012"),
    ("usr_shipper_kz13", "shipper", "阿谢特·茹马巴耶夫", "KZ", "阿斯塔纳公路运贸", "forwarder", "+7 7170002013"),
    ("usr_driver_kz12", "driver", "叶尔兰·萨特巴耶夫", "KZ", "霍尔果斯海关", "", "+7 7010002012"),
    ("usr_driver_ru12", "driver", "尼基塔·库兹涅佐夫", "RU", "满洲里海关", "", "+7 9160002012"),
    ("usr_driver_kg12", "driver", "阿尔曼·托克托古洛夫", "KG", "伊尔克什坦海关", "", "+996 5550002012"),
]


def _ensure_foreign_parties(db: Session, demo_pwd: str) -> None:
    """运营台用户统计补一批哈萨克、俄罗斯、吉尔吉斯账号。"""
    for uid, role, name, nation, extra, kind, phone in _EXTRA_PARTIES:
        user = db.get(User, uid)
        if user is None:
            user = User(
                id=uid,
                role=role,
                name=name,
                phone=phone,
                country=nation,
                kyc_status="approved",
                credit=110,
                password_hash=demo_pwd,
            )
            db.add(user)
            db.flush()
        else:
            user.name = name
            user.country = nation
            user.phone = phone
            if not user.password_hash:
                user.password_hash = demo_pwd
        if role == "shipper":
            profile = db.get(ShipperProfile, uid)
            if profile is None:
                db.add(ShipperProfile(user_id=uid, kind=kind or "enterprise", company=extra))
            else:
                profile.company = extra
                profile.kind = kind or "enterprise"
        else:
            profile = db.get(DriverProfile, uid)
            if profile is None:
                db.add(
                    DriverProfile(
                        user_id=uid,
                        nationality=nation,
                        green_card_no=f"GC-{uid[-2:]}",
                        green_card_expires="2027-06-30",
                        customs=extra,
                    )
                )
            else:
                profile.nationality = nation
                profile.customs = extra
        if db.get(DepositAccount, uid) is None:
            db.add(DepositAccount(user_id=uid, available=2400, frozen=0))


def polish_demo_identities(db: Session) -> None:
    """已有 SQLite 也把占位英文名改成可演示的人名、公司和接货信息。"""
    admin = db.get(User, "usr_admin_demo")
    if admin:
        admin.name = "王敏"
        admin.ops_role = "super"
        if not admin.password_hash:
            from app.rules import hash_password

            admin.password_hash = hash_password("Yunmm@2026")
    extra_cfg = {
        "grab_confirm_seconds": "1800",
        "estimate_cache_days": "7",
        "estimate_anon_limit": "2",
        "rate_base_cnkz": "18",
        "truck_factor_175": "1.15",
        "cargo_factor_reefer": "1.35",
    }
    for k, v in extra_cfg.items():
        row = db.get(SysConfig, k)
        if row is None:
            db.add(SysConfig(key=k, value=v))
        elif k == "grab_confirm_seconds" and row.value in ("30", "0"):
            row.value = "1800"
    from app.rules import hash_password as _hp

    demo_pwd = _hp("Yunmm@2026")
    for i, (name, company, kind, nation) in enumerate(_SHIPPERS, start=1):
        uid = "usr_shipper_demo" if i == 1 else f"usr_shipper_{i:02d}"
        user = db.get(User, uid)
        if user:
            user.name = name
            user.country = nation
            user.phone = _phone_shipper(nation, i)
            if not user.password_hash:
                user.password_hash = demo_pwd
        profile = db.get(ShipperProfile, uid)
        if profile:
            profile.company = company
            profile.kind = kind
    _ensure_foreign_parties(db, demo_pwd)
    for i, (name, nation, customs) in enumerate(_DRIVERS, start=1):
        uid = "usr_driver_demo" if i == 1 else f"usr_driver_{i:02d}"
        user = db.get(User, uid)
        if user:
            user.name = name
            user.country = nation
            if i == 1:
                user.phone = "+86 13900001001"
            elif nation != "CN":
                user.phone = f"+7 7010001{i:03d}"
            else:
                user.phone = f"+86 13900001{i:03d}"
            if not user.password_hash:
                user.password_hash = demo_pwd
        profile = db.get(DriverProfile, uid)
        if profile:
            profile.nationality = nation
            profile.customs = customs
    for load in db.scalars(select(Load)).all():
        recv = _RECEIVERS.get(load.dest)
        if recv:
            load.receiver_name, load.receiver_phone = recv
        remark = _REMARK_BY_CARGO.get(load.cargo_name)
        if remark:
            load.remark = remark
    review = db.scalar(select(Review).where(Review.order_id == "ord_done_01"))
    if review and (not review.comment or review.comment.strip() in {"ok", "OK"}):
        review.comment = "准时到达，车况干净，配合卸货"
    invite = db.scalar(select(AssignInvite).where(AssignInvite.message == "priority lane"))
    if invite:
        invite.message = "优先走霍尔果斯，请 24 小时内确认"
    quote = db.scalar(select(Quote).where(Quote.remark == "cover Khorgos"))
    if quote:
        quote.remark = "可走霍尔果斯，预计 36 小时"
    logger.info("演示账号与货盘文案已按真实人名/接货信息对齐")


def _days_from_now(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")


def _cover_photos(cargo: str) -> list[str]:
    text = cargo or ""
    if "机械" in text:
        return ["/covers/machine.svg", "/covers/building.svg", "/covers/electronics.svg"]
    if "电子" in text or "家电" in text:
        return ["/covers/electronics.svg", "/covers/machine.svg"]
    if "建材" in text or "钢" in text:
        return ["/covers/building.svg", "/covers/machine.svg"]
    if "食品" in text or "果" in text or "冷" in text:
        return ["/covers/food.svg", "/covers/general.svg"]
    if "汽" in text or "轮胎" in text:
        return ["/covers/auto.svg", "/covers/machine.svg"]
    if "纺" in text or "棉" in text:
        return ["/covers/textile.svg", "/covers/general.svg"]
    if "化" in text:
        return ["/covers/chemical.svg", "/covers/building.svg"]
    return ["/covers/general.svg", "/covers/building.svg"]


def _backfill_load_photos(db: Session) -> None:
    for load in db.scalars(select(Load)).all():
        raw = load.photos_json or ""
        if raw.startswith("[") and len(raw) > 4:
            continue
        load.photos_json = json.dumps(_cover_photos(load.cargo_name), ensure_ascii=False)


_EXTRA_LANES = [
    ("乌鲁木齐", "CN", "阿拉木图", "KZ"),
    ("霍尔果斯", "CN", "阿拉木图", "KZ"),
    ("奎屯", "CN", "阿斯塔纳", "KZ"),
    ("库尔勒", "CN", "奇姆肯特", "KZ"),
    ("昌吉", "CN", "塔拉兹", "KZ"),
    ("石河子", "CN", "阿拉木图", "KZ"),
    ("伊宁", "CN", "塔尔迪库尔干", "KZ"),
    ("阿拉山口", "CN", "多斯特克", "KZ"),
    ("喀什", "CN", "奥什", "KG"),
    ("乌鲁木齐", "CN", "比什凯克", "KG"),
    ("阿克苏", "CN", "纳рын", "KG"),
    ("喀什", "CN", "安集延", "UZ"),
    ("乌鲁木齐", "CN", "塔什干", "UZ"),
    ("哈密", "CN", "新西伯利亚", "RU"),
    ("乌鲁木齐", "CN", "莫斯科", "RU"),
    ("乌鲁木齐", "CN", "叶卡捷琳堡", "RU"),
    ("霍尔果斯", "CN", "喀山", "RU"),
    ("奎屯", "CN", "鄂木斯克", "RU"),
    ("乌鲁木齐", "CN", "圣彼得堡", "RU"),
    ("库尔勒", "CN", "阿拉木图", "KZ"),
]
_EXTRA_CARGOS = ["机械零件", "电子产品", "建材", "冷链食品", "汽车配件", "棉纱", "家具", "日用百货", "钢材", "水果", "家电", "轮胎", "纺织品"]
_QUOTE_NOTES = [
    "可走霍尔果斯，预计 36 小时",
    "有 17.5 米厢货，今晚可装",
    "绿卡有效，熟悉阿拉山口换装",
    "冷链不断电，温度可追溯",
    "已订口岸短驳，明早报关",
]


def _ensure_bulk_catalog(db: Session) -> None:
    """把货盘、报价、运单、通知补到可演示的体量，已有库启动时也会补。"""
    _backfill_load_photos(db)
    if db.get(SysConfig, "bulk_market_v2") is not None:
        return
    db.add(SysConfig(key="bulk_market_v2", value="1"))

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    shippers = db.scalars(select(User).where(User.role == "shipper")).all()
    drivers = db.scalars(select(User).where(User.role == "driver", User.blacklisted.is_(False))).all()
    if not shippers or not drivers:
        return
    demo_shipper = next((u for u in shippers if u.id == "usr_shipper_demo"), shippers[0])
    demo_driver = next((u for u in drivers if u.id == "usr_driver_demo"), drivers[0])
    approved_drivers = [u for u in drivers if u.kyc_status == "approved"] or drivers

    extra_loads: list[Load] = []
    statuses = [
        "matching",
        "matching",
        "published",
        "matching",
        "published",
        "matching",
        "pending_review",
        "matching",
        "published",
        "matching",
        "dealt",
        "completed",
        "matching",
        "published",
        "draft",
        "matching",
        "matching",
        "published",
        "matching",
        "cancelled",
    ]
    modes = ["bid", "bid", "grab", "bid", "assign", "grab", "bid", "bid"]
    packings = ["pallet", "carton", "pallet", "crate"]
    for i in range(1, 97):
        lid = f"lod_x{i:03d}"
        if db.get(Load, lid) is not None:
            continue
        o, oc, d, dc = _EXTRA_LANES[(i - 1) % len(_EXTRA_LANES)]
        cargo = _EXTRA_CARGOS[i % len(_EXTRA_CARGOS)]
        mode = modes[i % len(modes)]
        st = statuses[i % len(statuses)]
        if i <= 22:
            owner = demo_shipper
            if i <= 8:
                st, mode = "matching", "bid"
            elif i <= 12:
                st, mode = "published", "grab"
            elif i == 13:
                st, mode = "pending_review", "bid"
            elif i == 14:
                st, mode = "draft", "bid"
            elif i <= 18:
                st, mode = "completed", "bid"
            elif i <= 20:
                st, mode = "dealt", "grab"
            else:
                st, mode = "matching", "assign"
        else:
            owner = shippers[(i - 1) % len(shippers)]
        o_lat, o_lng = city_ll(o)
        d_lat, d_lng = city_ll(d)
        recv = _RECEIVERS.get(d, (f"{d} 接货人", f"+7 7770002{i:03d}"))
        load = Load(
            id=lid,
            shipper_id=owner.id,
            origin=o,
            origin_country=oc,
            dest=d,
            dest_country=dc,
            load_time=(now + timedelta(days=(i % 6) + 1)).strftime("%Y-%m-%d %H:00"),
            cargo_name=cargo,
            weight_t=10 + (i % 22),
            volume_m3=28 + i % 40,
            packing=packings[i % len(packings)],
            cargo_class="reefer" if "冷" in cargo or "果" in cargo else "general",
            truck_length=17.5 if i % 3 == 0 else 13.5,
            truck_tonnage=40 if i % 3 == 0 else 32,
            receiver_name=recv[0],
            receiver_phone=recv[1],
            remark=_REMARK_BY_CARGO.get(cargo, "按随车清单交接，口岸换装提前 2 小时到达"),
            match_mode=mode,
            expect_price=14800 + i * 220,
            floor_price=12800 + i * 160,
            grab_price=16200 + i * 180,
            bid_deadline=now + timedelta(hours=8 + (i % 40)),
            status="dealt" if st in {"wait_load", "loading"} else st,
            photos_json=json.dumps(_cover_photos(cargo), ensure_ascii=False),
            origin_lat=o_lat,
            origin_lng=o_lng,
            dest_lat=d_lat,
            dest_lng=d_lng,
            is_draft=st == "draft",
            created_at=now - timedelta(hours=i * 2),
        )
        db.add(load)
        extra_loads.append(load)
    db.flush()

    qn = 0
    pending_inv = 0
    for load in extra_loads:
        if load.match_mode == "bid" and load.status in {"matching", "published"}:
            seen: set[str] = set()
            for j, drv in enumerate(approved_drivers[: 3 + (qn % 2)]):
                if drv.id in seen:
                    continue
                seen.add(drv.id)
                qn += 1
                db.add(
                    Quote(
                        id=f"quo_x{qn:03d}",
                        load_id=load.id,
                        driver_id=drv.id,
                        amount=max(load.floor_price, load.expect_price - 600 + j * 350),
                        eta=f"{30 + j * 6}h",
                        remark=_QUOTE_NOTES[j % len(_QUOTE_NOTES)],
                        status="active",
                        created_at=now - timedelta(hours=j + 1),
                    )
                )
        if load.match_mode == "assign" and load.status in {"matching", "published"} and pending_inv < 5:
            iid = f"inv_x{load.id[-3:]}"
            if db.get(AssignInvite, iid) is None:
                db.add(
                    AssignInvite(
                        id=iid,
                        load_id=load.id,
                        driver_id=demo_driver.id,
                        message="优先走霍尔果斯，请 24 小时内确认",
                        status="pending",
                        expires_at=now + timedelta(hours=18),
                    )
                )
                pending_inv += 1
    db.flush()

    def add_hist(oid: str, load: Load, driver: User, status: str, freight: int) -> None:
        if db.get(Order, oid) is not None:
            return
        load.status = "completed" if status == "completed" else "dealt"
        db.add(
            Order(
                id=oid,
                load_id=load.id,
                shipper_id=load.shipper_id,
                driver_id=driver.id,
                vehicle_id="veh_01" if driver.id == demo_driver.id else "",
                match_mode=load.match_mode,
                freight=freight,
                deposit=200,
                status=status,
                track_index=5 if status == "completed" else 2,
                created_at=now - timedelta(days=int(oid[-2:]) % 12, hours=3),
            )
        )
        db.flush()
        db.add(Waybill(id=f"wb_{oid}", order_id=oid, signed=status == "completed"))
        db.add(
            Conversation(
                id=f"cv_{oid}",
                load_id=load.id,
                order_id=oid,
                shipper_id=load.shipper_id,
                driver_id=driver.id,
            )
        )
        db.add(StatusLog(order_id=oid, from_status="", to_status=status, actor_id="system", actor_role="system"))
        if status in {"in_transit", "wait_confirm", "completed"}:
            for lat, lng in TRACK_ROUTE[: 6 if status == "completed" else 4]:
                db.add(TrackingPoint(order_id=oid, lat=lat, lng=lng))
        db.add(
            Message(
                conversation_id=f"cv_{oid}",
                sender_id=load.shipper_id,
                kind="text",
                body="请按随车清单清点，口岸换装后拍照确认。",
                translated="Please count by packing list and photo after border transfer.",
            )
        )
        db.add(
            Message(
                conversation_id=f"cv_{oid}",
                sender_id=driver.id,
                kind="text",
                body="收到，已过霍尔果斯，预计今晚抵达。",
                translated="Copy. Passed Khorgos, arriving tonight.",
            )
        )
        if status == "completed":
            db.add(
                Review(
                    order_id=oid,
                    from_user=load.shipper_id,
                    to_user=driver.id,
                    stars=5 if int(oid[-2:]) % 3 else 4,
                    tags="on_time",
                    comment="准时到达，车况干净，配合卸货",
                )
            )

    hist = [x for x in extra_loads if x.status in {"completed", "dealt"}]
    for n, load in enumerate(hist[:16], start=1):
        driver = demo_driver if n % 2 else approved_drivers[n % len(approved_drivers)]
        status = "completed" if load.status == "completed" or n > 4 else ("wait_confirm" if n == 2 else "in_transit")
        if driver.id == demo_driver.id and status in {"in_transit", "wait_load", "loading"}:
            status = "completed"
        add_hist(f"ord_x{n:02d}", load, driver, status, load.expect_price)

    notes = [
        (demo_shipper.id, "quote", "新报价待确认", "乌鲁木齐 → 阿拉木图，3 名司机关注本票，最低已到货主底价附近。"),
        (demo_shipper.id, "order", "待签收运单", "电子运单已生成，请核对件数后签字。"),
        (demo_shipper.id, "port", "霍尔果斯排队回落", "当前约 70 分钟，适合今晚发车。"),
        (demo_shipper.id, "pay", "保证金冻结 ¥200", "成交后冻结，签收完成自动解冻。"),
        (demo_shipper.id, "kyc", "企业证件在有效期内", "营业执照与授权书无需重复提交。"),
        (demo_driver.id, "lane", "奎屯 → 阿斯塔纳 新货源", "13.5 米厢货，抢单价已公布。"),
        (demo_driver.id, "order", "历史运单已评价", "货主给出 5 星，信用 +2。"),
        (demo_driver.id, "docs", "绿卡有效期正常", "乌鲁木齐海关备案至 2027-06-30。"),
        (demo_driver.id, "grab", "指派邀请待处理", "优先走霍尔果斯，请 24 小时内确认。"),
        (demo_driver.id, "port", "阿拉山口通关正常", "换装约 40 分钟，上报可积口岸分。"),
    ]
    existing_n = db.scalar(select(func.count(Notification.id))) or 0
    for i, (uid, kind, title, body) in enumerate(notes, start=1):
        nid = f"nt_b{i:02d}"
        if db.get(Notification, nid) is None:
            db.add(
                Notification(
                    id=nid,
                    user_id=uid,
                    kind=kind,
                    title=title,
                    body=body,
                    read=i > 6,
                    created_at=now - timedelta(hours=i * 2),
                )
            )
    logger.info(
        "演示货盘已扩容 extra_loads=%s notes_before=%s",
        len(extra_loads),
        existing_n,
    )


def enrich_demo_surfaces(db: Session) -> None:
    """已有库补齐车辆档案、通知、线路、待确认支付、举证和看板日期。"""
    covers = ["/covers/machine.svg", "/covers/electronics.svg", "/covers/building.svg", "/covers/food.svg", "/covers/auto.svg"]
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    vehicles = db.scalars(select(Vehicle)).all()
    for idx, v in enumerate(vehicles, start=1):
        driver = db.get(DriverProfile, v.driver_id)
        nation = driver.nationality if driver else "CN"
        if not v.brand:
            v.brand = _BRANDS[idx % len(_BRANDS)]
        if not v.vin:
            v.vin = f"LFW{idx:04d}XJ{1800 + idx}"
        if not v.body_type:
            v.body_type = "reefer" if idx % 5 == 0 else "van"
        if not v.energy:
            v.energy = "diesel"
        if not v.inspect_expires:
            v.inspect_expires = "2027-03-31"
        if not v.insurance_expires:
            v.insurance_expires = "2026-12-18"
        if not v.status:
            v.status = "active"
        if v.plate.startswith("新A·D") and len(v.plate) <= 9:
            v.plate = _plate_for(nation, idx)

    if db.get(Vehicle, "veh_01b") is None:
        db.add(
            Vehicle(
                id="veh_01b",
                driver_id="usr_driver_demo",
                plate="新A·F1906",
                length_m=17.5,
                tonnage=40,
                body_type="van",
                energy="diesel",
                axles=8,
                vin="LFW0001XJ1906",
                brand="陕汽德龙 X6000",
                inspect_expires="2027-01-12",
                insurance_expires="2026-11-30",
                status="active",
            )
        )

    if db.get(Notification, "nt_01") is None:
        notes = [
            ("usr_driver_demo", "order", "库尔勒 → 阿拉木图 运输中", "已过霍尔果斯，预计今晚抵达阿拉木图货站。"),
            ("usr_driver_demo", "docs", "绿卡有效期正常", "乌鲁木齐海关备案至 2027-06-30，续期入口在资质中心。"),
            ("usr_driver_demo", "port", "霍尔果斯排队回落", "当前约 70 分钟，上报可积口岸分。"),
            ("usr_driver_demo", "lane", "乌鲁木齐 → 阿拉木图 新货源", "13.5 米厢货，抢单价 ¥18,500。"),
            ("usr_shipper_demo", "grab", "司机已抢单，请在 30 分钟内确认", "乌鲁木齐 → 阿拉木图，努尔兰·别科夫 · 信用 120。"),
            ("usr_shipper_demo", "order", "电子运单待签收", "ord_waitc_01 已送达，请核对件数后签字。"),
            ("usr_shipper_demo", "pay", "保证金冻结 ¥200", "成交单 ord_transit_demo，解冻随签收完成。"),
        ]
        for i, (uid, kind, title, body) in enumerate(notes, start=1):
            db.add(
                Notification(
                    id=f"nt_{i:02d}",
                    user_id=uid,
                    kind=kind,
                    title=title,
                    body=body,
                    read=i > 4,
                    created_at=now - timedelta(hours=i * 3),
                )
            )

    if db.scalar(select(func.count(LaneSubscribe.id))) == 0:
        for i, (origin, dest) in enumerate(
            [("乌鲁木齐", "阿拉木图"), ("库尔勒", "阿拉木图"), ("霍尔果斯", "阿拉木图")],
            start=1,
        ):
            db.add(LaneSubscribe(id=f"ln_{i:02d}", driver_id="usr_driver_demo", origin=origin, dest=dest))

    pending = db.scalar(select(func.count(DepositLedger.id)).where(DepositLedger.status == "pending")) or 0
    if pending == 0:
        db.add(
            DepositLedger(
                user_id="usr_shipper_02",
                kind="pay",
                amount=2000,
                channel="kaspi",
                status="pending",
                note="Kaspi Gold 待人工核对",
            )
        )
        db.add(
            DepositLedger(
                user_id="usr_driver_03",
                kind="pay",
                amount=800,
                channel="kaspi",
                status="pending",
                note="哈萨克司机保证金，待确认",
            )
        )

    dispute = db.get(Dispute, "dsp_01")
    if dispute:
        try:
            ev = json.loads(dispute.evidence_json or "[]")
        except json.JSONDecodeError:
            ev = []
        if not any((x.get("note") or x.get("url")) for x in ev if isinstance(x, dict)):
            dispute.evidence_json = json.dumps(
                [
                    {"note": "箱体进水照片，底部托盘受潮", "url": "/covers/building.svg", "by": "赵建军"},
                    {"note": "装货时车厢干燥，霍尔果斯换装后发现", "url": "/covers/machine.svg", "by": "谢尔盖·奥尔洛夫"},
                    {"note": "随车温度记录 4 月 2 日 02:18 异常跳变", "url": "/covers/electronics.svg", "by": "王敏"},
                ],
                ensure_ascii=False,
            )

    note5 = db.get(Notification, "nt_05")
    if note5 and note5.body and "马卫东" in note5.body:
        note5.body = note5.body.replace("马卫东", "努尔兰·别科夫").replace("Нұрлан Беков", "努尔兰·别科夫")

    for c in db.scalars(select(Credential)).all():
        if not _kyc_file_ok(c.file_url):
            c.file_url = _kyc_file(c.kind)
        if c.kind == "green_card" and not c.expires_at:
            c.expires_at = "2027-06-30"

    def _ensure_creds(user_id: str, kinds: tuple[str, ...], status: str) -> None:
        existing = {c.kind: c for c in db.scalars(select(Credential).where(Credential.user_id == user_id)).all()}
        for kind in kinds:
            row = existing.get(kind)
            if row is None:
                db.add(
                    Credential(
                        id=f"crd_{user_id.replace('usr_', '')}_{kind}"[:40],
                        user_id=user_id,
                        kind=kind,
                        status=status,
                        file_url=_kyc_file(kind),
                    )
                )
            else:
                if not _kyc_file_ok(row.file_url):
                    row.file_url = _kyc_file(kind)

    for i, (_name, _nation, _customs) in enumerate(_DRIVERS, start=1):
        uid = "usr_driver_demo" if i == 1 else f"usr_driver_{i:02d}"
        status = "rejected" if i == 11 else ("pending" if i >= 10 else "approved")
        _ensure_creds(uid, ("id_card", "license", "vehicle", "green_card"), status)

    pending_shipper = db.get(User, "usr_shipper_11")
    if pending_shipper:
        _ensure_creds(pending_shipper.id, ("business_license", "operator_id"), pending_shipper.kyc_status or "pending")
        keep = {"business_license", "operator_id"}
        for c in db.scalars(select(Credential).where(Credential.user_id == pending_shipper.id)).all():
            if c.kind in keep:
                c.file_url = _kyc_file(c.kind)
                if pending_shipper.kyc_status == "pending" and c.status == "rejected":
                    c.status = "pending"
            elif c.kind in {"biz", "auth", "agent"}:
                db.delete(c)
        if pending_shipper.kyc_status == "rejected":
            pending_shipper.kyc_status = "pending"
    other_pending = db.get(User, "usr_shipper_10")
    if other_pending:
        _ensure_creds(other_pending.id, ("biz", "agent"), other_pending.kyc_status or "pending")

    profile2 = db.get(DriverProfile, "usr_driver_02")
    if profile2:
        profile2.green_card_expires = _days_from_now(18)
        cred = db.scalar(select(Credential).where(Credential.user_id == "usr_driver_02", Credential.kind == "green_card"))
        if cred:
            cred.expires_at = profile2.green_card_expires

    shipper_kinds = ("biz", "agent", "auth")
    shipper = db.get(User, "usr_shipper_demo")
    if shipper and db.scalar(select(func.count(Credential.id)).where(Credential.user_id == shipper.id)) == 0:
        for kind in shipper_kinds:
            db.add(
                Credential(
                    id=f"crd_sp_{kind}",
                    user_id=shipper.id,
                    kind=kind,
                    status="approved",
                    file_url=_kyc_file(kind),
                )
            )

    orders = db.scalars(select(Order)).all()
    for i, order in enumerate(orders):
        order.created_at = now - timedelta(days=i % 7, hours=(i * 3) % 20)

    wb = db.scalar(select(Waybill).where(Waybill.order_id == "ord_transit_demo"))
    if wb:
        if not wb.load_photo:
            wb.load_photo = "/covers/machine.svg"
        if not wb.deliver_photo:
            wb.deliver_photo = "/covers/building.svg"

    report = db.scalar(select(PortReport).where(PortReport.port_id == "khorgos"))
    if report:
        if not report.photo_url:
            report.photo_url = "/covers/building.svg"
        if not report.lat:
            report.lat, report.lng = 44.2143, 80.4189
    if db.scalar(select(func.count(PortReport.id))) < 3:
        db.add(
            PortReport(
                port_id="alashankou",
                driver_id="usr_driver_demo",
                status="slow",
                wait_min=95,
                approved=True,
                photo_url="/covers/food.svg",
                lat=45.168,
                lng=82.572,
            )
        )
        db.add(
            PortReport(
                port_id="dostyk",
                driver_id="usr_driver_03",
                status="smooth",
                wait_min=35,
                approved=False,
                photo_url="/covers/auto.svg",
                lat=45.25,
                lng=82.48,
            )
        )

    extra_i18n = [
        ("order.wait_load", "待装货", "Ожидание погрузки", "Awaiting load", "Жүк күту"),
        ("order.in_transit", "运输中", "В пути", "In transit", "Жолда"),
        ("port.stale", "待更新", "", "Needs update", ""),
        ("pay.kaspi", "Kaspi", "Kaspi", "Kaspi", "Kaspi"),
    ]
    for key, zh, ru, en, kk in extra_i18n:
        row = db.get(I18nEntry, key)
        if row is None:
            db.add(I18nEntry(key=key, zh=zh, ru=ru, en=en, kk=kk))

    if db.get(EstimateCache, "est_urumqi_almaty") is None:
        db.add(
            EstimateCache(
                id="est_urumqi_almaty",
                origin="乌鲁木齐",
                dest="阿拉木图",
                truck="13.5x32",
                cargo="general",
                result_json=json.dumps(
                    {"totalKm": 860, "domesticKm": 670, "borderKm": 28, "foreignKm": 162, "hours": 18, "feeLow": 15400, "feeHigh": 19800, "port": "霍尔果斯"},
                    ensure_ascii=False,
                ),
            )
        )

    _ensure_bulk_catalog(db)
    logger.info(
        "演示表面数据已补齐 vehicles=%s notes=%s loads=%s orders=%s",
        db.scalar(select(func.count(Vehicle.id))),
        db.scalar(select(func.count(Notification.id))),
        db.scalar(select(func.count(Load.id))),
        db.scalar(select(func.count(Order.id))),
    )

