# Sistema de Gestion de Postas (SGP)

Aplicacion web para la gestion de postas, ASP (Agentes de Seguridad y Proteccion), guardias, cargos y reportes. Single-user system.

**Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic
**Frontend:** Vue 3 + Vite + Vuetify 3 (MD3) + Pinia + Vue Router

## Requisitos

- Python 3.10+ (backend)
- Node.js `^20.19.0` o `>=22.12.0` (frontend)
- PostgreSQL (base de datos)
- Yarn (frontend)

## Instalacion

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configura las variables de entorno:

```bash
cp .env.example .env
# Editar .env con tus credenciales de DB y SECRET_KEY (min 32 caracteres)
```

Ejecuta las migraciones:

```bash
alembic upgrade head
```

**Opcional** — Cargar datos de prueba (reinicia la DB):

```bash
python seed.py
```

Levanta el servidor:

```bash
uvicorn app.main:app --reload
```

El admin se crea automaticamente al iniciar (configurado en `.env`).

### Frontend

```bash
cd frontend
yarn install
yarn dev
```

El frontend corre en `http://localhost:5173` y conecta al backend en `http://localhost:8000/api/v1`.

## Comandos utiles

### Backend

```bash
uvicorn app.main:app --reload    # Servidor de desarrollo
alembic revision --autogenerate -m "descripcion"  # Generar migracion
python seed.py                    # Recrear DB con datos de prueba
```

### Frontend

```bash
yarn dev          # Servidor de desarrollo (port 5173)
yarn build        # Build de produccion
yarn lint         # Linting (oxlint + eslint)
yarn format       # Formatear con Prettier
```

## Estructura

```
SGP/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, database, security (JWT + bcrypt)
│   │   ├── models/         # SQLAlchemy ORM (Cargo, ASP, Posta, Guardia, Novedad, Usuario)
│   │   ├── schemas/        # Pydantic request/response
│   │   ├── services/       # Logica de negocio
│   │   ├── routers/        # FastAPI endpoints (montados en /api/v1)
│   │   └── utils/          # Utilidades compartidas (_escape_like, etc.)
│   ├── alembic/            # Migraciones
│   ├── seed.py             # Datos de prueba
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/            # Clientes axios por entidad
│       ├── composables/    # useToast
│       ├── plugins/        # Vuetify (theme MD3, palette corporativa)
│       ├── router/         # Vue Router con auth guard
│       ├── stores/         # Pinia (auth)
│       ├── utils/          # error.js (normalizeApiError), constants.js
│       └── views/          # Componentes por vista (Login, Dashboard, CRUDs, Reportes)
```

## API

Todos los endpoints estan bajo `/api/v1`. Autenticacion via Bearer token (JWT).

| Endpoint | Descripcion |
|----------|-------------|
| `POST /auth/login` | Login, retorna access_token |
| `GET/POST /cargos` | CRUD de cargos (paginado) |
| `GET/POST /asp` | CRUD de ASP (paginado, con foto) |
| `GET/POST /postas` | CRUD de postas (paginado, con sub-CRUD de turnos) |
| `GET/POST /guardias` | CRUD de guardias + acciones (confirmar llegada, finalizar, novedades) |
| `GET /reportes/*` | 5 reportes: cobertura, ausentismo, horas ASP, incidencias, tardanzas |

## Stack tecnico

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, PyJWT, bcrypt, slowapi (rate limiting), asyncpg
- **Frontend:** Vue 3 (Composition API), Vuetify 3 (Material Design 3), Pinia, Axios, jsPDF (exportar PDF), jspdf-autotable
- **DB:** PostgreSQL con Alembic para migraciones
- **Theme:** Paleta corporativa azul (`#1565C0`), MDI icons, Roboto font
