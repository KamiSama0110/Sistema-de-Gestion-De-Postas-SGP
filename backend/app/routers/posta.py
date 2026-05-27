from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.models.enums import TipoPostaEnum
from app.schemas.posta import (
    PostaCreate,
    PostaUpdate,
    PostaResponse,
    TurnoPostaCreate,
    TurnoPostaUpdate,
    TurnoPostaResponse,
)
from app.services import posta_service

router = APIRouter(prefix="/postas", tags=["Postas"])


@router.get("", response_model=list[PostaResponse])
async def listar_postas(
    activa: Optional[bool] = None,
    tipo: Optional[TipoPostaEnum] = None,
    buscar: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.listar_postas(db, activa, tipo, buscar)


@router.post("", response_model=PostaResponse, status_code=201)
async def crear_posta(
    datos: PostaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.crear_posta(db, datos)


@router.get("/{posta_id}", response_model=PostaResponse)
async def obtener_posta(
    posta_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.get_posta_by_id(db, posta_id)


@router.patch("/{posta_id}", response_model=PostaResponse)
async def actualizar_posta(
    posta_id: int,
    datos: PostaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.actualizar_posta(db, posta_id, datos)


@router.patch("/{posta_id}/estado", response_model=PostaResponse)
async def cambiar_estado_posta(
    posta_id: int,
    activa: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.cambiar_estado_posta(db, posta_id, activa)


@router.post("/{posta_id}/turnos", response_model=TurnoPostaResponse, status_code=201)
async def agregar_turno(
    posta_id: int,
    datos: TurnoPostaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.agregar_turno(db, posta_id, datos)


@router.patch("/turnos/{turno_id}", response_model=TurnoPostaResponse)
async def actualizar_turno(
    turno_id: int,
    datos: TurnoPostaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.actualizar_turno(db, turno_id, datos)


@router.patch("/turnos/{turno_id}/estado", response_model=TurnoPostaResponse)
async def cambiar_estado_turno(
    turno_id: int,
    activo: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await posta_service.cambiar_estado_turno(db, turno_id, activo)