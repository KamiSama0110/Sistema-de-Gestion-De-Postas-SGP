from datetime import time
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from app.models.enums import TipoPostaEnum


class TurnoPostaBase(BaseModel):
    nombre: str
    hora_inicio: time
    hora_fin: time
    asp_requeridos: int = 1

    @field_validator("asp_requeridos")
    @classmethod
    def validar_asp_requeridos(cls, v: int) -> int:
        if v < 1:
            raise ValueError("El turno debe requerir al menos un ASP")
        return v

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio > self.hora_fin:
            raise ValueError("La hora de inicio no puede ser posterior a la hora de fin")
        return self


class TurnoPostaCreate(TurnoPostaBase):
    pass


class TurnoPostaUpdate(BaseModel):
    nombre: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    asp_requeridos: Optional[int] = None

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio is None or self.hora_fin is None:
            return self
        if self.hora_inicio > self.hora_fin:
            raise ValueError("La hora de inicio no puede ser posterior a la hora de fin")
        return self


class TurnoPostaResponse(TurnoPostaBase):
    id: int
    posta_id: int
    cruza_medianoche: bool
    activo: bool

    model_config = {"from_attributes": True}


class PostaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    tipo: TipoPostaEnum
    observaciones: Optional[str] = None
    
    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str):
        if not v.strip():
            raise ValueError("El nombre de la posta no puede estar vacio")
        return v


class PostaCreate(PostaBase):
    turnos: list[TurnoPostaCreate] = []


class PostaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    tipo: Optional[TipoPostaEnum] = None
    observaciones: Optional[str] = None


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