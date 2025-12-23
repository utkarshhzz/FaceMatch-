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
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "facematch_user"
    POSTGRES_PASSWORD: str = "facematch_password"
    POSTGRES_DB: str = "facematch_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct async PostgreSQL connection string"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
        
    # ==================== Redis Configuration ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
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