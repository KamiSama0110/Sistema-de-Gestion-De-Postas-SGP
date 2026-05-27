from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario
from app.core.security import verify_password, get_password_hash
from app.core.config import settings


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
    usuario.ultimo_acceso = datetime.now() 
    await db.commit()


async def cambiar_password(
    db: AsyncSession, usuario: Usuario, password_actual: str, password_nueva: str
) -> bool:
    if not verify_password(password_actual, usuario.hashed_password):
        return False
    usuario.hashed_password = get_password_hash(password_nueva)
    await db.commit()
    return True


async def crear_admin_inicial(db: AsyncSession) -> None:
    # Crea el usuario administrador, para las veces que reseteo las base de datos
    usuario = await get_usuario_by_username(db, settings.ADMIN_USERNAME)
    if not usuario:
        admin = Usuario(
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            activo=True,
        )
        db.add(admin)
        await db.commit()