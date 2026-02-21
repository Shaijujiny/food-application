from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Config Settings for the Application."""

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    # ==========================================
    # Application Settings
    # ==========================================
    APP_NAME: str = "My FastAPI Application"
    PROJECT_NAME: str = "my_fastapi_project"  # Used for JWT issuer
    API_VERSION: str = "1.0.0"
    DESCRIPTION: str = "This is a sample FastAPI application."
    IS_SWAGGER_ENABLED: bool = True
    ROOT_PATH: str = ""
    FASTAPI_DEBUG: bool = True
    DEBUG: bool = True


    # ==========================================
    # Database Settings
    # ==========================================
    POSTGRESQL_DB_HOST: str = "localhost"
    POSTGRESQL_DB_PORT: int = 5432
    POSTGRESQL_DB_NAME: str = "food"
    POSTGRESQL_DB_USER: str = "postgres"
    POSTGRESQL_DB_PASSWORD: str = "postgres"
    POSTGRESQL_DB_POOL_SIZE: int = 10
    POSTGRESQL_DB_MAX_OVERFLOW: int = 20


    # ==========================================
    # Redis Settings
    # ==========================================
    REDIS_DB_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASS: str ="YOURPASSWORD"
    SSL_CA_CERTS: str | None = None


    # ==========================================
    # JWT Settings
    # ==========================================
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    APP_JWT_PRIVATE_KEY: str = ""
    APP_JWT_PUBLIC_KEY: str = ""


    # ==========================================
    # Security / Encryption
    # ==========================================
    ENCRYPTION_KEY: str = "mysecretkey123"
    ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = "api"


    # ==========================================
    # CORS Settings
    # ==========================================
    BACKEND_CORS_ORIGINS: List[str] = ["*"]


CONFIG_SETTINGS = Settings()