from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")
    
    APP_NAME:str="FaceMatch"
    APP_ENV:str="development"
    APP_DEBUG:bool=True
    APP_V1_PREFIX:str="/api/v1"
    
    JWT_SECRET_KEY:str= Field(...,min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "facematch_db"
    POSTGRES_USER: str = "facematch_user"
    POSTGRES_PASSWORD: str = "facematch_password"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "FaceMatch System"
    ADMIN_EMAIL: str
    
    
    UPLOAD_DIR: str = "data/uploads"
    TEMP_DIR: str = "data/temp"
    MAX_FILE_SIZE_MB: int = 10

    FACE_DETECTION_THRESHOLD: float = 0.6
    FACE_MATCH_THRESHOLD: float = 0.6
    MAX_FACES_PER_USER: int = 5

    THREAD_POOL_WORKERS: int = 4
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    
@lru_cache
def get_settings()-> Settings:
    return Settings()
    
settings=get_settings()