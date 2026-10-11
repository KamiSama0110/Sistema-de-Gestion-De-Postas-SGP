from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints, field_validator

from app.utils.validators import texto_no_vacio, texto_opcional_no_vacio

Descripcion = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]


class FeriadoBase(BaseModel):
    fecha: date
    descripcion: Descripcion

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v):
        return texto_no_vacio(v, "La descripción del feriado")


class FeriadoCreate(FeriadoBase):
    pass


class FeriadoUpdate(BaseModel):
    fecha: Optional[date] = None
    descripcion: Optional[Descripcion] = None

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v):
        return texto_opcional_no_vacio(v, "La descripción del feriado")


class FeriadoResponse(BaseModel):
    id: int
    fecha: date
    descripcion: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class FeriadoSugerido(BaseModel):
    fecha: date
    descripcion: str


class FeriadosSugeridosResponse(BaseModel):
    sugeridos: list[FeriadoSugerido]


class FeriadosCargarResponse(BaseModel):
    creados: int
    omitidos: int


class PaginatedFeriado(BaseModel):
    total: int
    page: int
    size: int
    items: list[FeriadoResponse]