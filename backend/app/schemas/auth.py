from pydantic import BaseModel, Field, field_validator

from app.utils.validators import validar_password


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., max_length=4096)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(None, max_length=4096)


class CambiarPasswordRequest(BaseModel):
    password_actual: str = Field(..., max_length=100)
    password_nueva: str = Field(..., max_length=100)

    @field_validator("password_nueva")
    @classmethod
    def validar_password_nueva(cls, v: str) -> str:
        return validar_password(v)


class MensajeResponse(BaseModel):
    mensaje: str
