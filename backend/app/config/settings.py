import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Environment & Server
    APP_NAME: str = "AutoReels Enterprise"
    APP_VERSION: str = "2.0.0"
    SPEC_VERSION: str = "2.0 (Free-First Addendum)"
    ENV: str = Field(default="development", description="development | test | staging | production")
    DEBUG: bool = Field(default=True)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Database (MySQL 8.0+ / MariaDB)
    # Default to local MySQL on 127.0.0.1:3306 with autoreels_db
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:@127.0.0.1:3306/autoreels_db",
        description="SQLAlchemy database connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE_SEC: int = 3600
    
    # Redis / Job Queue
    REDIS_URL: str = Field(default="redis://127.0.0.1:6379/0")
    
    # Storage Backend (local | s3 | minio)
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage"))
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "autoreels-assets"
    MINIO_SECURE: bool = False
    
    # Authentication & Cryptography (Spec 10.2 / 10.3)
    JWT_SECRET: str = Field(default="autoreels_enterprise_super_secret_jwt_key_2026_change_in_prod")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access JWT
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # Long-lived rotating refresh token
    MASTER_ENCRYPTION_KEY: str = Field(
        default="0123456789abcdef0123456789abcdef",  # 32-byte key for AES-256-GCM
        description="Master envelope encryption key for tenant API credentials"
    )
    
    # Email / Mailpit (Dev SMTP)
    SMTP_HOST: str = "127.0.0.1"
    SMTP_PORT: int = 1025
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@autoreels.local"
    
    # Free-First Generation Pipeline Defaults
    DEFAULT_PLAN: str = "FREE"
    DEFAULT_MONTHLY_QUOTA: int = 2
    WATERMARK_ENABLED_DEFAULT: bool = True
    DEFAULT_RESOLUTION: str = "720x1280"

settings = Settings()
