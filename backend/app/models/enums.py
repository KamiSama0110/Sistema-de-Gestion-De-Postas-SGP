import enum


class SexoEnum(str, enum.Enum):
    masculino = "masculino"
    femenino = "femenino"


class EscolaridadEnum(str, enum.Enum):
    primaria = "primaria"
    secundaria = "secundaria"
    preuniversitario = "preuniversitario"
    tecnico_medio = "tecnico_medio"
    universitario = "universitario"


class EstadoASPEnum(str, enum.Enum):
    activo = "activo"
    suspendido = "suspendido"
    baja_temporal = "baja_temporal"
    baja_definitiva = "baja_definitiva"


class TipoPostaEnum(str, enum.Enum):
    interior = "interior"
    perimetral = "perimetral"
    movil = "movil"
    punto_critico = "punto_critico"


class EstadoGuardiaEnum(str, enum.Enum):
    planificada = "planificada"
    activa = "activa"
    finalizada = "finalizada"
    ausente = "ausente"
    cancelada = "cancelada"


class TipoNovedadEnum(str, enum.Enum):
    incidente = "incidente"
    comunicado = "comunicado"
    entrega_recepcion = "entrega_recepcion"
    solicitud = "solicitud"
    otro = "otro"


class SeveridadEnum(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"