from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator, model_validator, StringConstraints

from app.models.enums import SexoEnum
from app.utils.validators import (
    texto_opcional_no_vacio,
    normalizar_telefono,
    validar_ci_formato,
    validar_ci_paridad,
)

CI = Annotated[str, StringConstraints(strip_whitespace=True, max_length=20)]
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
Apellidos = Annotated[str, StringConstraints(strip_whitespace=True, max_length=150)]
Telefono = Annotated[str, StringConstraints(strip_whitespace=True, max_length=20)]
Observaciones = Annotated[str, StringConstraints(strip_whitespace=True)]


class CuadroBase(BaseModel):
    nombre: Nombre
    apellidos: Apellidos
    ci: CI
    cargo: str = Field(..., max_length=100)
    area: str = Field(..., max_length=100)
    telefono: Optional[Telefono] = None
    sexo: SexoEnum
    sin_guardia_vie_dom: bool = False
    observaciones: Optional[Observaciones] = None

    @field_validator("nombre", "apellidos", "cargo", "area", "observaciones")
    @classmethod
    def validar_textos(cls, v: Optional[str], info) -> Optional[str]:
        return texto_opcional_no_vacio(v, f"El campo {info.field_name}")

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return normalizar_telefono(v)

    @field_validator("ci")
    @classmethod
    def validar_ci_formato(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validar_ci_formato(v.strip())


class CuadroCreate(CuadroBase):
    @model_validator(mode="after")
    def validar_ci_consistente(self):
        validar_ci_paridad(self.ci, self.sexo)
        return self


class CuadroUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    apellidos: Optional[Apellidos] = None
    ci: Optional[CI] = None
    cargo: Optional[str] = Field(None, max_length=100)
    area: Optional[str] = Field(None, max_length=100)
    telefono: Optional[Telefono] = None
    sexo: Optional[SexoEnum] = None
    sin_guardia_vie_dom: Optional[bool] = None
    observaciones: Optional[Observaciones] = None

    @field_validator("nombre", "apellidos", "cargo", "area", "observaciones")
    @classmethod
    def validar_textos(cls, v: Optional[str], info) -> Optional[str]:
        return texto_opcional_no_vacio(v, f"El campo {info.field_name}")

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        return normalizar_telefono(v)

    @field_validator("ci")
    @classmethod
    def validar_ci_formato(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validar_ci_formato(v.strip())

    @model_validator(mode="after")
    def validar_ci_consistente(self):
        # Solo se revalida la paridad si el PATCH envía los dos campos juntos
        if self.ci is not None and self.sexo is not None:
            validar_ci_paridad(self.ci, self.sexo)
        return self


class CuadroCambiarEstado(BaseModel):
    activo: bool


class CuadroResponse(BaseModel):
    id: int
    nombre: str
    apellidos: str
    ci: Optional[str]
    cargo: str
    area: str
    telefono: Optional[str]
    sexo: SexoEnum
    activo: bool
    sin_guardia_vie_dom: bool
    observaciones: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}


class CuadroListResponse(BaseModel):
    id: int
    nombre: str
    apellidos: str
    ci: Optional[str]
    cargo: str
    area: str
    sexo: SexoEnum
    activo: bool
    sin_guardia_vie_dom: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class PaginatedCuadro(BaseModel):
    total: int
    page: int
    size: int
    items: list[CuadroListResponse]


class CuadroCuentaResponse(BaseModel):
    existe: bool
    username: Optional[str] = None
    activo: Optional[bool] = None


class CuadroCuentaCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class CuadroCuentaPassword(BaseModel):
    password_nueva: str = Field(..., min_length=8, max_length=100)
