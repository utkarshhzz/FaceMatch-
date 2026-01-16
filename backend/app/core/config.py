import os
from typing import Optional,List
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field,validator
import secrets


class Settings(BaseSettings):
    #uses pydantic for validaton and safety
    
    #API configuration
    API_V1_STR: str= "/api/v1"
    PROJECT_NAME: str= "FaceMatch++"
    VERSION: str= "1.0.0"
    DESCRIPTION: str= "Facial recognition and identity verification Platform"
    
    
    #security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    #CORS- resource sharing
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    
    
    # ==================== Database Configuration ====================
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER","localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER","facematch_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD","facematch_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB","facematch_db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT",5432))
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct async PostgreSQL connection string"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
        
    # ==================== Redis Configuration ====================
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection string"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ==================== ML Model Configuration ====================
    
    # Face Detection
    DETECTION_BACKEND: str = "retinaface"  # retinaface, mtcnn
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.9
    
    # Face Recognition
    RECOGNITION_MODEL: str = "arcface"  # arcface, facenet
    EMBEDDING_SIZE: int = 512
    
    # Face Matching
    MATCHING_THRESHOLD: float = 0.6  # Cosine similarity threshold
    FAISS_INDEX_TYPE: str = "Flat"  # Flat, IVF
    FAISS_NPROBE: int = 10
    
    
    # Face Quality Checks
    MIN_FACE_SIZE: int = 80  # Minimum face dimension in pixels
    MAX_BLUR_THRESHOLD: float = 100.0  # Laplacian variance
    MIN_BRIGHTNESS: int = 40
    MAX_BRIGHTNESS: int = 220
    
    # Liveness Detection
    ENABLE_LIVENESS: bool = True
    LIVENESS_THRESHOLD: float = 0.7
    
    # ==================== File Storage ====================
    UPLOAD_DIR: str = "./data/uploads"
    FACES_DIR: str = "./data/faces"
    EMBEDDINGS_DIR: str = "./data/embeddings"
    FAISS_INDEX_PATH: str = "./data/faiss_index.bin"
    
    # ==================== Performance ====================
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 32
    USE_ONNX: bool = True  # Use ONNX runtime for faster inference
    
    # ==================== Rate Limiting ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ==================== Logging ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "./logs/facematch.log"
    
    # ==================== Email Configuration ====================
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "FaceMatch")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    
     # Root Admin (from .env for security)
    ROOT_ADMIN_ID: Optional[str] = None
    ROOT_ADMIN_EMAIL: Optional[str] = None
    ROOT_ADMIN_PASSWORD: Optional[str] = None
    
    
    
    # ==================== Environment ====================
    ENVIRONMENT: str = "development"  # development, staging, production
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    


# Global settings instance
settings = Settings()