"""
Application configuration.

Concept: "Settings" is a Pydantic model that reads values from environment
variables (and a .env file). Each attribute here becomes a setting the whole
app can use via `settings.XYZ`.

Key idea — pydantic-settings field matching:
    A field named `JWT_SECRET_KEY` looks for an env var called `JWT_SECRET_KEY`.
    We also add aliases (validation_alias) so that the *existing* .env variable
    names like SECRET_KEY keep working. Without this, the app would crash on
    startup because a required field was missing.

`Field(..., ...)` — the `...` (Ellipsis) means "REQUIRED, no default".
Give it a default value (e.g. Field("localhost")) and it becomes optional.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Tells Pydantic: read a file named ".env", treat unknown keys as ignored.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---------- App ----------
    APP_NAME: str = "FaceMatch"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_V1_PREFIX: str = "/api/v1"

    # Which origins may call our API (frontend dev server, etc.)
    # Comma-separated string -> parsed into a list below.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ---------- Security / JWT ----------
    # IMPORTANT: alias so the existing .env variable `SECRET_KEY` is accepted.
    # min_length=32 keeps the key reasonably strong.
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-please-use-32-chars",
        min_length=32,
        validation_alias="SECRET_KEY",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days — friendly for a demo app
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------- PostgreSQL ----------
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "facematch_db"
    POSTGRES_USER: str = "facematch_user"
    POSTGRES_PASSWORD: str = "facematch_password"

    # ---------- Redis (optional — app still works without it) ----------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # ---------- Email (optional for core features — defaults avoid startup crash) ----------
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@facematch.local"
    SMTP_FROM_NAME: str = "FaceMatch System"
    ADMIN_EMAIL: str = "admin@example.com"

    # ---------- Root admin (auto-created on first startup) ----------
    ROOT_ADMIN_ID: str = "245816470"
    ROOT_ADMIN_EMAIL: str = "admin@facematch.com"
    ROOT_ADMIN_PASSWORD: str = "Admin@123"

    # ---------- Face recognition ----------
    # InsightFace needs a "detection size" — higher = more accurate, slower.
    # MATCHING_THRESHOLD is the cosine-distance cutoff: a *distance* below this
    # counts as the same person. (Distance is LOW when faces are similar.)
    DETECTION_BACKEND: str = "retinaface"
    RECOGNITION_MODEL: str = "arcface"
    MATCHING_THRESHOLD: float = 0.6
    FACE_MATCH_THRESHOLD: float = 0.6
    MAX_FACES_PER_USER: int = 5

    # ---------- File storage ----------
    UPLOAD_DIR: str = "data/uploads"
    TEMP_DIR: str = "data/temp"
    MAX_FILE_SIZE_MB: int = 10

    THREAD_POOL_WORKERS: int = 4

    # ---------- Derived properties ----------
    @property
    def DATABASE_URL(self) -> str:
        """Builds the async Postgres connection string.

        Example: postgresql+asyncpg://user:pass@host:5432/db
        The `+asyncpg` part tells SQLAlchemy to use the asyncpg driver.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Sync version of the URL — used by the standalone reset-password
        script (which is simpler to run synchronously). psycopg2 driver."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Turn 'http://a,http://b' into ['http://a','http://b']."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cache one Settings instance for the whole process.
    `@lru_cache` = "remember the result so we don't re-read .env every call."
    """
    return Settings()


# Eager singleton — imported everywhere as `from app.core.config import settings`.
settings = get_settings()
