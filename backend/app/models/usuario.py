from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)