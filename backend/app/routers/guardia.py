from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.models.enums import EstadoGuardiaEnum
from app.schemas.guardia import (
    GuardiaCreate,
    GuardiaUpdate,
    GuardiaResponse,
    GuardiaListResponse,
    ConfirmarLlegadaRequest,
    FinalizarGuardiaRequest,
    NovedadCreate,
    NovedadResponse,
)
from app.services import guardia_service

router = APIRouter(prefix="/guardias", tags=["Guardias"])


@router.get("", response_model=list[GuardiaListResponse])
async def listar_guardias(
    fecha: Optional[date] = None,
    estado: Optional[EstadoGuardiaEnum] = None,
    asp_id: Optional[int] = None,
    posta_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await guardia_service.listar_guardias(db, fecha, estado, asp_id, posta_id)


@router.post("", response_model=GuardiaResponse, status_code=201)
async def crear_guardia(
    datos: GuardiaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await guardia_service.crear_guardia(db, datos)


@router.get("/{guardia_id}", response_model=GuardiaResponse)
async def obtener_guardia(
    guardia_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await guardia_service.get_guardia_con_tardanza(db, guardia_id)


@router.patch("/{guardia_id}", response_model=GuardiaResponse)
async def actualizar_guardia(
    guardia_id: int,
    datos: GuardiaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await guardia_service.actualizar_guardia(db, guardia_id, datos)


@router.patch("/{guardia_id}/confirmar-llegada", response_model=GuardiaResponse)
async def confirmar_llegada(
    guardia_id: int,
    datos: ConfirmarLlegadaRequest,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    await guardia_service.confirmar_llegada(db, guardia_id, datos)
    return await guardia_service.get_guardia_con_tardanza(db, guardia_id)


@router.patch("/{guardia_id}/finalizar", response_model=GuardiaResponse)
async def finalizar_guardia(
    guardia_id: int,
    datos: FinalizarGuardiaRequest,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    await guardia_service.finalizar_guardia(db, guardia_id, datos)
    return await guardia_service.get_guardia_con_tardanza(db, guardia_id)


@router.post("/{guardia_id}/novedades", response_model=NovedadResponse, status_code=201)
async def registrar_novedad(
    guardia_id: int,
    datos: NovedadCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await guardia_service.registrar_novedad(db, guardia_id, datos)


@router.get("/{guardia_id}/novedades", response_model=list[NovedadResponse])
async def listar_novedades(
    guardia_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    guardia = await guardia_service.get_guardia_by_id(db, guardia_id)
    return guardia.novedades