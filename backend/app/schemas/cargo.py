from pydantic import BaseModel, field_validator
from typing import Optional

from app.utils.validators import texto_no_vacio, texto_opcional_no_vacio


class CargoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v):
        return texto_no_vacio(v, "El nombre del cargo")

    @field_validator('descripcion')
    @classmethod
    def validar_descripcion(cls, v):
        return texto_opcional_no_vacio(v, "La descripción del cargo")


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v):
        return texto_opcional_no_vacio(v, "El nombre del cargo")

    @field_validator('descripcion')
    @classmethod
    def validar_descripcion(cls, v):
        return texto_opcional_no_vacio(v, "La descripción del cargo")


class CargoCambiarEstado(BaseModel):
    activo: bool


class CargoResponse(CargoBase):
    id: int
    activo: bool

    model_config = {"from_attributes": True}


class PaginatedCargo(BaseModel):
    total: int
    page: int
    size: int
    items: list[CargoResponse]
