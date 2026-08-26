from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    usuario: Mapped[str] = mapped_column(String(50), index=True)
    entidad: Mapped[str] = mapped_column(String(50), index=True)
    entidad_id: Mapped[int] = mapped_column(index=True)
    accion: Mapped[str] = mapped_column(String(20), index=True)
    datos_anteriores: Mapped[str | None] = mapped_column(Text)
    datos_nuevos: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_audit_entidad_fecha", "entidad", "fecha"),
    )
