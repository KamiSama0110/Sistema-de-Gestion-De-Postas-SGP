from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional
from app.models.enums import EstadoGuardiaEnum, TipoNovedadEnum, SeveridadEnum


class GuardiaCreate(BaseModel):
    asp_id: int
    turno_posta_id: int
    fecha: date
    observaciones: Optional[str] = None


class GuardiaUpdate(BaseModel):
    asp_id: Optional[int] = None
    motivo_ausencia: Optional[str] = None
    observaciones: Optional[str] = None


class ConfirmarLlegadaRequest(BaseModel):
    hora_llegada: datetime


class FinalizarGuardiaRequest(BaseModel):
    hora_fin_real: datetime
    observaciones: Optional[str] = None


class NovedadCreate(BaseModel):
    tipo: TipoNovedadEnum
    descripcion: str
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