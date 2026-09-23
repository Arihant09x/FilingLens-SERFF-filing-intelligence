# app/core/config.py
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
# Resolve env files from both the backend directory and the repo root.
# The project currently stores the live DB/Redis secrets in backend/.env, while
# older setups keep them at the repo root. Load both, with backend/.env taking
# precedence when it exists.
BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
BACKEND_ENV_FILE = BACKEND_DIR / ".env"
REPO_ENV_FILE = REPO_ROOT / ".env"
ENV_FILES = [BACKEND_ENV_FILE, REPO_ENV_FILE]


class Settings(BaseSettings):
    # These names must match the KEYS in your .env (case-insensitive)
    app_name: str = "PDF-Extraction-Platform"
    environment: str

    database_url: str
    redis_url: str 
    jwt_secret: str = Field(validation_alias="SECRET_KEY")
    jwt_access_expire_minutes: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    processing_stale_minutes: int = 15

    cors_origins: list[str] = ["http://localhost:5173"]
    max_upload_size_mb: int = 50

    storage_backend: str = "local"
    local_storage_path: str = "./storage"
    s3_bucket: str = ""
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        # If .env has a JSON list, pydantic already gives us a list.
        # If .env has "a,b,c", split on commas.
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                import json
                return json.loads(value)
            return [o.strip() for o in value.split(",") if o.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 👇 module-level instance so `from app.core.config import settings` works
settings = get_settings()