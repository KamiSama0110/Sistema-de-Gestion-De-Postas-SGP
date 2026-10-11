"""Helpers de validación compartidos entre schemas (principio DRY).

Reglas unificadas del proyecto:
- Textos: no vacíos, se normalizan con strip.
- Teléfono: formato cubano, se normaliza a +53 seguido de 8 dígitos.
- CI: 11 dígitos numéricos; en ASP además debe coincidir con la fecha de
  nacimiento y el séptimo dígito debe ser par/impar según el sexo.
- Fechas: `add_years` para sumar años y `validar_fecha_no_futura` para
  rechazar fechas futuras.
"""

from datetime import date
from typing import Any, Optional

from app.models.enums import SexoEnum


def add_years(base_date: date, years: int) -> date:
    """Suma años a una fecha, ajustando el 29/02 al 28/02 si no es bisiesto."""
    try:
        return base_date.replace(year=base_date.year + years)
    except ValueError:
        return base_date.replace(year=base_date.year + years, month=2, day=28)


def texto_no_vacio(value: Any, field_name: str) -> str:
    """Valida que un texto obligatorio no esté vacío y devuelve el valor limpio."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} debe ser un texto")
    if not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío ni contener solo espacios")
    return value.strip()


def texto_opcional_no_vacio(value: Any, field_name: str) -> Optional[str]:
    """Igual que `texto_no_vacio` pero admite None (campos opcionales de UPDATE)."""
    if value is None:
        return None
    return texto_no_vacio(value, field_name)


def normalizar_telefono(value: Any) -> Optional[str]:
    """Normaliza teléfonos cubanos a +53 seguido de 8 dígitos. None pasa."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("El teléfono debe ser un texto")
    raw = value.strip().replace(" ", "").replace("-", "")
    if not raw:
        return None
    if raw.startswith("+53") and len(raw) == 11 and raw[3:].isdigit():
        return raw
    if raw.isdigit() and len(raw) == 8:
        return f"+53{raw}"
    raise ValueError("El teléfono debe tener formato +53 seguido de 8 dígitos")


def validar_ci_formato(ci: str) -> str:
    """Valida que el CI tenga exactamente 11 dígitos numéricos."""
    if not ci.isdigit() or len(ci) != 11:
        raise ValueError("El CI debe tener exactamente 11 dígitos numéricos")
    return ci


def validar_ci_paridad(ci: str, sexo: SexoEnum) -> str:
    """Valida el séptimo dígito del CI: par para masculino, impar para femenino."""
    septimo_digito = int(ci[6])
    if sexo == SexoEnum.masculino and septimo_digito % 2 != 0:
        raise ValueError("El séptimo dígito del CI debe ser par para masculino")
    if sexo == SexoEnum.femenino and septimo_digito % 2 == 0:
        raise ValueError("El séptimo dígito del CI debe ser impar para femenino")
    return ci


def validar_ci_cubano(ci: str, fecha_nacimiento: date, sexo: SexoEnum) -> str:
    """Validación completa del CI cubano: formato, fecha de nacimiento y paridad."""
    validar_ci_formato(ci)
    if ci[:6] != fecha_nacimiento.strftime("%y%m%d"):
        raise ValueError("El CI debe coincidir con la fecha de nacimiento")
    validar_ci_paridad(ci, sexo)
    return ci


def validar_password(value: str) -> str:
    """Valida que la contraseña tenga al menos 8 caracteres."""
    if len(value) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    return value


def validar_fecha_no_futura(value: date, field_name: str) -> date:
    """Valida que una fecha no sea posterior a hoy."""
    if value > date.today():
        raise ValueError(f"{field_name} no puede ser futura")
    return value
