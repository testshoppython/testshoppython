from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """OWRE Application settings"""
    
    # App settings
    app_name: str = "OWRE - Premium Storage Solutions"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database settings - SQLite default
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./owre.db")
    
    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]
    
    # Paths
    static_dir: str = "static"
    templates_dir: str = "templates"
    upload_dir: str = "static/uploads"
    
    # i18n settings
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "de")
    supported_languages: list = ["de", "en", "fr", "es", "it"]
    
    # Render.com
    render_deployment: bool = os.getenv("RENDER", "False").lower() == "true"
    
    # Brevo Newsletter
    brevo_api_key: Optional[str] = os.getenv("BREVO_API_KEY")
    
    # Stripe Payments
    stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    stripe_publishable_key: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
