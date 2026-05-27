from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.auth_service import crear_admin_inicial
from app.routers import auth, asp, cargo, posta, guardia, reporte


security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        await crear_admin_inicial(db)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(asp.router, prefix="/api/v1")
app.include_router(cargo.router, prefix="/api/v1")
app.include_router(posta.router, prefix="/api/v1")
app.include_router(guardia.router, prefix="/api/v1")
app.include_router(reporte.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "activo",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}