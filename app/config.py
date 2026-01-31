from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    """Config Settings for the Application."""

    model_config = SettingsConfigDict(env_file="./.env", env_file_encoding="utf-8", case_sensitive=True, extra="allow")

    # Application settings
    APP_NAME: str = "My FastAPI Application"
    API_VERSION: str = "1.0.0"
    DESCRIPTION: str = "This is a sample FastAPI application."
    IS_SWAGGER_ENABLED: bool = True
    ROOT_PATH: str = ""
    FASTAPI_DEBUG: bool = True
    DEBUG: bool = True

    # Database settings
    POSTGRESQL_DB_HOST: str = ""
    POSTGRESQL_DB_PORT: int = 5432
    POSTGRESQL_DB_NAME: str = ""
    POSTGRESQL_DB_USER: str = ""
    POSTGRESQL_DB_PASSWORD: str = ""
    POSTGRESQL_DB_POOL_SIZE: int = 10
    POSTGRESQL_DB_MAX_OVERFLOW: int = 20

    # Encryption settings
    ENCRYPTION_KEY: str = "mysecretkey123"

CONFIG_SETTINGS = Settings()