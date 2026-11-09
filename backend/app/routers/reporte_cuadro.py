from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.enums import SeveridadEnum, TipoNovedadEnum
from app.models.usuario import Usuario
from app.schemas.reporte import PeriodoRequest
from app.schemas.reporte_cuadro import (
    ReporteCumplimientoResponse,
    ReporteDiasSinCubrirResponse,
    ReporteGuardiasPorCuadroResponse,
    ReporteIncidenciasCuadroResponse,
    ReporteIncumplimientosResponse,
)
from app.services import reporte_cuadro_service

router = APIRouter(prefix="/reportes-cuadros", tags=["Reportes de Cuadros"])

MAX_DIAS_RANGO = 366


async def get_periodo_cuadro(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
) -> PeriodoRequest:
    if fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha desde no puede ser posterior a la fecha hasta",
        )
    if (fecha_hasta - fecha_desde).days > MAX_DIAS_RANGO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rango no puede superar los {MAX_DIAS_RANGO} días",
        )
    return PeriodoRequest(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/cumplimiento", response_model=ReporteCumplimientoResponse)
async def reporte_cumplimiento(
    anio: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await reporte_cuadro_service.reporte_cumplimiento(db, anio, mes)


@router.get("/guardias-por-cuadro", response_model=ReporteGuardiasPorCuadroResponse)
async def reporte_guardias_por_cuadro(
    periodo: PeriodoRequest = Depends(get_periodo_cuadro),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await reporte_cuadro_service.reporte_guardias_por_cuadro(
        db, periodo.fecha_desde, periodo.fecha_hasta
    )


@router.get("/incidencias", response_model=ReporteIncidenciasCuadroResponse)
async def reporte_incidencias(
    periodo: PeriodoRequest = Depends(get_periodo_cuadro),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severidad: Optional[SeveridadEnum] = None,
    tipo: Optional[TipoNovedadEnum] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await reporte_cuadro_service.reporte_incidencias(
        db, periodo.fecha_desde, periodo.fecha_hasta, page, size, severidad, tipo
    )


@router.get("/dias-sin-cubrir", response_model=ReporteDiasSinCubrirResponse)
async def reporte_dias_sin_cubrir(
    anio: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await reporte_cuadro_service.reporte_dias_sin_cubrir(db, anio, mes)


@router.get("/incumplimientos", response_model=ReporteIncumplimientosResponse)
async def reporte_incumplimientos(
    periodo: PeriodoRequest = Depends(get_periodo_cuadro),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await reporte_cuadro_service.reporte_incumplimientos(
        db, periodo.fecha_desde, periodo.fecha_hasta
    )
