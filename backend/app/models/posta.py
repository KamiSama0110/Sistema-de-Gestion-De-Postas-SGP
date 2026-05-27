from datetime import time
from sqlalchemy import String, Boolean, Text, Time, SmallInteger, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TipoPostaEnum


class Posta(Base):
    __tablename__ = "posta"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[TipoPostaEnum] = mapped_column(nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    turnos: Mapped[list["TurnoPosta"]] = relationship(
        back_populates="posta",
        cascade="all, delete-orphan",
    )


class TurnoPosta(Base):
    __tablename__ = "turno_posta"

    __table_args__ = (
        CheckConstraint("asp_requeridos >= 1", name="ck_turno_asp_requeridos"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    posta_id: Mapped[int] = mapped_column(ForeignKey("posta.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    cruza_medianoche: Mapped[bool] = mapped_column(Boolean, default=False)
    asp_requeridos: Mapped[int] = mapped_column(SmallInteger, default=1)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    posta: Mapped["Posta"] = relationship(back_populates="turnos")
    guardias: Mapped[list["Guardia"]] = relationship(back_populates="turno_posta")