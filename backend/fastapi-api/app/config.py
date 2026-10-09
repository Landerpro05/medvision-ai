from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Los valores se cargan desde variables de entorno o el archivo .env.
    """

    # PostgreSQL – sin valor por defecto para forzar configuración explícita
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    # Server
    APP_NAME: str = "medvision-backend"
    APP_PORT: int = 8080
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Base de datos
    SQL_ECHO: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
