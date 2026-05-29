<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <div class="dashboard-title-block">
        <div class="dashboard-title-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div>
          <h2 class="dashboard-title">Dashboard</h2>
          <p class="dashboard-subtitle">{{ fechaHoy }}</p>
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <Card v-for="stat in statCards" :key="stat.title" class="stat-card">
        <template #content>
          <div class="stat-head">
            <div>
              <div class="stat-label">{{ stat.title }}</div>
              <div class="stat-value" :class="stat.valueClass">{{ stat.value }}</div>
              <div class="stat-subtitle">{{ stat.description }}</div>
            </div>
            <div class="stat-icon" :class="stat.iconClass">
              <i :class="stat.icon"></i>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Card class="coverage-card">
      <template #content>
        <div class="coverage-head">
          <div>
            <h3 class="section-title">Cobertura del Dia</h3>
            <p class="section-subtitle">Porcentaje de postas cubiertas hoy</p>
          </div>
          <div class="coverage-badge">
            <i class="pi pi-shield"></i>
          </div>
        </div>

        <div class="coverage-body">
          <div class="coverage-main">
            <div class="coverage-row">
              <span>Progreso</span>
              <strong>{{ cobertura }}%</strong>
            </div>
            <div class="coverage-bar">
              <div class="coverage-fill" :style="{ width: `${cobertura}%` }"></div>
            </div>
          </div>

          <div class="coverage-state">
            <i class="pi pi-trending-up"></i>
            <span>Activo</span>
          </div>
        </div>
      </template>
    </Card>

    <div class="activity-grid">
      <Card class="activity-card">
        <template #content>
          <div class="section-head">
            <div>
              <h3 class="section-title">Guardias Recientes</h3>
              <p class="section-subtitle">Ultimas guardias programadas</p>
            </div>
          </div>

          <div v-if="cargando" class="empty-state">Cargando dashboard...</div>

          <div v-else-if="recentGuardias.length === 0" class="empty-state compact">
            <i class="pi pi-calendar empty-icon"></i>
            <p>No hay guardias programadas</p>
          </div>

          <div v-else class="recent-list">
            <div v-for="guardia in recentGuardias" :key="guardia.id" class="recent-item">
              <div class="recent-icon">
                <i class="pi pi-calendar"></i>
              </div>
              <div class="recent-copy">
                <p class="recent-name">{{ getNombreGuardia(guardia) }}</p>
                <p class="recent-meta">{{ getDetalleGuardia(guardia) }}</p>
              </div>
              <Tag :value="getEstadoLabel(guardia.estado)" :severity="getEstadoSeverity(guardia.estado)" />
            </div>
          </div>
        </template>
      </Card>

      <Card class="activity-card">
        <template #content>
          <div class="section-head">
            <div>
              <h3 class="section-title">Estado del Dia</h3>
              <p class="section-subtitle">Distribucion operativa actual</p>
            </div>
          </div>

          <div v-if="cargando" class="empty-state">Cargando estado...</div>

          <div v-else class="status-list">
            <div v-for="item in statusCards" :key="item.label" class="status-item">
              <div class="status-copy">
                <div class="status-dot" :class="item.dotClass"></div>
                <div>
                  <p class="status-label">{{ item.label }}</p>
                  <p class="status-sub">{{ item.description }}</p>
                </div>
              </div>
              <strong class="status-value">{{ item.value }}</strong>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import { guardiaApi } from '../api/guardia'
import { aspApi } from '../api/asp'
import { postaApi } from '../api/posta'

const cargando = ref(true)
const guardias = ref([])
const aspById = ref({})
const turnoById = ref({})
const aspsActivos = ref(0)
const postasActivas = ref(0)

const fechaHoy = new Date().toLocaleDateString('es-ES', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
})

const recentGuardias = computed(() => guardias.value.slice(0, 5))

const guardiasHoy = computed(() => guardias.value.length)
const ausenciasHoy = computed(() =>
  guardias.value.filter((guardia) => guardia.estado === 'ausente').length
)
const guardiasCubiertas = computed(() =>
  guardias.value.filter((guardia) => guardia.estado === 'activa' || guardia.estado === 'finalizada').length
)
const cobertura = computed(() => {
  const totalPostas = postasActivas.value
  if (!totalPostas) return 0
  return Math.min(100, Math.round((guardiasCubiertas.value / totalPostas) * 100))
})

const statCards = computed(() => [
  {
    title: 'Personal Activo',
    value: aspsActivos.value,
    description: 'ASP registrados',
    icon: 'pi pi-users',
    iconClass: 'icon-blue',
    valueClass: 'value-blue',
  },
  {
    title: 'Postas Activas',
    value: postasActivas.value,
    description: 'Ubicaciones',
    icon: 'pi pi-building',
    iconClass: 'icon-teal',
    valueClass: 'value-teal',
  },
  {
    title: 'Guardias Hoy',
    value: guardiasHoy.value,
    description: 'Programadas',
    icon: 'pi pi-calendar',
    iconClass: 'icon-gold',
    valueClass: 'value-gold',
  },
  {
    title: 'Ausencias Hoy',
    value: ausenciasHoy.value,
    description: 'En el dia',
    icon: 'pi pi-exclamation-triangle',
    iconClass: 'icon-red',
    valueClass: 'value-red',
  },
])

const statusCards = computed(() => [
  {
    label: 'Planificadas',
    description: 'Guardias aún por iniciar',
    value: guardias.value.filter((guardia) => guardia.estado === 'planificada').length,
    dotClass: 'dot-secondary',
  },
  {
    label: 'Activas',
    description: 'Guardias en curso',
    value: guardias.value.filter((guardia) => guardia.estado === 'activa').length,
    dotClass: 'dot-success',
  },
  {
    label: 'Finalizadas',
    description: 'Guardias cerradas',
    value: guardias.value.filter((guardia) => guardia.estado === 'finalizada').length,
    dotClass: 'dot-info',
  },
  {
    label: 'Ausentes',
    description: 'Guardias no cubiertas',
    value: ausenciasHoy.value,
    dotClass: 'dot-danger',
  },
])

function formatHora(valor) {
  if (!valor) return ''
  return new Date(valor).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

function formatHoraCorta(valor) {
  if (!valor) return ''
  const partes = String(valor).split(':')
  if (partes.length < 2) return valor
  return `${partes[0].padStart(2, '0')}:${partes[1].padStart(2, '0')}`
}

function getAspNombreDesdeCache(id) {
  const asp = aspById.value[id]
  if (!asp) return `ASP #${id}`
  const apellido = asp.apellido || asp.apellidos || ''
  return `${asp.nombre} ${apellido}`.trim()
}

function getNombreGuardia(guardia) {
  const asp = guardia.asp
  if (asp) {
    const apellido = asp.apellido || asp.apellidos || ''
    return `${asp.nombre} ${apellido}`.trim()
  }

  return getAspNombreDesdeCache(guardia.asp_id)
}

function getDetalleGuardia(guardia) {
  const posta = guardia.posta
  const turno = guardia.turno
  const postaNombre = posta?.nombre || turnoById.value[guardia.turno_posta_id || guardia.turno_id]?.posta_nombre || 'Posta'
  const turnoNombre = turno?.nombre || turnoById.value[guardia.turno_posta_id || guardia.turno_id]?.nombre || 'Turno'
  const horarioTurno = (() => {
    const turnoCache = turnoById.value[guardia.turno_posta_id || guardia.turno_id]
    if (!turnoCache) return ''
    const rango = `${formatHoraCorta(turnoCache.hora_inicio)}-${formatHoraCorta(turnoCache.hora_fin)}`
    return ` (${rango})`
  })()

  return `${postaNombre} - ${turnoNombre}${horarioTurno}`
}

function getEstadoLabel(estado) {
  const labels = {
    planificada: 'Programada',
    activa: 'Activa',
    finalizada: 'Finalizada',
    ausente: 'Ausente',
    cancelada: 'Cancelada',
  }

  return labels[estado] || estado
}

function getEstadoSeverity(estado) {
  const severities = {
    planificada: 'secondary',
    activa: 'success',
    finalizada: 'info',
    ausente: 'danger',
    cancelada: 'secondary',
  }

  return severities[estado] || 'secondary'
}

async function cargarMapas(guardiasHoy) {
  const aspIds = [...new Set((guardiasHoy || []).map((guardia) => guardia.asp_id))]
  const aspIndex = {}

  await Promise.all(
    aspIds.map(async (id) => {
      try {
        const respuesta = await aspApi.obtener(id)
        aspIndex[id] = respuesta.data
      } catch (error) {
        console.error(error)
      }
    })
  )

  aspById.value = aspIndex

  const postasRespuesta = await postaApi.listar({ activa: true })
  const postas = postasRespuesta.data || []
  const turnoIndex = {}

  postas.forEach((posta) => {
    const turnos = posta.turnos || []
    turnos.forEach((turno) => {
      turnoIndex[turno.id] = { ...turno, posta_nombre: posta.nombre }
    })
  })

  turnoById.value = turnoIndex
}

onMounted(async () => {
  try {
    const hoy = new Date().toISOString().split('T')[0]
    const [guardiasRespuesta, aspsRespuesta, postasRespuesta] = await Promise.all([
      guardiaApi.listar({ fecha: hoy }),
      aspApi.listar({ estado: 'activo', size: 1 }),
      postaApi.listar({ activa: true }),
    ])

    guardias.value = guardiasRespuesta.data || []
    aspsActivos.value = aspsRespuesta.data?.total || 0
    postasActivas.value = Array.isArray(postasRespuesta.data) ? postasRespuesta.data.length : 0

    try {
      await cargarMapas(guardias.value)
    } catch (error) {
      console.error(error)
    }
  } catch (error) {
    console.error(error)
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dashboard-title-block {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.dashboard-title-icon {
  width: 2.625rem;
  height: 2.625rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-50);
  color: var(--brand-600);
  font-size: 1.25rem;
}

.dashboard-title {
  margin: 0;
  font-size: 1.6rem;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text);
}

.dashboard-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
  text-transform: capitalize;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.stat-card,
.coverage-card,
.activity-card {
  border: 1px solid color-mix(in srgb, var(--border) 75%, transparent);
  box-shadow: 0 16px 50px rgba(15, 23, 42, 0.05);
}

.stat-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}

.stat-value {
  font-size: 1.75rem;
  line-height: 1;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.icon-blue {
  background: rgba(14, 165, 233, 0.1);
  color: #0284c7;
}

.icon-teal {
  background: rgba(20, 184, 166, 0.1);
  color: #0f766e;
}

.icon-gold {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.icon-red {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.value-blue {
  color: #0284c7;
}

.value-teal {
  color: #0f766e;
}

.value-gold {
  color: #d97706;
}

.value-red {
  color: #dc2626;
}

.coverage-head,
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.coverage-badge {
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(14, 165, 233, 0.1);
  color: var(--brand-600);
  font-size: 1.2rem;
}

.section-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
}

.section-subtitle {
  margin: 0.35rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.coverage-body {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-top: 1rem;
}

.coverage-main {
  flex: 1;
}

.coverage-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.55rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.coverage-row strong {
  color: var(--text);
}

.coverage-bar {
  height: 0.5rem;
  overflow: hidden;
  border-radius: 9999px;
  background: rgba(148, 163, 184, 0.18);
}

.coverage-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--brand-500), var(--brand-600));
  transition: width 0.35s ease;
}

.coverage-state {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--brand-600);
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.recent-list,
.status-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.recent-item,
.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.875rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  border-radius: 0.9rem;
  background: color-mix(in srgb, var(--surface) 70%, transparent);
}

.recent-item {
  min-height: 4.25rem;
}

.recent-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: rgba(148, 163, 184, 0.14);
  color: var(--text-muted);
  flex-shrink: 0;
}

.recent-copy {
  flex: 1;
  min-width: 0;
}

.recent-name,
.status-label {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.recent-meta,
.status-sub {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.status-copy {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.status-dot {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 9999px;
  flex-shrink: 0;
}

.dot-secondary {
  background: #94a3b8;
}

.dot-success {
  background: #22c55e;
}

.dot-info {
  background: #0ea5e9;
}

.dot-danger {
  background: #ef4444;
}

.status-value {
  font-size: 1rem;
  color: var(--text);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  min-height: 12rem;
  color: var(--text-muted);
}

.empty-state.compact {
  min-height: 10rem;
}

.empty-icon {
  font-size: 1.5rem;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .activity-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .coverage-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .coverage-state {
    width: 100%;
    justify-content: flex-start;
  }

  .dashboard-title {
    font-size: 1.35rem;
  }

  .recent-item,
  .status-item {
    align-items: flex-start;
  }

  .recent-item {
    flex-wrap: wrap;
  }

  .recent-item :deep(.p-tag) {
    margin-left: auto;
  }
}
</style>
