from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cuadro import FranjaCuadro
from app.schemas.franja import FranjaCuadroUpdate


async def get_franja_by_id(db: AsyncSession, franja_id: int) -> FranjaCuadro:
    result = await db.execute(select(FranjaCuadro).where(FranjaCuadro.id == franja_id))
    franja = result.scalar_one_or_none()
    if not franja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Franja no encontrada"
        )
    return franja


async def listar_franjas(db: AsyncSession) -> list[FranjaCuadro]:
    result = await db.execute(select(FranjaCuadro).order_by(FranjaCuadro.id))
    return result.scalars().all()


async def actualizar_franja(
    db: AsyncSession, franja_id: int, datos: FranjaCuadroUpdate
) -> FranjaCuadro:
    franja = await get_franja_by_id(db, franja_id)

    update_data = datos.model_dump(exclude_unset=True)

    if "hora_inicio" in update_data and "hora_fin" in update_data:
        if update_data["hora_inicio"] == update_data["hora_fin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de inicio y fin deben ser distintas",
            )
    elif (
        "hora_inicio" in update_data
        and update_data["hora_inicio"] == franja.hora_fin
        or "hora_fin" in update_data
        and update_data["hora_fin"] == franja.hora_inicio
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de inicio y fin deben ser distintas",
        )

    for field, value in update_data.items():
        setattr(franja, field, value)

    await db.commit()
    await db.refresh(franja)
    return franja
