from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.models.enums import EstadoASPEnum
from app.schemas.asp import (
    ASPCreate,
    ASPUpdate,
    ASPCambiarEstado,
    ASPResponse,
    PaginatedASP,
)
from app.services import asp_service

router = APIRouter(prefix="/asp", tags=["ASP"])


@router.get("", response_model=PaginatedASP)
async def listar_asp(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    estado: Optional[EstadoASPEnum] = None,
    buscar: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await asp_service.listar_asp(db, page, size, estado, buscar)


@router.post("", response_model=ASPResponse, status_code=201)
async def crear_asp(
    datos: ASPCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await asp_service.crear_asp(db, datos)


@router.get("/{asp_id}", response_model=ASPResponse)
async def obtener_asp(
    asp_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await asp_service.get_asp_by_id(db, asp_id)


@router.patch("/{asp_id}", response_model=ASPResponse)
async def actualizar_asp(
    asp_id: int,
    datos: ASPUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await asp_service.actualizar_asp(db, asp_id, datos)


@router.patch("/{asp_id}/estado", response_model=ASPResponse)
async def cambiar_estado(
    asp_id: int,
    datos: ASPCambiarEstado,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return await asp_service.cambiar_estado_asp(db, asp_id, datos)


# @router.get("/{asp_id}/capacitaciones")
# async def listar_capacitaciones(
#     asp_id: int,
#     db: AsyncSession = Depends(get_db),
#     _: Usuario = Depends(get_current_user),
# ):
#     asp = await asp_service.get_asp_by_id(db, asp_id)
#     return asp.capacitaciones


@router.post("/{asp_id}/foto")
async def subir_foto(
    asp_id: int,
    foto: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    # TODO de momento camino listo para guardarlo en local y en servidor externo, pero este endpoint ni esta completado ni se usa
    asp = await asp_service.get_asp_by_id(db, asp_id)
    asp.foto_url = foto.filename
    await db.commit()
    return {"mensaje": "Foto actualizada", "foto_url": foto.filename}