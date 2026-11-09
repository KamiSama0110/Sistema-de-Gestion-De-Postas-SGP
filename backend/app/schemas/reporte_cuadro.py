from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.models.enums import EstadoPlanGuardiaEnum
from app.schemas.incidencia import IncidenciaResponse


class ReporteCumplimientoResponse(BaseModel):
    anio: int
    mes: int
    plan_id: int
    slots_totales: int
    cubiertos: int
    sin_cubrir: int
    planificadas: int
    activas: int
    finalizadas: int
    incumplidas: int
    incumplidas_justificadas: int
    incumplidas_injustificadas: int
    canceladas: int
    porcentaje_cumplimiento: Optional[float] = None
    porcentaje_cobertura: float


class CuadroReporteItem(BaseModel):
    cuadro_id: int
    cuadro_nombre: str
    total: int
    planificadas: int
    activas: int
    finalizadas: int
    incumplidas: int
    canceladas: int
    ultima_guardia: Optional[date] = None


class ReporteGuardiasPorCuadroResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    items: list[CuadroReporteItem]


class ReporteIncidenciasCuadroResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    total: int
    por_severidad: dict[str, int]
    por_tipo: dict[str, int]
    requieren_seguimiento: int
    page: int
    size: int
    items: list[IncidenciaResponse]


class SlotSinCubrir(BaseModel):
    fecha: date
    franja_id: int
    franja_nombre: str
    cancelada: bool


class FeriadoItem(BaseModel):
    fecha: date
    descripcion: str


class ReporteDiasSinCubrirResponse(BaseModel):
    anio: int
    mes: int
    plan_id: int
    estado_plan: EstadoPlanGuardiaEnum
    slots_totales: int
    sin_cubrir: int
    dias: list[SlotSinCubrir]
    feriados: list[FeriadoItem]


class IncumplimientoItem(BaseModel):
    guardia_id: int
    cuadro_id: int
    cuadro_nombre: str
    fecha: date
    franja_id: int
    franja_nombre: str
    motivo: Optional[str] = None
    justificada: bool


class ReporteIncumplimientosResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    total: int
    justificadas: int
    injustificadas: int
    items: list[IncumplimientoItem]
