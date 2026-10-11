from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.enums import SexoEnum


class FranjaCuadroBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    hora_inicio: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    hora_fin: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    dias_semana: list[int] = Field(..., min_length=1, max_length=7)
    sexo_permitido: SexoEnum
    activa: bool = True

    @field_validator("dias_semana")
    @classmethod
    def validar_dias_semana(cls, v):
        for dia in v:
            if not isinstance(dia, int) or dia < 0 or dia > 6:
                raise ValueError("Los días de la semana deben ser enteros entre 0 (lunes) y 6 (domingo)")
        return v

    @field_validator("hora_fin")
    @classmethod
    def validar_hora_distinta(cls, v, info):
        if "hora_inicio" in info.data and v == info.data["hora_inicio"]:
            raise ValueError("La hora de fin debe ser distinta a la hora de inicio")
        return v


class FranjaCuadroUpdate(BaseModel):
    hora_inicio: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    hora_fin: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    activa: Optional[bool] = None

    @field_validator("hora_fin")
    @classmethod
    def validar_hora_distinta_update(cls, v, info):
        if v is not None and "hora_inicio" in info.data and info.data["hora_inicio"] is not None:
            if v == info.data["hora_inicio"]:
                raise ValueError("La hora de fin debe ser distinta a la hora de inicio")
        return v


class FranjaCuadroResponse(BaseModel):
    id: int
    nombre: str
    hora_inicio: str
    hora_fin: str
    dias_semana: list[int]
    sexo_permitido: SexoEnum
    activa: bool

    model_config = {"from_attributes": True}


class FranjaCuadroListResponse(BaseModel):
    id: int
    nombre: str
    hora_inicio: str
    hora_fin: str
    dias_semana: list[int]
    sexo_permitido: SexoEnum
    activa: bool

    model_config = {"from_attributes": True}