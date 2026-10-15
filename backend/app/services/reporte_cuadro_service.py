from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cuadro import Cuadro, Feriado
from app.models.enums import (
    EstadoGuardiaCuadroEnum,
    EstadoPlanGuardiaEnum,
    SeveridadEnum,
    TipoNovedadEnum,
)
from app.models.incidencia_cuadro import IncidenciaCuadro
from app.models.plan_guardia_cuadro import GuardiaCuadro, PlanGuardiaCuadro
from app.schemas.reporte_cuadro import (
    CuadroReporteItem,
    FeriadoItem,
    IncumplimientoItem,
    ReporteCumplimientoResponse,
    ReporteDiasSinCubrirResponse,
    ReporteGuardiasPorCuadroResponse,
    ReporteIncidenciasCuadroResponse,
    ReporteIncumplimientosResponse,
    SlotSinCubrir,
)
from app.services.guardia_cuadro_service import get_franjas_activas

_RELACIONES_INCIDENCIA = (
    selectinload(IncidenciaCuadro.guardia).selectinload(GuardiaCuadro.cuadro),
    selectinload(IncidenciaCuadro.posta),
    selectinload(IncidenciaCuadro.asp),
)


def _dias_del_mes(anio: int, mes: int) -> int:
    if mes == 12:
        return 31
    return (date(anio, mes + 1, 1) - date(anio, mes, 1)).days


async def _get_plan(db: AsyncSession, anio: int, mes: int, solo_aprobado: bool):
    query = select(PlanGuardiaCuadro).where(
        PlanGuardiaCuadro.anio == anio, PlanGuardiaCuadro.mes == mes
    )
    if solo_aprobado:
        query = query.where(PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado)
    return (await db.execute(query)).scalar_one_or_none()


async def _slots_y_feriados(db: AsyncSession, anio: int, mes: int):
    franjas = await get_franjas_activas(db)
    feriados_db = (
        (
            await db.execute(
                select(Feriado)
                .where(
                    func.extract("year", Feriado.fecha) == anio,
                    func.extract("month", Feriado.fecha) == mes,
                )
                .order_by(Feriado.fecha)
            )
        )
        .scalars()
        .all()
    )
    feriados_por_fecha = {f.fecha.date(): f for f in feriados_db}

    slots = []
    for dia in range(1, _dias_del_mes(anio, mes) + 1):
        fecha = date(anio, mes, dia)
        if fecha in feriados_por_fecha:
            continue
        for franja in franjas:
            if fecha.weekday() in franja.dias_semana:
                slots.append((fecha, franja))

    return slots, feriados_db


async def reporte_cumplimiento(
    db: AsyncSession, anio: int, mes: int
) -> ReporteCumplimientoResponse:
    plan = await _get_plan(db, anio, mes, solo_aprobado=True)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay un plan aprobado para ese mes",
        )

    guardias = (
        (await db.execute(select(GuardiaCuadro).where(GuardiaCuadro.plan_id == plan.id)))
        .scalars()
        .all()
    )

    slots, _ = await _slots_y_feriados(db, anio, mes)
    slots_totales = len(slots)

    conteos = {estado: 0 for estado in EstadoGuardiaCuadroEnum}
    justificadas = 0
    injustificadas = 0
    for g in guardias:
        conteos[g.estado] += 1
        if g.estado == EstadoGuardiaCuadroEnum.incumplida:
            if g.justificada:
                justificadas += 1
            else:
                injustificadas += 1

    canceladas = conteos[EstadoGuardiaCuadroEnum.cancelada]
    cubiertos = len(guardias) - canceladas
    finalizadas = conteos[EstadoGuardiaCuadroEnum.finalizada]
    incumplidas = conteos[EstadoGuardiaCuadroEnum.incumplida]

    denominador = finalizadas + incumplidas
    porcentaje_cumplimiento = (
        round(finalizadas / denominador * 100, 2) if denominador else None
    )
    porcentaje_cobertura = (
        round(cubiertos / slots_totales * 100, 2) if slots_totales else 0.0
    )

    return ReporteCumplimientoResponse(
        anio=anio,
        mes=mes,
        plan_id=plan.id,
        slots_totales=slots_totales,
        cubiertos=cubiertos,
        sin_cubrir=slots_totales - cubiertos,
        planificadas=conteos[EstadoGuardiaCuadroEnum.planificada],
        activas=conteos[EstadoGuardiaCuadroEnum.activa],
        finalizadas=finalizadas,
        incumplidas=incumplidas,
        incumplidas_justificadas=justificadas,
        incumplidas_injustificadas=injustificadas,
        canceladas=canceladas,
        porcentaje_cumplimiento=porcentaje_cumplimiento,
        porcentaje_cobertura=porcentaje_cobertura,
    )


async def reporte_guardias_por_cuadro(
    db: AsyncSession, desde: date, hasta: date
) -> ReporteGuardiasPorCuadroResponse:
    cuadros = (
        (
            await db.execute(
                select(Cuadro)
                .where(Cuadro.activo.is_(True))
                .order_by(Cuadro.apellidos, Cuadro.nombre)
            )
        )
        .scalars()
        .all()
    )

    guardias = (
        (
            await db.execute(
                select(GuardiaCuadro)
                .join(PlanGuardiaCuadro)
                .where(
                    PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
                    GuardiaCuadro.fecha >= desde,
                    GuardiaCuadro.fecha <= hasta,
                )
            )
        )
        .scalars()
        .all()
    )

    stats: dict[int, dict] = {}
    for g in guardias:
        s = stats.setdefault(g.cuadro_id, {"total": 0, "ultima": None, **{e: 0 for e in EstadoGuardiaCuadroEnum}})
        s["total"] += 1
        s[g.estado] += 1
        if s["ultima"] is None or g.fecha > s["ultima"]:
            s["ultima"] = g.fecha

    items = []
    for c in cuadros:
        s = stats.get(c.id)
        items.append(
            CuadroReporteItem(
                cuadro_id=c.id,
                cuadro_nombre=f"{c.nombre} {c.apellidos}",
                total=s["total"] if s else 0,
                planificadas=s[EstadoGuardiaCuadroEnum.planificada] if s else 0,
                activas=s[EstadoGuardiaCuadroEnum.activa] if s else 0,
                finalizadas=s[EstadoGuardiaCuadroEnum.finalizada] if s else 0,
                incumplidas=s[EstadoGuardiaCuadroEnum.incumplida] if s else 0,
                canceladas=s[EstadoGuardiaCuadroEnum.cancelada] if s else 0,
                ultima_guardia=s["ultima"] if s else None,
            )
        )

    return ReporteGuardiasPorCuadroResponse(
        fecha_desde=desde, fecha_hasta=hasta, items=items
    )


async def reporte_incidencias(
    db: AsyncSession,
    desde: date,
    hasta: date,
    page: int = 1,
    size: int = 20,
    severidad: SeveridadEnum | None = None,
    tipo: TipoNovedadEnum | None = None,
) -> ReporteIncidenciasCuadroResponse:
    query = (
        select(IncidenciaCuadro)
        .join(GuardiaCuadro, GuardiaCuadro.id == IncidenciaCuadro.guardia_cuadro_id)
        .join(PlanGuardiaCuadro, PlanGuardiaCuadro.id == GuardiaCuadro.plan_id)
        .where(
            PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
            func.date(IncidenciaCuadro.fecha_hora) >= desde,
            func.date(IncidenciaCuadro.fecha_hora) <= hasta,
        )
        .options(*_RELACIONES_INCIDENCIA)
    )
    if severidad is not None:
        query = query.where(IncidenciaCuadro.severidad == severidad)
    if tipo is not None:
        query = query.where(IncidenciaCuadro.tipo == tipo)

    incidencias = (await db.execute(query)).scalars().all()

    por_severidad = {s.value: 0 for s in SeveridadEnum}
    por_tipo = {t.value: 0 for t in TipoNovedadEnum}
    requieren_seguimiento = 0
    for i in incidencias:
        por_severidad[i.severidad.value] += 1
        por_tipo[i.tipo.value] += 1
        if i.requiere_seguimiento:
            requieren_seguimiento += 1

    incidencias.sort(key=lambda i: (i.fecha_hora, i.id), reverse=True)
    inicio = (page - 1) * size
    items = incidencias[inicio : inicio + size]

    return ReporteIncidenciasCuadroResponse(
        fecha_desde=desde,
        fecha_hasta=hasta,
        total=len(incidencias),
        por_severidad=por_severidad,
        por_tipo=por_tipo,
        requieren_seguimiento=requieren_seguimiento,
        page=page,
        size=size,
        items=items,
    )


async def reporte_dias_sin_cubrir(
    db: AsyncSession, anio: int, mes: int
) -> ReporteDiasSinCubrirResponse:
    plan = await _get_plan(db, anio, mes, solo_aprobado=False)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay un plan de guardia para ese mes",
        )

    slots, feriados = await _slots_y_feriados(db, anio, mes)

    guardias = (
        (await db.execute(select(GuardiaCuadro).where(GuardiaCuadro.plan_id == plan.id)))
        .scalars()
        .all()
    )
    guardias_por_slot = {(g.fecha, g.franja_id): g for g in guardias}

    dias = []
    for fecha, franja in slots:
        guardia = guardias_por_slot.get((fecha, franja.id))
        if guardia is None:
            dias.append(
                SlotSinCubrir(
                    fecha=fecha,
                    franja_id=franja.id,
                    franja_nombre=franja.nombre,
                    cancelada=False,
                )
            )
        elif guardia.estado == EstadoGuardiaCuadroEnum.cancelada:
            dias.append(
                SlotSinCubrir(
                    fecha=fecha,
                    franja_id=franja.id,
                    franja_nombre=franja.nombre,
                    cancelada=True,
                )
            )

    return ReporteDiasSinCubrirResponse(
        anio=anio,
        mes=mes,
        plan_id=plan.id,
        estado_plan=plan.estado,
        slots_totales=len(slots),
        sin_cubrir=len(dias),
        dias=dias,
        feriados=[
            FeriadoItem(fecha=f.fecha.date(), descripcion=f.descripcion)
            for f in feriados
        ],
    )


async def reporte_incumplimientos(
    db: AsyncSession, desde: date, hasta: date
) -> ReporteIncumplimientosResponse:
    guardias = (
        (
            await db.execute(
                select(GuardiaCuadro)
                .join(PlanGuardiaCuadro)
                .options(
                    selectinload(GuardiaCuadro.cuadro),
                    selectinload(GuardiaCuadro.franja),
                )
                .where(
                    PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
                    GuardiaCuadro.estado == EstadoGuardiaCuadroEnum.incumplida,
                    GuardiaCuadro.fecha >= desde,
                    GuardiaCuadro.fecha <= hasta,
                )
                .order_by(GuardiaCuadro.fecha, GuardiaCuadro.id)
            )
        )
        .scalars()
        .all()
    )

    items = [
        IncumplimientoItem(
            guardia_id=g.id,
            cuadro_id=g.cuadro_id,
            cuadro_nombre=g.cuadro_nombre,
            fecha=g.fecha,
            franja_id=g.franja_id,
            franja_nombre=g.franja_nombre,
            motivo=g.motivo_incumplimiento,
            justificada=bool(g.justificada),
        )
        for g in guardias
    ]

    justificadas = sum(1 for i in items if i.justificada)

    return ReporteIncumplimientosResponse(
        fecha_desde=desde,
        fecha_hasta=hasta,
        total=len(items),
        justificadas=justificadas,
        injustificadas=len(items) - justificadas,
        items=items,
    )
