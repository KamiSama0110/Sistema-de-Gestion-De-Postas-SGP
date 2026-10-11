from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    fecha: datetime
    usuario: str
    entidad: str
    entidad_id: int
    accion: str
    datos_anteriores: str | None = None
    datos_nuevos: str | None = None
    model_config = {"from_attributes": True}


class AuditDiffCampo(BaseModel):
    campo: str
    antes: str | None = None
    despues: str | None = None


class AuditDiffResponse(BaseModel):
    entidad: str
    entidad_id: int
    fecha: datetime
    cambios: list[AuditDiffCampo]


class PaginatedAudit(BaseModel):
    total: int
    page: int
    size: int
    items: list[AuditLogResponse]
