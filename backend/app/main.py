from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.limiter import limiter
from app.services.auth_service import crear_admin_inicial
from app.routers import auth, asp, cargo, posta, guardia, reporte


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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
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