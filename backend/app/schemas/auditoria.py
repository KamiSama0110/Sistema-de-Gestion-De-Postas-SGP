from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    fecha: datetime
    usuario: str
    entidad: str
    entidad_id: int
    accion: str
    datos_anteriores: Optional[str] = None
    datos_nuevos: Optional[str] = None
    model_config = {"from_attributes": True}


class AuditDiffCampo(BaseModel):
    campo: str
    antes: Optional[str] = None
    despues: Optional[str] = None


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
