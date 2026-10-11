from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_admin
from app.models.usuario import Usuario
from app.schemas.franja import FranjaCuadroUpdate, FranjaCuadroResponse, FranjaCuadroListResponse
from app.services import franja_service

router = APIRouter(prefix="/franjas-cuadro", tags=["Franjas de Cuadro"])


@router.get("", response_model=list[FranjaCuadroListResponse])
async def listar_franjas(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await franja_service.listar_franjas(db)


@router.patch("/{franja_id}", response_model=FranjaCuadroResponse)
async def actualizar_franja(
    franja_id: int,
    datos: FranjaCuadroUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await franja_service.actualizar_franja(db, franja_id, datos)