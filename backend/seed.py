"""
Seed de base de datos para SGP.
Recrea todas las tablas con datos de prueba consistentes y realistas.

Uso:
    cd backend
    python seed.py
    python seed.py --cuadros-prueba  # Para B4: inserta 30 hombres y 12 mujeres extra con CI TEST-
"""

import asyncio
import random
import sys
from datetime import date, datetime, time, timedelta, timezone
from app.core.database import engine, Base
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.enums import (
    SexoEnum, EscolaridadEnum, EstadoASPEnum,
    TipoPostaEnum, EstadoGuardiaEnum, TipoNovedadEnum, SeveridadEnum,
    EstadoPlanGuardiaEnum, EstadoGuardiaCuadroEnum,
)
from app.models.cargo import Cargo
from app.models.asp import ASP
from app.models.posta import Posta, TurnoPosta
from app.models.guardia import Guardia, Novedad
from app.models.usuario import Usuario
from app.models.cuadro import Cuadro, FranjaCuadro, Feriado
from app.models.plan_guardia_cuadro import PlanGuardiaCuadro, GuardiaCuadro
from sqlalchemy import select

random.seed(42)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generar_ci(fecha_nac: date, sexo: SexoEnum) -> str:
    base = fecha_nac.strftime('%y%m%d')
    sexo_digit = random.choice([0, 2, 4, 6, 8] if sexo == SexoEnum.masculino else [1, 3, 5, 7, 9])
    cola = ''.join(str(random.randint(0, 9)) for _ in range(4))
    return f'{base}{sexo_digit}{cola}'


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def pick(lst):
    return random.choice(lst)


# ---------------------------------------------------------------------------
# Datos realistas
# ---------------------------------------------------------------------------

CARGOS_DATA = [
    ('Oficial de Seguridad', 'Responsable directo de la vigilancia en su zona asignada'),
    ('Supervisor de Seguridad', 'Supervisa el cumplimiento de los turnos y protocolos'),
    ('Jefe de Seguridad', 'Dirige el equipo de seguridad del recinto'),
    ('Asistente de Seguridad', 'Brinda apoyo logístico y operativo al equipo'),
    ('Técnico de Seguridad', 'Operador y mantenimiento de equipos de seguridad'),
    ('Coordinador de Seguridad', 'Coordina la distribución de guardias entre postas'),
]

NOMBRES_M = [
    'Carlos', 'Manuel', 'José', 'Luis', 'Miguel', 'Alejandro', 'Pedro',
    'Juan', 'Francisco', 'Raúl', 'Jorge', 'Ernesto', 'Roberto', 'Ricardo',
    'Antonio', 'Fernando', 'Héctor', 'Emilio',
]
NOMBRES_F = [
    'María', 'Ana', 'Yanet', 'Odalis', 'Yamila', 'Daiquis', 'Lisneida',
    'Yudith', 'Evelyn', 'Yoana', 'Grettel', 'Alina',
]
APELLIDOS = [
    'García Rodríguez', 'López Martínez', 'Hernández Sánchez', 'González Pérez',
    'Rodríguez Díaz', 'Fernández Castro', 'Morales Rivas', 'Sánchez Torres',
    'Pérez Herrera', 'Díaz Lima', 'Ramírez Cruz', 'Torres Campos',
    'Rivero Medina', 'Vargas León', 'Mendoza Rojas', 'Álvarez Reyes',
    'Jiménez Ortega', 'Delgado Salazar',
]

# --- Cuadros (14: 8 hombres, 6 mujeres, 3 con sin_guardia_vie_dom, 1 inactivo) ---
CUADROS_DATA = [
    # Hombres (8)
    ('Roberto', 'Pérez Herrera', 'Director de Seguridad', 'Dirección General', 'masculino', True, False, None),
    ('Fernando', 'Díaz Lima', 'Vicerrector Académico', 'Vicerrectorado', 'masculino', True, False, None),
    ('Héctor', 'Ramírez Cruz', 'Rector', 'Rectorado', 'masculino', True, False, 'Rector titular'),
    ('Emilio', 'Torres Campos', 'Jefe de Departamento', 'Seguridad Física', 'masculino', True, True, None),
    ('Antonio', 'Vargas León', 'Coordinador de Turnos', 'Operaciones', 'masculino', True, True, None),
    ('Ricardo', 'Mendoza Rojas', 'Supervisor General', 'Control y Supervisión', 'masculino', True, False, None),
    ('Jorge', 'Álvarez Reyes', 'Oficial de Enlace', 'Relaciones Institucionales', 'masculino', True, True, None),
    ('Ernesto', 'Jiménez Ortega', 'Inspector de Seguridad', 'Inspección', 'masculino', False, False, 'En licencia médica'),

    # Mujeres (6)
    ('María', 'García Rodríguez', 'Directora Adjunta', 'Dirección General', 'femenino', True, False, None),
    ('Ana', 'López Martínez', 'Vicerrectora Administrativa', 'Vicerrectorado', 'femenino', True, False, None),
    ('Yanet', 'Hernández Sánchez', 'Jefa de Área', 'Recursos Humanos', 'femenino', True, False, None),
    ('Odalis', 'González Pérez', 'Coordinadora de Personal', 'Administración', 'femenino', True, False, None),
    ('Yamila', 'Rodríguez Díaz', 'Especialista en Protocolos', 'Normativa', 'femenino', True, False, None),
    ('Daiquis', 'Fernández Castro', 'Analista de Riesgos', 'Planificación', 'femenino', True, False, None),
]

# Feriados fijos para get_feriados_sugeridos
FERIADOS_FIJOS = [
    (1, 1, "Año Nuevo"),
    (1, 2, "Día de la Liberación"),
    (5, 1, "Día del Trabajo"),
    (7, 25, "Conmemoración del Asalto al Cuartel Moncada"),
    (7, 26, "Día de la Rebeldía Nacional"),
    (7, 27, "Día de la Rebeldía Nacional"),
    (10, 10, "Inicio de las Guerras de Independencia"),
    (12, 25, "Navidad"),
]

DIRECCIONES = [
    'Loma No. 45 entre 10 y 12, Camagüey',
    'Calle Martí No. 201, esquina a Maceo, Camagüey',
    'Av. Republica No. 304, entre Céspedes y Sanguily, Camagüey',
    'Calle San Esteban No. 112, Camagüey',
    'Av. Libertad No. 150, entre Ibáñez y Legrá, Camagüey',
    'Calle O\'Reilly No. 56, esquina a Independencia, Camagüey',
    'Calle República No. 412, entre Padre Valencia y Dulce María, Camagüey',
    'Barrio San Fernando, calle 5 No. 302, Camagüey',
]
POSTAS_DATA = [
    ('Posta Interior Principal', 'Vigilancia principal del edificio administrativo', 'Edificio Central, piso 1', TipoPostaEnum.interior),
    ('Posta Perimetral Norte', 'Control de acceso perimetral zona norte', 'Perímetro norte del recinto', TipoPostaEnum.perimetral),
    ('Ronda Móvil Centro', 'Patrullaje motorizado zona centro', 'Zona centro - radio 2km', TipoPostaEnum.movil),
    ('Punto Crítico Alma', 'Vigilancia permanente zona de alta sensibilidad', 'Almacén central', TipoPostaEnum.punto_critico),
    ('Posta Interior Sur', 'Vigilancia del ala sur del edificio', 'Edificio Sur, entrada principal', TipoPostaEnum.interior),
]
TURNOS_DATA = [
    # (posta_idx, nombre, hora_inicio, hora_fin, cruza, asp_requeridos)
    (0, 'Mañana', time(6, 0), time(14, 0), False, 2),
    (0, 'Tarde', time(14, 0), time(22, 0), False, 2),
    (0, 'Noche', time(22, 0), time(6, 0), True, 1),
    (1, 'Diurno', time(7, 0), time(19, 0), False, 2),
    (1, 'Nocturno', time(19, 0), time(7, 0), True, 1),
    (2, 'Completo', time(8, 0), time(20, 0), False, 1),
    (3, 'Turno A', time(6, 0), time(18, 0), False, 2),
    (3, 'Turno B', time(18, 0), time(6, 0), True, 1),
    (4, 'Mañana', time(6, 0), time(14, 0), False, 1),
    (4, 'Tarde', time(14, 0), time(22, 0), False, 1),
]

NOVEDADES_DATA = [
    (TipoNovedadEnum.incidente, SeveridadEnum.media, 'Se detectó persona no autorizada intentando acceso por la puerta lateral. Se activó protocolo de contención.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Recibido comunicado del departamento de recursos humanos sobre nuevo horario de visitas.'),
    (TipoNovedadEnum.entrega_recepcion, SeveridadEnum.baja, 'Entrega de llaves del almacén central. Se verificó inventario con el supervisor saliente.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.alta, 'Falla en iluminación de la zona perimetral norte. Se notificó a mantenimiento de emergencia.'),
    (TipoNovedadEnum.solicitud, SeveridadEnum.baja, 'Solicitud de refuerzo para evento especial del próximo fin de semana.'),
    (TipoNovedadEnum.otro, SeveridadEnum.baja, 'Cambio de turno con observaciones: equipo de radio con batería baja, pendiente reposición.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.media, 'Alarma de incendio activada accidentalmente en el piso 2. Se verificó sin novedad.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Actualización del protocolo de evacuación entregado por la dirección.'),
]


# ---------------------------------------------------------------------------
# Seed principal
# ---------------------------------------------------------------------------

async def seed():
    print('Borrando tablas...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print('Creando tablas...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # --- Cargos ---
        cargos = []
        for nombre, desc in CARGOS_DATA:
            cargo = Cargo(nombre=nombre, descripcion=desc, activo=True)
            db.add(cargo)
            cargos.append(cargo)
        await db.flush()
        print(f'  {len(cargos)} cargos creados')

        # --- Cuadros ---
        cuadros = []
        usados_ci = set()
        for i, (nombre, apellidos, cargo_str, area, sexo_str, activo, sin_guardia_vie_dom, observaciones) in enumerate(CUADROS_DATA):
            sexo = SexoEnum.masculino if sexo_str == 'masculino' else SexoEnum.femenino
            # Generar CI único
            fecha_nac = random_date(date(1965, 1, 1), date(1995, 12, 31))
            while True:
                ci = generar_ci(fecha_nac, sexo)
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break

            cuadro = Cuadro(
                nombre=nombre,
                apellidos=apellidos,
                ci=ci,
                cargo=cargo_str,
                area=area,
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=sexo,
                activo=activo,
                sin_guardia_vie_dom=sin_guardia_vie_dom,
                observaciones=observaciones,
            )
            db.add(cuadro)
            cuadros.append(cuadro)
        await db.flush()
        print(f'  {len(cuadros)} cuadros creados')

        # --- Franjas ---
        franjas = [
            FranjaCuadro(
                nombre="diurna",
                hora_inicio="09:00",
                hora_fin="16:00",
                dias_semana=[5, 6],  # sábado, domingo
                sexo_permitido=SexoEnum.femenino,
                activa=True,
            ),
            FranjaCuadro(
                nombre="nocturna",
                hora_inicio="17:00",
                hora_fin="07:00",
                dias_semana=[0, 1, 2, 3, 4, 5, 6],  # lunes a domingo
                sexo_permitido=SexoEnum.masculino,
                activa=True,
            ),
        ]
        for franja in franjas:
            db.add(franja)
        await db.flush()
        print(f'  {len(franjas)} franjas creadas')

        # --- Feriados sugeridos del año en curso ---
        anio_actual = date.today().year
        for mes, dia, descripcion in FERIADOS_FIJOS:
            feriado = Feriado(
                fecha=datetime(anio_actual, mes, dia),
                descripcion=descripcion,
            )
            db.add(feriado)
        await db.flush()
        print(f'  {len(FERIADOS_FIJOS)} feriados sugeridos creados')

        # --- Plan de guardias de cuadro (borrador, mes en curso) ---
        anio_plan = date.today().year
        mes_plan = date.today().month
        plan = PlanGuardiaCuadro(
            anio=anio_plan,
            mes=mes_plan,
            estado=EstadoPlanGuardiaEnum.borrador,
            generado_automaticamente=False,
            observaciones="Plan de prueba generado por seed",
        )
        db.add(plan)
        await db.flush()

        # Asignaciones válidas: 2 nocturnas (hombres) y 2 diurnas (mujeres)
        guardias_plan = [
            (1, 2, date(anio_plan, mes_plan, 13)),  # Roberto, nocturna
            (2, 2, date(anio_plan, mes_plan, 14)),  # Fernando, nocturna
            (9, 1, date(anio_plan, mes_plan, 17)),  # María, diurna (sábado)
            (10, 1, date(anio_plan, mes_plan, 18)),  # Ana, diurna (domingo)
        ]
        for cuadro_id, franja_id, fecha in guardias_plan:
            if fecha.month != mes_plan:
                continue
            db.add(
                GuardiaCuadro(
                    plan_id=plan.id,
                    cuadro_id=cuadro_id,
                    franja_id=franja_id,
                    fecha=fecha,
                    estado=EstadoGuardiaCuadroEnum.planificada,
                )
            )
        await db.flush()
        print(f'  Plan {anio_plan}-{mes_plan:02d} creado con {len(guardias_plan)} guardias')

        # --- ASPs ---
        asps = []
        usados_ci = set()
        # Generar 18 ASPs: 12M + 6F
        asp_data_pool = []
        for nombre in NOMBRES_M[:12]:
            sexo = SexoEnum.masculino
            asp_data_pool.append((nombre, sexo))
        for nombre in NOMBRES_F[:6]:
            sexo = SexoEnum.femenino
            asp_data_pool.append((nombre, sexo))
        random.shuffle(asp_data_pool)

        for i, (nombre, sexo) in enumerate(asp_data_pool):
            fecha_nac = random_date(date(1970, 1, 1), date(2002, 12, 31))
            while True:
                ci = generar_ci(fecha_nac, sexo)
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            fecha_ingreso = random_date(fecha_nac + timedelta(days=365 * 18), date.today())
            if fecha_ingreso > date.today():
                fecha_ingreso = date.today() - timedelta(days=random.randint(30, 365 * 5))
            escolaridad = pick(list(EscolaridadEnum))
            # Distribuir cargos: 3 oficiales, 2 supervisores, 1 jefe, 3 asistentes, 4 tecnicos, 5 coordinadores
            cargo_dist = [0]*3 + [1]*2 + [2]*1 + [3]*3 + [4]*4 + [5]*5
            cargo_id = cargos[cargo_dist[i % len(cargo_dist)]].id
            telefono = f'+53{random.randint(50000000, 59999999)}'
            estado = EstadoASPEnum.activo
            if i == 15:
                estado = EstadoASPEnum.suspendido
            elif i == 16:
                estado = EstadoASPEnum.baja_temporal
            elif i == 17:
                estado = EstadoASPEnum.baja_temporal
            asp = ASP(
                ci=ci, nombre=nombre, apellidos=pick(APELLIDOS),
                fecha_nacimiento=fecha_nac, sexo=sexo,
                nivel_escolaridad=escolaridad, telefono=telefono,
                direccion=pick(DIRECCIONES), estado=estado,
                fecha_ingreso=fecha_ingreso, cargo_id=cargo_id,
            )
            db.add(asp)
            asps.append(asp)
        await db.flush()
        print(f'  {len(asps)} ASPs creados')

        # --- Postas ---
        postas = []
        for nombre, desc, ubic, tipo in POSTAS_DATA:
            posta = Posta(nombre=nombre, descripcion=desc, ubicacion=ubic, tipo=tipo, activa=True)
            db.add(posta)
            postas.append(posta)
        await db.flush()
        print(f'  {len(postas)} postas creadas')

        # --- Turnos ---
        turnos = []
        for posta_idx, nombre, h_inicio, h_fin, cruza, asp_req in TURNOS_DATA:
            turno = TurnoPosta(
                posta_id=postas[posta_idx].id, nombre=nombre,
                hora_inicio=h_inicio, hora_fin=h_fin,
                cruza_medianoche=cruza, asp_requeridos=asp_req, activo=True,
            )
            db.add(turno)
            turnos.append(turno)
        await db.flush()
        print(f'  {len(turnos)} turnos creados')

        # --- Guardias (30 días, al menos 3 por día) ---
        asps_activos = [a for a in asps if a.estado == EstadoASPEnum.activo]
        hoy = date.today()
        guardias_creadas = []

        for dia_offset in range(1, 31):
            fecha = hoy + timedelta(days=dia_offset)
            fecha_str = fecha.isoformat()
            # Seleccionar al menos 3 turnos para este día
            turnos_hoy = list(range(len(turnos)))
            random.shuffle(turnos_hoy)
            turnos_hoy = turnos_hoy[:random.randint(3, min(5, len(turnos)))]

            asps_disponibles = list(asps_activos)
            random.shuffle(asps_disponibles)
            asp_cursor = 0

            for turno_idx in turnos_hoy:
                turno = turnos[turno_idx]
                asp_necesarios = turno.asp_requeridos
                asignados = []

                for _ in range(asp_necesarios):
                    if asp_cursor >= len(asps_disponibles):
                        asp_cursor = 0
                        random.shuffle(asps_disponibles)
                    asp = asps_disponibles[asp_cursor]
                    asp_cursor += 1
                    # Verificar que no esté ya asignado a este turno en esta fecha
                    duplicado = any(
                        g.asp_id == asp.id and g.turno_posta_id == turno.id and g.fecha == fecha
                        for g in guardias_creadas
                    )
                    if duplicado:
                        continue
                    guardia = Guardia(
                        asp_id=asp.id, turno_posta_id=turno.id,
                        fecha=fecha, estado=EstadoGuardiaEnum.planificada,
                    )
                    db.add(guardia)
                    guardias_creadas.append(guardia)
                    asignados.append(asp)

        await db.flush()
        print(f'  {len(guardias_creadas)} guardias creadas (30 días)')

        # --- Novedad en algunas guardias de los primeros 3 días ---
        guardias_pasadas = [g for g in guardias_creadas if g.fecha <= hoy + timedelta(days=3)]
        if guardias_pasadas:
            novedades_creadas = 0
            for g in guardias_pasadas[:8]:
                tipo, severidad, desc = pick(NOVEDADES_DATA)
                novedad = Novedad(
                    guardia_id=g.id,
                    tipo=tipo, descripcion=desc, severidad=severidad,
                )
                db.add(novedad)
                novedades_creadas += 1
            await db.flush()
            print(f'  {novedades_creadas} novedades creadas')

        # --- Usuario admin ---
        admin = Usuario(
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            activo=True,
            rol="admin",
        )
        db.add(admin)

        # --- Cuenta cuadro1 (vinculada a un hombre activo sin marca) ---
        # Buscar el primer hombre activo sin sin_guardia_vie_dom (Roberto Pérez Herrera)
        cuadro1 = next((c for c in cuadros if c.sexo == SexoEnum.masculino and c.activo and not c.sin_guardia_vie_dom), None)
        if cuadro1:
            usuario_cuadro1 = Usuario(
                username="cuadro1",
                hashed_password=get_password_hash("cuadro1234"),
                activo=True,
                rol="cuadro",
                cuadro_id=cuadro1.id,
            )
            db.add(usuario_cuadro1)
            print(f'  Cuenta cuadro1 creada para: {cuadro1.nombre} {cuadro1.apellidos}')

        await db.commit()
        print(f'\nSeed completado exitosamente.')
        print(f'  Cargos:     {len(cargos)}')
        print(f'  Cuadros:    {len(cuadros)} ({sum(1 for c in cuadros if c.activo)} activos, {sum(1 for c in cuadros if not c.activo)} inactivos)')
        print(f'  Franjas:    {len(franjas)}')
        print(f'  Feriados:   {len(FERIADOS_FIJOS)}')
        print(f'  ASPs:       {len(asps)} ({len(asps_activos)} activos)')
        print(f'  Postas:     {len(postas)}')
        print(f'  Turnos:     {len(turnos)}')
        print(f'  Guardias:   {len(guardias_creadas)}')
        print(f'  Novedades:  {novedades_creadas if guardias_pasadas else 0}')
        print(f'  Admin:      {settings.ADMIN_USERNAME}')
        print(f'  Cuadro1:    cuadro1 / cuadro1234')

async def seed_cuadros_prueba():
    """Seed adicional para B4: 30 hombres y 12 mujeres extra con CI TEST-"""
    print('Insertando cuadros de prueba (TEST-)...')
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        usados_ci = set()
        result = await db.execute(select(Cuadro).where(Cuadro.ci.like('TEST-%')))
        for c in result.scalars().all():
            usados_ci.add(c.ci)

        # 30 hombres extra
        for i in range(30):
            fecha_nac = random_date(date(1965, 1, 1), date(1995, 12, 31))
            while True:
                ci = f'TEST-{random.randint(100000, 999999)}'
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            cuadro = Cuadro(
                nombre=f'TestM{i+1}',
                apellidos=pick(APELLIDOS),
                ci=ci,
                cargo='Oficial de Prueba',
                area='Pruebas',
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=SexoEnum.masculino,
                activo=True,
                sin_guardia_vie_dom=False,
            )
            db.add(cuadro)

        # 12 mujeres extra
        for i in range(12):
            fecha_nac = random_date(date(1965, 1, 1), date(1995, 12, 31))
            while True:
                ci = f'TEST-{random.randint(100000, 999999)}'
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            cuadro = Cuadro(
                nombre=f'TestF{i+1}',
                apellidos=pick(APELLIDOS),
                ci=ci,
                cargo='Oficial de Prueba',
                area='Pruebas',
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=SexoEnum.femenino,
                activo=True,
                sin_guardia_vie_dom=False,
            )
            db.add(cuadro)

        await db.commit()
        print('  42 cuadros de prueba insertados (30 hombres, 12 mujeres)')


if __name__ == '__main__':
    if "--cuadros-prueba" in sys.argv:
        asyncio.run(seed_cuadros_prueba())
    else:
        asyncio.run(seed())
