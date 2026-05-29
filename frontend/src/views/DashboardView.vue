<template>
  <div>
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div>
          <h2 class="page-title">Dashboard</h2>
          <p class="page-subtitle">{{ fechaHoy }}</p>
        </div>
      </div>
    </div>

    <div class="metrics-grid">
      <Card class="metric-card">
        <template #content>
          <div class="metric-label">Guardias activas hoy</div>
          <div class="metric-value text-success">{{ metricas.activas }}</div>
          <div class="metric-sub">de {{ metricas.planificadas }} planificadas</div>
        </template>
      </Card>
      <Card class="metric-card">
        <template #content>
          <div class="metric-label">Postas sin cubrir</div>
          <div class="metric-value text-danger">{{ metricas.sinCubrir }}</div>
          <div class="metric-sub">turno actual</div>
        </template>
      </Card>
      <Card class="metric-card">
        <template #content>
          <div class="metric-label">Ausencias hoy</div>
          <div class="metric-value text-warning">{{ metricas.ausentes }}</div>
          <div class="metric-sub">en el dia</div>
        </template>
      </Card>
      <Card class="metric-card">
        <template #content>
          <div class="metric-label">Total ASP activos</div>
          <div class="metric-value text-info">{{ metricas.aspActivos }}</div>
          <div class="metric-sub">en el sistema</div>
        </template>
      </Card>
    </div>

    <Card style="margin-top: 24px">
      <template #content>
        <div class="card-header">
          <h3>Guardias de hoy</h3>
          <RouterLink to="/guardias" class="btn-link">Ver todas</RouterLink>
        </div>
        <div v-if="cargando" class="empty-state">Cargando...</div>
        <div v-else-if="guardias.length === 0" class="empty-state">
          No hay guardias registradas para hoy
        </div>
        <DataTable
          v-else
          :value="guardias"
          stripedRows
          size="small"
        >
          <Column header="ASP">
            <template #body="{ data }">
              {{ nombreAsp(data.asp_id) }}
            </template>
          </Column>
          <Column header="Posta / Turno">
            <template #body="{ data }">
              {{ labelTurno(data.turno_posta_id) }}
            </template>
          </Column>
          <Column header="Hora llegada">
            <template #body="{ data }">
              {{ data.hora_inicio_real ? formatHora(data.hora_inicio_real) : '—' }}
            </template>
          </Column>
          <Column header="Tardanza">
            <template #body="{ data }">
              <Tag v-if="data.tardanza_minutos > 0" :value="`${data.tardanza_minutos} min`" severity="warn" />
              <Tag v-else-if="data.hora_inicio_real" value="A tiempo" severity="success" />
              <span v-else>—</span>
            </template>
          </Column>
          <Column header="Estado">
            <template #body="{ data }">
              <Tag :value="labelEstado(data.estado)" :severity="severidadEstado(data.estado)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { guardiaApi } from '../api/guardia'
import { aspApi } from '../api/asp'
import { postaApi } from '../api/posta'

const cargando = ref(true)
const guardias = ref([])
const aspById = ref({})
const turnoById = ref({})
const metricas = ref({
  activas: 0,
  planificadas: 0,
  sinCubrir: 0,
  ausentes: 0,
  aspActivos: 0,
})

const fechaHoy = new Date().toLocaleDateString('es-ES', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
})

function formatHora(dt) {
  return new Date(dt).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

function formatHoraCorta(value) {
  if (!value) return ''
  const parts = String(value).split(':')
  if (parts.length < 2) return value
  return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`
}

function nombreAsp(id) {
  const asp = aspById.value[id]
  return asp ? `${asp.nombre} ${asp.apellidos}` : `ASP #${id}`
}

function labelTurno(turnoId) {
  const turno = turnoById.value[turnoId]
  if (!turno) return `Turno #${turnoId}`
  const horario = `${formatHoraCorta(turno.hora_inicio)}-${formatHoraCorta(turno.hora_fin)}`
  return `${turno.posta_nombre} - ${turno.nombre} (${horario})`
}

function labelEstado(estado) {
  const map = {
    planificada: 'Planificada',
    activa: 'Activa',
    finalizada: 'Finalizada',
    ausente: 'Ausente',
    cancelada: 'Cancelada',
  }
  return map[estado] || 'Desconocido'
}

function severidadEstado(estado) {
  const map = {
    planificada: 'secondary',
    activa: 'success',
    finalizada: 'success',
    ausente: 'danger',
    cancelada: 'secondary',
  }
  return map[estado] || 'secondary'
}

async function cargarMapas(guardiasHoy) {
  const aspIds = [...new Set((guardiasHoy || []).map(g => g.asp_id))]
  const aspIndex = {}
  await Promise.all(
    aspIds.map(async id => {
      try {
        const res = await aspApi.obtener(id)
        aspIndex[id] = res.data
      } catch (e) {
        console.error(e)
      }
    })
  )
  aspById.value = aspIndex

  const postasRes = await postaApi.listar({})
  const postas = postasRes.data || []
  const turnoIndex = {}
  postas.forEach(posta => {
    const turnos = posta.turnos || []
    turnos.forEach(turno => {
      turnoIndex[turno.id] = { ...turno, posta_nombre: posta.nombre }
    })
  })
  turnoById.value = turnoIndex
}

onMounted(async () => {
  try {
    const hoy = new Date().toISOString().split('T')[0]
    const [gRes, aspRes] = await Promise.all([
      guardiaApi.listar({ fecha: hoy }),
      aspApi.listar({ estado: 'activo', size: 1 }),
    ])
    guardias.value = gRes.data
    metricas.value.planificadas = guardias.value.length
    metricas.value.activas = guardias.value.filter(g => g.estado === 'activa').length
    metricas.value.ausentes = guardias.value.filter(g => g.estado === 'ausente').length
    metricas.value.sinCubrir = guardias.value.filter(
      g => g.estado === 'planificada' || g.estado === 'ausente'
    ).length
    metricas.value.aspActivos = aspRes.data.total

    try {
      await cargarMapas(guardias.value)
    } catch (e) {
      console.error(e)
    }
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.metric-card {
  border: 1px solid var(--border);
}
.metric-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}
.metric-sub {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-header h3 {
  font-size: 14px;
  font-weight: 600;
}
.page-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title-icon {
  width: 42px;
  height: 42px;
  background: var(--brand-50);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--brand-600);
}
.page-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
  text-transform: capitalize;
}
.btn-link {
  font-size: 12px;
  color: var(--brand-600);
  text-decoration: none;
  font-weight: 600;
}
.btn-link:hover {
  text-decoration: underline;
}
.empty-state {
  text-align: center;
  padding: 32px;
  color: #9ca3af;
  font-size: 13px;
}

@media (max-width: 960px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .metric-value {
    font-size: 24px;
  }
}
</style>
