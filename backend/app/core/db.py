"""SQLAlchemy 引擎。默认 SQLite，可用 DATABASE_URL 切到 Postgres。"""

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger("yunmm")

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine_kwargs: dict = {
    "echo": False,
    "future": True,
    "connect_args": connect_args,
}
if not settings.database_url.startswith("sqlite"):
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(settings.database_url, **engine_kwargs)
if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _sqlite_enable_fk(dbapi_conn, _connection_record) -> None:
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        from app.rules import tick_rules

        tick_rules(db)
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


_ALTERS: list[tuple[str, str, str]] = [
    ("users", "password_hash", "VARCHAR(80) DEFAULT ''"),
    ("users", "chat_strikes", "INTEGER DEFAULT 0"),
    ("users", "frozen_reason", "VARCHAR(120) DEFAULT ''"),
    ("users", "ops_role", "VARCHAR(20) DEFAULT ''"),
    ("users", "notify_push", "BOOLEAN DEFAULT 1"),
    ("users", "notify_sms", "BOOLEAN DEFAULT 1"),
    ("users", "quiet_hours", "BOOLEAN DEFAULT 0"),
    ("loads", "photos_json", "TEXT DEFAULT '[]'"),
    ("loads", "origin_lat", "FLOAT DEFAULT 0"),
    ("loads", "origin_lng", "FLOAT DEFAULT 0"),
    ("loads", "dest_lat", "FLOAT DEFAULT 0"),
    ("loads", "dest_lng", "FLOAT DEFAULT 0"),
    ("loads", "is_draft", "BOOLEAN DEFAULT 0"),
    ("orders", "grab_hold_id", "VARCHAR(40) DEFAULT ''"),
    ("waybills", "load_photo", "VARCHAR(240) DEFAULT ''"),
    ("waybills", "deliver_photo", "VARCHAR(240) DEFAULT ''"),
    ("waybills", "sign_data", "TEXT DEFAULT ''"),
    ("messages", "read_at", "DATETIME"),
    ("deposit_ledgers", "status", "VARCHAR(20) DEFAULT 'ok'"),
    ("deposit_ledgers", "note", "VARCHAR(120) DEFAULT ''"),
    ("estimate_logs", "result_json", "TEXT DEFAULT ''"),
    ("estimate_logs", "anon_key", "VARCHAR(80) DEFAULT ''"),
    ("disputes", "evidence_json", "TEXT DEFAULT '[]'"),
    ("disputes", "review_status", "VARCHAR(20) DEFAULT ''"),
    ("announcements", "audience", "VARCHAR(20) DEFAULT 'all'"),
    ("port_reports", "photo_url", "VARCHAR(240) DEFAULT ''"),
    ("port_reports", "lat", "FLOAT DEFAULT 0"),
    ("port_reports", "lng", "FLOAT DEFAULT 0"),
    ("credentials", "file_url", "VARCHAR(240) DEFAULT ''"),
    ("credentials", "extra_json", "TEXT DEFAULT ''"),
    ("vehicles", "body_type", "VARCHAR(24) DEFAULT 'van'"),
    ("vehicles", "energy", "VARCHAR(16) DEFAULT 'diesel'"),
    ("vehicles", "axles", "INTEGER DEFAULT 6"),
    ("vehicles", "vin", "VARCHAR(24) DEFAULT ''"),
    ("vehicles", "brand", "VARCHAR(40) DEFAULT ''"),
    ("vehicles", "inspect_expires", "VARCHAR(20) DEFAULT ''"),
    ("vehicles", "insurance_expires", "VARCHAR(20) DEFAULT ''"),
    ("vehicles", "status", "VARCHAR(16) DEFAULT 'active'"),
]


def _column_ddl(ddl: str) -> str:
    """补列语句最初按 SQLite 写，Postgres 不认 DATETIME / BOOLEAN DEFAULT 1。"""
    if settings.database_url.startswith("sqlite"):
        return ddl
    return (
        ddl.replace("DATETIME", "TIMESTAMP")
        .replace("BOOLEAN DEFAULT 1", "BOOLEAN DEFAULT TRUE")
        .replace("BOOLEAN DEFAULT 0", "BOOLEAN DEFAULT FALSE")
    )


def ensure_schema() -> None:
    """已有库不会因 create_all 自动加列，启动时按表补齐字段。"""
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    stmts: list[str] = []
    for table, col, ddl in _ALTERS:
        if table not in tables:
            continue
        cols = {c["name"] for c in insp.get_columns(table)}
        if col not in cols:
            stmts.append(f"ALTER TABLE {table} ADD COLUMN {col} {_column_ddl(ddl)}")
    if not stmts:
        return
    with engine.begin() as conn:
        for sql in stmts:
            conn.execute(text(sql))
    logger.info("已补齐表字段 count=%s", len(stmts))
