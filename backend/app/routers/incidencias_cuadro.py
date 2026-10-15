from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.enums import SeveridadEnum, TipoNovedadEnum
from app.models.usuario import Usuario
from app.schemas.incidencia import (
    IncidenciaResponse,
    IncidenciaUpdate,
    PaginatedIncidencia,
)
from app.services import incidencia_cuadro_service

router = APIRouter(prefix="/incidencias-cuadro", tags=["Incidencias de Cuadro"])


@router.get("", response_model=PaginatedIncidencia)
async def listar_incidencias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    guardia_id: int | None = None,
    cuadro_id: int | None = None,
    severidad: SeveridadEnum | None = None,
    tipo: TipoNovedadEnum | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    requiere_seguimiento: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await incidencia_cuadro_service.listar_incidencias(
        db,
        page,
        size,
        guardia_id,
        cuadro_id,
        severidad,
        tipo,
        desde,
        hasta,
        requiere_seguimiento,
    )


@router.get("/{incidencia_id}", response_model=IncidenciaResponse)
async def obtener_incidencia(
    incidencia_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await incidencia_cuadro_service.get_incidencia_by_id(db, incidencia_id)


@router.patch("/{incidencia_id}", response_model=IncidenciaResponse)
async def actualizar_incidencia(
    incidencia_id: int,
    datos: IncidenciaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    incidencia = await incidencia_cuadro_service.get_incidencia_by_id(db, incidencia_id)
    return await incidencia_cuadro_service.actualizar_incidencia(db, incidencia, datos)
