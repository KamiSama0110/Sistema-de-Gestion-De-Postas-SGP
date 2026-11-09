from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.core.types import Id, IdOpcional
from app.models.enums import EstadoGuardiaEnum, TipoNovedadEnum, SeveridadEnum


class GuardiaCreate(BaseModel):
    asp_id: Id
    turno_posta_id: Id
    fecha: date
    observaciones: Optional[str] = Field(None, max_length=2000)


class GuardiaUpdate(BaseModel):
    asp_id: IdOpcional = None
    motivo_ausencia: Optional[str] = Field(None, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=2000)


class ConfirmarLlegadaRequest(BaseModel):
    hora_llegada: datetime


class FinalizarGuardiaRequest(BaseModel):
    hora_fin_real: datetime
    observaciones: Optional[str] = Field(None, max_length=2000)


class MarcarAusenteRequest(BaseModel):
    motivo_ausencia: Optional[str] = Field(None, min_length=1, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=2000)


class CancelarGuardiaRequest(BaseModel):
    motivo: Optional[str] = Field(None, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=2000)


class NovedadCreate(BaseModel):
    tipo: TipoNovedadEnum
    descripcion: str = Field(..., min_length=1, max_length=500)
    severidad: SeveridadEnum = SeveridadEnum.baja


class NovedadResponse(BaseModel):
    id: int
    guardia_id: int
    fecha_hora: datetime
    tipo: TipoNovedadEnum
    descripcion: str
    severidad: SeveridadEnum

    model_config = {"from_attributes": True}


class GuardiaResponse(BaseModel):
    id: int
    asp_id: int
    turno_posta_id: int
    fecha: date
    estado: EstadoGuardiaEnum
    hora_inicio_real: Optional[datetime] = None
    hora_fin_real: Optional[datetime] = None
    motivo_ausencia: Optional[str] = None
    observaciones: Optional[str] = None
    tardanza_minutos: Optional[int] = None
    novedades: list[NovedadResponse] = []

    model_config = {"from_attributes": True}


class GuardiaListResponse(BaseModel):
    id: int
    asp_id: int
    turno_posta_id: int
    fecha: date
    estado: EstadoGuardiaEnum
    hora_inicio_real: Optional[datetime] = None
    tardanza_minutos: Optional[int] = None

    model_config = {"from_attributes": True}


class PaginatedGuardia(BaseModel):
    total: int
    page: int
    size: int
    items: list[GuardiaListResponse]


class PaginatedNovedad(BaseModel):
    total: int
    page: int
    size: int
    items: list[NovedadResponse]