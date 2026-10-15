import math
import random
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cuadro import Cuadro
from app.models.enums import EstadoGuardiaCuadroEnum, EstadoPlanGuardiaEnum
from app.models.plan_guardia_cuadro import GuardiaCuadro, PlanGuardiaCuadro
from app.schemas.plan import GenerarPlanRequest
from app.services.feriado_service import get_feriado_by_fecha
from app.services.franja_service import listar_franjas
from app.services.guardia_cuadro_service import (
    MAX_GUARDIAS_CUADRO_POR_MES,
    validar_asignacion,
)

_DIAS_POR_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _dias_del_mes(anio: int, mes: int) -> list[date]:
    dia_max = _DIAS_POR_MES[mes - 1]
    if mes == 2 and (anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)):
        dia_max = 29
    return [date(anio, mes, dia) for dia in range(1, dia_max + 1)]


def _ordenar_candidatos(
    candidatos: list[dict],
    historial: dict[int, date | None],
    semilla: int | None,
) -> list[dict]:
    """Prioridad: más tiempo sin guardia primero (sin historial va primero).

    Desempate por id; con semilla, por un orden pseudoaleatorio reproducible.
    """
    orden = sorted(candidatos, key=lambda c: c["cuadro_id"])
    if semilla is not None:
        random.Random(semilla).shuffle(orden)
    orden.sort(
        key=lambda c: (
            0 if historial.get(c["cuadro_id"]) is None else 1,
            historial.get(c["cuadro_id"]) or date.min,
        )
    )
    return orden


def _seleccionar_slots(slots_ordenados: list[dict], k: int) -> list[dict]:
    """Hasta k slots elegidos con espaciado uniforme sobre la lista ordenada."""
    n = len(slots_ordenados)
    if k >= n:
        return list(slots_ordenados)
    if k <= 0:
        return []
    indices = sorted({math.floor((i + 0.5) * n / k) for i in range(k)})
    return [slots_ordenados[i] for i in indices]


def generar_asignaciones(
    cuadros: list[dict],
    slots: list[dict],
    historial: dict[int, date | None],
    semilla: int | None = None,
) -> list[dict]:
    
    asignaciones: list[dict] = []
    for franja_id in sorted({s["franja_id"] for s in slots}):
        slots_franja = sorted(
            (s for s in slots if s["franja_id"] == franja_id),
            key=lambda s: s["fecha"],
        )
        if not slots_franja:
            continue

        sexo = slots_franja[0]["sexo_permitido"]
        candidatos = _ordenar_candidatos(
            [c for c in cuadros if c["sexo"] == sexo], historial, semilla
        )
        seleccionados = _seleccionar_slots(slots_franja, len(candidatos))

        # Viernes a domingo primero (solo sin marca); después lunes a
        # jueves con el resto, incluidos los marcados.
        vie_dom = [s for s in seleccionados if s["es_finde"]]
        lun_jue = [s for s in seleccionados if not s["es_finde"]]

        disponibles = list(candidatos)
        for slot in vie_dom + lun_jue:
            idx = None
            for i, cand in enumerate(disponibles):
                if slot["es_finde"] and cand["sin_guardia_vie_dom"]:
                    continue
                idx = i
                break
            if idx is None:
                continue
            candidato = disponibles.pop(idx)
            asignaciones.append(
                {
                    "fecha": slot["fecha"],
                    "franja_id": franja_id,
                    "cuadro_id": candidato["cuadro_id"],
                }
            )
    return asignaciones


async def generar_plan(
    db: AsyncSession, plan: PlanGuardiaCuadro, datos: GenerarPlanRequest
) -> dict:
    
    if plan.estado != EstadoPlanGuardiaEnum.borrador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede generar un plan en estado borrador",
        )

    if datos.modo == "reemplazar":
        await db.execute(
            delete(GuardiaCuadro).where(
                GuardiaCuadro.plan_id == plan.id,
                GuardiaCuadro.estado == EstadoGuardiaCuadroEnum.planificada,
            )
        )
        await db.commit()

    franjas = [f for f in await listar_franjas(db) if f.activa]
    existentes = (
        await db.execute(
            select(GuardiaCuadro).where(GuardiaCuadro.plan_id == plan.id)
        )
    ).scalars().all()

   
    ocupadas_all: set[tuple[date, int]] = set()
    ocupadas_cubiertas: set[tuple[date, int]] = set()
    conteo_cuadro: dict[int, int] = {}
    for g in existentes:
        ocupadas_all.add((g.fecha, g.franja_id))
        if g.estado != EstadoGuardiaCuadroEnum.cancelada:
            ocupadas_cubiertas.add((g.fecha, g.franja_id))
            conteo_cuadro[g.cuadro_id] = conteo_cuadro.get(g.cuadro_id, 0) + 1

    slots_aplicables: list[dict] = []
    for fecha in _dias_del_mes(plan.anio, plan.mes):
        if await get_feriado_by_fecha(db, fecha):
            continue
        for franja in franjas:
            if fecha.weekday() not in franja.dias_semana:
                continue
            slots_aplicables.append(
                {
                    "fecha": fecha,
                    "franja_id": franja.id,
                    "franja_nombre": franja.nombre,
                    "sexo_permitido": franja.sexo_permitido,
                    "es_finde": fecha.weekday() >= 4,
                }
            )

    slots_libres = [
        s
        for s in slots_aplicables
        if (s["fecha"], s["franja_id"]) not in ocupadas_all
    ]

    cuadros_db = (
        await db.execute(select(Cuadro).where(Cuadro.activo.is_(True)))
    ).scalars().all()

    cuadros: list[dict] = []
    for c in cuadros_db:
        if conteo_cuadro.get(c.id, 0) >= MAX_GUARDIAS_CUADRO_POR_MES:
            continue
        cuadros.append(
            {
                "cuadro_id": c.id,
                "sexo": c.sexo,
                "sin_guardia_vie_dom": c.sin_guardia_vie_dom,
            }
        )

    historial = {
        fila[0]: fila[1]
        for fila in (
            await db.execute(
                select(GuardiaCuadro.cuadro_id, func.max(GuardiaCuadro.fecha))
                .join(
                    PlanGuardiaCuadro,
                    PlanGuardiaCuadro.id == GuardiaCuadro.plan_id,
                )
                .where(PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado)
                .group_by(GuardiaCuadro.cuadro_id)
            )
        ).all()
    }

    asignaciones = generar_asignaciones(cuadros, slots_libres, historial, datos.semilla)

    asignadas: set[tuple[date, int]] = set()
    creadas = 0
    descartadas = 0
    for a in asignaciones:
        try:
            await validar_asignacion(
                db, plan, a["cuadro_id"], a["fecha"], a["franja_id"]
            )
        except HTTPException:
            descartadas += 1
            continue
        db.add(
            GuardiaCuadro(
                plan_id=plan.id,
                cuadro_id=a["cuadro_id"],
                franja_id=a["franja_id"],
                fecha=a["fecha"],
                estado=EstadoGuardiaCuadroEnum.planificada,
            )
        )
        asignadas.add((a["fecha"], a["franja_id"]))
        creadas += 1

    plan.generado_automaticamente = True
    await db.commit()
    await db.refresh(plan)

    cubiertos = len(ocupadas_cubiertas) + creadas
    sin_cubrir = [
        {
            "fecha": s["fecha"],
            "franja_id": s["franja_id"],
            "franja_nombre": s["franja_nombre"],
        }
        for s in slots_aplicables
        if (s["fecha"], s["franja_id"]) not in ocupadas_cubiertas
        and (s["fecha"], s["franja_id"]) not in asignadas
    ]

    asignados_ids = {a["cuadro_id"] for a in asignaciones if (a["fecha"], a["franja_id"]) in asignadas}
    asignados_ids |= {cid for cid, n in conteo_cuadro.items() if n > 0}

    cuadros_sin_asignar = []
    for c in cuadros_db:
        if c.id in asignados_ids:
            continue
        if conteo_cuadro.get(c.id, 0) >= MAX_GUARDIAS_CUADRO_POR_MES:
            motivo = "Ya alcanzó el límite mensual en el plan"
        elif c.sin_guardia_vie_dom:
            motivo = "Marca de viernes a domingo y sin slots entre semana"
        else:
            motivo = "No seleccionado por prioridad"
        cuadros_sin_asignar.append(
            {
                "cuadro_id": c.id,
                "nombre": f"{c.nombre} {c.apellidos}",
                "motivo": motivo,
            }
        )

    advertencias = []
    if descartadas:
        advertencias.append(
            f"{descartadas} asignaciones se descartaron por no superar la validación"
        )

    return {
        "plan_id": plan.id,
        "slots_totales": len(slots_aplicables),
        "cubiertos": cubiertos,
        "creadas": creadas,
        "sin_cubrir": sin_cubrir,
        "cuadros_sin_asignar": cuadros_sin_asignar,
        "advertencias": advertencias,
    }
