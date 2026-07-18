from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.core.security import verify_password, get_password_hash
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def get_usuario_by_username(db: AsyncSession, username: str) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.username == username))
    return result.scalar_one_or_none()


async def autenticar_usuario(db: AsyncSession, username: str, password: str) -> Usuario | None:
    usuario = await get_usuario_by_username(db, username)
    if not usuario:
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    if not usuario.activo:
        return None
    return usuario


async def actualizar_ultimo_acceso(db: AsyncSession, usuario: Usuario) -> None:
    try:
        usuario.ultimo_acceso = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.warning("No se pudo actualizar ultimo_acceso del usuario %s", usuario.username)


async def cambiar_password(
    db: AsyncSession, usuario: Usuario, password_actual: str, password_nueva: str
) -> None:
    if not verify_password(password_actual, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    usuario.hashed_password = get_password_hash(password_nueva)
    await db.commit()


async def crear_admin_inicial(db: AsyncSession) -> None:
    try:
        usuario = await get_usuario_by_username(db, settings.ADMIN_USERNAME)
        if not usuario:
            admin = Usuario(
                username=settings.ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                activo=True,
            )
            db.add(admin)
            await db.commit()
    except Exception as e:
        logger.error("Error creando admin inicial: %s", e)