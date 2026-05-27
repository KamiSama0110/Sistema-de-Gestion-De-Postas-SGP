from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import SexoEnum, EscolaridadEnum, EstadoASPEnum



class ASP(Base):
    __tablename__ = "asp"

    __table_args__ = (
        CheckConstraint("LENGTH(ci) = 11", name="ck_asp_ci_length"),
        CheckConstraint("fecha_ingreso >= fecha_nacimiento", name="ck_asp_fechas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ci: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[SexoEnum] = mapped_column(nullable=False)
    nivel_escolaridad: Mapped[EscolaridadEnum] = mapped_column(nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[EstadoASPEnum] = mapped_column(nullable=False, default=EstadoASPEnum.activo, index=True)
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    cargo_id: Mapped[int] = mapped_column(ForeignKey("cargo.id"), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    cargo: Mapped["Cargo"] = relationship(back_populates="asp_list")
    guardias: Mapped[list["Guardia"]] = relationship(
        back_populates="asp",
        foreign_keys="Guardia.asp_id",
    )