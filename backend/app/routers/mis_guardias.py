from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_cuadro
from app.models.usuario import Usuario
from app.models.enums import EstadoGuardiaCuadroEnum
from app.schemas.incidencia import (
    IncidenciaCreate,
    IncidenciaUpdate,
    IncidenciaResponse,
    PaginatedIncidencia,
    OpcionesIncidenciaResponse,
)
from app.schemas.plan import (
    GuardiaCuadroResponse,
    PaginatedGuardiaCuadro,
    MiPlanificacionResponse,
)
from app.services import (
    incidencia_cuadro_service,
    mis_guardias_service,
)

router = APIRouter(tags=["Panel del cuadro"])


async def cuadro_id_actual(usuario: Usuario = Depends(require_cuadro)) -> int:
    if usuario.cuadro_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene un cuadro asignado",
        )
    return usuario.cuadro_id


@router.get("/mis-guardias", response_model=PaginatedGuardiaCuadro)
async def listar_mis_guardias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    estado: Optional[EstadoGuardiaCuadroEnum] = None,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await mis_guardias_service.listar_mis_guardias(
        db, cuadro_id, page, size, anio, mes, estado
    )


@router.get(
    "/mis-guardias/opciones-incidencia",
    response_model=OpcionesIncidenciaResponse,
)
async def opciones_incidencia(
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await incidencia_cuadro_service.get_opciones(db)


@router.get("/mi-planificacion", response_model=MiPlanificacionResponse)
async def mi_planificacion(
    anio: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await mis_guardias_service.mi_planificacion(db, cuadro_id, anio, mes)


@router.get("/mis-guardias/{guardia_id}", response_model=GuardiaCuadroResponse)
async def obtener_mi_guardia(
    guardia_id: int,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await mis_guardias_service.get_mi_guardia(db, guardia_id, cuadro_id)


@router.post("/mis-guardias/{guardia_id}/iniciar", response_model=GuardiaCuadroResponse)
async def iniciar_mi_guardia(
    guardia_id: int,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await mis_guardias_service.iniciar_mi_guardia(db, guardia_id, cuadro_id)


@router.post(
    "/mis-guardias/{guardia_id}/finalizar", response_model=GuardiaCuadroResponse
)
async def finalizar_mi_guardia(
    guardia_id: int,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    return await mis_guardias_service.finalizar_mi_guardia(db, guardia_id, cuadro_id)


@router.get(
    "/mis-guardias/{guardia_id}/incidencias", response_model=PaginatedIncidencia
)
async def listar_mis_incidencias(
    guardia_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    await mis_guardias_service.get_mi_guardia(db, guardia_id, cuadro_id)
    return await incidencia_cuadro_service.listar_incidencias(
        db, page, size, guardia_id=guardia_id
    )


@router.post(
    "/mis-guardias/{guardia_id}/incidencias",
    response_model=IncidenciaResponse,
    status_code=201,
)
async def crear_mi_incidencia(
    guardia_id: int,
    datos: IncidenciaCreate,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    guardia = await mis_guardias_service.get_mi_guardia(db, guardia_id, cuadro_id)
    return await incidencia_cuadro_service.crear_incidencia(db, guardia, datos)


@router.patch("/mis-incidencias/{incidencia_id}", response_model=IncidenciaResponse)
async def actualizar_mi_incidencia(
    incidencia_id: int,
    datos: IncidenciaUpdate,
    cuadro_id: int = Depends(cuadro_id_actual),
    db: AsyncSession = Depends(get_db),
):
    incidencia = await incidencia_cuadro_service.get_incidencia_propia(
        db, incidencia_id, cuadro_id
    )
    return await incidencia_cuadro_service.actualizar_incidencia(db, incidencia, datos)
