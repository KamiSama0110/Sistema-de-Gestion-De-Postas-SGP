from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import generate_refresh_token, hash_refresh_token
from app.core.config import settings
from app.models.refresh_token import RefreshToken


def _ahora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _expiracion() -> datetime:
    return _ahora_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


async def crear_refresh_token(db: AsyncSession, usuario_id: int) -> str:
    raw = generate_refresh_token()
    db.add(
        RefreshToken(
            usuario_id=usuario_id,
            token_hash=hash_refresh_token(raw),
            expires_at=_expiracion(),
        )
    )
    await db.commit()
    return raw


async def obtener_usuario_id_por_token(db: AsyncSession, refresh_raw: str) -> int | None:
    if not refresh_raw:
        return None
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(refresh_raw)
        )
    )
    token = result.scalar_one_or_none()
    if not token or token.revocado_en is not None or token.expires_at < _ahora_utc():
        return None
    return token.usuario_id


async def rotar_refresh_token(db: AsyncSession, refresh_raw: str) -> tuple[str, int]:
    if not refresh_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o expirado",
        )
    token_hash = hash_refresh_token(refresh_raw)
    now = _ahora_utc()
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )
    token = result.scalar_one_or_none()
    if not token or token.revocado_en is not None or token.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o expirado",
        )
    token.revocado_en = now
    nuevo_raw = generate_refresh_token()
    db.add(
        RefreshToken(
            usuario_id=token.usuario_id,
            token_hash=hash_refresh_token(nuevo_raw),
            expires_at=_expiracion(),
        )
    )
    await db.commit()
    return nuevo_raw, token.usuario_id


async def revocar_refresh_token(db: AsyncSession, refresh_raw: str | None) -> None:
    if not refresh_raw:
        return
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(refresh_raw)
        )
    )
    token = result.scalar_one_or_none()
    if token and token.revocado_en is None:
        token.revocado_en = _ahora_utc()
        await db.commit()


async def revocar_todos_refresh_tokens(db: AsyncSession, usuario_id: int) -> None:
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revocado_en.is_(None),
        )
        .values(revocado_en=_ahora_utc())
    )
    await db.commit()