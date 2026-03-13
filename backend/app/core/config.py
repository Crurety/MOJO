from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MOJO"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_platform_logs"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_API_WIRE: Optional[str] = None
    OPENAI_REASONING_EFFORT: Optional[str] = None
    OPENAI_DISABLE_RESPONSE_STORAGE: bool = False
    OPENAI_CONTEXT_WINDOW: Optional[int] = None

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    STABILITY_API_KEY: Optional[str] = None
    STABILITY_API_BASE: str = "https://api.stability.ai/v1"
    STABILITY_ENGINE: str = "stable-diffusion-xl-1024-v1-0"

    RUNWAY_API_KEY: Optional[str] = None
    RUNWAY_API_BASE: str = "https://api.runwayml.com/v1"

    WECHAT_APP_ID: Optional[str] = None
    WECHAT_MCH_ID: Optional[str] = None
    WECHAT_API_KEY: Optional[str] = None

    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None

    UNIONPAY_MERCHANT_ID: Optional[str] = None
    UNIONPAY_API_KEY: Optional[str] = None

    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = None
    OSS_ENDPOINT: Optional[str] = None

    SERVER_PUBLIC_URL: Optional[str] = None
    ADMIN_INIT_USERNAME: Optional[str] = None
    ADMIN_INIT_PASSWORD: Optional[str] = None
    ADMIN_INIT_EMAIL: Optional[str] = None
    ADMIN_INIT_NICKNAME: str = "Administrator"
    ADMIN_USER_IDS: list[int] = []

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
