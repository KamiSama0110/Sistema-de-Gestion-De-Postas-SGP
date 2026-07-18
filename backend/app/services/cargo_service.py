from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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
    db: AsyncSession, solo_activos: bool = True, page: int = 1, size: int = 10
) -> dict:
    query = select(Cargo)
    if solo_activos:
        query = query.where(Cargo.activo)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    result = await db.execute(
        query.order_by(Cargo.nombre)
        .offset((page - 1) * size)
        .limit(size)
    )
    cargos = result.scalars().all()
    return {"total": total, "page": page, "size": size, "items": cargos}


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

    if "nombre" in update_data:
        existente = await db.execute(
            select(Cargo).where(
                Cargo.nombre == update_data["nombre"],
                Cargo.id != cargo_id,
            )
        )
        if existente.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cargo con el nombre '{update_data['nombre']}'",
            )

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