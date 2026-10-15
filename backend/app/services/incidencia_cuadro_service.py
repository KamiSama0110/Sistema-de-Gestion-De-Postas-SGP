from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asp import ASP
from app.models.enums import EstadoASPEnum, EstadoGuardiaCuadroEnum, SeveridadEnum, TipoNovedadEnum
from app.models.incidencia_cuadro import IncidenciaCuadro
from app.models.posta import Posta
from app.models.plan_guardia_cuadro import GuardiaCuadro
from app.schemas.incidencia import IncidenciaCreate, IncidenciaUpdate
from app.services.asp_service import get_asp_by_id
from app.services.posta_service import get_posta_by_id

ESTADOS_PERMITIDOS_INCIDENCIA = {
    EstadoGuardiaCuadroEnum.activa,
    EstadoGuardiaCuadroEnum.finalizada,
}

_RELACIONES = (
    selectinload(IncidenciaCuadro.guardia).selectinload(GuardiaCuadro.cuadro),
    selectinload(IncidenciaCuadro.posta),
    selectinload(IncidenciaCuadro.asp),
)


def _validar_estado_guardia(guardia: GuardiaCuadro) -> None:
    if guardia.estado not in ESTADOS_PERMITIDOS_INCIDENCIA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden registrar incidencias en guardias activas o finalizadas",
        )


async def _validar_vinculos(db: AsyncSession, datos) -> None:
    if datos.posta_id is not None:
        await get_posta_by_id(db, datos.posta_id)
    if datos.asp_id is not None:
        await get_asp_by_id(db, datos.asp_id)


async def _get_incidencia(db: AsyncSession, incidencia_id: int) -> IncidenciaCuadro:
    result = await db.execute(
        select(IncidenciaCuadro)
        .options(*_RELACIONES)
        .where(IncidenciaCuadro.id == incidencia_id)
    )
    incidencia = result.scalar_one_or_none()
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidencia no encontrada",
        )
    return incidencia


async def get_incidencia_by_id(
    db: AsyncSession, incidencia_id: int
) -> IncidenciaCuadro:
    return await _get_incidencia(db, incidencia_id)


async def crear_incidencia(
    db: AsyncSession, guardia: GuardiaCuadro, datos: IncidenciaCreate
) -> IncidenciaCuadro:
    _validar_estado_guardia(guardia)
    await _validar_vinculos(db, datos)

    incidencia = IncidenciaCuadro(
        guardia_cuadro_id=guardia.id,
        tipo=datos.tipo,
        severidad=datos.severidad,
        descripcion=datos.descripcion,
        fecha_hora=datos.fecha_hora or datetime.now(),
        posta_id=datos.posta_id,
        asp_id=datos.asp_id,
        area=datos.area,
        acciones_tomadas=datos.acciones_tomadas,
        requiere_seguimiento=datos.requiere_seguimiento,
    )
    db.add(incidencia)
    await db.commit()
    await db.refresh(incidencia)
    return await _get_incidencia(db, incidencia.id)


async def actualizar_incidencia(
    db: AsyncSession, incidencia: IncidenciaCuadro, datos: IncidenciaUpdate
) -> IncidenciaCuadro:
    update_data = datos.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incidencia, field, value)
    await db.commit()
    return await _get_incidencia(db, incidencia.id)


async def listar_incidencias(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    guardia_id: int | None = None,
    cuadro_id: int | None = None,
    severidad: SeveridadEnum | None = None,
    tipo: TipoNovedadEnum | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    requiere_seguimiento: bool | None = None,
) -> dict:
    query = select(IncidenciaCuadro).options(*_RELACIONES)

    if cuadro_id is not None:
        query = query.join(GuardiaCuadro, GuardiaCuadro.id == IncidenciaCuadro.guardia_cuadro_id)
        query = query.where(GuardiaCuadro.cuadro_id == cuadro_id)
    if guardia_id is not None:
        query = query.where(IncidenciaCuadro.guardia_cuadro_id == guardia_id)
    if severidad is not None:
        query = query.where(IncidenciaCuadro.severidad == severidad)
    if tipo is not None:
        query = query.where(IncidenciaCuadro.tipo == tipo)
    if desde is not None:
        query = query.where(func.date(IncidenciaCuadro.fecha_hora) >= desde)
    if hasta is not None:
        query = query.where(func.date(IncidenciaCuadro.fecha_hora) <= hasta)
    if requiere_seguimiento is not None:
        query = query.where(IncidenciaCuadro.requiere_seguimiento == requiere_seguimiento)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(IncidenciaCuadro.fecha_hora.desc(), IncidenciaCuadro.id.desc())
    query = query.offset((page - 1) * size).limit(size)
    items = (await db.execute(query)).scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def get_incidencia_propia(
    db: AsyncSession, incidencia_id: int, cuadro_id: int
) -> IncidenciaCuadro:
    incidencia = await _get_incidencia(db, incidencia_id)
    if incidencia.guardia is None or incidencia.guardia.cuadro_id != cuadro_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidencia no encontrada",
        )
    return incidencia


async def listar_incidencias_de_guardia(
    db: AsyncSession, guardia_id: int, page: int = 1, size: int = 20
) -> dict:
    return await listar_incidencias(db, page, size, guardia_id=guardia_id)


async def get_opciones(db: AsyncSession) -> dict:
    postas = (
        (
            await db.execute(
                select(Posta).where(Posta.activa.is_(True)).order_by(Posta.nombre)
            )
        )
        .scalars()
        .all()
    )
    asps = (
        (
            await db.execute(
                select(ASP)
                .where(ASP.estado == EstadoASPEnum.activo)
                .order_by(ASP.nombre, ASP.apellidos)
            )
        )
        .scalars()
        .all()
    )
    return {
        "postas": [{"id": p.id, "nombre": p.nombre} for p in postas],
        "asp": [{"id": a.id, "nombre": f"{a.nombre} {a.apellidos}"} for a in asps],
    }
