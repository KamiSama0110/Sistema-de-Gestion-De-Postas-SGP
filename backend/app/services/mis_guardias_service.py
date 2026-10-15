from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.enums import EstadoGuardiaCuadroEnum, EstadoPlanGuardiaEnum
from app.models.plan_guardia_cuadro import GuardiaCuadro, PlanGuardiaCuadro
from app.services.guardia_cuadro_service import (
    _construir_intervalo_franja,
    _transicionar_guardia,
    get_guardia_by_id,
)

_RELACIONES = (
    selectinload(GuardiaCuadro.plan),
    selectinload(GuardiaCuadro.cuadro),
    selectinload(GuardiaCuadro.franja),
)


async def _get_guardia_aprobada(
    db: AsyncSession, guardia_id: int, cuadro_id: int
) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    plan_aprobado = (
        guardia.plan is not None
        and guardia.plan.estado == EstadoPlanGuardiaEnum.aprobado
    )
    if guardia.cuadro_id != cuadro_id or not plan_aprobado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guardia no encontrada",
        )
    return guardia


async def listar_mis_guardias(
    db: AsyncSession,
    cuadro_id: int,
    page: int = 1,
    size: int = 20,
    anio: int | None = None,
    mes: int | None = None,
    estado: EstadoGuardiaCuadroEnum | None = None,
) -> dict:
    query = (
        select(GuardiaCuadro)
        .options(*_RELACIONES)
        .join(PlanGuardiaCuadro, PlanGuardiaCuadro.id == GuardiaCuadro.plan_id)
        .where(
            GuardiaCuadro.cuadro_id == cuadro_id,
            PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
        )
    )
    if anio is not None:
        query = query.where(extract("year", GuardiaCuadro.fecha) == anio)
    if mes is not None:
        query = query.where(extract("month", GuardiaCuadro.fecha) == mes)
    if estado is not None:
        query = query.where(GuardiaCuadro.estado == estado)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(GuardiaCuadro.fecha, GuardiaCuadro.id)
    query = query.offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def get_mi_guardia(
    db: AsyncSession, guardia_id: int, cuadro_id: int
) -> GuardiaCuadro:
    return await _get_guardia_aprobada(db, guardia_id, cuadro_id)


async def mi_planificacion(
    db: AsyncSession, cuadro_id: int, anio: int, mes: int
) -> dict:
    result = await db.execute(
        select(PlanGuardiaCuadro).where(
            PlanGuardiaCuadro.anio == anio,
            PlanGuardiaCuadro.mes == mes,
            PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
        )
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        return {"plan_id": None, "anio": anio, "mes": mes, "guardias": []}

    guardias = (
        (
            await db.execute(
                select(GuardiaCuadro)
                .options(*_RELACIONES)
                .where(
                    GuardiaCuadro.plan_id == plan.id,
                    GuardiaCuadro.cuadro_id == cuadro_id,
                )
                .order_by(GuardiaCuadro.fecha, GuardiaCuadro.id)
            )
        )
        .scalars()
        .all()
    )
    return {
        "plan_id": plan.id,
        "anio": anio,
        "mes": mes,
        "guardias": guardias,
    }


async def iniciar_mi_guardia(
    db: AsyncSession, guardia_id: int, cuadro_id: int
) -> GuardiaCuadro:
    guardia = await _get_guardia_aprobada(db, guardia_id, cuadro_id)
    inicio, fin = _construir_intervalo_franja(guardia.fecha, guardia.franja)
    ventana = timedelta(minutes=settings.CUADRO_VENTANA_INICIO_MIN)
    ahora = datetime.now()
    if not (inicio - ventana <= ahora <= fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Fuera de la ventana para iniciar la guardia: solo se permite "
                f"entre {inicio - ventana:%Y-%m-%d %H:%M} y {fin:%Y-%m-%d %H:%M}"
            ),
        )

    await _transicionar_guardia(db, guardia, EstadoGuardiaCuadroEnum.activa)
    guardia.inicio_real = ahora
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def finalizar_mi_guardia(
    db: AsyncSession, guardia_id: int, cuadro_id: int
) -> GuardiaCuadro:
    guardia = await _get_guardia_aprobada(db, guardia_id, cuadro_id)
    await _transicionar_guardia(db, guardia, EstadoGuardiaCuadroEnum.finalizada)
    guardia.fin_real = datetime.now()
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia
