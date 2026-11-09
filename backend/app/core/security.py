import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer()

token_blacklist: set[str] = set()


def revoke_token(jti: str) -> None:
    token_blacklist.add(jti)


def is_token_revoked(jti: str) -> bool:
    return jti in token_blacklist


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return credentials.credentials


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    jti = str(uuid.uuid4())
    to_encode.update({"type": "access", "exp": expire, "jti": jti})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def set_current_user(username: str) -> None:
    from app.services.auditoria_service import current_user_var

    current_user_var.set(username)


async def get_current_user(
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    jti = payload.get("jti", "")
    if is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.cuadro)).where(Usuario.username == username)
    )
    usuario = result.scalar_one_or_none()
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    if usuario.rol == "cuadro" and (usuario.cuadro is None or not usuario.cuadro.activo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    set_current_user(usuario.username)
    return usuario


async def require_admin(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return usuario


async def require_cuadro(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if usuario.rol != "cuadro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de cuadro",
        )
    return usuario
