from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.schemas.reporte import (
    ReporteCoberturaResponse,
    ReporteAusentismoResponse,
    ReporteHorasResponse,
    ReporteIncidenciasResponse,
    ReporteTardanzasResponse,
)
from app.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/cobertura", response_model=ReporteCoberturaResponse)
async def reporte_cobertura(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_cobertura(db, fecha_desde, fecha_hasta)


@router.get("/ausentismo", response_model=ReporteAusentismoResponse)
async def reporte_ausentismo(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_ausentismo(db, fecha_desde, fecha_hasta)


@router.get("/horas-asp", response_model=ReporteHorasResponse)
async def reporte_horas(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_horas(db, fecha_desde, fecha_hasta)


@router.get("/incidencias", response_model=ReporteIncidenciasResponse)
async def reporte_incidencias(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    severidad: Optional[str] = None,
    posta_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_incidencias(
        db, fecha_desde, fecha_hasta, severidad, posta_id
    )


@router.get("/tardanzas", response_model=ReporteTardanzasResponse)
async def reporte_tardanzas(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    asp_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await reporte_service.reporte_tardanzas(
        db, fecha_desde, fecha_hasta, asp_id
    )