from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import EstadoPlanGuardiaEnum, EstadoGuardiaCuadroEnum


class PlanGuardiaCuadro(Base):
    __tablename__ = "plan_guardia_cuadro"

    __table_args__ = (
        UniqueConstraint("anio", "mes", name="uq_plan_guardia_anio_mes"),
        CheckConstraint("mes >= 1 AND mes <= 12", name="ck_plan_guardia_mes_rango"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    anio: Mapped[int] = mapped_column(nullable=False)
    mes: Mapped[int] = mapped_column(nullable=False)
    estado: Mapped[EstadoPlanGuardiaEnum] = mapped_column(
        nullable=False, default=EstadoPlanGuardiaEnum.borrador
    )
    generado_automaticamente: Mapped[bool] = mapped_column(default=False, server_default="false")
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    guardias: Mapped[list["GuardiaCuadro"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class GuardiaCuadro(Base):
    __tablename__ = "guardia_cuadro"

    __table_args__ = (
        UniqueConstraint("plan_id", "fecha", "franja_id", name="uq_guardia_cuadro_plan_fecha_franja"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_guardia_cuadro.id"), nullable=False, index=True)
    cuadro_id: Mapped[int] = mapped_column(ForeignKey("cuadro.id"), nullable=False, index=True)
    franja_id: Mapped[int] = mapped_column(ForeignKey("franja_cuadro.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    estado: Mapped[EstadoGuardiaCuadroEnum] = mapped_column(
        nullable=False, default=EstadoGuardiaCuadroEnum.planificada
    )
    inicio_real: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fin_real: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_incumplimiento: Mapped[str | None] = mapped_column(String(300), nullable=True)
    justificada: Mapped[bool | None] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    plan: Mapped["PlanGuardiaCuadro"] = relationship(back_populates="guardias")
    cuadro: Mapped["Cuadro"] = relationship()
    franja: Mapped["FranjaCuadro"] = relationship()

    @property
    def cuadro_nombre(self) -> str:
        if self.cuadro is None:
            return ""
        return f"{self.cuadro.nombre} {self.cuadro.apellidos}"

    @property
    def franja_nombre(self) -> str:
        if self.franja is None:
            return ""
        return self.franja.nombre
