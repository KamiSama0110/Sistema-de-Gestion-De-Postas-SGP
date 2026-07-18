from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.security import get_token, revoke_token, is_token_revoked, decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, CambiarPasswordRequest, MensajeResponse
from app.services.auth_service import (
    autenticar_usuario,
    actualizar_ultimo_acceso,
    cambiar_password,
    get_usuario_by_username,
)
from app.models.usuario import Usuario
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Autenticación"])


async def get_current_user(
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
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
    usuario = await get_usuario_by_username(db, username)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return usuario


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    datos: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    usuario = await autenticar_usuario(db, datos.username, datos.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    await actualizar_ultimo_acceso(db, usuario)
    token = create_access_token(data={"sub": usuario.username})
    return TokenResponse(access_token=token)


@router.post("/logout", response_model=MensajeResponse)
async def logout(
    usuario: Usuario = Depends(get_current_user),
    token: str = Depends(get_token),
):
    payload = decode_access_token(token)
    if payload:
        revoke_token(payload.get("jti", ""))
    return MensajeResponse(mensaje="Sesión cerrada correctamente")


@router.patch("/cambiar-contrasena", response_model=MensajeResponse)
async def cambiar_contrasena(
    datos: CambiarPasswordRequest,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await cambiar_password(db, usuario, datos.password_actual, datos.password_nueva)
    return MensajeResponse(mensaje="Contraseña actualizada correctamente")