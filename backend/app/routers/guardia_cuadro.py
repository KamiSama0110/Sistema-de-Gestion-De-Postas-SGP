from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.usuario import Usuario
from app.models.enums import EstadoGuardiaCuadroEnum
from app.schemas.plan import (
    GuardiaCuadroUpdate,
    GuardiaCuadroResponse,
    PaginatedGuardiaCuadro,
)
from app.services import guardia_cuadro_service

router = APIRouter(prefix="/guardias-cuadro", tags=["Guardias de Cuadro"])


@router.get("", response_model=PaginatedGuardiaCuadro)
async def listar_guardias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    plan_id: Optional[int] = None,
    cuadro_id: Optional[int] = None,
    estado: Optional[EstadoGuardiaCuadroEnum] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.listar_guardias(
        db, page, size, plan_id, cuadro_id, estado, desde, hasta
    )


@router.patch("/{guardia_id}", response_model=GuardiaCuadroResponse)
async def actualizar_guardia(
    guardia_id: int,
    datos: GuardiaCuadroUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.actualizar_guardia(db, guardia_id, datos)


@router.delete("/{guardia_id}", status_code=204)
async def eliminar_guardia(
    guardia_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    await guardia_cuadro_service.eliminar_guardia(db, guardia_id)
