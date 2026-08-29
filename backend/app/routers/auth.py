from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.security import get_token, revoke_token, is_token_revoked, decode_access_token, set_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    CambiarPasswordRequest,
    MensajeResponse,
    RefreshRequest,
    LogoutRequest,
)
from app.services.auth_service import (
    autenticar_usuario,
    actualizar_ultimo_acceso,
    cambiar_password,
    get_usuario_by_username,
    get_usuario_by_id,
)
from app.services.token_service import (
    crear_refresh_token,
    obtener_usuario_id_por_token,
    rotar_refresh_token,
    revocar_refresh_token,
    revocar_todos_refresh_tokens,
)
from app.services.auditoria_service import registrar_evento_auth
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
    usuario = await get_usuario_by_username(db, username)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    set_current_user(usuario.username)
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
    set_current_user(usuario.username)
    await registrar_evento_auth(db, "login")
    await actualizar_ultimo_acceso(db, usuario)
    refresh_token = await crear_refresh_token(db, usuario.id)
    access_token = create_access_token(data={"sub": usuario.username})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    datos: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    usuario_id = await obtener_usuario_id_por_token(db, datos.refresh_token)
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o expirado",
        )
    usuario = await get_usuario_by_id(db, usuario_id)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    nuevo_refresh, _ = await rotar_refresh_token(db, datos.refresh_token)
    set_current_user(usuario.username)
    await registrar_evento_auth(db, "refresh_token")
    await db.commit()
    access_token = create_access_token(data={"sub": usuario.username})
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)


@router.post("/logout", response_model=MensajeResponse)
async def logout(
    datos: LogoutRequest | None = None,
    usuario: Usuario = Depends(get_current_user),
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_access_token(token)
    if payload:
        revoke_token(payload.get("jti", ""))
    if datos and datos.refresh_token:
        await revocar_refresh_token(db, datos.refresh_token)
    await registrar_evento_auth(db, "logout")
    await db.commit()
    return MensajeResponse(mensaje="Sesión cerrada correctamente")


@router.patch("/cambiar-contrasena", response_model=MensajeResponse)
async def cambiar_contrasena(
    datos: CambiarPasswordRequest,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await cambiar_password(db, usuario, datos.password_actual, datos.password_nueva)
    await revocar_todos_refresh_tokens(db, usuario.id)
    await registrar_evento_auth(db, "cambiar_password")
    await db.commit()
    return MensajeResponse(mensaje="Contraseña actualizada correctamente")