"""运行时配置。业务规则值来自开发大纲，后续由管理后台覆盖。"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Railway 等平台会注入 postgres://，SQLAlchemy + psycopg2 需要 postgresql+psycopg2://。"""
    value = url.strip()
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://") :]
    if value.startswith("postgresql://"):
        value = "postgresql+psycopg2://" + value[len("postgresql://") :]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "yunmm-api"
    env: str = "demo"
    api_prefix: str = "/api/v1"
    cors_origins: str = (
        "http://localhost:5175,http://127.0.0.1:5175,"
        "http://localhost:5180,http://127.0.0.1:5180,"
        "http://localhost:5181,http://127.0.0.1:5181,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )
    database_url: str = "sqlite:///./yunmm_demo.db"
    redis_url: str = "redis://127.0.0.1:6379/0"
    upload_dir: str = "./data/uploads"
    web_dir: str = ""

    @field_validator("database_url", mode="before")
    @classmethod
    def _database_url(cls, value: object) -> object:
        if isinstance(value, str) and value.strip():
            return normalize_database_url(value)
        return value

    # 大纲可配置项（Demo 可压缩时长，含义不变）
    bid_close_hours: int = 24
    shipper_pick_hours: int = 48
    grab_confirm_seconds: int = 1800
    assign_invite_hours: int = 24
    assign_max_drivers: int = 5
    deposit_cny: int = 200
    late_hours: int = 4
    port_status_ttl_hours: int = 2
    driver_active_order_limit: int = 3
    phone_unlock_credit: int = 120
    credit_initial: int = 100

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
