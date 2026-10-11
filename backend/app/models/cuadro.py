from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import SexoEnum


class Cuadro(Base):
    __tablename__ = "cuadro"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(150), nullable=False)
    ci: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sexo: Mapped[SexoEnum] = mapped_column(nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sin_guardia_vie_dom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="cuadro", foreign_keys="Usuario.cuadro_id", uselist=False)


class FranjaCuadro(Base):
    __tablename__ = "franja_cuadro"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hora_inicio: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    hora_fin: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    dias_semana: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)  # 0=lunes, 6=domingo
    sexo_permitido: Mapped[SexoEnum] = mapped_column(nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Feriado(Base):
    __tablename__ = "feriado"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())