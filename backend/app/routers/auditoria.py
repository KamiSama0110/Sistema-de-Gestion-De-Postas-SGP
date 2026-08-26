import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.usuario import Usuario
from app.models.auditoria import AuditLog
from app.schemas.auditoria import (
    AuditLogResponse,
    AuditDiffCampo,
    AuditDiffResponse,
    PaginatedAudit,
)

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


@router.get("", response_model=PaginatedAudit)
async def listar_auditoria(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    entidad: Optional[str] = Query(None, max_length=50),
    accion: Optional[str] = Query(None, max_length=20),
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    query = select(AuditLog)

    if entidad:
        query = query.where(AuditLog.entidad == entidad)
    if accion:
        query = query.where(AuditLog.accion == accion)
    if fecha_desde:
        query = query.where(AuditLog.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.where(AuditLog.fecha <= fecha_hasta)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(AuditLog.fecha.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedAudit(total=total, page=page, size=size, items=items)


@router.get("/{log_id}/diff", response_model=AuditDiffResponse)
async def obtener_diff(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        from fastapi import HTTPException
        raise HTTPException(404, detail="Registro de auditoria no encontrado")

    cambios: list[AuditDiffCampo] = []

    if log.datos_anteriores and log.datos_nuevos:
        anteriores = json.loads(log.datos_anteriores)
        nuevos = json.loads(log.datos_nuevos)
        for campo in anteriores:
            antes = anteriores[campo]
            despues = nuevos.get(campo)
            if antes != despues:
                cambios.append(
                    AuditDiffCampo(
                        campo=campo,
                        antes=str(antes) if antes is not None else None,
                        despues=str(despues) if despues is not None else None,
                    )
                )
    elif log.datos_nuevos:
        nuevos = json.loads(log.datos_nuevos)
        for campo, valor in nuevos.items():
            cambios.append(
                AuditDiffCampo(
                    campo=campo,
                    antes=None,
                    despues=str(valor) if valor is not None else None,
                )
            )

    return AuditDiffResponse(
        entidad=log.entidad,
        entidad_id=log.entidad_id,
        fecha=log.fecha,
        cambios=cambios,
    )
