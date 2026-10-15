from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cuadro import Cuadro
from app.models.enums import EstadoGuardiaCuadroEnum, EstadoPlanGuardiaEnum
from app.models.plan_guardia_cuadro import GuardiaCuadro, PlanGuardiaCuadro
from app.schemas.plan import (
    GuardiaCuadroCreate,
    GuardiaCuadroUpdate,
    PlanCreate,
    PlanRechazar,
    PlanUpdate,
)
from app.schemas.plan import (
    IncumplirGuardiaRequest,
    CancelarGuardiaCuadroRequest,
)
from app.services.cuadro_service import get_cuadro_by_id
from app.services.feriado_service import get_feriado_by_fecha
from app.services.franja_service import get_franja_by_id

MAX_GUARDIAS_CUADRO_POR_MES = 1

TRANSICIONES_PLAN = {
    "borrador": {"pendiente_aprobacion"},
    "pendiente_aprobacion": {"aprobado", "rechazado"},
    "rechazado": {"borrador"},
    "aprobado": set(),
}

TRANSICIONES_GUARDIA_CUADRO = {
    "planificada": {"activa", "incumplida", "cancelada"},
    "activa": {"finalizada", "incumplida"},
    "finalizada": set(),
    "incumplida": set(),
    "cancelada": set(),
}


def _construir_intervalo_franja(fecha: date, franja) -> tuple[datetime, datetime]:
    hora_inicio = time.fromisoformat(franja.hora_inicio)
    hora_fin = time.fromisoformat(franja.hora_fin)
    inicio = datetime.combine(fecha, hora_inicio)
    if hora_fin < hora_inicio:
        fin = datetime.combine(fecha + timedelta(days=1), hora_fin)
    else:
        fin = datetime.combine(fecha, hora_fin)
    return inicio, fin


async def get_plan_by_id(db: AsyncSession, plan_id: int) -> PlanGuardiaCuadro:
    result = await db.execute(
        select(PlanGuardiaCuadro).where(PlanGuardiaCuadro.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado"
        )
    return plan


async def get_plan_by_anio_mes(
    db: AsyncSession, anio: int, mes: int
) -> PlanGuardiaCuadro | None:
    result = await db.execute(
        select(PlanGuardiaCuadro).where(
            PlanGuardiaCuadro.anio == anio, PlanGuardiaCuadro.mes == mes
        )
    )
    return result.scalar_one_or_none()


async def evaluar_asignacion(
    db: AsyncSession,
    plan: PlanGuardiaCuadro,
    cuadro_id: int,
    fecha: date,
    franja_id: int,
    excluir_guardia_id: int | None = None,
) -> tuple[bool, str | None]:
    """Evalúa las reglas de asignación de un cuadro a un slot del plan.

    Devuelve (elegible, motivo). Si elegible es True, motivo es None.
    El orden de las comprobaciones define el mensaje de descarte.
    """
    cuadro = await get_cuadro_by_id(db, cuadro_id)
    franja = await get_franja_by_id(db, franja_id)

    # 1. El cuadro está activo
    if not cuadro.activo:
        return False, "El cuadro está inactivo"

    # 2. La fecha pertenece al mes y año del plan
    if fecha.year != plan.anio or fecha.month != plan.mes:
        return False, "La fecha no corresponde al mes del plan"

    # 3. La franja está activa y aplica ese día de la semana
    if not franja.activa:
        return False, "La franja está inactiva"
    if fecha.weekday() not in franja.dias_semana:
        return False, "La franja no aplica ese día de la semana"

    # 4. La fecha no es feriado
    feriado = await get_feriado_by_fecha(db, fecha)
    if feriado:
        return False, "Día feriado"

    # 5. El sexo del cuadro coincide con sexo_permitido de la franja
    if cuadro.sexo != franja.sexo_permitido:
        return False, "El sexo del cuadro no coincide con la franja"

    # 6. sin_guardia_vie_dom: ni viernes (4) ni sábado (5) ni domingo (6)
    if cuadro.sin_guardia_vie_dom and fecha.weekday() >= 4:
        return False, "El cuadro no recibe guardias de viernes a domingo"

    # 7. La franja ese día no está ocupada en el plan
    slot_query = select(GuardiaCuadro.id).where(
        GuardiaCuadro.plan_id == plan.id,
        GuardiaCuadro.fecha == fecha,
        GuardiaCuadro.franja_id == franja.id,
        GuardiaCuadro.estado != EstadoGuardiaCuadroEnum.cancelada,
    )
    if excluir_guardia_id is not None:
        slot_query = slot_query.where(GuardiaCuadro.id != excluir_guardia_id)
    if (await db.execute(slot_query)).scalar_one_or_none() is not None:
        return False, "La franja ya está ocupada ese día"

    # 8. Límite mensual del cuadro en el plan (las canceladas no cuentan)
    count_query = (
        select(func.count())
        .select_from(GuardiaCuadro)
        .where(
            GuardiaCuadro.plan_id == plan.id,
            GuardiaCuadro.cuadro_id == cuadro.id,
            GuardiaCuadro.estado != EstadoGuardiaCuadroEnum.cancelada,
        )
    )
    if excluir_guardia_id is not None:
        count_query = count_query.where(GuardiaCuadro.id != excluir_guardia_id)
    cantidad = (await db.execute(count_query)).scalar() or 0
    if cantidad >= MAX_GUARDIAS_CUADRO_POR_MES:
        return (
            False,
            f"El cuadro ya tiene {MAX_GUARDIAS_CUADRO_POR_MES} guardia este mes",
        )

    # 9. Solape en el tiempo con otras guardias del cuadro (la nocturna
    #    ocupa hasta las 07:00 del día siguiente)
    inicio_nuevo, fin_nuevo = _construir_intervalo_franja(fecha, franja)
    solape_query = (
        select(GuardiaCuadro)
        .options(selectinload(GuardiaCuadro.franja))
        .where(
            GuardiaCuadro.cuadro_id == cuadro.id,
            GuardiaCuadro.estado != EstadoGuardiaCuadroEnum.cancelada,
        )
    )
    if excluir_guardia_id is not None:
        solape_query = solape_query.where(GuardiaCuadro.id != excluir_guardia_id)
    guardias_del_cuadro = (await db.execute(solape_query)).scalars().all()

    for existente in guardias_del_cuadro:
        if not existente.franja:
            continue
        inicio_ex, fin_ex = _construir_intervalo_franja(
            existente.fecha, existente.franja
        )
        if inicio_nuevo < fin_ex and inicio_ex < fin_nuevo:
            return False, "Se solapa con otra guardia del cuadro"

    # PUNTO DE EXTENSIÓN: regla de "esperar al menos dos fines de semana antes
    # de repetir" (pendiente de confirmación con el tutor). Se implementaría
    # aquí consultando las guardias previas del cuadro en planes aprobados.

    return True, None


async def validar_asignacion(
    db: AsyncSession,
    plan: PlanGuardiaCuadro,
    cuadro_id: int,
    fecha: date,
    franja_id: int,
    excluir_guardia_id: int | None = None,
) -> None:
    """Levanta 409 con un mensaje específico si la asignación no es válida."""
    elegible, motivo = await evaluar_asignacion(
        db, plan, cuadro_id, fecha, franja_id, excluir_guardia_id
    )
    if not elegible:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=motivo)


async def listar_planes(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    anio: int | None = None,
    mes: int | None = None,
    estado: EstadoPlanGuardiaEnum | None = None,
) -> dict:
    query = select(PlanGuardiaCuadro)
    if anio is not None:
        query = query.where(PlanGuardiaCuadro.anio == anio)
    if mes is not None:
        query = query.where(PlanGuardiaCuadro.mes == mes)
    if estado is not None:
        query = query.where(PlanGuardiaCuadro.estado == estado)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    conteo_subq = (
        select(GuardiaCuadro.plan_id, func.count().label("cantidad"))
        .group_by(GuardiaCuadro.plan_id)
        .subquery()
    )
    query = query.outerjoin(
        conteo_subq, conteo_subq.c.plan_id == PlanGuardiaCuadro.id
    ).add_columns(func.coalesce(conteo_subq.c.cantidad, 0).label("cantidad_guardias"))
    query = query.order_by(PlanGuardiaCuadro.anio.desc(), PlanGuardiaCuadro.mes.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    filas = result.all()

    items = [
        {
            "id": fila[0].id,
            "anio": fila[0].anio,
            "mes": fila[0].mes,
            "estado": fila[0].estado,
            "generado_automaticamente": fila[0].generado_automaticamente,
            "cantidad_guardias": fila[1],
        }
        for fila in filas
    ]
    return {"total": total, "page": page, "size": size, "items": items}


async def crear_plan(db: AsyncSession, datos: PlanCreate) -> PlanGuardiaCuadro:
    existente = await get_plan_by_anio_mes(db, datos.anio, datos.mes)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un plan para ese mes",
        )
    plan = PlanGuardiaCuadro(
        anio=datos.anio,
        mes=datos.mes,
        estado=EstadoPlanGuardiaEnum.borrador,
        generado_automaticamente=False,
        observaciones=datos.observaciones,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def actualizar_plan(
    db: AsyncSession, plan_id: int, datos: PlanUpdate
) -> PlanGuardiaCuadro:
    plan = await get_plan_by_id(db, plan_id)
    # Una vez aprobado, el admin solo puede editar guardias (ver reglas en
    # las asignaciones). Las observaciones se editan en estado borrador,
    # pendiente_aprobacion y rechazado.
    if plan.estado == EstadoPlanGuardiaEnum.aprobado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plan está aprobado y no se puede modificar",
        )
    if datos.observaciones is not None:
        plan.observaciones = datos.observaciones
    await db.commit()
    await db.refresh(plan)
    return plan


async def eliminar_plan(db: AsyncSession, plan_id: int) -> None:
    plan = await get_plan_by_id(db, plan_id)
    if plan.estado != EstadoPlanGuardiaEnum.borrador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede eliminar un plan en estado borrador",
        )
    # La relación guardias tiene cascade delete-orphan: se borran con el plan
    await db.delete(plan)
    await db.commit()


async def _transicionar_plan(
    db: AsyncSession,
    plan: PlanGuardiaCuadro,
    nuevo_estado: EstadoPlanGuardiaEnum,
) -> None:
    permitidas = TRANSICIONES_PLAN.get(plan.estado.value, set())
    if nuevo_estado.value not in permitidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se puede transicionar de '{plan.estado.value}' "
                f"a '{nuevo_estado.value}'"
            ),
        )
    plan.estado = nuevo_estado
    await db.commit()


async def enviar_plan(db: AsyncSession, plan_id: int) -> PlanGuardiaCuadro:
    plan = await get_plan_by_id(db, plan_id)
    if plan.estado != EstadoPlanGuardiaEnum.borrador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede enviar un plan en estado borrador",
        )
    cantidad = (
        await db.execute(
            select(func.count())
            .select_from(GuardiaCuadro)
            .where(GuardiaCuadro.plan_id == plan.id)
        )
    ).scalar() or 0
    if cantidad == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plan no tiene guardias asignadas",
        )
    await _transicionar_plan(db, plan, EstadoPlanGuardiaEnum.pendiente_aprobacion)
    await db.refresh(plan)
    return plan


async def aprobar_plan(db: AsyncSession, plan_id: int) -> PlanGuardiaCuadro:
    plan = await get_plan_by_id(db, plan_id)
    await _transicionar_plan(db, plan, EstadoPlanGuardiaEnum.aprobado)
    await db.refresh(plan)
    return plan


async def rechazar_plan(
    db: AsyncSession, plan_id: int, datos: PlanRechazar
) -> PlanGuardiaCuadro:
    plan = await get_plan_by_id(db, plan_id)
    if datos.motivo:
        marca = f"Rechazado: {datos.motivo}"
        if plan.observaciones:
            plan.observaciones = f"{plan.observaciones}\n{marca}"
        else:
            plan.observaciones = marca
        await db.flush()
    await _transicionar_plan(db, plan, EstadoPlanGuardiaEnum.rechazado)
    await db.refresh(plan)
    return plan


async def reabrir_plan(db: AsyncSession, plan_id: int) -> PlanGuardiaCuadro:
    plan = await get_plan_by_id(db, plan_id)
    await _transicionar_plan(db, plan, EstadoPlanGuardiaEnum.borrador)
    await db.refresh(plan)
    return plan


async def _puede_editar_guardia(
    plan: PlanGuardiaCuadro, guardia: GuardiaCuadro
) -> bool:
    """Reglas de edición según el estado del plan."""
    if plan.estado in (
        EstadoPlanGuardiaEnum.borrador,
        EstadoPlanGuardiaEnum.pendiente_aprobacion,
    ):
        return True
    if plan.estado == EstadoPlanGuardiaEnum.rechazado:
        return False
    # aprobado: solo guardias planificada con fecha posterior a hoy
    return (
        guardia.estado == EstadoGuardiaCuadroEnum.planificada
        and guardia.fecha > date.today()
    )


async def asignar_guardia(
    db: AsyncSession, plan: PlanGuardiaCuadro, datos: GuardiaCuadroCreate
) -> GuardiaCuadro:
    if plan.estado == EstadoPlanGuardiaEnum.rechazado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plan está rechazado y no se puede modificar",
        )
    if plan.estado == EstadoPlanGuardiaEnum.aprobado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plan está aprobado; solo se pueden editar o borrar guardias",
        )
    await validar_asignacion(db, plan, datos.cuadro_id, datos.fecha, datos.franja_id)
    guardia = GuardiaCuadro(
        plan_id=plan.id,
        cuadro_id=datos.cuadro_id,
        franja_id=datos.franja_id,
        fecha=datos.fecha,
        estado=EstadoGuardiaCuadroEnum.planificada,
    )
    db.add(guardia)
    await db.commit()
    return await get_guardia_by_id(db, guardia.id)


async def get_guardia_by_id(db: AsyncSession, guardia_id: int) -> GuardiaCuadro:
    result = await db.execute(
        select(GuardiaCuadro)
        .options(
            selectinload(GuardiaCuadro.plan),
            selectinload(GuardiaCuadro.cuadro),
            selectinload(GuardiaCuadro.franja),
        )
        .where(GuardiaCuadro.id == guardia_id)
    )
    guardia = result.scalar_one_or_none()
    if not guardia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guardia de cuadro no encontrada",
        )
    return guardia


async def actualizar_guardia(
    db: AsyncSession, guardia_id: int, datos: GuardiaCuadroUpdate
) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    if not _puede_editar_guardia(guardia.plan, guardia):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("No se puede modificar esta guardia con el estado actual del plan"),
        )

    nuevo_cuadro_id = (
        datos.cuadro_id if datos.cuadro_id is not None else guardia.cuadro_id
    )
    nueva_fecha = datos.fecha if datos.fecha is not None else guardia.fecha
    nueva_franja_id = (
        datos.franja_id if datos.franja_id is not None else guardia.franja_id
    )

    await validar_asignacion(
        db, guardia.plan, nuevo_cuadro_id, nueva_fecha, nueva_franja_id, guardia.id
    )

    guardia.cuadro_id = nuevo_cuadro_id
    guardia.fecha = nueva_fecha
    guardia.franja_id = nueva_franja_id
    await db.commit()
    # expire_on_commit=False deja las relaciones viejas en el identity map;
    # las recargamos explícitamente para que la respuesta no quede stale
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def eliminar_guardia(db: AsyncSession, guardia_id: int) -> None:
    guardia = await get_guardia_by_id(db, guardia_id)
    if guardia.estado != EstadoGuardiaCuadroEnum.planificada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede eliminar una guardia en estado planificada",
        )
    if not _puede_editar_guardia(guardia.plan, guardia):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar este plan en su estado actual",
        )
    await db.delete(guardia)
    await db.commit()


def _plan_aprobado(guardia: GuardiaCuadro) -> bool:
    return (
        guardia.plan is not None
        and guardia.plan.estado == EstadoPlanGuardiaEnum.aprobado
    )


async def _transicionar_guardia(
    db: AsyncSession,
    guardia: GuardiaCuadro,
    nuevo_estado: EstadoGuardiaCuadroEnum,
    requerir_aprobado: bool = True,
) -> None:
    if requerir_aprobado and not _plan_aprobado(guardia):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden iniciar, finalizar o incumplir guardias de planes aprobados",
        )
    permitidas = TRANSICIONES_GUARDIA_CUADRO.get(guardia.estado.value, set())
    if nuevo_estado.value not in permitidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se puede transicionar de '{guardia.estado.value}' "
                f"a '{nuevo_estado.value}'"
            ),
        )
    guardia.estado = nuevo_estado


async def iniciar_guardia(db: AsyncSession, guardia_id: int) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    await _transicionar_guardia(db, guardia, EstadoGuardiaCuadroEnum.activa)
    guardia.inicio_real = datetime.now()
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def finalizar_guardia(db: AsyncSession, guardia_id: int) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    await _transicionar_guardia(db, guardia, EstadoGuardiaCuadroEnum.finalizada)
    guardia.fin_real = datetime.now()
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def incumplir_guardia(
    db: AsyncSession, guardia_id: int, datos: IncumplirGuardiaRequest
) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    await _transicionar_guardia(db, guardia, EstadoGuardiaCuadroEnum.incumplida)
    guardia.motivo_incumplimiento = datos.motivo
    guardia.justificada = datos.justificada
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def cancelar_guardia(
    db: AsyncSession, guardia_id: int, datos: CancelarGuardiaCuadroRequest
) -> GuardiaCuadro:
    guardia = await get_guardia_by_id(db, guardia_id)
    await _transicionar_guardia(
        db, guardia, EstadoGuardiaCuadroEnum.cancelada, requerir_aprobado=False
    )
    guardia.motivo_cancelacion = datos.motivo
    await db.commit()
    await db.refresh(guardia, ["plan", "cuadro", "franja"])
    return guardia


async def listar_guardias(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    plan_id: int | None = None,
    cuadro_id: int | None = None,
    estado: EstadoGuardiaCuadroEnum | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> dict:
    query = select(GuardiaCuadro).options(
        selectinload(GuardiaCuadro.cuadro), selectinload(GuardiaCuadro.franja)
    )
    if plan_id is not None:
        query = query.where(GuardiaCuadro.plan_id == plan_id)
    if cuadro_id is not None:
        query = query.where(GuardiaCuadro.cuadro_id == cuadro_id)
    if estado is not None:
        query = query.where(GuardiaCuadro.estado == estado)
    if desde is not None:
        query = query.where(GuardiaCuadro.fecha >= desde)
    if hasta is not None:
        query = query.where(GuardiaCuadro.fecha <= hasta)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(GuardiaCuadro.fecha, GuardiaCuadro.id)
    query = query.offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def generar_calendario(db: AsyncSession, plan: PlanGuardiaCuadro) -> dict:
    """Calendario mensual: una entrada por día con sus franjas y guardias."""
    dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dia_max = dias_por_mes[plan.mes - 1]
    if plan.mes == 2 and (
        plan.anio % 4 == 0 and (plan.anio % 100 != 0 or plan.anio % 400 == 0)
    ):
        dia_max = 29

    franjas = await get_franjas_activas(db)
    guardias = (
        (
            await db.execute(
                select(GuardiaCuadro)
                .options(
                    selectinload(GuardiaCuadro.cuadro),
                    selectinload(GuardiaCuadro.franja),
                )
                .where(GuardiaCuadro.plan_id == plan.id)
            )
        )
        .scalars()
        .all()
    )
    guardias_por_slot = {(g.fecha, g.franja_id): g for g in guardias}

    dias = []
    slots_totales = 0
    cubiertos = 0
    feriados = 0

    for dia_num in range(1, dia_max + 1):
        fecha = date(plan.anio, plan.mes, dia_num)
        feriado = await get_feriado_by_fecha(db, fecha)
        es_feriado = feriado is not None
        if es_feriado:
            feriados += 1

        franjas_dia = []
        for franja in franjas:
            aplica = (
                franja.activa
                and fecha.weekday() in franja.dias_semana
                and not es_feriado
            )
            guardia_info = None
            if aplica:
                slots_totales += 1
                guardia = guardias_por_slot.get((fecha, franja.id))
                if guardia and guardia.estado != EstadoGuardiaCuadroEnum.cancelada:
                    cubiertos += 1
                    guardia_info = {
                        "id": guardia.id,
                        "cuadro_id": guardia.cuadro_id,
                        "cuadro_nombre": f"{guardia.cuadro.nombre} {guardia.cuadro.apellidos}",
                        "estado": guardia.estado.value,
                    }
            franjas_dia.append(
                {
                    "franja_id": franja.id,
                    "nombre": franja.nombre,
                    "aplica": aplica,
                    "guardia": guardia_info,
                }
            )

        dias.append(
            {
                "fecha": fecha,
                "dia_semana": fecha.weekday(),
                "es_feriado": es_feriado,
                "feriado_descripcion": feriado.descripcion if feriado else None,
                "franjas": franjas_dia,
            }
        )

    return {
        "plan_id": plan.id,
        "anio": plan.anio,
        "mes": plan.mes,
        "dias": dias,
        "resumen": {
            "slots_totales": slots_totales,
            "cubiertos": cubiertos,
            "sin_cubrir": slots_totales - cubiertos,
            "feriados": feriados,
        },
    }


async def get_franjas_activas(db: AsyncSession) -> list:
    from app.services.franja_service import listar_franjas

    franjas = await listar_franjas(db)
    return [f for f in franjas if f.activa]


async def get_candidatos(
    db: AsyncSession,
    plan: PlanGuardiaCuadro,
    fecha: date,
    franja_id: int,
) -> dict:
    """Cuadros elegibles y descartados para un slot, con el motivo de descarte."""
    # Población: todos los activo e inactivo (los inactivos aparecen descartados)
    result = await db.execute(select(Cuadro))
    cuadros = result.scalars().all()

    elegibles = []
    descartados = []

    for cuadro in cuadros:
        nombre = f"{cuadro.nombre} {cuadro.apellidos}"
        if not cuadro.activo:
            descartados.append(
                {
                    "cuadro_id": cuadro.id,
                    "cuadro_nombre": nombre,
                    "motivo": "El cuadro está inactivo",
                }
            )
            continue
        elegible, motivo = await evaluar_asignacion(
            db, plan, cuadro.id, fecha, franja_id
        )
        if elegible:
            elegibles.append(
                {"cuadro_id": cuadro.id, "cuadro_nombre": nombre, "activo": True}
            )
        else:
            descartados.append(
                {"cuadro_id": cuadro.id, "cuadro_nombre": nombre, "motivo": motivo}
            )

    return {
        "fecha": fecha,
        "franja_id": franja_id,
        "elegibles": elegibles,
        "descartados": descartados,
    }
