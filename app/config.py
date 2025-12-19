from pydantic import BaseSettings  # Changed from pydantic_settings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Security
    secret_key: str
    encryption_key: str
    
    # Proxy Provider
    proxy_provider_api_key: str
    proxy_provider_url: str
    
    # Email
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    
    # Frontend
    frontend_url: str
    
    # Instagram
    session_dir: str = "./sessions"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
