from pydantic import BaseModel, field_validator
from typing import Optional


def _validar_nombre_cargo(v):
    if v is not None and isinstance(v, str) and not v.strip():
        raise ValueError("El nombre del cargo no puede estar vacío")
    return v


def _validar_descripcion_cargo(v):
    if v is not None and isinstance(v, str) and not v.strip():
        raise ValueError("La descripción del cargo no puede estar vacía")
    return v


class CargoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

    @field_validator('nombre')
    def validar_nombre(cls, v):
        return _validar_nombre_cargo(v)

    @field_validator('descripcion')
    def validar_descripcion(cls, v):
        return _validar_descripcion_cargo(v)


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator('nombre')
    def validar_nombre(cls, v):
        return _validar_nombre_cargo(v)

    @field_validator('descripcion')
    def validar_descripcion(cls, v):
        return _validar_descripcion_cargo(v)


class CargoCambiarEstado(BaseModel):
    activo: bool


class CargoResponse(CargoBase):
    id: int
    activo: bool

    model_config = {"from_attributes": True}