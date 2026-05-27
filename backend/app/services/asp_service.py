from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models.asp import ASP
from app.models.enums import EstadoASPEnum
from app.schemas.asp import ASPCreate, ASPUpdate, ASPCambiarEstado
from fastapi import HTTPException, status


async def get_asp_by_id(db: AsyncSession, asp_id: int) -> ASP:
    result = await db.execute(
        select(ASP)
        .options(selectinload(ASP.cargo))
        .where(ASP.id == asp_id)
    )
    asp = result.scalar_one_or_none()
    if not asp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ASP con id {asp_id} no encontrado",
        )
    return asp


async def get_asp_by_ci(db: AsyncSession, ci: str) -> Optional[ASP]:
    result = await db.execute(select(ASP).where(ASP.ci == ci))
    return result.scalar_one_or_none()


async def listar_asp(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    estado: Optional[EstadoASPEnum] = None,
    buscar: Optional[str] = None,
) -> dict:
    query = select(ASP)

    if estado:
        query = query.where(ASP.estado == estado)
    if buscar:
        query = query.where(
            ASP.nombre.ilike(f"%{buscar}%")
            | ASP.apellidos.ilike(f"%{buscar}%")
            | ASP.ci.ilike(f"%{buscar}%")
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def crear_asp(db: AsyncSession, datos: ASPCreate) -> ASP:
    existente = await get_asp_by_ci(db, datos.ci)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un ASP con el CI {datos.ci}",
        )

    asp = ASP(**datos.model_dump())
    db.add(asp)
    await db.commit()
    await db.refresh(asp)
    return asp


async def actualizar_asp(db: AsyncSession, asp_id: int, datos: ASPUpdate) -> ASP:
    asp = await get_asp_by_id(db, asp_id)

    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(asp, campo, valor)

    await db.commit()
    await db.refresh(asp)
    return asp


async def cambiar_estado_asp(
    db: AsyncSession, asp_id: int, datos: ASPCambiarEstado
) -> ASP:
    asp = await get_asp_by_id(db, asp_id)
    asp.estado = datos.estado
    if datos.observacion:
        asp.observaciones = datos.observacion
    await db.commit()
    await db.refresh(asp)
    return asp
