import json
import logging
from contextvars import ContextVar
from datetime import date, time, datetime
from enum import Enum
from typing import Any

from sqlalchemy import inspect, event
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import AuditLog

logger = logging.getLogger(__name__)

current_user_var: ContextVar[str] = ContextVar("current_user", default="admin")

_tablas_excluidas: set[str] = {"novedad", "refresh_token"}

_objetos_nuevos_pendientes: list[Any] = []


def _serializar_valor(valor: Any) -> Any:
    if valor is None or isinstance(valor, (int, float, str, bool)):
        return valor
    if isinstance(valor, Enum):
        return valor.value
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, time):
        return valor.isoformat()
    return str(valor)


def _serializar_objeto(obj: Any) -> str:
    mapper = inspect(obj).mapper
    datos: dict[str, Any] = {}
    for col in mapper.column_attrs:
        valor = getattr(obj, col.key)
        datos[col.key] = _serializar_valor(valor)
    return json.dumps(datos, default=_serializar_valor)


@event.listens_for(Session, "before_flush")
def _before_flush(session, flush_context, instances):
    user = current_user_var.get()

    for obj in list(session.new):
        tabla = inspect(obj).mapper.local_table.name
        if tabla in _tablas_excluidas or tabla == "audit_log":
            continue
        _objetos_nuevos_pendientes.append(obj)

    for obj in session.dirty:
        tabla = inspect(obj).mapper.local_table.name
        if tabla in _tablas_excluidas or tabla == "audit_log":
            continue

        state = inspect(obj)
        old: dict[str, Any] = {}
        new: dict[str, Any] = {}
        for attr in state.attrs:
            hist = attr.history
            if not hist.has_changes():
                continue
            old_value = hist.deleted[0] if hist.deleted else hist.unchanged[0] if hist.unchanged else None
            new_value = hist.added[0] if hist.added else getattr(obj, attr.key)
            old[attr.key] = _serializar_valor(old_value)
            new[attr.key] = _serializar_valor(new_value)

        if not old:
            continue

        if "estado" in old or "activo" in old:
            accion = "estado"
        else:
            accion = "actualizar"

        ident = inspect(obj).identity
        if ident is None:
            continue
        pk = ident[0]
        session.add(
            AuditLog(
                usuario=user,
                entidad=inspect(obj).mapper.class_.__name__,
                entidad_id=pk,
                accion=accion,
                datos_anteriores=json.dumps(old, default=_serializar_valor),
                datos_nuevos=json.dumps(new, default=_serializar_valor),
            )
        )


@event.listens_for(Session, "after_flush_postexec")
def _after_flush(session, flush_context):
    if not _objetos_nuevos_pendientes:
        return

    user = current_user_var.get()

    for obj in _objetos_nuevos_pendientes:
        tabla = inspect(obj).mapper.local_table.name
        if tabla in _tablas_excluidas or tabla == "audit_log":
            continue
        ident = inspect(obj).identity
        if ident is None:
            continue
        pk = ident[0]
        session.add(
            AuditLog(
                usuario=user,
                entidad=inspect(obj).mapper.class_.__name__,
                entidad_id=pk,
                accion="crear",
                datos_anteriores=None,
                datos_nuevos=_serializar_objeto(obj),
            )
        )

    _objetos_nuevos_pendientes.clear()


async def registrar_evento_auth(
    db: AsyncSession, accion: str, detalle: str | None = None
):
    user = current_user_var.get()
    db.add(
        AuditLog(
            usuario=user,
            entidad="Auth",
            entidad_id=0,
            accion=accion,
            datos_anteriores=None,
            datos_nuevos=json.dumps({"detalle": detalle}) if detalle else None,
        )
    )
