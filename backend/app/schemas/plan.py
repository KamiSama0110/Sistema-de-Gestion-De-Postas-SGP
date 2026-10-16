from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import EstadoPlanGuardiaEnum, EstadoGuardiaCuadroEnum
from app.schemas.franja import FranjaCuadroListResponse
from app.utils.validators import texto_opcional_no_vacio


class PlanCreate(BaseModel):
    anio: int = Field(..., ge=2000, le=2100)
    mes: int = Field(..., ge=1, le=12)
    observaciones: Optional[str] = None

    @field_validator("observaciones")
    @classmethod
    def validar_observaciones(cls, v):
        return texto_opcional_no_vacio(v, "Las observaciones")


class PlanUpdate(BaseModel):
    observaciones: Optional[str] = None

    @field_validator("observaciones")
    @classmethod
    def validar_observaciones(cls, v):
        return texto_opcional_no_vacio(v, "Las observaciones")


class PlanRechazar(BaseModel):
    motivo: Optional[str] = None

    @field_validator("motivo")
    @classmethod
    def validar_motivo(cls, v):
        return texto_opcional_no_vacio(v, "El motivo")


class PlanResponse(BaseModel):
    id: int
    anio: int
    mes: int
    estado: EstadoPlanGuardiaEnum
    generado_automaticamente: bool
    observaciones: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}


class PlanListResponse(BaseModel):
    id: int
    anio: int
    mes: int
    estado: EstadoPlanGuardiaEnum
    generado_automaticamente: bool
    cantidad_guardias: int

    model_config = {"from_attributes": True}


class PaginatedPlan(BaseModel):
    total: int
    page: int
    size: int
    items: list[PlanListResponse]


class GuardiaCuadroCreate(BaseModel):
    cuadro_id: int
    franja_id: int
    fecha: date


class GuardiaCuadroUpdate(BaseModel):
    cuadro_id: Optional[int] = None
    franja_id: Optional[int] = None
    fecha: Optional[date] = None


class IniciarGuardiaRequest(BaseModel):
    inicio_real: Optional[datetime] = None


class FinalizarGuardiaRequest(BaseModel):
    fin_real: Optional[datetime] = None


class IncumplirGuardiaRequest(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=300)
    justificada: bool


class CancelarGuardiaCuadroRequest(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=300)


class GuardiaCuadroResponse(BaseModel):
    id: int
    plan_id: int
    cuadro_id: int
    cuadro_nombre: str
    franja_id: int
    franja_nombre: str
    franja: Optional[FranjaCuadroListResponse] = None
    fecha: date
    estado: EstadoGuardiaCuadroEnum
    inicio_real: Optional[datetime] = None
    fin_real: Optional[datetime] = None
    motivo_incumplimiento: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    justificada: Optional[bool] = None

    model_config = {"from_attributes": True}


class PaginatedGuardiaCuadro(BaseModel):
    total: int
    page: int
    size: int
    items: list[GuardiaCuadroResponse]


class CalendarioFranja(BaseModel):
    franja_id: int
    nombre: str
    aplica: bool
    guardia: Optional[dict] = None


class CalendarioDia(BaseModel):
    fecha: date
    dia_semana: int
    es_feriado: bool
    feriado_descripcion: Optional[str] = None
    franjas: list[CalendarioFranja]


class CalendarioResumen(BaseModel):
    slots_totales: int
    cubiertos: int
    sin_cubrir: int
    feriados: int


class CalendarioResponse(BaseModel):
    plan_id: int
    anio: int
    mes: int
    dias: list[CalendarioDia]
    resumen: CalendarioResumen


class CandidatoDescartado(BaseModel):
    cuadro_id: int
    cuadro_nombre: str
    motivo: str


class CandidatosResponse(BaseModel):
    fecha: date
    franja_id: int
    elegibles: list[dict]
    descartados: list[CandidatoDescartado]


class GenerarPlanRequest(BaseModel):
    modo: Literal["completar", "reemplazar"]
    semilla: Optional[int] = None


class SlotSinCubrir(BaseModel):
    fecha: date
    franja_id: int
    franja_nombre: str


class CuadroSinAsignar(BaseModel):
    cuadro_id: int
    nombre: str
    motivo: str


class GenerarPlanResponse(BaseModel):
    plan_id: int
    slots_totales: int
    cubiertos: int
    creadas: int
    sin_cubrir: list[SlotSinCubrir]
    cuadros_sin_asignar: list[CuadroSinAsignar]
    advertencias: list[str]


class MiPlanificacionResponse(BaseModel):
    plan_id: Optional[int] = None
    anio: int
    mes: int
    guardias: list[GuardiaCuadroResponse]
