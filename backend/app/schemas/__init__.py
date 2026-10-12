from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    CambiarPasswordRequest,
    MensajeResponse,
)
from app.schemas.asp import (
    ASPCreate,
    ASPUpdate,
    ASPCambiarEstado,
    ASPResponse,
    ASPListResponse,
    PaginatedASP,
)
from app.schemas.cargo import (
    CargoCreate,
    CargoUpdate,
    CargoCambiarEstado,
    CargoResponse,
    PaginatedCargo,
)
from app.schemas.posta import (
    PostaCreate,
    PostaUpdate,
    PostaResponse,
    PostaListResponse,
    PaginatedPosta,
    TurnoPostaCreate,
    TurnoPostaUpdate,
    TurnoPostaResponse,
    PaginatedTurno,
)
from app.schemas.guardia import (
    GuardiaCreate,
    GuardiaUpdate,
    GuardiaResponse,
    GuardiaListResponse,
    PaginatedGuardia,
    ConfirmarLlegadaRequest,
    FinalizarGuardiaRequest,
    MarcarAusenteRequest,
    CancelarGuardiaRequest,
    NovedadCreate,
    NovedadResponse,
    PaginatedNovedad,
)
from app.schemas.reporte import (
    PeriodoRequest,
    ReporteCoberturaResponse,
    ReporteAusentismoResponse,
    ReporteHorasResponse,
    ReporteIncidenciasResponse,
    ReporteTardanzasResponse,
)
from app.schemas.auditoria import (
    AuditLogResponse,
    AuditDiffCampo,
    AuditDiffResponse,
    PaginatedAudit,
)
from app.schemas.cuadro import (
    CuadroCreate,
    CuadroUpdate,
    CuadroCambiarEstado,
    CuadroResponse,
    CuadroListResponse,
    PaginatedCuadro,
    CuadroCuentaResponse,
    CuadroCuentaCreate,
    CuadroCuentaPassword,
)
from app.schemas.franja import (
    FranjaCuadroUpdate,
    FranjaCuadroResponse,
    FranjaCuadroListResponse,
)
from app.schemas.feriado import (
    FeriadoCreate,
    FeriadoUpdate,
    FeriadoResponse,
    FeriadosSugeridosResponse,
    FeriadosCargarResponse,
    PaginatedFeriado,
)
from app.schemas.plan import (
    PlanCreate,
    PlanUpdate,
    PlanRechazar,
    PlanResponse,
    PlanListResponse,
    PaginatedPlan,
    GuardiaCuadroCreate,
    GuardiaCuadroUpdate,
    GuardiaCuadroResponse,
    GuardiaCuadroListResponse,
    PaginatedGuardiaCuadro,
    CalendarioResponse,
    CandidatosResponse,
)