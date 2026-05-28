from pydantic import BaseModel, field_validator
from typing import Optional


class CargoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    
    @field_validator('nombre')
    def nombre_no_vacio(cls, v: str):
        if not v.strip():
            raise ValueError("El nombre del cargo no puede estar vacio")
        return v

    @field_validator('descripcion')
    def descripcion_no_vacia(cls, v: Optional[str]):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("La descripcion del cargo no puede estar vacia")
        return v
        


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator('nombre')
    def nombre_no_vacio(cls, v: Optional[str]):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("El nombre del cargo no puede estar vacio")
        return v

    @field_validator('descripcion')
    def descripcion_no_vacia(cls, v: Optional[str]):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("La descripcion del cargo no puede estar vacia")
        return v


class CargoCambiarEstado(BaseModel):
    activo: bool


class CargoResponse(CargoBase):
    id: int
    activo: bool

    model_config = {"from_attributes": True}