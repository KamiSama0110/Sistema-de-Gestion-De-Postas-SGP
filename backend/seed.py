"""
Seed de base de datos para SGP.

Recrea todas las tablas con un conjunto de datos amplio, consistente y
realista para poder probar la aplicacion de punta a punta:

- Modulo ASP/postas: cargos, ASP, postas, turnos, guardias (pasadas y
  futuras, con estados variados), novedades.
- Modulo de cuadros: cuadros, franjas, feriados, planes de varios meses
  (aprobados con guardias ejecutadas y borradores), guardias de cuadro con
  todos los estados e incidencias.
- Usuarios: admin y varias cuentas de cuadro.

Uso:
    cd backend
    python seed.py
    python seed.py --cuadros-prueba  # inserta cuadros extra con CI TEST-
"""

import asyncio
import random
import sys
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

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
from app.models.incidencia_cuadro import IncidenciaCuadro
from app.schemas.plan import GenerarPlanRequest
from app.services.generacion_cuadros_service import generar_plan
from app.services.guardia_cuadro_service import aprobar_plan, enviar_plan

random.seed(42)

HOY = date.today()


# ---------------------------------------------------------------------------
# Helpers generales
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


def mes_desplazado(anio: int, mes: int, delta: int) -> tuple[int, int]:
    total = anio * 12 + (mes - 1) + delta
    return total // 12, total % 12 + 1


def intervalo(hora_inicio: str, hora_fin: str, fecha: date) -> tuple[datetime, datetime]:
    """Intervalo datetime de una franja/turno, contemplando cruce de medianoche."""
    hi = time.fromisoformat(hora_inicio)
    hf = time.fromisoformat(hora_fin)
    inicio = datetime.combine(fecha, hi)
    if hf <= hi:
        fin = datetime.combine(fecha + timedelta(days=1), hf)
    else:
        fin = datetime.combine(fecha, hf)
    return inicio, fin


# ---------------------------------------------------------------------------
# Datos base
# ---------------------------------------------------------------------------

CARGOS_DATA = [
    ('Oficial de Seguridad', 'Responsable directo de la vigilancia en su zona asignada'),
    ('Supervisor de Seguridad', 'Supervisa el cumplimiento de los turnos y protocolos'),
    ('Jefe de Seguridad', 'Dirige el equipo de seguridad del recinto'),
    ('Asistente de Seguridad', 'Brinda apoyo logistico y operativo al equipo'),
    ('Tecnico de Seguridad', 'Operador y mantenimiento de equipos de seguridad'),
    ('Coordinador de Seguridad', 'Coordina la distribucion de guardias entre postas'),
]

NOMBRES_M = [
    'Carlos', 'Manuel', 'Jose', 'Luis', 'Miguel', 'Alejandro', 'Pedro',
    'Juan', 'Francisco', 'Raul', 'Jorge', 'Ernesto', 'Roberto', 'Ricardo',
    'Antonio', 'Fernando', 'Hector', 'Emilio', 'Osmany', 'Yordan', 'Lazaro',
    'Reinaldo', 'Orlando', 'Sergio', 'Ramon', 'Alberto', 'Julio', 'Ivan',
    'Dariel', 'Yoel', 'Andy', 'Leandro', 'Raudel', 'Ernesto', 'Felix',
]
NOMBRES_F = [
    'Maria', 'Ana', 'Yanet', 'Odalis', 'Yamila', 'Daiquis', 'Lisneida',
    'Yudith', 'Evelyn', 'Yoana', 'Grettel', 'Alina', 'Mayra', 'Dalia',
    'Ileana', 'Nereida', 'Zulema', 'Caridad', 'Marlene', 'Dayana',
    'Yusimi', 'Liudmila', 'Mabel', 'Odette', 'Tamara', 'Vivian',
]
APELLIDOS = [
    'Garcia Rodriguez', 'Lopez Martinez', 'Hernandez Sanchez', 'Gonzalez Perez',
    'Rodriguez Diaz', 'Fernandez Castro', 'Morales Rivas', 'Sanchez Torres',
    'Perez Herrera', 'Diaz Lima', 'Ramirez Cruz', 'Torres Campos',
    'Rivero Medina', 'Vargas Leon', 'Mendoza Rojas', 'Alvarez Reyes',
    'Jimenez Ortega', 'Delgado Salazar', 'Suarez Beltran', 'Nunez Aguilar',
    'Pena Guerra', 'Cruz Betancourt', 'Reyes Morales', 'Guerra Santiesteban',
    'Quesada Leon', 'Sosa Valdes', 'Padron Acosta', 'Cordero Ruiz',
]

AREAS = [
    'Direccion General', 'Vicerrectorado', 'Rectorado', 'Seguridad Fisica',
    'Operaciones', 'Control y Supervision', 'Relaciones Institucionales',
    'Inspeccion', 'Recursos Humanos', 'Administracion', 'Normativa',
    'Planificacion', 'Docencia', 'Mantenimiento', 'Economia',
]

CARGOS_CUADRO = [
    'Director de Seguridad', 'Vicerrector Academico', 'Rector',
    'Jefe de Departamento', 'Coordinador de Turnos', 'Supervisor General',
    'Oficial de Enlace', 'Inspector de Seguridad', 'Directora Adjunta',
    'Vicerrectora Administrativa', 'Jefa de Area', 'Coordinadora de Personal',
    'Especialista en Protocolos', 'Analista de Riesgos', 'Jefe de Brigada',
    'Metodologo', 'Secretario Docente', 'Tecnico Especialista',
]

# Base de cuadros: 8 hombres (ids 1-8) y 6 mujeres (ids 9-14).
# Se conserva el orden original para mantener los ids 1 y 9.
CUADROS_BASE = [
    ('Roberto', 'Perez Herrera', 'Director de Seguridad', 'Direccion General', 'masculino', True, False, None),
    ('Fernando', 'Diaz Lima', 'Vicerrector Academico', 'Vicerrectorado', 'masculino', True, False, None),
    ('Hector', 'Ramirez Cruz', 'Rector', 'Rectorado', 'masculino', True, False, 'Rector titular'),
    ('Emilio', 'Torres Campos', 'Jefe de Departamento', 'Seguridad Fisica', 'masculino', True, True, None),
    ('Antonio', 'Vargas Leon', 'Coordinador de Turnos', 'Operaciones', 'masculino', True, True, None),
    ('Ricardo', 'Mendoza Rojas', 'Supervisor General', 'Control y Supervision', 'masculino', True, False, None),
    ('Jorge', 'Alvarez Reyes', 'Oficial de Enlace', 'Relaciones Institucionales', 'masculino', True, True, None),
    ('Ernesto', 'Jimenez Ortega', 'Inspector de Seguridad', 'Inspeccion', 'masculino', False, False, 'En licencia medica'),
    ('Maria', 'Garcia Rodriguez', 'Directora Adjunta', 'Direccion General', 'femenino', True, False, None),
    ('Ana', 'Lopez Martinez', 'Vicerrectora Administrativa', 'Vicerrectorado', 'femenino', True, False, None),
    ('Yanet', 'Hernandez Sanchez', 'Jefa de Area', 'Recursos Humanos', 'femenino', True, False, None),
    ('Odalis', 'Gonzalez Perez', 'Coordinadora de Personal', 'Administracion', 'femenino', True, False, None),
    ('Yamila', 'Rodriguez Diaz', 'Especialista en Protocolos', 'Normativa', 'femenino', True, False, None),
    ('Daiquis', 'Fernandez Castro', 'Analista de Riesgos', 'Planificacion', 'femenino', True, False, None),
]

FERIADOS_FIJOS = [
    (1, 1, "Ano Nuevo"),
    (1, 2, "Dia de la Liberacion"),
    (5, 1, "Dia del Trabajo"),
    (7, 25, "Conmemoracion del Asalto al Cuartel Moncada"),
    (7, 26, "Dia de la Rebeldia Nacional"),
    (7, 27, "Dia de la Rebeldia Nacional"),
    (10, 10, "Inicio de las Guerras de Independencia"),
    (12, 25, "Navidad"),
]

DIRECCIONES = [
    'Loma No. 45 entre 10 y 12, Camaguey',
    'Calle Marti No. 201, esquina a Maceo, Camaguey',
    'Av. Republica No. 304, entre Cespedes y Sanguily, Camaguey',
    'Calle San Esteban No. 112, Camaguey',
    'Av. Libertad No. 150, entre Ibanez y Legra, Camaguey',
    "Calle O'Reilly No. 56, esquina a Independencia, Camaguey",
    'Calle Republica No. 412, entre Padre Valencia y Dulce Maria, Camaguey',
    'Barrio San Fernando, calle 5 No. 302, Camaguey',
    'Calle Oscar Primelles No. 78, Camaguey',
    'Carretera Central Km 4, Reparto Jayama, Camaguey',
]

POSTAS_DATA = [
    ('Posta Interior Principal', 'Vigilancia principal del edificio administrativo', 'Edificio Central, piso 1', TipoPostaEnum.interior),
    ('Posta Perimetral Norte', 'Control de acceso perimetral zona norte', 'Perimetro norte del recinto', TipoPostaEnum.perimetral),
    ('Ronda Movil Centro', 'Patrullaje motorizado zona centro', 'Zona centro - radio 2km', TipoPostaEnum.movil),
    ('Punto Critico Alma', 'Vigilancia permanente zona de alta sensibilidad', 'Almacen central', TipoPostaEnum.punto_critico),
    ('Posta Interior Sur', 'Vigilancia del ala sur del edificio', 'Edificio Sur, entrada principal', TipoPostaEnum.interior),
    ('Posta Rectorado', 'Control de acceso al area del rectorado', 'Edificio del Rectorado', TipoPostaEnum.interior),
    ('Posta Biblioteca', 'Vigilancia del fondo bibliografico', 'Biblioteca central', TipoPostaEnum.interior),
    ('Ronda Movil Norte', 'Patrullaje motorizado perimetro norte', 'Zona norte - radio 3km', TipoPostaEnum.movil),
    ('Punto Critico Datos', 'Vigilancia del centro de datos', 'Edificio tecnologico, planta baja', TipoPostaEnum.punto_critico),
    ('Posta Perimetral Sur', 'Control de acceso perimetral zona sur', 'Perimetro sur del recinto', TipoPostaEnum.perimetral),
]

# (posta_idx, nombre, hora_inicio, hora_fin, cruza, asp_requeridos)
TURNOS_DATA = [
    (0, 'Manana', time(6, 0), time(14, 0), False, 2),
    (0, 'Tarde', time(14, 0), time(22, 0), False, 2),
    (0, 'Noche', time(22, 0), time(6, 0), True, 1),
    (1, 'Diurno', time(7, 0), time(19, 0), False, 2),
    (1, 'Nocturno', time(19, 0), time(7, 0), True, 1),
    (2, 'Completo', time(8, 0), time(20, 0), False, 1),
    (3, 'Turno A', time(6, 0), time(18, 0), False, 2),
    (3, 'Turno B', time(18, 0), time(6, 0), True, 1),
    (4, 'Manana', time(6, 0), time(14, 0), False, 1),
    (4, 'Tarde', time(14, 0), time(22, 0), False, 1),
    (5, 'Diurno', time(7, 0), time(19, 0), False, 1),
    (5, 'Nocturno', time(19, 0), time(7, 0), True, 1),
    (6, 'Manana', time(8, 0), time(14, 0), False, 1),
    (6, 'Tarde', time(14, 0), time(20, 0), False, 1),
    (7, 'Diurno', time(7, 0), time(19, 0), False, 1),
    (7, 'Nocturno', time(19, 0), time(7, 0), True, 1),
    (8, 'Turno A', time(7, 0), time(19, 0), False, 2),
    (8, 'Turno B', time(19, 0), time(7, 0), True, 1),
    (9, 'Diurno', time(6, 0), time(18, 0), False, 2),
    (9, 'Nocturno', time(18, 0), time(6, 0), True, 1),
]

NOVEDADES_DATA = [
    (TipoNovedadEnum.incidente, SeveridadEnum.media, 'Se detecto persona no autorizada intentando acceso por la puerta lateral. Se activo protocolo de contencion.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Recibido comunicado del departamento de recursos humanos sobre nuevo horario de visitas.'),
    (TipoNovedadEnum.entrega_recepcion, SeveridadEnum.baja, 'Entrega de llaves del almacen central. Se verifico inventario con el supervisor saliente.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.alta, 'Falla en iluminacion de la zona perimetral norte. Se notifico a mantenimiento de emergencia.'),
    (TipoNovedadEnum.solicitud, SeveridadEnum.baja, 'Solicitud de refuerzo para evento especial del proximo fin de semana.'),
    (TipoNovedadEnum.otro, SeveridadEnum.baja, 'Cambio de turno con observaciones: equipo de radio con bateria baja, pendiente reposicion.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.media, 'Alarma de incendio activada accidentalmente en el piso 2. Se verifico sin novedad.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Actualizacion del protocolo de evacuacion entregado por la direccion.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.critica, 'Intento de intrusion en el punto critico de datos. Se reforzo la vigilancia y se notifico a la seguridad del Estado.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.alta, 'Cristal roto en ventana del area de archivo. Se aseguro el perimetro y se reporto a mantenimiento.'),
    (TipoNovedadEnum.solicitud, SeveridadEnum.media, 'Solicitud de cambio de posta por parte del ASP debido a problema de salud.'),
    (TipoNovedadEnum.entrega_recepcion, SeveridadEnum.baja, 'Relevo de turno sin novedades. Se entrego equipamiento completo.'),
]

INCIDENCIAS_CUADRO_DATA = [
    (TipoNovedadEnum.incidente, SeveridadEnum.media, 'Se reporto una persona sin autorizacion en el perimetro. Se dio aviso a la posta.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.alta, 'Intento de acceso a area restringida fuera del horario. Se reforzo la vigilancia.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Se informa cambio de recorrido de la ronda nocturna por trabajos en el pasillo.'),
    (TipoNovedadEnum.entrega_recepcion, SeveridadEnum.baja, 'Entrega de novedades y equipos al supervisor de turno sin incidencias.'),
    (TipoNovedadEnum.incidente, SeveridadEnum.critica, 'Falla total del sistema de alarma en el bloque principal. Se notifico a mantenimiento urgente.'),
    (TipoNovedadEnum.solicitud, SeveridadEnum.media, 'Se solicita revision de la dotacion de la franja por aumento de actividad.'),
    (TipoNovedadEnum.comunicado, SeveridadEnum.baja, 'Comunicado sobre nueva ruta de evacuacion aprobada por la direccion.'),
    (TipoNovedadEnum.otro, SeveridadEnum.baja, 'Se detecto luminaria fundida en el acceso posterior. Pendiente reposicion.'),
]


# ---------------------------------------------------------------------------
# Construccion de cuadros
# ---------------------------------------------------------------------------

def _construir_cuadros() -> list[dict]:
    """Cuadros base + ampliacion para tener una poblacion de tamano realista.

    Devuelve dicts listos para instanciar. Los primeros 14 conservan el
    orden original (ids 1-14); los ids 1 y 9 se mantienen como en el seed
    anterior para compatibilidad con pruebas.
    """
    definiciones: list[dict] = []

    for nombre, apellidos, cargo, area, sexo, activo, sin_vie_dom, obs in CUADROS_BASE:
        definiciones.append({
            'nombre': nombre, 'apellidos': apellidos, 'cargo': cargo, 'area': area,
            'sexo': sexo, 'activo': activo, 'sin_guardia_vie_dom': sin_vie_dom,
            'observaciones': obs,
        })

    usados = {(c['nombre'], c['apellidos']) for c in definiciones}

    def agregar(cantidad, sexo, activo=True, sin_vie_dom=False):
        for _ in range(cantidad):
            if sexo == 'masculino':
                nombre = pick(NOMBRES_M)
            else:
                nombre = pick(NOMBRES_F)
            apellidos = pick(APELLIDOS)
            while (nombre, apellidos) in usados:
                apellidos = pick(APELLIDOS)
            usados.add((nombre, apellidos))
            definiciones.append({
                'nombre': nombre,
                'apellidos': apellidos,
                'cargo': pick(CARGOS_CUADRO),
                'area': pick(AREAS),
                'sexo': sexo,
                'activo': activo,
                'sin_guardia_vie_dom': sin_vie_dom,
                'observaciones': None,
            })

    # Ampliacion: mas hombres (cubren la franja nocturna, todos los dias)
    # y mas mujeres (cubren la franja diurna de fin de semana).
    agregar(20, 'masculino', activo=True, sin_vie_dom=False)
    agregar(4, 'masculino', activo=True, sin_vie_dom=True)
    agregar(10, 'femenino', activo=True, sin_vie_dom=False)
    # Algunos inactivos para ejercitar filtros y validaciones.
    agregar(2, 'masculino', activo=False)
    agregar(1, 'femenino', activo=False)

    return definiciones


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
        usados_ci: set[str] = set()
        for definicion in _construir_cuadros():
            sexo = SexoEnum.masculino if definicion['sexo'] == 'masculino' else SexoEnum.femenino
            fecha_nac = random_date(date(1965, 1, 1), date(1995, 12, 31))
            while True:
                ci = generar_ci(fecha_nac, sexo)
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            cuadro = Cuadro(
                nombre=definicion['nombre'],
                apellidos=definicion['apellidos'],
                ci=ci,
                cargo=definicion['cargo'],
                area=definicion['area'],
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=sexo,
                activo=definicion['activo'],
                sin_guardia_vie_dom=definicion['sin_guardia_vie_dom'],
                observaciones=definicion['observaciones'],
            )
            db.add(cuadro)
            cuadros.append(cuadro)
        await db.flush()
        cuadros_m = [c for c in cuadros if c.sexo == SexoEnum.masculino and c.activo]
        cuadros_f = [c for c in cuadros if c.sexo == SexoEnum.femenino and c.activo]
        print(f'  {len(cuadros)} cuadros creados ({len(cuadros_m)} hombres activos, {len(cuadros_f)} mujeres activas)')

        # --- Franjas ---
        franjas = [
            FranjaCuadro(
                nombre="diurna",
                hora_inicio="09:00",
                hora_fin="16:00",
                dias_semana=[5, 6],  # sabado, domingo
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
        franja_diurna, franja_nocturna = franjas
        print(f'  {len(franjas)} franjas creadas')

        # --- Feriados (ano anterior, actual y siguiente) ---
        anios_feriados = {HOY.year - 1, HOY.year, HOY.year + 1}
        total_feriados = 0
        for anio in sorted(anios_feriados):
            for mes, dia, descripcion in FERIADOS_FIJOS:
                db.add(Feriado(fecha=datetime(anio, mes, dia), descripcion=descripcion))
                total_feriados += 1
        await db.flush()
        print(f'  {total_feriados} feriados creados')

        # --- Postas y turnos (modulo ASP) ---
        postas = []
        for nombre, desc, ubic, tipo in POSTAS_DATA:
            posta = Posta(nombre=nombre, descripcion=desc, ubicacion=ubic, tipo=tipo, activa=True)
            db.add(posta)
            postas.append(posta)
        await db.flush()

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
        print(f'  {len(postas)} postas y {len(turnos)} turnos creados')

        # --- ASP ---
        asps = []
        usados_ci = set()
        asp_data_pool = [(n, SexoEnum.masculino) for n in NOMBRES_M[:28]]
        asp_data_pool += [(n, SexoEnum.femenino) for n in NOMBRES_F[:14]]
        random.shuffle(asp_data_pool)

        for i, (nombre, sexo) in enumerate(asp_data_pool):
            fecha_nac = random_date(date(1970, 1, 1), date(2002, 12, 31))
            while True:
                ci = generar_ci(fecha_nac, sexo)
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            fecha_ingreso = random_date(fecha_nac + timedelta(days=365 * 18), HOY)
            if fecha_ingreso > HOY:
                fecha_ingreso = HOY - timedelta(days=random.randint(30, 365 * 5))
            escolaridad = pick(list(EscolaridadEnum))
            cargo_id = cargos[i % len(cargos)].id
            estado = EstadoASPEnum.activo
            if i % 17 == 15:
                estado = EstadoASPEnum.suspendido
            elif i % 17 == 16:
                estado = EstadoASPEnum.baja_temporal
            elif i % 29 == 28:
                estado = EstadoASPEnum.baja_definitiva
            asp = ASP(
                ci=ci, nombre=nombre, apellidos=pick(APELLIDOS),
                fecha_nacimiento=fecha_nac, sexo=sexo,
                nivel_escolaridad=escolaridad,
                telefono=f'+53{random.randint(50000000, 59999999)}',
                direccion=pick(DIRECCIONES), estado=estado,
                fecha_ingreso=fecha_ingreso, cargo_id=cargo_id,
            )
            db.add(asp)
            asps.append(asp)
        await db.flush()
        asps_activos = [a for a in asps if a.estado == EstadoASPEnum.activo]
        print(f'  {len(asps)} ASPs creados ({len(asps_activos)} activos)')

        # --- Guardias ASP: 120 dias atras hasta 30 dias adelante ---
        guardias_asp, novedades_creadas = await _crear_guardias_asp(db, turnos, asps_activos, postas)
        print(f'  {len(guardias_asp)} guardias ASP y {novedades_creadas} novedades creadas')

        # --- Planes de guardia de cuadro ---
        planes_info = await _crear_planes_cuadro(db)
        print(f'  {planes_info["planes"]} planes de cuadro creados, {planes_info["guardias"]} guardias de cuadro')

        # --- Incidencias de cuadro (sobre guardias de planes aprobados) ---
        incidencias = await _crear_incidencias_cuadro(db, postas, asps)
        print(f'  {incidencias} incidencias de cuadro creadas')

        # --- Usuarios ---
        db.add(Usuario(
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            activo=True,
            rol="admin",
        ))

        cuentas_cuadro = _crear_cuentas_cuadro(db, cuadros)
        print(f'  Usuario admin: {settings.ADMIN_USERNAME}')

        await db.commit()

        print('\nSeed completado exitosamente.')
        print(f'  Cargos:        {len(cargos)}')
        print(f'  Cuadros:       {len(cuadros)} ({sum(1 for c in cuadros if c.activo)} activos, {sum(1 for c in cuadros if not c.activo)} inactivos)')
        print(f'  Franjas:       {len(franjas)}')
        print(f'  Feriados:      {total_feriados}')
        print(f'  ASPs:          {len(asps)} ({len(asps_activos)} activos)')
        print(f'  Postas:        {len(postas)}')
        print(f'  Turnos:        {len(turnos)}')
        print(f'  Guardias ASP:  {len(guardias_asp)}')
        print(f'  Novedades:     {novedades_creadas}')
        print(f'  Planes cuadro: {planes_info["planes"]}')
        print(f'  Guardias cuad: {planes_info["guardias"]}')
        print(f'  Incidencias c: {incidencias}')
        print(f'  Cuentas cuadro:{cuentas_cuadro}')
        print('\n  Cuentas de acceso:')
        print(f'    admin    / {settings.ADMIN_PASSWORD}')
        print('    cuadro1  / cuadro1234')
        print('    cuadro2  / cuadro1234')
        print('    cuadro3  / cuadro1234')
        print('    cuadro4  / cuadro1234')


# ---------------------------------------------------------------------------
# Guardias ASP y novedades
# ---------------------------------------------------------------------------

async def _crear_guardias_asp(db, turnos, asps_activos, postas) -> tuple[list, int]:
    guardias: list[Guardia] = []
    novedades_pendientes: list[tuple[Guardia, datetime, TipoNovedadEnum, str, SeveridadEnum]] = []

    for offset in range(-120, 31):
        fecha = HOY + timedelta(days=offset)
        # Seleccionar un subconjunto de turnos para el dia.
        turnos_dia = list(turnos)
        random.shuffle(turnos_dia)
        turnos_dia = turnos_dia[:random.randint(3, min(len(turnos_dia), 8))]

        pool = list(asps_activos)
        random.shuffle(pool)
        cursor = 0

        for turno in turnos_dia:
            for _ in range(turno.asp_requeridos):
                if cursor >= len(pool):
                    break
                asp = pool[cursor]
                cursor += 1

                estado = _estado_guardia_asp(fecha)
                guardia = Guardia(
                    asp_id=asp.id,
                    turno_posta_id=turno.id,
                    fecha=fecha,
                    estado=estado,
                )

                inicio, fin = intervalo(
                    turno.hora_inicio.strftime('%H:%M'),
                    turno.hora_fin.strftime('%H:%M'),
                    fecha,
                )
                if estado == EstadoGuardiaEnum.finalizada:
                    tardanza = random.choices(
                        [0, 5, 8, 12, 15, 20, 30, 45],
                        weights=[72, 8, 6, 4, 4, 3, 2, 1],
                    )[0]
                    guardia.hora_inicio_real = inicio + timedelta(minutes=tardanza)
                    guardia.hora_fin_real = inicio + timedelta(minutes=tardanza) + (fin - inicio)
                elif estado == EstadoGuardiaEnum.activa:
                    guardia.hora_inicio_real = inicio + timedelta(minutes=random.choice([0, 5, 10]))
                elif estado == EstadoGuardiaEnum.ausente:
                    if random.random() < 0.6:
                        guardia.motivo_ausencia = pick([
                            'Aviso de salud presentado por el ASP',
                            'Problema personal justificado',
                            'Incomparecencia justificada por la jefatura',
                        ])
                elif estado == EstadoGuardiaEnum.cancelada:
                    guardia.motivo_ausencia = pick([
                        'Turno cancelado por la jefatura',
                        'Posta desactivada temporalmente',
                    ])

                db.add(guardia)
                guardias.append(guardia)

                if estado == EstadoGuardiaEnum.finalizada and random.random() < 0.12:
                    tipo, severidad, desc = pick(NOVEDADES_DATA)
                    novedades_pendientes.append((
                        guardia,
                        inicio + timedelta(minutes=random.randint(30, 300)),
                        tipo, desc, severidad,
                    ))

    await db.flush()

    for guardia, fecha_hora, tipo, desc, severidad in novedades_pendientes:
        db.add(Novedad(
            guardia_id=guardia.id,
            tipo=tipo, descripcion=desc, severidad=severidad,
            fecha_hora=fecha_hora,
        ))

    await db.flush()
    return guardias, len(novedades_pendientes)


def _estado_guardia_asp(fecha: date) -> EstadoGuardiaEnum:
    if fecha < HOY:
        r = random.random()
        if r < 0.84:
            return EstadoGuardiaEnum.finalizada
        if r < 0.90:
            return EstadoGuardiaEnum.ausente
        if r < 0.94:
            return EstadoGuardiaEnum.cancelada
        return EstadoGuardiaEnum.planificada
    if fecha == HOY:
        return random.choice([EstadoGuardiaEnum.activa, EstadoGuardiaEnum.finalizada, EstadoGuardiaEnum.planificada])
    return EstadoGuardiaEnum.planificada


# ---------------------------------------------------------------------------
# Planes de guardia de cuadro
# ---------------------------------------------------------------------------

async def _crear_planes_cuadro(db) -> dict:
    """Crea planes mes a mes usando el generador real de la aplicacion.

    Meses anteriores y el actual quedan aprobados; el mes siguiente queda en
    borrador para poder practicar la edicion. Luego se ajustan los estados de
    las guardias para reflejar la operacion (finalizadas, incumplidas, etc.).
    """
    # Meses: 5 anteriores, el actual y el siguiente.
    periodos = []
    for delta in range(-5, 2):
        periodos.append(mes_desplazado(HOY.year, HOY.month, delta))

    planes: list[PlanGuardiaCuadro] = []
    total_guardias = 0

    for idx, (anio, mes) in enumerate(periodos):
        plan = PlanGuardiaCuadro(
            anio=anio,
            mes=mes,
            estado=EstadoPlanGuardiaEnum.borrador,
            generado_automaticamente=True,
            observaciones='Plan generado por el seed de demostracion',
        )
        db.add(plan)
        await db.flush()

        resultado = await generar_plan(
            db, plan, GenerarPlanRequest(modo="completar", semilla=1000 + idx)
        )
        total_guardias += resultado["creadas"]

        es_futuro = (anio, mes) > (HOY.year, HOY.month)
        if not es_futuro:
            await enviar_plan(db, plan.id)
            await aprobar_plan(db, plan.id)
        planes.append(plan)

    # Ajustar estados de las guardias de los planes aprobados.
    for plan in planes:
        if plan.estado != EstadoPlanGuardiaEnum.aprobado:
            continue
        guardias = (
            await db.execute(select(GuardiaCuadro).where(GuardiaCuadro.plan_id == plan.id))
        ).scalars().all()
        franjas_por_id = {f.id: f for f in await _franjas(db)}
        for guardia in guardias:
            _ajustar_estado_guardia_cuadro(guardia, franjas_por_id.get(guardia.franja_id))

    await db.flush()
    return {"planes": len(planes), "guardias": total_guardias}


async def _franjas(db) -> list[FranjaCuadro]:
    return (await db.execute(select(FranjaCuadro))).scalars().all()


def _ajustar_estado_guardia_cuadro(guardia: GuardiaCuadro, franja) -> None:
    fecha = guardia.fecha
    if fecha < HOY:
        r = random.random()
        if r < 0.80:
            guardia.estado = EstadoGuardiaCuadroEnum.finalizada
            if franja is not None:
                inicio, fin = intervalo(franja.hora_inicio, franja.hora_fin, fecha)
                tardanza = random.choice([0, 0, 0, 5, 10, 15, 20, 30])
                guardia.inicio_real = inicio + timedelta(minutes=tardanza)
                guardia.fin_real = guardia.inicio_real + (fin - inicio)
        elif r < 0.88:
            guardia.estado = EstadoGuardiaCuadroEnum.incumplida
            guardia.justificada = random.random() < 0.5
            guardia.motivo_incumplimiento = (
                'Aviso de salud presentado con antelacion'
                if guardia.justificada
                else 'Incomparecencia sin aviso previo'
            )
        elif r < 0.93:
            guardia.estado = EstadoGuardiaCuadroEnum.cancelada
            guardia.motivo_cancelacion = pick([
                'Cancelada por la jefatura',
                'Actividad institucional en el area',
                'Franja suspendida temporalmente',
            ])
        # resto: queda planificada (no se registro la operacion)
    elif fecha == HOY:
        guardia.estado = random.choice([
            EstadoGuardiaCuadroEnum.activa,
            EstadoGuardiaCuadroEnum.finalizada,
            EstadoGuardiaCuadroEnum.planificada,
        ])
        if guardia.estado == EstadoGuardiaCuadroEnum.finalizada and franja is not None:
            inicio, fin = intervalo(franja.hora_inicio, franja.hora_fin, fecha)
            guardia.inicio_real = inicio + timedelta(minutes=random.choice([0, 5, 15]))
            guardia.fin_real = guardia.inicio_real + (fin - inicio)
        elif guardia.estado == EstadoGuardiaCuadroEnum.activa and franja is not None:
            inicio, _ = intervalo(franja.hora_inicio, franja.hora_fin, fecha)
            guardia.inicio_real = inicio + timedelta(minutes=random.choice([0, 5, 10]))
    # futuro: queda planificada


# ---------------------------------------------------------------------------
# Incidencias de cuadro
# ---------------------------------------------------------------------------

async def _crear_incidencias_cuadro(db, postas, asps) -> int:
    guardias = (
        await db.execute(
            select(GuardiaCuadro)
            .join(PlanGuardiaCuadro)
            .where(
                PlanGuardiaCuadro.estado == EstadoPlanGuardiaEnum.aprobado,
                GuardiaCuadro.fecha <= HOY,
                GuardiaCuadro.estado != EstadoGuardiaCuadroEnum.cancelada,
            )
        )
    ).scalars().all()

    total = 0
    for guardia in guardias:
        if random.random() >= 0.10:
            continue
        tipo, severidad, desc = pick(INCIDENCIAS_CUADRO_DATA)
        inicio = datetime.combine(
            guardia.fecha, time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
        )
        db.add(IncidenciaCuadro(
            guardia_cuadro_id=guardia.id,
            tipo=tipo,
            severidad=severidad,
            descripcion=desc,
            fecha_hora=inicio,
            posta_id=pick(postas).id if random.random() < 0.7 else None,
            asp_id=pick(asps).id if random.random() < 0.5 else None,
            area=pick(AREAS),
            acciones_tomadas=pick([
                'Se dio parte al supervisor de turno',
                'Se coordino con la posta mas cercana',
                'Se registro en el libro de novedades',
                None,
            ]),
            requiere_seguimiento=severidad in (SeveridadEnum.alta, SeveridadEnum.critica),
        ))
        total += 1

    await db.flush()
    return total


# ---------------------------------------------------------------------------
# Cuentas de usuario de cuadro
# ---------------------------------------------------------------------------

def _crear_cuentas_cuadro(db, cuadros) -> int:
    creadas = 0
    # Cuadro de referencia: primer hombre activo sin marca y primera mujer activa.
    candidatos = []
    primero_m = next(
        (c for c in cuadros if c.sexo == SexoEnum.masculino and c.activo and not c.sin_guardia_vie_dom),
        None,
    )
    primera_f = next((c for c in cuadros if c.sexo == SexoEnum.femenino and c.activo), None)
    if primero_m:
        candidatos.append(('cuadro1', primero_m))
    if primera_f:
        candidatos.append(('cuadro2', primera_f))

    # Dos cuentas adicionales para probar el panel.
    for c in cuadros:
        if len(candidatos) >= 4:
            break
        if c.activo and all(c.id != candidato[1].id for candidato in candidatos):
            candidatos.append((f'cuadro{len(candidatos) + 1}', c))

    for username, cuadro in candidatos:
        db.add(Usuario(
            username=username,
            hashed_password=get_password_hash("cuadro1234"),
            activo=True,
            rol="cuadro",
            cuadro_id=cuadro.id,
        ))
        creadas += 1
    return creadas


# ---------------------------------------------------------------------------
# Seed auxiliar: cuadros de prueba con CI TEST-
# ---------------------------------------------------------------------------

async def seed_cuadros_prueba():
    """Inserta cuadros adicionales con CI TEST- para pruebas puntuales."""
    print('Insertando cuadros de prueba (TEST-)...')
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        usados_ci = set()
        result = await db.execute(select(Cuadro).where(Cuadro.ci.like('TEST-%')))
        for c in result.scalars().all():
            usados_ci.add(c.ci)

        for i in range(30):
            while True:
                ci = f'TEST-{random.randint(100000, 999999)}'
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            db.add(Cuadro(
                nombre=f'TestM{i + 1}', apellidos=pick(APELLIDOS), ci=ci,
                cargo='Oficial de Prueba', area='Pruebas',
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=SexoEnum.masculino, activo=True, sin_guardia_vie_dom=False,
            ))

        for i in range(12):
            while True:
                ci = f'TEST-{random.randint(100000, 999999)}'
                if ci not in usados_ci:
                    usados_ci.add(ci)
                    break
            db.add(Cuadro(
                nombre=f'TestF{i + 1}', apellidos=pick(APELLIDOS), ci=ci,
                cargo='Oficial de Prueba', area='Pruebas',
                telefono=f'+53{random.randint(50000000, 59999999)}',
                sexo=SexoEnum.femenino, activo=True, sin_guardia_vie_dom=False,
            ))

        await db.commit()
        print('  42 cuadros de prueba insertados (30 hombres, 12 mujeres)')


if __name__ == '__main__':
    if "--cuadros-prueba" in sys.argv:
        asyncio.run(seed_cuadros_prueba())
    else:
        asyncio.run(seed())
