from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.usuario import Usuario
from app.models.enums import SexoEnum
from app.schemas.cuadro import (
    CuadroCreate,
    CuadroUpdate,
    CuadroCambiarEstado,
    CuadroResponse,
    PaginatedCuadro,
    CuadroCuentaResponse,
    CuadroCuentaCreate,
    CuadroCuentaPassword,
)
from app.services import cuadro_service

router = APIRouter(prefix="/cuadros", tags=["Cuadros"])


@router.get("", response_model=PaginatedCuadro)
async def listar_cuadros(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, max_length=100),
    sexo: Optional[SexoEnum] = None,
    activo: Optional[bool] = None,
    sin_guardia_vie_dom: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.listar_cuadros(db, page, size, q, sexo, activo, sin_guardia_vie_dom)


@router.post("", response_model=CuadroResponse, status_code=201)
async def crear_cuadro(
    datos: CuadroCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.crear_cuadro(db, datos)


@router.get("/{cuadro_id}", response_model=CuadroResponse)
async def obtener_cuadro(
    cuadro_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.get_cuadro_by_id(db, cuadro_id)


@router.patch("/{cuadro_id}", response_model=CuadroResponse)
async def actualizar_cuadro(
    cuadro_id: int,
    datos: CuadroUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.actualizar_cuadro(db, cuadro_id, datos)


@router.patch("/{cuadro_id}/estado", response_model=CuadroResponse)
async def cambiar_estado_cuadro(
    cuadro_id: int,
    datos: CuadroCambiarEstado,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.cambiar_estado_cuadro(db, cuadro_id, datos)


@router.get("/{cuadro_id}/cuenta", response_model=CuadroCuentaResponse)
async def obtener_cuadro_cuenta(
    cuadro_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await cuadro_service.get_cuadro_cuenta(db, cuadro_id)


@router.post("/{cuadro_id}/cuenta", response_model=CuadroCuentaResponse, status_code=201)
async def crear_cuadro_cuenta(
    cuadro_id: int,
    datos: CuadroCuentaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    await cuadro_service.crear_cuadro_cuenta(db, cuadro_id, datos)
    return await cuadro_service.get_cuadro_cuenta(db, cuadro_id)


@router.patch("/{cuadro_id}/cuenta/password")
async def cambiar_cuadro_cuenta_password(
    cuadro_id: int,
    datos: CuadroCuentaPassword,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    await cuadro_service.cambiar_password_cuadro_cuenta(db, cuadro_id, datos)
    return {"mensaje": "Contraseña actualizada correctamente"}