from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.guardia import Guardia, Novedad
from app.models.posta import Posta, TurnoPosta
from app.models.asp import ASP
from app.models.enums import EstadoGuardiaEnum, TipoNovedadEnum
from app.services.guardia_service import calcular_tardanza
from app.schemas.reporte import (
    ReporteCoberturaResponse, CoberturaPosta,
    ReporteAusentismoResponse, AusentismoASP,
    ReporteHorasResponse, HorasASP,
    ReporteIncidenciasResponse, IncidenciaItem,
    ReporteTardanzasResponse, TardanzaASP,
)


async def reporte_cobertura(
    db: AsyncSession, fecha_desde: date, fecha_hasta: date
) -> ReporteCoberturaResponse:
    guardias_result = await db.execute(
        select(Guardia)
        .where(and_(Guardia.fecha >= fecha_desde, Guardia.fecha <= fecha_hasta))
        .options(selectinload(Guardia.turno_posta))
    )
    guardias = guardias_result.scalars().all()

    postas_result = await db.execute(select(Posta))
    postas = {p.id: p for p in postas_result.scalars().all()}

    stats = {}
    for g in guardias:
        posta_id = g.turno_posta.posta_id
        if posta_id not in stats:
            stats[posta_id] = {"planificadas": 0, "finalizadas": 0, "ausentes": 0}
        stats[posta_id]["planificadas"] += 1
        if g.estado == EstadoGuardiaEnum.finalizada:
            stats[posta_id]["finalizadas"] += 1
        elif g.estado == EstadoGuardiaEnum.ausente:
            stats[posta_id]["ausentes"] += 1

    por_posta = []
    total_planificadas = 0
    total_finalizadas = 0

    for posta_id, s in stats.items():
        pct = (s["finalizadas"] / s["planificadas"] * 100) if s["planificadas"] > 0 else 0
        por_posta.append(CoberturaPosta(
            posta_id=posta_id,
            posta_nombre=postas[posta_id].nombre if posta_id in postas else f"Posta {posta_id}",
            planificadas=s["planificadas"],
            finalizadas=s["finalizadas"],
            ausentes=s["ausentes"],
            porcentaje_cobertura=round(pct, 1),
        ))
        total_planificadas += s["planificadas"]
        total_finalizadas += s["finalizadas"]

    por_posta.sort(key=lambda x: x.porcentaje_cobertura)
    cobertura_general = (total_finalizadas / total_planificadas * 100) if total_planificadas > 0 else 0

    return ReporteCoberturaResponse(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        cobertura_general=round(cobertura_general, 1),
        total_planificadas=total_planificadas,
        total_finalizadas=total_finalizadas,
        total_sin_cubrir=total_planificadas - total_finalizadas,
        por_posta=por_posta,
    )


async def reporte_ausentismo(
    db: AsyncSession, fecha_desde: date, fecha_hasta: date
) -> ReporteAusentismoResponse:
    guardias_result = await db.execute(
        select(Guardia)
        .where(and_(Guardia.fecha >= fecha_desde, Guardia.fecha <= fecha_hasta))
    )
    guardias = guardias_result.scalars().all()

    asps_result = await db.execute(select(ASP))
    asps = {a.id: f"{a.nombre} {a.apellidos}" for a in asps_result.scalars().all()}

    stats = {}
    total_ausencias = 0
    sin_cubrir = 0

    for g in guardias:
        if g.estado == EstadoGuardiaEnum.ausente:
            total_ausencias += 1
            sin_cubrir += 1
            asp_id = g.asp_id
            if asp_id not in stats:
                stats[asp_id] = {"total": 0, "justificadas": 0, "injustificadas": 0}
            stats[asp_id]["total"] += 1
            if g.motivo_ausencia:
                stats[asp_id]["justificadas"] += 1
            else:
                stats[asp_id]["injustificadas"] += 1

    por_asp = [
        AusentismoASP(
            asp_id=asp_id,
            asp_nombre=asps.get(asp_id, f"ASP {asp_id}"),
            total_ausencias=s["total"],
            justificadas=s["justificadas"],
            injustificadas=s["injustificadas"],
        )
        for asp_id, s in stats.items()
    ]
    por_asp.sort(key=lambda x: x.total_ausencias, reverse=True)

    total_planificadas = len(guardias)
    pct = (total_ausencias / total_planificadas * 100) if total_planificadas > 0 else 0

    return ReporteAusentismoResponse(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_planificadas=total_planificadas,
        total_ausencias=total_ausencias,
        porcentaje_ausentismo=round(pct, 1),
        guardias_sin_cubrir=sin_cubrir,
        por_asp=por_asp,
    )


async def reporte_horas(
    db: AsyncSession, fecha_desde: date, fecha_hasta: date
) -> ReporteHorasResponse:
    guardias_result = await db.execute(
        select(Guardia).where(
            and_(
                Guardia.fecha >= fecha_desde,
                Guardia.fecha <= fecha_hasta,
                Guardia.estado == EstadoGuardiaEnum.finalizada,
                Guardia.hora_inicio_real.is_not(None),
                Guardia.hora_fin_real.is_not(None),
            )
        )
    )
    guardias = guardias_result.scalars().all()

    asps_result = await db.execute(select(ASP))
    asps = {a.id: f"{a.nombre} {a.apellidos}" for a in asps_result.scalars().all()}

    stats = {}
    for g in guardias:
        asp_id = g.asp_id
        if asp_id not in stats:
            stats[asp_id] = {"guardias": 0, "horas": 0.0}
        stats[asp_id]["guardias"] += 1
        duracion = (g.hora_fin_real - g.hora_inicio_real).total_seconds() / 3600
        stats[asp_id]["horas"] += duracion

    por_asp = [
        HorasASP(
            asp_id=asp_id,
            asp_nombre=asps.get(asp_id, f"ASP {asp_id}"),
            total_guardias=s["guardias"],
            total_horas=round(s["horas"], 2),
        )
        for asp_id, s in stats.items()
    ]
    por_asp.sort(key=lambda x: x.total_horas, reverse=True)

    return ReporteHorasResponse(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        por_asp=por_asp,
    )


async def reporte_incidencias(
    db: AsyncSession, fecha_desde: date, fecha_hasta: date,
    severidad: str = None, posta_id: int = None
) -> ReporteIncidenciasResponse:
    query = (
        select(Novedad)
        .join(Guardia)
        .join(TurnoPosta)
        .join(Posta)
        .join(ASP, ASP.id == Guardia.asp_id)
        .where(
            and_(
                Guardia.fecha >= fecha_desde,
                Guardia.fecha <= fecha_hasta,
                Novedad.tipo == TipoNovedadEnum.incidente,
            )
        )
        .options(
            selectinload(Novedad.guardia)
        )
    )
    if severidad:
        query = query.where(Novedad.severidad == severidad)
    if posta_id:
        query = query.where(TurnoPosta.posta_id == posta_id)

    result = await db.execute(query)
    novedades = result.scalars().all()

    asps_result = await db.execute(select(ASP))
    asps = {a.id: f"{a.nombre} {a.apellidos}" for a in asps_result.scalars().all()}

    postas_result = await db.execute(select(Posta))
    postas = {p.id: p.nombre for p in postas_result.scalars().all()}

    turnos_result = await db.execute(select(TurnoPosta))
    turnos = {t.id: t.posta_id for t in turnos_result.scalars().all()}

    items = []
    for n in novedades:
        posta_id_turno = turnos.get(n.guardia.turno_posta_id)
        items.append(IncidenciaItem(
            guardia_id=n.guardia_id,
            posta_nombre=postas.get(posta_id_turno, "Desconocida"),
            asp_nombre=asps.get(n.guardia.asp_id, "Desconocido"),
            fecha=n.guardia.fecha,
            fecha_hora=str(n.fecha_hora),
            tipo=n.tipo.value,
            descripcion=n.descripcion,
            severidad=n.severidad.value,
        ))

    items.sort(key=lambda x: x.severidad, reverse=True)

    return ReporteIncidenciasResponse(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_incidencias=len(items),
        items=items,
    )


async def reporte_tardanzas(
    db: AsyncSession, fecha_desde: date, fecha_hasta: date,
    asp_id: int = None
) -> ReporteTardanzasResponse:
    query = (
        select(Guardia)
        .join(TurnoPosta)
        .where(
            and_(
                Guardia.fecha >= fecha_desde,
                Guardia.fecha <= fecha_hasta,
                Guardia.hora_inicio_real.is_not(None),
                Guardia.estado == EstadoGuardiaEnum.finalizada,
            )
        )
        .options(selectinload(Guardia.turno_posta))
    )
    if asp_id:
        query = query.where(Guardia.asp_id == asp_id)

    result = await db.execute(query)
    guardias = result.scalars().all()

    asps_result = await db.execute(select(ASP))
    asps = {a.id: f"{a.nombre} {a.apellidos}" for a in asps_result.scalars().all()}

    stats = {}
    total_tardanzas = 0

    for g in guardias:
        tardanza = calcular_tardanza(g.turno_posta, g.hora_inicio_real, g.fecha)
        if tardanza > 0:
            total_tardanzas += 1
            a_id = g.asp_id
            if a_id not in stats:
                stats[a_id] = {"tardanzas": 0, "minutos": [], "max": 0}
            stats[a_id]["tardanzas"] += 1
            stats[a_id]["minutos"].append(tardanza)
            stats[a_id]["max"] = max(stats[a_id]["max"], tardanza)

    por_asp = [
        TardanzaASP(
            asp_id=a_id,
            asp_nombre=asps.get(a_id, f"ASP {a_id}"),
            total_tardanzas=s["tardanzas"],
            promedio_minutos=round(sum(s["minutos"]) / len(s["minutos"]), 1),
            max_minutos=s["max"],
        )
        for a_id, s in stats.items()
    ]
    por_asp.sort(key=lambda x: x.total_tardanzas, reverse=True)

    return ReporteTardanzasResponse(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_guardias=len(guardias),
        total_tardanzas=total_tardanzas,
        por_asp=por_asp,
    )