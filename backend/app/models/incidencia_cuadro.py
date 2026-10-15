from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TipoNovedadEnum, SeveridadEnum


class IncidenciaCuadro(Base):
    __tablename__ = "incidencia_cuadro"

    id: Mapped[int] = mapped_column(primary_key=True)
    guardia_cuadro_id: Mapped[int] = mapped_column(
        ForeignKey("guardia_cuadro.id"), nullable=False, index=True
    )
    tipo: Mapped[TipoNovedadEnum] = mapped_column(nullable=False)
    severidad: Mapped[SeveridadEnum] = mapped_column(
        nullable=False, default=SeveridadEnum.baja
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    posta_id: Mapped[int | None] = mapped_column(
        ForeignKey("posta.id"), nullable=True, index=True
    )
    asp_id: Mapped[int | None] = mapped_column(
        ForeignKey("asp.id"), nullable=True, index=True
    )
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    acciones_tomadas: Mapped[str | None] = mapped_column(Text, nullable=True)
    requiere_seguimiento: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    guardia: Mapped["GuardiaCuadro"] = relationship(back_populates="incidencias")
    posta: Mapped["Posta | None"] = relationship()
    asp: Mapped["ASP | None"] = relationship()

    @property
    def posta_nombre(self) -> str | None:
        return self.posta.nombre if self.posta else None

    @property
    def asp_nombre(self) -> str | None:
        if self.asp is None:
            return None
        return f"{self.asp.nombre} {self.asp.apellidos}"

    @property
    def cuadro_nombre(self) -> str:
        if self.guardia is None or self.guardia.cuadro is None:
            return ""
        return f"{self.guardia.cuadro.nombre} {self.guardia.cuadro.apellidos}"

    @property
    def cuadro_id(self) -> int | None:
        return self.guardia.cuadro_id if self.guardia else None
