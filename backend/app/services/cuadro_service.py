from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.models.cuadro import Cuadro
from app.models.enums import SexoEnum
from app.models.usuario import Usuario
from app.schemas.cuadro import (
    CuadroCambiarEstado,
    CuadroCreate,
    CuadroCuentaCreate,
    CuadroCuentaPassword,
    CuadroUpdate,
)


async def get_cuadro_by_id(db: AsyncSession, cuadro_id: int) -> Cuadro:
    result = await db.execute(select(Cuadro).where(Cuadro.id == cuadro_id))
    cuadro = result.scalar_one_or_none()
    if not cuadro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cuadro no encontrado"
        )
    return cuadro


async def get_cuadro_by_id_with_usuario(db: AsyncSession, cuadro_id: int) -> Cuadro:
    result = await db.execute(
        select(Cuadro)
        .options(selectinload(Cuadro.usuario))
        .where(Cuadro.id == cuadro_id)
    )
    cuadro = result.scalar_one_or_none()
    if not cuadro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cuadro no encontrado"
        )
    return cuadro


async def get_cuadro_by_ci(db: AsyncSession, ci: str) -> Cuadro | None:
    result = await db.execute(select(Cuadro).where(Cuadro.ci == ci))
    return result.scalar_one_or_none()


async def listar_cuadros(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    q: str | None = None,
    sexo: SexoEnum | None = None,
    activo: bool | None = None,
    sin_guardia_vie_dom: bool | None = None,
) -> dict:
    query = select(Cuadro)

    if q:
        search = f"%{q}%"
        query = query.where(
            or_(
                Cuadro.nombre.ilike(search),
                Cuadro.apellidos.ilike(search),
                Cuadro.ci.ilike(search),
            )
        )
    if sexo:
        query = query.where(Cuadro.sexo == sexo)
    if activo is not None:
        query = query.where(Cuadro.activo == activo)
    if sin_guardia_vie_dom is not None:
        query = query.where(Cuadro.sin_guardia_vie_dom == sin_guardia_vie_dom)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Cuadro.apellidos, Cuadro.nombre)
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def crear_cuadro(db: AsyncSession, datos: CuadroCreate) -> Cuadro:
    if datos.ci:
        existing = await get_cuadro_by_ci(db, datos.ci)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="El CI ya está registrado"
            )

    cuadro = Cuadro(
        nombre=datos.nombre,
        apellidos=datos.apellidos,
        ci=datos.ci,
        cargo=datos.cargo,
        area=datos.area,
        telefono=datos.telefono,
        sexo=datos.sexo,
        sin_guardia_vie_dom=datos.sin_guardia_vie_dom,
        observaciones=datos.observaciones,
        activo=True,
    )
    db.add(cuadro)
    await db.commit()
    await db.refresh(cuadro)
    return cuadro


async def actualizar_cuadro(
    db: AsyncSession, cuadro_id: int, datos: CuadroUpdate
) -> Cuadro:
    cuadro = await get_cuadro_by_id(db, cuadro_id)

    update_data = datos.model_dump(exclude_unset=True)

    if "ci" in update_data and update_data["ci"] is not None:
        existing = await get_cuadro_by_ci(db, update_data["ci"])
        if existing and existing.id != cuadro_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="El CI ya está registrado"
            )

    for field, value in update_data.items():
        setattr(cuadro, field, value)

    await db.commit()
    await db.refresh(cuadro)
    return cuadro


async def cambiar_estado_cuadro(
    db: AsyncSession, cuadro_id: int, datos: CuadroCambiarEstado
) -> Cuadro:
    cuadro = await get_cuadro_by_id_with_usuario(db, cuadro_id)
    cuadro.activo = datos.activo

    if cuadro.usuario:
        cuadro.usuario.activo = datos.activo

    await db.commit()
    await db.refresh(cuadro)
    return cuadro


async def get_cuadro_cuenta(db: AsyncSession, cuadro_id: int) -> dict:
    cuadro = await get_cuadro_by_id_with_usuario(db, cuadro_id)
    if not cuadro.usuario:
        return {"existe": False}
    return {
        "existe": True,
        "username": cuadro.usuario.username,
        "activo": cuadro.usuario.activo,
    }


async def crear_cuadro_cuenta(
    db: AsyncSession, cuadro_id: int, datos: CuadroCuentaCreate
) -> Usuario:
    cuadro = await get_cuadro_by_id_with_usuario(db, cuadro_id)

    if cuadro.usuario:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El cuadro ya tiene una cuenta de acceso",
        )

    result = await db.execute(select(Usuario).where(Usuario.username == datos.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya existe",
        )

    usuario = Usuario(
        username=datos.username,
        hashed_password=get_password_hash(datos.password),
        activo=True,
        rol="cuadro",
        cuadro_id=cuadro.id,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


async def cambiar_password_cuadro_cuenta(
    db: AsyncSession, cuadro_id: int, datos: CuadroCuentaPassword
) -> Usuario:
    cuadro = await get_cuadro_by_id_with_usuario(db, cuadro_id)

    if not cuadro.usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El cuadro no tiene cuenta de acceso",
        )

    cuadro.usuario.hashed_password = get_password_hash(datos.password_nueva)
    await db.commit()
    await db.refresh(cuadro.usuario)
    return cuadro.usuario
