from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models.guardia import Guardia, Novedad
from app.models.posta import TurnoPosta
from app.models.asp import ASP
from app.models.enums import EstadoGuardiaEnum, TipoNovedadEnum
from app.schemas.guardia import (
    GuardiaCreate, GuardiaUpdate, NovedadCreate,
    ConfirmarLlegadaRequest, FinalizarGuardiaRequest
)
from fastapi import HTTPException, status


def strip_timezone(dt: datetime) -> datetime:
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def calcular_tardanza(
    turno: TurnoPosta,
    hora_llegada: datetime,
    fecha_guardia: Optional[date] = None,
) -> int:
    hora_llegada = strip_timezone(hora_llegada)
    hora_inicio = datetime.combine(fecha_guardia or hora_llegada.date(), turno.hora_inicio)
    diferencia = (hora_llegada - hora_inicio).total_seconds() / 60
    return max(0, int(diferencia))

async def get_guardia_by_id(db: AsyncSession, guardia_id: int) -> Guardia:
    result = await db.execute(
        select(Guardia)
        .options(selectinload(Guardia.novedades))
        .where(Guardia.id == guardia_id)
    )
    guardia = result.scalar_one_or_none()
    if not guardia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Guardia con id {guardia_id} no encontrada",
        )
    return guardia


async def verificar_solapamiento(
    db: AsyncSession, asp_id: int, turno_posta_id: int, fecha: date, excluir_id: Optional[int] = None
) -> bool:
    turno_result = await db.execute(
        select(TurnoPosta).where(TurnoPosta.id == turno_posta_id)
    )
    turno = turno_result.scalar_one_or_none()
    if not turno:
        return False

    query = select(Guardia).where(
        and_(
            Guardia.asp_id == asp_id,
            Guardia.fecha == fecha,
            Guardia.estado != EstadoGuardiaEnum.cancelada,
            Guardia.turno_posta_id != turno_posta_id,
        )
    )
    if excluir_id:
        query = query.where(Guardia.id != excluir_id)

    result = await db.execute(query)
    guardias_existentes = result.scalars().all()

    for g in guardias_existentes:
        turno_existente = await db.execute(
            select(TurnoPosta).where(TurnoPosta.id == g.turno_posta_id)
        )
        te = turno_existente.scalar_one_or_none()
        if te:
            if not (turno.hora_fin <= te.hora_inicio or turno.hora_inicio >= te.hora_fin):
                return True
    return False


async def listar_guardias(
    db: AsyncSession,
    fecha: Optional[date] = None,
    estado: Optional[EstadoGuardiaEnum] = None,
    asp_id: Optional[int] = None,
    posta_id: Optional[int] = None,
) -> list[Guardia]:
    query = select(Guardia).options(
        selectinload(Guardia.novedades),
        selectinload(Guardia.turno_posta),
    )
    if fecha:
        query = query.where(Guardia.fecha == fecha)
    if estado:
        query = query.where(Guardia.estado == estado)
    if asp_id:
        query = query.where(Guardia.asp_id == asp_id)
    if posta_id:
        query = query.join(TurnoPosta).where(TurnoPosta.posta_id == posta_id)
    result = await db.execute(query)
    guardias = result.scalars().all()

    data = []
    for guardia in guardias:
        tardanza = None
        if guardia.hora_inicio_real and guardia.turno_posta:
            tardanza = calcular_tardanza(guardia.turno_posta, guardia.hora_inicio_real, guardia.fecha)
        data.append({
            "id": guardia.id,
            "asp_id": guardia.asp_id,
            "turno_posta_id": guardia.turno_posta_id,
            "fecha": guardia.fecha,
            "estado": guardia.estado,
            "hora_inicio_real": guardia.hora_inicio_real,
            "tardanza_minutos": tardanza,
        })

    return data


async def crear_guardia(db: AsyncSession, datos: GuardiaCreate) -> Guardia:
    asp_result = await db.execute(select(ASP).where(ASP.id == datos.asp_id))
    asp = asp_result.scalar_one_or_none()
    if not asp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ASP con id {datos.asp_id} no encontrado",
        )
    if asp.estado.value != "activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ASP no está activo",
        )

    turno_result = await db.execute(
        select(TurnoPosta).where(TurnoPosta.id == datos.turno_posta_id)
    )
    turno = turno_result.scalar_one_or_none()
    if not turno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id {datos.turno_posta_id} no encontrado",
        )
    if not turno.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El turno seleccionado esta inactivo",
        )

    solapamiento = await verificar_solapamiento(
        db, datos.asp_id, datos.turno_posta_id, datos.fecha
    )
    if solapamiento:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El ASP ya tiene una guardia asignada que se solapa en ese horario",
        )

    guardia = Guardia(**datos.model_dump())
    db.add(guardia)
    await db.commit()
    return await get_guardia_by_id(db, guardia.id)


async def confirmar_llegada(
    db: AsyncSession, guardia_id: int, datos: ConfirmarLlegadaRequest
) -> Guardia:
    guardia = await get_guardia_by_id(db, guardia_id)

    if guardia.estado != EstadoGuardiaEnum.planificada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede confirmar llegada de una guardia en estado {guardia.estado.value}",
        )

    guardia.hora_inicio_real = strip_timezone(datos.hora_llegada)
    guardia.estado = EstadoGuardiaEnum.activa
    await db.commit()
    return await get_guardia_by_id(db, guardia_id)


async def registrar_novedad(
    db: AsyncSession, guardia_id: int, datos: NovedadCreate
) -> Novedad:
    guardia = await get_guardia_by_id(db, guardia_id)

    if guardia.estado != EstadoGuardiaEnum.activa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden registrar novedades en guardias activas",
        )

    novedad = Novedad(guardia_id=guardia_id, **datos.model_dump())
    db.add(novedad)
    await db.commit()
    await db.refresh(novedad)
    return novedad


async def finalizar_guardia(
    db: AsyncSession, guardia_id: int, datos: FinalizarGuardiaRequest
) -> Guardia:
    guardia = await get_guardia_by_id(db, guardia_id)

    if guardia.estado != EstadoGuardiaEnum.activa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede finalizar una guardia en estado {guardia.estado.value}",
        )

    tiene_entrega = any(
        n.tipo == TipoNovedadEnum.entrega_recepcion
        for n in guardia.novedades
    )
    if not tiene_entrega:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debe registrar la novedad de entrega-recepción antes de finalizar la guardia",
        )

    guardia.hora_fin_real = strip_timezone(datos.hora_fin_real)
    guardia.estado = EstadoGuardiaEnum.finalizada
    if datos.observaciones:
        guardia.observaciones = datos.observaciones

    await db.commit()
    return await get_guardia_by_id(db, guardia_id)


async def actualizar_guardia(
    db: AsyncSession, guardia_id: int, datos: GuardiaUpdate
) -> Guardia:
    guardia = await get_guardia_by_id(db, guardia_id)

    if guardia.estado == EstadoGuardiaEnum.finalizada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una guardia finalizada",
        )

    update_data = datos.model_dump(exclude_unset=True)

    if "asp_id" in update_data:
        asp_result = await db.execute(
            select(ASP).where(ASP.id == update_data["asp_id"])
        )
        asp = asp_result.scalar_one_or_none()
        if not asp or asp.estado.value != "activo":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ASP sustituto no existe o no está activo",
            )

    motivo_enviado = "motivo_ausencia" in update_data
    if update_data.get("asp_id") or update_data.get("asp_id") == 0 or motivo_enviado:
        guardia.estado = EstadoGuardiaEnum.ausente

    for campo, valor in update_data.items():
        setattr(guardia, campo, valor)

    await db.commit()
    return await get_guardia_by_id(db, guardia_id)

async def get_guardia_con_tardanza(db: AsyncSession, guardia_id: int) -> dict:
    guardia = await get_guardia_by_id(db, guardia_id)
    tardanza = None
    if guardia.hora_inicio_real:
        turno_result = await db.execute(
            select(TurnoPosta).where(TurnoPosta.id == guardia.turno_posta_id)
        )
        turno = turno_result.scalar_one_or_none()
        if turno:
            tardanza = calcular_tardanza(turno, guardia.hora_inicio_real, guardia.fecha)

    data = {
        "id": guardia.id,
        "asp_id": guardia.asp_id,
        "turno_posta_id": guardia.turno_posta_id,
        "fecha": guardia.fecha,
        "estado": guardia.estado,
        "hora_inicio_real": guardia.hora_inicio_real,
        "hora_fin_real": guardia.hora_fin_real,
        "motivo_ausencia": guardia.motivo_ausencia,
        "observaciones": guardia.observaciones,
        "tardanza_minutos": tardanza,
        "novedades": guardia.novedades,
    }
    return data