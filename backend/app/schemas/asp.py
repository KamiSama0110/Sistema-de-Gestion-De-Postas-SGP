from datetime import date, datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from app.models.enums import (
    SexoEnum,
    EscolaridadEnum,
    EstadoASPEnum,
)


class ASPBase(BaseModel):
    ci: str
    nombre: str
    apellidos: str
    fecha_nacimiento: date
    sexo: SexoEnum
    nivel_escolaridad: EscolaridadEnum
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_ingreso: date
    cargo_id: int
    observaciones: Optional[str] = None

    @field_validator("ci")
    @classmethod
    def validar_ci(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 11:
            raise ValueError("El CI debe tener exactamente 11 dígitos numéricos")
        return v

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, v: date, info) -> date:
        fecha_nacimiento = info.data.get("fecha_nacimiento")
        if fecha_nacimiento and v < fecha_nacimiento:
            raise ValueError("La fecha de ingreso no puede ser anterior al nacimiento")
        return v


class ASPCreate(ASPBase):
    pass


class ASPUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[SexoEnum] = None
    nivel_escolaridad: Optional[EscolaridadEnum] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    cargo_id: Optional[int] = None
    observaciones: Optional[str] = None


class ASPCambiarEstado(BaseModel):
    estado: EstadoASPEnum
    observacion: Optional[str] = None


class ASPResponse(ASPBase):
    id: int
    estado: EstadoASPEnum
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class ASPListResponse(BaseModel):
    id: int
    ci: str
    nombre: str
    apellidos: str
    cargo_id: int
    estado: EstadoASPEnum

    model_config = {"from_attributes": True}


class PaginatedASP(BaseModel):
    total: int
    page: int
    size: int
    items: list[ASPListResponse]