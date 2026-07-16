from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def validar_password_nueva(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña nueva debe tener al menos 8 caracteres")
        return v


class MensajeResponse(BaseModel):
    mensaje: str