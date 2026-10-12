from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.usuario import Usuario
from app.models.enums import EstadoPlanGuardiaEnum
from app.schemas.plan import (
    PlanCreate,
    PlanUpdate,
    PlanRechazar,
    PlanResponse,
    PaginatedPlan,
    GuardiaCuadroCreate,
    GuardiaCuadroResponse,
    CalendarioResponse,
    CandidatosResponse,
)
from app.services import guardia_cuadro_service

router = APIRouter(prefix="/planes-guardia-cuadro", tags=["Planes de Guardia de Cuadro"])


@router.get("", response_model=PaginatedPlan)
async def listar_planes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    anio: Optional[int] = None,
    mes: Optional[int] = Query(None, ge=1, le=12),
    estado: Optional[EstadoPlanGuardiaEnum] = None,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.listar_planes(db, page, size, anio, mes, estado)


@router.post("", response_model=PlanResponse, status_code=201)
async def crear_plan(
    datos: PlanCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.crear_plan(db, datos)


@router.get("/{plan_id}", response_model=PlanResponse)
async def obtener_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.get_plan_by_id(db, plan_id)


@router.patch("/{plan_id}", response_model=PlanResponse)
async def actualizar_plan(
    plan_id: int,
    datos: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.actualizar_plan(db, plan_id, datos)


@router.delete("/{plan_id}", status_code=204)
async def eliminar_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    await guardia_cuadro_service.eliminar_plan(db, plan_id)


@router.post("/{plan_id}/enviar", response_model=PlanResponse)
async def enviar_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.enviar_plan(db, plan_id)


@router.post("/{plan_id}/aprobar", response_model=PlanResponse)
async def aprobar_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.aprobar_plan(db, plan_id)


@router.post("/{plan_id}/rechazar", response_model=PlanResponse)
async def rechazar_plan(
    plan_id: int,
    datos: PlanRechazar,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.rechazar_plan(db, plan_id, datos)


@router.post("/{plan_id}/reabrir", response_model=PlanResponse)
async def reabrir_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await guardia_cuadro_service.reabrir_plan(db, plan_id)


@router.post("/{plan_id}/guardias", response_model=GuardiaCuadroResponse, status_code=201)
async def asignar_guardia(
    plan_id: int,
    datos: GuardiaCuadroCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    plan = await guardia_cuadro_service.get_plan_by_id(db, plan_id)
    return await guardia_cuadro_service.asignar_guardia(db, plan, datos)


@router.get("/{plan_id}/calendario", response_model=CalendarioResponse)
async def obtener_calendario(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    plan = await guardia_cuadro_service.get_plan_by_id(db, plan_id)
    return await guardia_cuadro_service.generar_calendario(db, plan)


@router.get("/{plan_id}/candidatos", response_model=CandidatosResponse)
async def obtener_candidatos(
    plan_id: int,
    fecha: date = Query(...),
    franja_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    plan = await guardia_cuadro_service.get_plan_by_id(db, plan_id)
    return await guardia_cuadro_service.get_candidatos(db, plan, fecha, franja_id)
