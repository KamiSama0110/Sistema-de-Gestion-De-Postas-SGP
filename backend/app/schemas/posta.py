from datetime import time
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from app.models.enums import TipoPostaEnum


class TurnoPostaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    hora_inicio: time
    hora_fin: time
    asp_requeridos: int = 1


class TurnoPostaCreate(TurnoPostaBase):
    asp_requeridos: int = Field(1, ge=1, le=100)

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio == self.hora_fin:
            raise ValueError("La hora de inicio y la hora de fin no pueden ser iguales")
        return self


class TurnoPostaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    asp_requeridos: Optional[int] = Field(None, ge=1, le=100)

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio is None or self.hora_fin is None:
            return self
        if self.hora_inicio == self.hora_fin:
            raise ValueError("La hora de inicio y la hora de fin no pueden ser iguales")
        return self


class TurnoPostaResponse(TurnoPostaBase):
    id: int
    posta_id: int
    cruza_medianoche: bool
    activo: bool

    model_config = {"from_attributes": True}


class PostaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=2000)
    ubicacion: Optional[str] = Field(None, max_length=255)
    tipo: TipoPostaEnum
    observaciones: Optional[str] = Field(None, max_length=2000)

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str):
        if not v.strip():
            raise ValueError("El nombre de la posta no puede estar vacio")
        return v


class PostaCreate(PostaBase):
    turnos: list[TurnoPostaCreate] = []


class PostaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=2000)
    ubicacion: Optional[str] = Field(None, max_length=255)
    tipo: Optional[TipoPostaEnum] = None
    observaciones: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def validar_nombre_no_vacio(self):
        if self.nombre is not None and not self.nombre.strip():
            raise ValueError("El nombre de la posta no puede estar vacio")
        return self


class PostaResponse(PostaBase):
    id: int
    activa: bool
    turnos: list[TurnoPostaResponse] = []

    model_config = {"from_attributes": True}


class PostaListResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoPostaEnum
    activa: bool
    total_turnos: int = 0

    model_config = {"from_attributes": True}


class PaginatedPosta(BaseModel):
    total: int
    page: int
    size: int
    items: list[PostaListResponse]


# --- NUEVO: listado paginado de turnos, independiente de Posta ---
class TurnoPostaListResponse(TurnoPostaBase):
    id: int
    posta_id: int
    posta_nombre: str
    cruza_medianoche: bool
    activo: bool

    model_config = {"from_attributes": True}


class PaginatedTurno(BaseModel):
    total: int
    page: int
    size: int
    items: list[TurnoPostaListResponse]