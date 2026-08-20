from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from urllib.parse import quote_plus


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Base
    APP_NAME: str = "Sistema de Gestión de Postas"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Base de datos
    DATABASE_URL: str = ""

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sgp_db"
    DB_USER: str = "sgp_user"
    DB_PASSWORD: str = "sgp_password"

    @property
    def DATABASE_URL_RESOLVED(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = "postgresql+asyncpg://" + url[len("postgresql://"):]
            return url
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql+asyncpg://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Seguridad
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str = Field(..., min_length=8)

    # CORS (lista separada por comas)
    CORS_ORIGINS: str = "http://localhost:5173"


settings = Settings()