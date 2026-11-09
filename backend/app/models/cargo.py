from sqlalchemy import Boolean, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Cargo(Base):
    __tablename__ = "cargo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False,)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # El nombre no distingue mayúsculas ni espacios de más
    __table_args__ = (
        Index("ix_cargo_nombre_lower", func.lower(nombre), unique=True),
    )

    # Relaciones
    asp_list: Mapped[list["ASP"]] = relationship(back_populates="cargo")
