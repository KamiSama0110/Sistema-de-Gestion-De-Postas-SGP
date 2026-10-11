from pydantic import BaseModel, field_validator

from app.utils.validators import validar_password


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def validar_password_nueva(cls, v: str) -> str:
        return validar_password(v)


class MensajeResponse(BaseModel):
    mensaje: str
