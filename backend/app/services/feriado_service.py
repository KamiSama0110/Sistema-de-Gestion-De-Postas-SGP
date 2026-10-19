from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cuadro import Feriado
from app.models.enums import EstadoGuardiaCuadroEnum, EstadoPlanGuardiaEnum
from app.models.plan_guardia_cuadro import GuardiaCuadro, PlanGuardiaCuadro
from app.schemas.feriado import FeriadoCreate, FeriadoUpdate

FERIADOS_FIJOS = [
    (1, 1, "Año Nuevo"),
    (1, 2, "Día de la Liberación"),
    (5, 1, "Día del Trabajo"),
    (7, 25, "Conmemoración del Asalto al Cuartel Moncada"),
    (7, 26, "Día de la Rebeldía Nacional"),
    (7, 27, "Día de la Rebeldía Nacional"),
    (10, 10, "Inicio de las Guerras de Independencia"),
    (12, 25, "Navidad"),
]


async def get_feriado_by_id(db: AsyncSession, feriado_id: int) -> Feriado:
    result = await db.execute(select(Feriado).where(Feriado.id == feriado_id))
    feriado = result.scalar_one_or_none()
    if not feriado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feriado no encontrado"
        )
    return feriado


async def get_feriado_by_fecha(db: AsyncSession, fecha: date) -> Feriado | None:
    result = await db.execute(select(Feriado).where(func.date(Feriado.fecha) == fecha))
    return result.scalar_one_or_none()


async def listar_feriados(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    anio: int | None = None,
) -> dict:
    query = select(Feriado)

    if anio:
        query = query.where(func.extract("year", Feriado.fecha) == anio)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Feriado.fecha.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def _desasignar_guardias_no_aprobadas(
    db: AsyncSession, fecha: date
) -> list[dict]:
    result = await db.execute(
        select(GuardiaCuadro)
        .join(PlanGuardiaCuadro, PlanGuardiaCuadro.id == GuardiaCuadro.plan_id)
        .options(
            selectinload(GuardiaCuadro.plan),
            selectinload(GuardiaCuadro.cuadro),
            selectinload(GuardiaCuadro.franja),
        )
        .where(
            GuardiaCuadro.fecha == fecha,
            GuardiaCuadro.estado == EstadoGuardiaCuadroEnum.planificada,
            PlanGuardiaCuadro.estado != EstadoPlanGuardiaEnum.aprobado,
        )
        .order_by(GuardiaCuadro.id)
    )

    desasignadas = []
    for guardia in result.scalars().all():
        desasignadas.append(
            {
                "guardia_id": guardia.id,
                "plan_id": guardia.plan_id,
                "anio": guardia.plan.anio,
                "mes": guardia.plan.mes,
                "fecha": guardia.fecha,
                "cuadro_id": guardia.cuadro_id,
                "cuadro_nombre": (
                    f"{guardia.cuadro.nombre} {guardia.cuadro.apellidos}"
                    if guardia.cuadro
                    else ""
                ),
                "franja_nombre": guardia.franja.nombre if guardia.franja else None,
            }
        )
        await db.delete(guardia)

    return desasignadas


async def crear_feriado(db: AsyncSession, datos: FeriadoCreate) -> Feriado:
    existing = await get_feriado_by_fecha(db, datos.fecha)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un feriado en esa fecha",
        )

    feriado = Feriado(
        fecha=datetime.combine(datos.fecha, datetime.min.time()),
        descripcion=datos.descripcion,
    )
    db.add(feriado)
    desasignadas = await _desasignar_guardias_no_aprobadas(db, datos.fecha)
    await db.commit()
    await db.refresh(feriado)
    feriado.guardias_desasignadas = desasignadas
    return feriado


async def actualizar_feriado(
    db: AsyncSession, feriado_id: int, datos: FeriadoUpdate
) -> Feriado:
    feriado = await get_feriado_by_id(db, feriado_id)

    update_data = datos.model_dump(exclude_unset=True)
    fecha_afectada: date | None = None

    if "fecha" in update_data and update_data["fecha"] is not None:
        new_fecha = update_data["fecha"]
        existing = await get_feriado_by_fecha(db, new_fecha)
        if existing and existing.id != feriado_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un feriado en esa fecha",
            )
        update_data["fecha"] = datetime.combine(new_fecha, datetime.min.time())
        fecha_afectada = new_fecha

    for field, value in update_data.items():
        setattr(feriado, field, value)

    desasignadas = (
        await _desasignar_guardias_no_aprobadas(db, fecha_afectada)
        if fecha_afectada is not None
        else []
    )

    await db.commit()
    await db.refresh(feriado)
    feriado.guardias_desasignadas = desasignadas
    return feriado


async def eliminar_feriado(db: AsyncSession, feriado_id: int) -> None:
    feriado = await get_feriado_by_id(db, feriado_id)
    await db.delete(feriado)
    await db.commit()


async def get_feriados_sugeridos(db: AsyncSession, anio: int) -> list[dict]:
    sugeridos = []
    for mes, dia, descripcion in FERIADOS_FIJOS:
        fecha = date(anio, mes, dia)
        sugeridos.append({"fecha": fecha, "descripcion": descripcion})
    return sugeridos


async def cargar_feriados_sugeridos(db: AsyncSession, anio: int) -> dict:
    sugeridos = await get_feriados_sugeridos(db, anio)
    creados = 0
    omitidos = 0
    desasignadas: list[dict] = []

    for s in sugeridos:
        existing = await get_feriado_by_fecha(db, s["fecha"])
        if existing:
            omitidos += 1
        else:
            feriado = Feriado(
                fecha=datetime.combine(s["fecha"], datetime.min.time()),
                descripcion=s["descripcion"],
            )
            db.add(feriado)
            desasignadas.extend(
                await _desasignar_guardias_no_aprobadas(db, s["fecha"])
            )
            creados += 1

    await db.commit()
    return {
        "creados": creados,
        "omitidos": omitidos,
        "guardias_desasignadas": desasignadas,
    }
