from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.schemas.cargo import CargoCreate, CargoUpdate, CargoCambiarEstado, CargoResponse
from app.services import cargo_service

router = APIRouter(prefix="/cargos", tags=["Cargos"])


@router.get("", response_model=list[CargoResponse])
async def listar_cargos(
    solo_activos: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await cargo_service.listar_cargos(db, solo_activos)


@router.post("", response_model=CargoResponse, status_code=201)
async def crear_cargo(
    datos: CargoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await cargo_service.crear_cargo(db, datos)


@router.get("/{cargo_id}", response_model=CargoResponse)
async def obtener_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await cargo_service.get_cargo_by_id(db, cargo_id)


@router.patch("/{cargo_id}", response_model=CargoResponse)
async def actualizar_cargo(
    cargo_id: int,
    datos: CargoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await cargo_service.actualizar_cargo(db, cargo_id, datos)


@router.patch("/{cargo_id}/estado", response_model=CargoResponse)
async def cambiar_estado(
    cargo_id: int,
    datos: CargoCambiarEstado,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await cargo_service.cambiar_estado_cargo(db, cargo_id, datos.activo)