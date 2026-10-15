from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import SeveridadEnum, TipoNovedadEnum
from app.utils.validators import texto_opcional_no_vacio


def _sin_zona(valor: datetime | None) -> datetime | None:
    if valor is not None and valor.tzinfo is not None:
        return valor.replace(tzinfo=None)
    return valor


class IncidenciaCreate(BaseModel):
    tipo: TipoNovedadEnum
    severidad: SeveridadEnum = SeveridadEnum.baja
    descripcion: str = Field(..., min_length=1, max_length=1000)
    fecha_hora: Optional[datetime] = None
    posta_id: Optional[int] = None
    asp_id: Optional[int] = None
    area: Optional[str] = Field(None, max_length=120)
    acciones_tomadas: Optional[str] = None
    requiere_seguimiento: bool = False

    @field_validator("descripcion", "acciones_tomadas")
    @classmethod
    def validar_textos(cls, v: Optional[str], info) -> Optional[str]:
        return texto_opcional_no_vacio(v, f"El campo {info.field_name}")

    @field_validator("area")
    @classmethod
    def validar_area(cls, v: Optional[str]) -> Optional[str]:
        return texto_opcional_no_vacio(v, "El área")

    @field_validator("fecha_hora")
    @classmethod
    def validar_fecha_hora(cls, v: Optional[datetime]) -> Optional[datetime]:
        v = _sin_zona(v)
        if v is not None and v > datetime.now():
            raise ValueError("La fecha y hora no puede ser futura")
        return v


class IncidenciaUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=1, max_length=1000)
    severidad: Optional[SeveridadEnum] = None
    tipo: Optional[TipoNovedadEnum] = None
    area: Optional[str] = Field(None, max_length=120)
    acciones_tomadas: Optional[str] = None
    requiere_seguimiento: Optional[bool] = None

    @field_validator("descripcion", "acciones_tomadas")
    @classmethod
    def validar_textos(cls, v: Optional[str], info) -> Optional[str]:
        return texto_opcional_no_vacio(v, f"El campo {info.field_name}")

    @field_validator("area")
    @classmethod
    def validar_area(cls, v: Optional[str]) -> Optional[str]:
        return texto_opcional_no_vacio(v, "El área")


class IncidenciaResponse(BaseModel):
    id: int
    guardia_cuadro_id: int
    cuadro_id: Optional[int] = None
    cuadro_nombre: str
    tipo: TipoNovedadEnum
    severidad: SeveridadEnum
    descripcion: str
    fecha_hora: datetime
    posta_id: Optional[int] = None
    posta_nombre: Optional[str] = None
    asp_id: Optional[int] = None
    asp_nombre: Optional[str] = None
    area: Optional[str] = None
    acciones_tomadas: Optional[str] = None
    requiere_seguimiento: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class PaginatedIncidencia(BaseModel):
    total: int
    page: int
    size: int
    items: list[IncidenciaResponse]


class OpcionSimple(BaseModel):
    id: int
    nombre: str


class OpcionesIncidenciaResponse(BaseModel):
    postas: list[OpcionSimple]
    asp: list[OpcionSimple]
