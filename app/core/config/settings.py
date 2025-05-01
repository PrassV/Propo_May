from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Deployment configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("PORT", 8000))  # Railway uses PORT
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # API configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Property Management Portal"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "MHO2+beTv9sniyrm5hJWneQWWu9pPj1BR4N/kdG9IyCa1xIKqldHg0hLgpDQlPCWFD2U3jMcQhWPhdxpimUGfA==")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Database
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
        
        # Use JWT_SECRET if SECRET_KEY is not set
        if os.getenv("JWT_SECRET") and self.SECRET_KEY == "MHO2+beTv9sniyrm5hJWneQWWu9pPj1BR4N/kdG9IyCa1xIKqldHg0hLgpDQlPCWFD2U3jMcQhWPhdxpimUGfA==":
            self.SECRET_KEY = os.getenv("JWT_SECRET")

settings = Settings() 