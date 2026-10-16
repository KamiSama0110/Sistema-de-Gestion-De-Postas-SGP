# Sistema de Gestion de Postas (SGP)

Aplicacion web para la gestion de seguridad: **postas, turnos, ASP (Agentes de Seguridad y Proteccion), guardias, novedades, cargos y reportes**, mas el modulo de **Guardias de Cuadros** (planificacion mensual por cuadros con franjas, feriados y generacion automatica).

Dos modulos principales:

1. **Operativo (ASP):** cargos, ASP, postas y turnos, guardias de ASP con confirmacion de llegada/finalizacion/ausencias, novedades, reportes y auditoria.
2. **Guardias de Cuadros:** cuadros (con su cuenta de acceso), franjas horarias, feriados, planes mensuales de guardia, generacion automatica, ciclo de vida de las guardias, incidencias, panel del cuadro y reportes.

**Backend:** FastAPI + SQLAlchemy 2 (async) + PostgreSQL + Alembic
**Frontend:** Vue 3 + Vite + Vuetify 3 (Material Design 3) + Pinia + Vue Router

## Requisitos

- Python 3.10+ (backend)
- Node.js `^20.19.0` o `>=22.12.0` (frontend)
- PostgreSQL 13+ (base de datos)
- Yarn (frontend)

## Instalacion

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configura las variables de entorno (el archivo `.env` debe estar en `backend/`):

```bash
cp .env.example .env
# Editar .env con tus credenciales de DB, SECRET_KEY (min 32) y ADMIN_PASSWORD (min 8)
```

Ejecuta las migraciones:

```bash
alembic upgrade head
```

**Opcional** — Cargar datos de prueba (recrea las tablas):

```bash
python seed.py                    # Dataset completo (ASP + cuadros)
python seed.py --cuadros-prueba   # Solo 42 cuadros de prueba (prefijo TEST-)
```

Levanta el servidor de desarrollo (FastAPI con Uvicorn):

```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000/api/v1`
- Documentacion interactiva: `http://localhost:8000/docs` (Swagger) y `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

El usuario admin se crea automaticamente al iniciar (segun `ADMIN_USERNAME` / `ADMIN_PASSWORD`).

### Frontend

```bash
cd frontend
yarn install
yarn dev
```

El frontend corre en `http://localhost:5173` y consume la API en `VITE_API_URL` (por defecto `http://localhost:8000/api/v1`).

## Roles y permisos

| Rol | Acceso |
|-----|--------|
| `admin` | Todo el sistema: CRUD operativo, cuadros, planes, reportes y auditoria. |
| `cuadro` | Solo su panel (`/mis-guardias`, `/mi-planificacion`) y sus propias incidencias. Bloqueado del resto por router (redireccion) y por backend (403). |

El rol se lee de la base de datos en cada peticion (no del token).

**Creacion de cuentas de cuadro:** el sistema no las crea solo. El admin primero crea el cuadro con `POST /cuadros` y luego su cuenta de acceso con `POST /cuadros/{id}/cuenta` (usuario y password). Las cuentas que aparecen en el seed son de ejemplo.

## Variables de entorno (backend)

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `APP_NAME` | `Sistema de Gestion de Postas` | Nombre de la app |
| `APP_VERSION` | `1.0.0` | Version |
| `DEBUG` | `false` | Modo debug |
| `DB_HOST` / `DB_PORT` / `DB_NAME` | `localhost` / `5432` / `sgp_db` | Conexion PostgreSQL |
| `DB_USER` / `DB_PASSWORD` | `sgp_user` / `sgp_password` | Credenciales PostgreSQL |
| `DATABASE_URL` | (vacio) | URL completa; si se define, tiene prioridad sobre `DB_*` |
| `SECRET_KEY` | (min 32) | Clave para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Duracion del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duracion del refresh token |
| `ADMIN_USERNAME` | - | Usuario admin inicial |
| `ADMIN_PASSWORD` | (min 8) | Password admin inicial |
| `CORS_ORIGINS` | `http://localhost:5173` | Origenes permitidos (separados por coma) |
| `SEED_DB` | `false` | Ejecuta el seed al arrancar (util en demos/Render) |
| `CUADRO_VENTANA_INICIO_MIN` | `30` | Ventana (min) para iniciar una guardia de cuadro |
| `MAX_GUARDIAS_CUADRO_POR_MES` | `1` | Maximo de guardias de un cuadro por mes |

## Datos de prueba (seed)

`python seed.py` recrea las tablas y carga:

- 6 cargos, 51 cuadros (47 activos), 2 franjas, 24 feriados.
- 42 ASP (37 activos), 10 postas, 20 turnos.
- Guardias de ASP de los ultimos meses con novedades.
- 7 planes mensuales de cuadro (pasados + actual + siguiente) con guardias generadas e incidencias.

Cuentas:

| Usuario | Password | Rol |
|---------|----------|-----|
| `admin` | `admin1234` | admin |

El unico usuario que crea el sistema es `admin`, y lo hace el backend al levantar (segun `ADMIN_USERNAME` / `ADMIN_PASSWORD`). Las cuentas de cuadro no las crea el sistema: se generan desde la app con `POST /cuadros/{id}/cuenta`.

## API

Todos los endpoints estan bajo `/api/v1`. Autenticacion via Bearer token (JWT).

### Autenticacion

| Metodo | Ruta | Rol |
|--------|------|-----|
| POST | `/auth/login` | publico |
| POST | `/auth/refresh` | publico |
| POST | `/auth/logout` | autenticado |
| GET | `/auth/me` | autenticado |
| PATCH | `/auth/cambiar-contrasena` | autenticado |

### Operativo (ASP)

| Recurso | Endpoints | Rol |
|---------|-----------|-----|
| Cargos | `GET/POST /cargos`, `GET/PATCH /cargos/{id}`, `PATCH /cargos/{id}/estado` | admin |
| ASP | `GET/POST /asp`, `GET/PATCH /asp/{id}`, `PATCH /asp/{id}/estado` | admin |
| Postas | `GET/POST /postas`, `GET/PATCH /postas/{id}`, `PATCH /postas/{id}/estado`, `POST /postas/{id}/turnos`, `GET /postas/turnos`, `PATCH /postas/turnos/{id}`, `PATCH /postas/turnos/{id}/estado` | admin |
| Guardias | `GET/POST /guardias`, `GET/PATCH /guardias/{id}`, `PATCH /guardias/{id}/confirmar-llegada`, `/finalizar`, `/ausente`, `/cancelar`, `GET/POST /guardias/{id}/novedades` | admin |
| Reportes | `GET /reportes/cobertura`, `/ausentismo`, `/horas-asp`, `/incidencias`, `/tardanzas` | admin |
| Auditoria | `GET /auditoria`, `GET /auditoria/{id}/diff` | admin |

### Guardias de Cuadros

| Recurso | Endpoints | Rol |
|---------|-----------|-----|
| Cuadros | `GET/POST /cuadros`, `GET/PATCH /cuadros/{id}`, `PATCH /cuadros/{id}/estado`, `GET/POST /cuadros/{id}/cuenta`, `PATCH /cuadros/{id}/cuenta/password` | admin |
| Franjas | `GET /franjas-cuadro`, `PATCH /franjas-cuadro/{id}` | admin |
| Feriados | `GET/POST /feriados`, `GET/POST /feriados/sugeridos`, `PATCH/DELETE /feriados/{id}` | admin |
| Planes | `GET/POST /planes-guardia-cuadro`, `GET/PATCH/DELETE /planes-guardia-cuadro/{id}`, `POST .../{id}/enviar`, `/aprobar`, `/rechazar`, `/reabrir`, `/generar`, `/guardias`, `GET .../{id}/calendario`, `/candidatos` | admin |
| Guardias de cuadro | `GET /guardias-cuadro`, `PATCH/DELETE /guardias-cuadro/{id}`, `POST /guardias-cuadro/{id}/iniciar`, `/finalizar`, `/incumplir`, `/cancelar`, `/incidencias` | admin |
| Incidencias | `GET /incidencias-cuadro`, `GET/PATCH /incidencias-cuadro/{id}` | admin |
| Reportes | `GET /reportes-cuadros/cumplimiento`, `/guardias-por-cuadro`, `/incidencias`, `/dias-sin-cubrir`, `/incumplimientos` | admin |

### Panel del cuadro

| Metodo | Ruta | Rol |
|--------|------|-----|
| GET | `/mis-guardias` | cuadro |
| GET | `/mis-guardias/{id}`, `/mis-guardias/{id}/incidencias` | cuadro |
| GET | `/mis-guardias/opciones-incidencia` | cuadro |
| POST | `/mis-guardias/{id}/incidencias` | cuadro |
| PATCH | `/mis-incidencias/{id}` | cuadro |
| GET | `/mi-planificacion?anio=&mes=` | cuadro |

Los listados paginados aceptan `page` y `size` (maximo 100) y devuelven `{ total, page, size, items }`.

## Estructura

```
SGP/
├── backend/
│   ├── app/
│   │   ├── core/           # config, database, security (JWT + bcrypt), limiter
│   │   ├── models/         # ORM: Cargo, ASP, Posta, TurnoPosta, Guardia, Novedad,
│   │   │                   #      Usuario, RefreshToken, AuditLog, Cuadro,
│   │   │                   #      FranjaCuadro, Feriado, PlanGuardiaCuadro,
│   │   │                   #      GuardiaCuadro, IncidenciaCuadro
│   │   ├── schemas/        # Pydantic request/response (paginados)
│   │   ├── services/       # logica de negocio (async)
│   │   ├── routers/        # endpoints FastAPI (montados en /api/v1)
│   │   └── utils/          # helpers compartidos (sql, validators)
│   ├── alembic/            # migraciones
│   ├── seed.py             # datos de prueba
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/            # clientes axios por entidad
        ├── components/     # GraficoBarras, ReporteResultados, IncidenciaDialog, ...
        ├── composables/    # useToast, usePagination
        ├── plugins/        # Vuetify (tema MD3, paleta corporativa)
        ├── router/         # Vue Router con auth guard por rol
        ├── stores/         # Pinia (auth)
        ├── utils/          # error.js, formatters.js, constants.js
        └── views/          # Login, Dashboard, CRUDs, Cuadros, Planes, Guardias,
                            # Incidencias, MisGuardias, Reportes
```

## Comandos utiles

### Backend

```bash
uvicorn app.main:app --reload                      # servidor de desarrollo
alembic revision --autogenerate -m "descripcion"   # generar migracion
alembic upgrade head                               # aplicar migraciones
alembic downgrade base                             # revertir todo
python seed.py                                     # recrear DB con datos de prueba
```

### Frontend

```bash
yarn dev          # servidor de desarrollo (5173)
yarn build        # build de produccion
yarn lint         # oxlint --fix + eslint --fix
yarn format       # prettier
```

## Stack tecnico

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, PyJWT, bcrypt, slowapi (rate limiting), asyncpg, Alembic.
- **Frontend:** Vue 3 (Composition API), Vuetify 3 (Material Design 3), Pinia, Vue Router, Axios, jsPDF + jspdf-autotable (exportar PDF).
- **DB:** PostgreSQL con migraciones Alembic.
- **Tema:** paleta corporativa azul (`#1565C0`), iconos MDI, fuente Roboto.

## Notas

- `alembic.ini` tiene una URL fija que se sobreescribe en tiempo de ejecucion desde `settings.DATABASE_URL_RESOLVED` (ver `alembic/env.py`).
- Fechas sin zona horaria (`Date` / `DateTime`); los turnos que cruzan medianoche se calculan con helpers compartidos.
- La auditoria de cambios se registra automaticamente via listener de SQLAlchemy (solo `novedad` esta excluida).
