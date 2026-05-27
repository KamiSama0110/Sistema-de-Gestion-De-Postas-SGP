# Sistema de Gestion de Postas (SGP)

Aplicacion web para la gestion de postas, ASP (Agentes de Seguridad y Proteccion), guardias, cargos y reportes. El proyecto se divide en un backend (FastAPI) y un frontend (Vue con Vite).

## Requisitos

- Python 3.10+ (backend)
- Node.js 18+ y Yarn (frontend)
- Base de datos configurada para el backend

## Instalacion

### Backend

1) Crear y activar un entorno virtual.
2) Instalar dependencias.
3) Configurar variables de entorno.
4) Ejecutar migraciones y levantar el servidor.

Comandos de ejemplo:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copia el archivo de ejemplo y ajusta valores segun tu entorno:

```bash
cp backend/.env.example backend/.env
```

Luego ejecuta las migraciones:

```bash
alembic upgrade head
```

Luego inicia el servidor:

```bash
uvicorn app.main:app --reload
```

### Frontend

1) Instalar dependencias.
2) Levantar el servidor de desarrollo.

Comandos:

```bash
cd frontend
yarn install
yarn dev
```

## Estructura general

- backend/: API, modelos, esquemas, servicios y migraciones
- frontend/: interfaz web y consumo de API
- nginx/: configuracion de despliegue
