from datetime import date, datetime
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from app.models.enums import (
    SexoEnum,
    EscolaridadEnum,
    EstadoASPEnum,
)
from app.utils.validators import (
    add_years,
    texto_no_vacio,
    texto_opcional_no_vacio,
    normalizar_telefono,
    validar_ci_cubano,
    validar_ci_formato,
)


class ASPBase(BaseModel):
    ci: str
    nombre: str
    apellidos: str
    fecha_nacimiento: date
    sexo: SexoEnum
    nivel_escolaridad: EscolaridadEnum
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_ingreso: date
    cargo_id: int
    observaciones: Optional[str] = None

    @field_validator("nombre", "apellidos", "direccion", "observaciones")
    @classmethod
    def validar_textos_no_vacios(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v
        return texto_no_vacio(v, info.field_name)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return normalizar_telefono(v)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: date) -> date:
        hoy = date.today()
        limite_minimo = add_years(hoy, -100)
        limite_maximo = add_years(hoy, -18)
        if v < limite_minimo or v > limite_maximo:
            raise ValueError("La fecha de nacimiento debe estar entre 18 y 100 años")
        return v

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, v: date, info) -> date:
        hoy = date.today()
        fecha_nacimiento = info.data.get("fecha_nacimiento")
        if v > hoy:
            raise ValueError("La fecha de ingreso no puede ser posterior a hoy")
        if fecha_nacimiento:
            minimo_ingreso = add_years(fecha_nacimiento, 18)
            if v < minimo_ingreso:
                raise ValueError(
                    "La fecha de ingreso debe ser al menos 18 años después del nacimiento"
                )
        return v

    @model_validator(mode="after")
    def validar_ci_consistente(self):
        validar_ci_cubano(self.ci, self.fecha_nacimiento, self.sexo)
        return self


class ASPCreate(ASPBase):
    pass


class ASPUpdate(BaseModel):
    ci: Optional[str] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[SexoEnum] = None
    nivel_escolaridad: Optional[EscolaridadEnum] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    cargo_id: Optional[int] = None
    observaciones: Optional[str] = None

    @field_validator("ci")
    @classmethod
    def validar_ci(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validar_ci_formato(v.strip())

    @field_validator("nombre", "apellidos", "direccion", "observaciones")
    @classmethod
    def validar_textos_no_vacios(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v
        return texto_opcional_no_vacio(v, info.field_name)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return normalizar_telefono(v)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        hoy = date.today()
        limite_minimo = add_years(hoy, -100)
        limite_maximo = add_years(hoy, -18)
        if v < limite_minimo or v > limite_maximo:
            raise ValueError("La fecha de nacimiento debe estar entre 18 y 100 años")
        return v

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, v: Optional[date], info) -> Optional[date]:
        if v is None:
            return v
        hoy = date.today()
        if v > hoy:
            raise ValueError("La fecha de ingreso no puede ser posterior a hoy")
        fecha_nacimiento = info.data.get("fecha_nacimiento")
        if fecha_nacimiento:
            minimo_ingreso = add_years(fecha_nacimiento, 18)
            if v < minimo_ingreso:
                raise ValueError(
                    "La fecha de ingreso debe ser al menos 18 años después del nacimiento"
                )
        return v

    @model_validator(mode="after")
    def validar_ci_consistente_update(self):
        if self.ci is not None and self.sexo is not None and self.fecha_nacimiento is not None:
            validar_ci_cubano(self.ci, self.fecha_nacimiento, self.sexo)
        return self


class ASPCambiarEstado(BaseModel):
    estado: EstadoASPEnum
    observacion: Optional[str] = None


class ASPResponse(BaseModel):
    id: int
    ci: str
    nombre: str
    apellidos: str
    fecha_nacimiento: date
    sexo: SexoEnum
    nivel_escolaridad: EscolaridadEnum
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_ingreso: date
    cargo_id: int
    observaciones: Optional[str] = None
    estado: EstadoASPEnum
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class ASPListResponse(BaseModel):
    id: int
    ci: str
    nombre: str
    apellidos: str
    cargo_id: int
    estado: EstadoASPEnum

    model_config = {"from_attributes": True}


class PaginatedASP(BaseModel):
    total: int
    page: int
    size: int
    items: list[ASPListResponse]