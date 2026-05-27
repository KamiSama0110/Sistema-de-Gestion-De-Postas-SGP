from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "password_actual": "admin1234",
                "password_nueva": "nueva_clave_segura",
            }
        }
    }