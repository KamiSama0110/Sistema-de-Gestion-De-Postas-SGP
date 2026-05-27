from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cargo import Cargo
from app.schemas.cargo import CargoCreate, CargoUpdate
from fastapi import HTTPException, status


async def get_cargo_by_id(db: AsyncSession, cargo_id: int) -> Cargo:
    result = await db.execute(select(Cargo).where(Cargo.id == cargo_id))
    cargo = result.scalar_one_or_none()
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo con id {cargo_id} no encontrado",
        )
    return cargo


async def listar_cargos(
    db: AsyncSession, solo_activos: bool = True
) -> list[Cargo]:
    query = select(Cargo)
    if solo_activos:
        query = query.where(Cargo.activo)
    result = await db.execute(query)
    return result.scalars().all()


async def crear_cargo(db: AsyncSession, datos: CargoCreate) -> Cargo:
    existente = await db.execute(
        select(Cargo).where(Cargo.nombre == datos.nombre)
    )
    if existente.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cargo con el nombre '{datos.nombre}'",
        )
    cargo = Cargo(**datos.model_dump())
    db.add(cargo)
    await db.commit()
    await db.refresh(cargo)
    return cargo


async def actualizar_cargo(
    db: AsyncSession, cargo_id: int, datos: CargoUpdate
) -> Cargo:
    cargo = await get_cargo_by_id(db, cargo_id)
    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(cargo, campo, valor)
    await db.commit()
    await db.refresh(cargo)
    return cargo


async def cambiar_estado_cargo(
    db: AsyncSession, cargo_id: int, activo: bool
) -> Cargo:
    cargo = await get_cargo_by_id(db, cargo_id)
    cargo.activo = activo
    await db.commit()
    await db.refresh(cargo)
    return cargo