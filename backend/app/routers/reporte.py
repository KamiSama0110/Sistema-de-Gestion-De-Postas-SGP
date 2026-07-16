from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.models.enums import SeveridadEnum
from app.schemas.reporte import (
    PeriodoRequest,
    ReporteCoberturaResponse,
    ReporteAusentismoResponse,
    ReporteHorasResponse,
    ReporteIncidenciasResponse,
    ReporteTardanzasResponse,
)
from app.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])


async def get_periodo(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
) -> PeriodoRequest:
    if fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha desde no puede ser posterior a la fecha hasta",
        )
    return PeriodoRequest(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/cobertura", response_model=ReporteCoberturaResponse)
async def reporte_cobertura(
    periodo: PeriodoRequest = Depends(get_periodo),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_cobertura(db, periodo.fecha_desde, periodo.fecha_hasta)


@router.get("/ausentismo", response_model=ReporteAusentismoResponse)
async def reporte_ausentismo(
    periodo: PeriodoRequest = Depends(get_periodo),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_ausentismo(db, periodo.fecha_desde, periodo.fecha_hasta)


@router.get("/horas-asp", response_model=ReporteHorasResponse)
async def reporte_horas(
    periodo: PeriodoRequest = Depends(get_periodo),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_horas(db, periodo.fecha_desde, periodo.fecha_hasta)


@router.get("/incidencias", response_model=ReporteIncidenciasResponse)
async def reporte_incidencias(
    periodo: PeriodoRequest = Depends(get_periodo),
    severidad: Optional[SeveridadEnum] = None,
    posta_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_incidencias(
        db, periodo.fecha_desde, periodo.fecha_hasta, severidad, posta_id
    )


@router.get("/tardanzas", response_model=ReporteTardanzasResponse)
async def reporte_tardanzas(
    periodo: PeriodoRequest = Depends(get_periodo),
    asp_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_tardanzas(
        db, periodo.fecha_desde, periodo.fecha_hasta, asp_id
    )
