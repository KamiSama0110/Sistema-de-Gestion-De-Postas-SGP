from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.schemas.auth import LoginRequest, TokenResponse, CambiarPasswordRequest
from app.services.auth_service import (
    autenticar_usuario,
    actualizar_ultimo_acceso,
    cambiar_password,
    get_usuario_by_username,
)
from app.models.usuario import Usuario

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
async def login(datos: LoginRequest, db: AsyncSession = Depends(get_db)):
    usuario = await autenticar_usuario(db, datos.username, datos.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    await actualizar_ultimo_acceso(db, usuario)
    token = create_access_token(data={"sub": usuario.username})
    return TokenResponse(access_token=token)


@router.post("/logout")
async def logout(usuario: Usuario = Depends(get_current_user)):
    return {"mensaje": "Sesión cerrada correctamente"}


@router.patch("/cambiar-contrasena")
async def cambiar_contrasena(
    datos: CambiarPasswordRequest,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exito = await cambiar_password(db, usuario, datos.password_actual, datos.password_nueva)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    return {"mensaje": "Contraseña actualizada correctamente"}