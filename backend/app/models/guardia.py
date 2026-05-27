from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import EstadoGuardiaEnum, TipoNovedadEnum, SeveridadEnum


class Guardia(Base):
    __tablename__ = "guardia"

    __table_args__ = (
        UniqueConstraint("asp_id", "turno_posta_id", "fecha", name="uq_guardia_asp_turno_fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asp_id: Mapped[int] = mapped_column(ForeignKey("asp.id"), nullable=False, index=True)
    turno_posta_id: Mapped[int] = mapped_column(ForeignKey("turno_posta.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio_real: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hora_fin_real: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[EstadoGuardiaEnum] = mapped_column(
        nullable=False, default=EstadoGuardiaEnum.planificada, index=True
    )
    motivo_ausencia: Mapped[str | None] = mapped_column(String(200), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    asp: Mapped["ASP"] = relationship(
        back_populates="guardias",
        foreign_keys=[asp_id],
    )
    turno_posta: Mapped["TurnoPosta"] = relationship(back_populates="guardias")
    novedades: Mapped[list["Novedad"]] = relationship(
        back_populates="guardia",
        cascade="all, delete-orphan",
    )


class Novedad(Base):
    __tablename__ = "novedad"

    id: Mapped[int] = mapped_column(primary_key=True)
    guardia_id: Mapped[int] = mapped_column(ForeignKey("guardia.id"), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    tipo: Mapped[TipoNovedadEnum] = mapped_column(nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    severidad: Mapped[SeveridadEnum] = mapped_column(
        nullable=False, default=SeveridadEnum.baja
    )

    # Relaciones
    guardia: Mapped["Guardia"] = relationship(back_populates="novedades")