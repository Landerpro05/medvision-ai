from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings – replaces Spring's application.properties.
    Values are loaded from environment variables or the .env file.
    """

    # PostgreSQL
    DATABASE_URL: str = "postgresql://medvision:medvision_dev@localhost:5432/medvision"

    # Server
    APP_NAME: str = "medvision-backend"
    APP_PORT: int = 8080

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
