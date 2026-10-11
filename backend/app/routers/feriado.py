from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.usuario import Usuario
from app.schemas.feriado import (
    FeriadoCreate,
    FeriadoUpdate,
    FeriadoResponse,
    FeriadosSugeridosResponse,
    FeriadosCargarResponse,
    PaginatedFeriado,
)
from app.services import feriado_service

router = APIRouter(prefix="/feriados", tags=["Feriados"])


@router.get("", response_model=PaginatedFeriado)
async def listar_feriados(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    anio: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await feriado_service.listar_feriados(db, page, size, anio)


@router.post("", response_model=FeriadoResponse, status_code=201)
async def crear_feriado(
    datos: FeriadoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await feriado_service.crear_feriado(db, datos)


@router.get("/sugeridos", response_model=FeriadosSugeridosResponse)
async def get_feriados_sugeridos(
    anio: int = Query(..., ge=2020, le=2050),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    sugeridos = await feriado_service.get_feriados_sugeridos(db, anio)
    return {"sugeridos": sugeridos}


@router.post("/sugeridos", response_model=FeriadosCargarResponse)
async def cargar_feriados_sugeridos(
    anio: int = Query(..., ge=2020, le=2050),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await feriado_service.cargar_feriados_sugeridos(db, anio)


@router.patch("/{feriado_id}", response_model=FeriadoResponse)
async def actualizar_feriado(
    feriado_id: int,
    datos: FeriadoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await feriado_service.actualizar_feriado(db, feriado_id, datos)


@router.delete("/{feriado_id}", status_code=204)
async def eliminar_feriado(
    feriado_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    await feriado_service.eliminar_feriado(db, feriado_id)