from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models.posta import Posta, TurnoPosta
from app.schemas.posta import PostaCreate, PostaUpdate, TurnoPostaCreate, TurnoPostaUpdate
from fastapi import HTTPException, status


def calcular_cruza_medianoche(hora_inicio, hora_fin) -> bool:
    return hora_fin < hora_inicio


async def get_posta_by_id(db: AsyncSession, posta_id: int) -> Posta:
    result = await db.execute(
        select(Posta)
        .options(selectinload(Posta.turnos))
        .where(Posta.id == posta_id)
    )
    posta = result.scalar_one_or_none()
    if not posta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Posta con id {posta_id} no encontrada",
        )
    return posta


async def listar_postas(
    db: AsyncSession,
    activa: Optional[bool] = None,
    tipo: Optional[str] = None,
    buscar: Optional[str] = None,
) -> list[Posta]:
    query = select(Posta).options(selectinload(Posta.turnos))
    if activa is not None:
        query = query.where(Posta.activa == activa)
    if tipo:
        query = query.where(Posta.tipo == tipo)
    if buscar:
        query = query.where(Posta.nombre.ilike(f"%{buscar}%"))
    result = await db.execute(query)
    return result.scalars().all()


async def crear_posta(db: AsyncSession, datos: PostaCreate) -> Posta:
    existente = await db.execute(
        select(Posta).where(Posta.nombre == datos.nombre)
    )
    if existente.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una posta con el nombre '{datos.nombre}'",
        )
    posta_data = datos.model_dump(exclude={"turnos"})
    posta = Posta(**posta_data)
    db.add(posta)
    await db.flush()

    for turno_data in datos.turnos:
        turno = TurnoPosta(
            posta_id=posta.id,
            cruza_medianoche=calcular_cruza_medianoche(
                turno_data.hora_inicio, turno_data.hora_fin
            ),
            **turno_data.model_dump(),
        )
        db.add(turno)

    await db.commit()

    return await get_posta_by_id(db, posta.id)


async def actualizar_posta(
    db: AsyncSession, posta_id: int, datos: PostaUpdate
) -> Posta:
    posta = await get_posta_by_id(db, posta_id)
    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(posta, campo, valor)
    await db.commit()
    await db.refresh(posta)
    return posta


async def cambiar_estado_posta(
    db: AsyncSession, posta_id: int, activa: bool
) -> Posta:
    posta = await get_posta_by_id(db, posta_id)
    posta.activa = activa
    await db.commit()
    await db.refresh(posta)
    return posta


async def listar_turnos(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    posta_id: Optional[int] = None,
    activo: Optional[bool] = None,
    buscar: Optional[str] = None,
) -> dict:
    def aplicar_filtros(query):
        if posta_id:
            query = query.where(TurnoPosta.posta_id == posta_id)
        if activo is not None:
            query = query.where(TurnoPosta.activo == activo)
        if buscar:
            query = query.where(
                TurnoPosta.nombre.ilike(f"%{buscar}%")
                | Posta.nombre.ilike(f"%{buscar}%")
            )
        return query

    conteo_query = aplicar_filtros(
        select(TurnoPosta.id).join(Posta, TurnoPosta.posta_id == Posta.id)
    )
    total_result = await db.execute(
        select(func.count()).select_from(conteo_query.subquery())
    )
    total = total_result.scalar()

    datos_query = aplicar_filtros(
        select(TurnoPosta, Posta.nombre.label("posta_nombre")).join(
            Posta, TurnoPosta.posta_id == Posta.id
        )
    )
    datos_query = datos_query.order_by(Posta.nombre, TurnoPosta.hora_inicio)
    datos_query = datos_query.offset((page - 1) * size).limit(size)

    result = await db.execute(datos_query)
    filas = result.all()

    items = [
        {
            "id": turno.id,
            "posta_id": turno.posta_id,
            "posta_nombre": posta_nombre,
            "nombre": turno.nombre,
            "hora_inicio": turno.hora_inicio,
            "hora_fin": turno.hora_fin,
            "asp_requeridos": turno.asp_requeridos,
            "cruza_medianoche": turno.cruza_medianoche,
            "activo": turno.activo,
        }
        for turno, posta_nombre in filas
    ]

    return {"total": total, "page": page, "size": size, "items": items}


async def agregar_turno(
    db: AsyncSession, posta_id: int, datos: TurnoPostaCreate
) -> TurnoPosta:
    await get_posta_by_id(db, posta_id)
    turno = TurnoPosta(
        posta_id=posta_id,
        cruza_medianoche=calcular_cruza_medianoche(
            datos.hora_inicio, datos.hora_fin
        ),
        **datos.model_dump(),
    )
    db.add(turno)
    await db.commit()
    await db.refresh(turno)
    return turno


async def get_turno_by_id(db: AsyncSession, turno_id: int) -> TurnoPosta:
    result = await db.execute(
        select(TurnoPosta).where(TurnoPosta.id == turno_id)
    )
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id {turno_id} no encontrado",
        )
    return turno


async def actualizar_turno(
    db: AsyncSession, turno_id: int, datos: TurnoPostaUpdate
) -> TurnoPosta:
    turno = await get_turno_by_id(db, turno_id)
    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(turno, campo, valor)
    if "hora_inicio" in update_data or "hora_fin" in update_data:
        turno.cruza_medianoche = calcular_cruza_medianoche(
            turno.hora_inicio, turno.hora_fin
        )
    await db.commit()
    await db.refresh(turno)
    return turno


async def cambiar_estado_turno(
    db: AsyncSession, turno_id: int, activo: bool
) -> TurnoPosta:
    turno = await get_turno_by_id(db, turno_id)
    turno.activo = activo
    await db.commit()
    await db.refresh(turno)
    return turno