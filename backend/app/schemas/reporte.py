from datetime import date
from pydantic import BaseModel

class PeriodoRequest(BaseModel):
    fecha_desde: date
    fecha_hasta: date


class CoberturaPosta(BaseModel):
    posta_id: int
    posta_nombre: str
    planificadas: int
    finalizadas: int
    ausentes: int
    porcentaje_cobertura: float


class ReporteCoberturaResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    cobertura_general: float
    total_planificadas: int
    total_finalizadas: int
    total_sin_cubrir: int
    por_posta: list[CoberturaPosta]


class AusentismoASP(BaseModel):
    asp_id: int
    asp_nombre: str
    total_ausencias: int
    justificadas: int
    injustificadas: int


class ReporteAusentismoResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    total_planificadas: int
    total_ausencias: int
    porcentaje_ausentismo: float
    guardias_sin_cubrir: int
    por_asp: list[AusentismoASP]


class HorasASP(BaseModel):
    asp_id: int
    asp_nombre: str
    total_guardias: int
    total_horas: float


class ReporteHorasResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    por_asp: list[HorasASP]


class IncidenciaItem(BaseModel):
    guardia_id: int
    posta_nombre: str
    asp_nombre: str
    fecha: date
    fecha_hora: str
    tipo: str
    descripcion: str
    severidad: str


class ReporteIncidenciasResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    total_incidencias: int
    items: list[IncidenciaItem]


class TardanzaASP(BaseModel):
    asp_id: int
    asp_nombre: str
    total_tardanzas: int
    promedio_minutos: float
    max_minutos: int


class ReporteTardanzasResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    total_guardias: int
    total_tardanzas: int
    por_asp: list[TardanzaASP]