"""跨境公路货运撮合平台 Demo API。"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.api import admin, auth, chat, extra, files, health, loads, orders
from app.core.config import settings
from app.core.db import SessionLocal, engine, ensure_schema
from app.core.logging import setup_logging
from app.core.storage import upload_root
from app.models import Base
from app.seed import seed_if_empty

setup_logging()
logger = logging.getLogger("yunmm")


def _boot_database() -> None:
    last_error: OperationalError | None = None
    for attempt in range(1, 16):
        try:
            Base.metadata.create_all(bind=engine)
            ensure_schema()
            upload_root()
            db = SessionLocal()
            try:
                seed_if_empty(db)
            finally:
                db.close()
            return
        except OperationalError as exc:
            last_error = exc
            logger.warning("数据库尚未就绪 attempt=%s", attempt)
            time.sleep(2)
    if last_error is not None:
        raise last_error


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _boot_database()
    logger.info("服务启动 name=%s env=%s db=%s", settings.app_name, settings.env, settings.database_url)
    yield


app = FastAPI(title="YunMM Demo API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(health.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(files.router, prefix=prefix)
app.include_router(loads.router, prefix=prefix)
app.include_router(orders.router, prefix=prefix)
app.include_router(chat.router, prefix=prefix)
app.include_router(extra.router, prefix=prefix)
app.include_router(admin.router, prefix=prefix)
app.mount("/files", StaticFiles(directory=str(upload_root())), name="files")

_kyc_dir = next(
    (
        path
        for path in (
            Path(__file__).resolve().parents[2] / "apps" / "admin" / "public" / "kyc",
            Path(__file__).resolve().parent / "static" / "kyc",
            Path("/app/kyc"),
        )
        if path.is_dir()
    ),
    None,
)
if _kyc_dir is not None:
    app.mount("/kyc", StaticFiles(directory=str(_kyc_dir)), name="kyc")

_web_dir = next(
    (
        path
        for path in (
            Path(settings.web_dir) if settings.web_dir else None,
            Path("/app/web"),
            Path(__file__).resolve().parents[2] / "apps" / "admin" / "dist",
        )
        if path is not None and (path / "index.html").is_file()
    ),
    None,
)
if _web_dir is not None:
    _web_root = _web_dir.resolve()
    logger.info("托管前端静态站 web=%s", _web_root)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        candidate = (_web_root / full_path).resolve()
        try:
            candidate.relative_to(_web_root)
        except ValueError:
            return FileResponse(_web_root / "index.html")
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_web_root / "index.html")
