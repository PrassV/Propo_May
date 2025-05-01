from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
import logging
import secrets

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Deployment configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("PORT", 8000))  # Railway uses PORT
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Frontend URL for redirects (used by Supabase email templates)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # API configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Property Management Portal"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase - Primary data access method for this application
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Database - DEPRECATED: This app now uses Supabase for all data access
    # This is kept for backward compatibility but should not be used for new code
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    
    # Email
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If SUPABASE_KEY is empty but SUPABASE_ANON_KEY exists, use that
        if not self.SUPABASE_KEY and os.getenv("SUPABASE_ANON_KEY"):
            self.SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
        
        # Generate a random secret key if not provided
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                # Log a warning in production but still provide a random key
                logger.warning(
                    "No SECRET_KEY or JWT_SECRET provided in production environment! "
                    "Using a randomly generated key, but this will change on restart. "
                    "Please set JWT_SECRET in environment variables."
                )
            self.SECRET_KEY = secrets.token_hex(32)

settings = Settings() 