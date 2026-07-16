from datetime import date, datetime
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from app.models.enums import (
    SexoEnum,
    EscolaridadEnum,
    EstadoASPEnum,
)


def _non_empty_str(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} debe ser un string")
    if len(value.strip()) < 1:
        raise ValueError(f"{field_name} no puede estar vacio ni solo espacios")
    return value


def _add_years(base_date: date, years: int) -> date:
    try:
        return base_date.replace(year=base_date.year + years)
    except ValueError:
        # Ajuste para 29 de febrero en anos no bisiestos
        return base_date.replace(year=base_date.year + years, month=2, day=28)


def _normalizar_telefono(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("telefono debe ser un string")
    raw = v.strip().replace(" ", "").replace("-", "")
    if not raw:
        return None
    if raw.startswith("+53") and len(raw) == 11 and raw[3:].isdigit():
        return raw
    if raw.isdigit() and len(raw) == 8:
        return f"+53{raw}"
    raise ValueError("telefono debe tener formato +53 seguido de 8 digitos")


def _validar_ci_cubano(ci: str, fecha_nacimiento: date, sexo: SexoEnum) -> str:
    if not ci.isdigit() or len(ci) != 11:
        raise ValueError("El CI debe tener exactamente 11 dígitos numéricos")

    if ci[:6] != fecha_nacimiento.strftime("%y%m%d"):
        raise ValueError("El CI debe coincidir con la fecha de nacimiento")

    septimo_digito = int(ci[6])
    if sexo == SexoEnum.masculino and septimo_digito % 2 != 0:
        raise ValueError("El séptimo dígito del CI debe ser par para masculino")
    if sexo == SexoEnum.femenino and septimo_digito % 2 == 0:
        raise ValueError("El séptimo dígito del CI debe ser impar para femenino")
    return ci


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
        return _non_empty_str(v, info.field_name)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return _normalizar_telefono(v)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: date) -> date:
        hoy = date.today()
        limite_minimo = _add_years(hoy, -100)
        limite_maximo = _add_years(hoy, -18)
        if v < limite_minimo or v > limite_maximo:
            raise ValueError("La fecha de nacimiento debe estar entre 18 y 100 anos")
        return v

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, v: date, info) -> date:
        hoy = date.today()
        fecha_nacimiento = info.data.get("fecha_nacimiento")
        if v > hoy:
            raise ValueError("La fecha de ingreso no puede ser posterior a hoy")
        if fecha_nacimiento:
            minimo_ingreso = _add_years(fecha_nacimiento, 18)
            if v < minimo_ingreso:
                raise ValueError(
                    "La fecha de ingreso debe ser al menos 18 anos despues del nacimiento"
                )
        return v

    @model_validator(mode="after")
    def validar_ci_consistente(self):
        _validar_ci_cubano(self.ci, self.fecha_nacimiento, self.sexo)
        return self


class ASPCreate(ASPBase):
    pass


class ASPUpdate(BaseModel):
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

    @field_validator("nombre", "apellidos", "direccion", "observaciones")
    @classmethod
    def validar_textos_no_vacios(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v
        return _non_empty_str(v, info.field_name)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return _normalizar_telefono(v)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        hoy = date.today()
        limite_minimo = _add_years(hoy, -100)
        limite_maximo = _add_years(hoy, -18)
        if v < limite_minimo or v > limite_maximo:
            raise ValueError("La fecha de nacimiento debe estar entre 18 y 100 anos")
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
            minimo_ingreso = _add_years(fecha_nacimiento, 18)
            if v < minimo_ingreso:
                raise ValueError(
                    "La fecha de ingreso debe ser al menos 18 anos despues del nacimiento"
                )
        return v


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