from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Supplier AP SaaS"
    debug: bool = False
    environment: str = "development"
    api_prefix: str = "/api/v1"
    
    # Database
    database_url: str
    
    # Supabase Auth
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Stripe (leave empty for now)
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    
    # SendGrid (leave empty for now)
    sendgrid_api_key: str = ""
    
    # Sentry (optional)
    sentry_dsn: str = ""
    
    # Freemium Limits
    free_tier_max_invoices_per_month: int = 10
    free_tier_max_users: int = 5
    free_tier_max_suppliers: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()