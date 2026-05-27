from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    APP_NAME: str = "Sistema de Gestión de Postas"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Base de datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sgp_db"
    DB_USER: str = "sgp_user"
    DB_PASSWORD: str = "sgp_password"
    #DATABASE_URL: str 

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Seguridad
    SECRET_KEY: str = "clave-segura"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin1234"

    # CORS (lista separada por comas)
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()