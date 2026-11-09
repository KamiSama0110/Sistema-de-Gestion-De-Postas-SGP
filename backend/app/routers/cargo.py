from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_admin
from app.core.types import IdPath
from app.models.usuario import Usuario
from app.schemas.cargo import (
    CargoCambiarEstado,
    CargoCambiarEstadoResponse,
    CargoCreate,
    CargoUpdate,
    CargoResponse,
    PaginatedCargo,
)
from app.services import cargo_service

router = APIRouter(prefix="/cargos", tags=["Cargos"])


@router.get("", response_model=PaginatedCargo)
async def listar_cargos(
    solo_activos: bool = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    buscar: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cargo_service.listar_cargos(db, solo_activos, page, size, buscar)


@router.post("", response_model=CargoResponse, status_code=201)
async def crear_cargo(
    datos: CargoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cargo_service.crear_cargo(db, datos)


@router.get("/{cargo_id}", response_model=CargoResponse)
async def obtener_cargo(
    cargo_id: IdPath,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cargo_service.get_cargo_by_id(db, cargo_id)


@router.patch("/{cargo_id}", response_model=CargoResponse)
async def actualizar_cargo(
    cargo_id: IdPath,
    datos: CargoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cargo_service.actualizar_cargo(db, cargo_id, datos)


@router.patch("/{cargo_id}/estado", response_model=CargoCambiarEstadoResponse)
async def cambiar_estado(
    cargo_id: IdPath,
    datos: CargoCambiarEstado,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cargo_service.cambiar_estado_cargo(db, cargo_id, datos.activo)