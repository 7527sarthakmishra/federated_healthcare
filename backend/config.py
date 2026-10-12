import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Privacy-Preserving Federated Healthcare Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fedhealth-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # SQLite Database
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'federated_health.db')}")
    
    # Fernet Encryption Key for sensitive fields
    # Generated default key or from env
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "b4U9z6o28M4Z-uKxL8X2gP1sZ-5J3B9k6N1Q8a4C7F0=")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Federated Learning Defaults
    DEFAULT_PRIVACY_EPSILON: float = 1.0
    DEFAULT_PRIVACY_DELTA: float = 1e-5
    TOTAL_PRIVACY_BUDGET: float = 10.0

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
