<template>
  <div class="dashboard mx-auto">
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      density="compact"
      class="mb-4"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>

    <div v-if="cargando" class="d-flex align-center justify-center" style="min-height: 300px">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <Transition name="fade-up" mode="out-in">
      <div v-if="!cargando" key="content">
      <v-row class="mb-6" dense>
        <v-col v-for="stat in stats" :key="stat.label" cols="6" md="3">
          <v-card rounded="lg" class="stat-card pa-4 d-flex flex-column" style="min-height: 120px">
            <div class="d-flex align-center ga-3 mb-auto">
              <v-avatar :color="stat.color" size="40" rounded="lg">
                <v-icon :icon="stat.icon" color="white" size="20" />
              </v-avatar>
              <span class="text-body-2 text-medium-emphasis">{{ stat.label }}</span>
            </div>
            <div class="mt-3">
              <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
              <div v-if="stat.sub" class="text-caption text-medium-emphasis mt-1">{{ stat.sub }}</div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-card v-if="cobertura && cobertura.total > 0" rounded="lg" class="mb-6 pa-sm-5 pa-3">
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="text-subtitle-2 font-weight-bold">Cobertura del día</div>
          <div class="text-h5 font-weight-bold" :class="coberturaColor">
            {{ cobertura.porcentaje }}%
          </div>
        </div>
        <v-progress-linear
          :model-value="cobertura.porcentaje"
          :color="coberturaBarColor"
          height="8"
          rounded
          aria-label="Porcentaje de cobertura del día"
        />
        <div class="d-flex justify-space-between text-caption text-medium-emphasis mt-3">
          <span>Planificadas: {{ cobertura.total }}</span>
          <span>Finalizadas: {{ cobertura.finalizadas }}</span>
          <span>Sin cubrir: {{ cobertura.sin_cubrir }}</span>
        </div>
      </v-card>

      <v-card rounded="lg" class="pa-sm-5 pa-3">
        <div class="d-flex align-center justify-space-between mb-4">
          <div class="text-subtitle-2 font-weight-bold">Guardias de hoy</div>
          <v-chip v-if="guardiasHoy.length" size="small" variant="tonal" color="primary">
            {{ guardiasHoy.length }}
          </v-chip>
        </div>

        <div v-if="guardiasHoy.length === 0" class="text-center py-8">
          <v-icon icon="mdi-shield-check-outline" size="48" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-2 text-medium-emphasis">No hay guardias programadas para hoy</p>
        </div>

        <template v-else>
          <div class="d-flex flex-wrap ga-2 mb-4">
            <v-chip
              v-for="s in estadoSummary"
              :key="s.estado"
              size="small"
              variant="tonal"
              :color="s.color"
              label
            >
              {{ s.count }} {{ s.estado }}
            </v-chip>
          </div>

          <v-table v-if="!mobile" density="comfortable">
            <thead>
              <tr>
                <th class="text-caption font-weight-bold text-medium-emphasis">ASP</th>
                <th class="text-caption font-weight-bold text-medium-emphasis">Posta</th>
                <th class="text-caption font-weight-bold text-medium-emphasis">Horario</th>
                <th class="text-caption font-weight-bold text-medium-emphasis">Estado</th>
                <th class="text-caption font-weight-bold text-medium-emphasis text-right">Tardanza</th>
                <th class="text-caption font-weight-bold text-medium-emphasis text-right"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="g in guardiasHoy" :key="g.id">
                <td class="font-weight-medium">{{ g.asp_nombre }}</td>
                <td class="text-medium-emphasis">{{ g.posta_nombre }}</td>
                <td class="text-medium-emphasis mono">{{ g.horario }}</td>
                <td>
                  <v-chip :color="estadoColor(g.estado)" size="x-small" variant="tonal" label>
                    {{ g.estado }}
                  </v-chip>
                </td>
                <td class="text-right">
                  <span v-if="g.tardanza" class="text-error text-body-2">{{ g.tardanza }} min</span>
                  <span v-else class="text-medium-emphasis">—</span>
                </td>
                <td class="text-right">
                  <v-btn
                    icon variant="text" size="small" color="primary"
                    @click="router.push({ name: 'guardias', query: { detalle: g.id } })"
                    aria-label="Ver guardia"
                  >
                    <v-icon icon="mdi-eye-outline" size="18" />
                    <v-tooltip activator="parent" location="top">Ver</v-tooltip>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>

          <div v-else class="dashboard-guardias-mobile">
            <div v-for="g in guardiasHoy" :key="g.id" class="dashboard-guardia-card pa-3 mb-2">
              <div class="d-flex align-center justify-space-between mb-1">
                <div class="d-flex align-center ga-2">
                  <v-avatar :color="estadoColor(g.estado)" size="32" rounded="lg">
                    <v-icon icon="mdi-account-outline" size="16" color="white" />
                  </v-avatar>
                  <div>
                    <div class="text-body-2 font-weight-medium">{{ g.asp_nombre }}</div>
                    <div class="text-caption text-medium-emphasis">{{ g.posta_nombre }}</div>
                  </div>
                </div>
                <v-chip :color="estadoColor(g.estado)" size="x-small" variant="tonal" label>
                  {{ g.estado }}
                </v-chip>
              </div>
              <div class="d-flex align-center justify-space-between mt-2">
                <span class="text-caption text-medium-emphasis mono">{{ g.horario }}</span>
                <div class="d-flex align-center ga-2">
                  <span v-if="g.tardanza" class="text-caption text-error">+{{ g.tardanza }} min</span>
                  <v-btn
                    icon variant="text" size="x-small" color="primary"
                    @click="router.push({ name: 'guardias', query: { detalle: g.id } })"
                    aria-label="Ver guardia"
                  >
                    <v-icon icon="mdi-eye-outline" size="16" />
                  </v-btn>
                </div>
              </div>
            </div>
          </div>
        </template>
      </v-card>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { aspApi } from '../api/asp'
import { guardiaApi } from '../api/guardia'
import { postaApi } from '../api/posta'
import { reporteApi } from '../api/reporte'
import { normalizeApiError } from '../utils/error'

const router = useRouter()
const { mobile } = useDisplay()
const cargando = ref(true)
const error = ref('')

const totalAsp = ref(0)
const totalPostas = ref(0)
const guardiasRaw = ref([])
const coberturaData = ref(null)
const aspMap = ref({})
const postaMap = ref({})

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

const stats = computed(() => [
  {
    label: 'ASP Registrados',
    value: totalAsp.value,
    icon: 'mdi-account-group-outline',
    color: 'primary',
    sub: null,
  },
  {
    label: 'Postas Activas',
    value: totalPostas.value,
    icon: 'mdi-office-building-outline',
    color: 'success',
    sub: null,
  },
  {
    label: 'Guardias Hoy',
    value: guardiasRaw.value.length,
    icon: 'mdi-shield-check-outline',
    color: 'warning',
    sub: null,
  },
  {
    label: 'Cobertura',
    value: coberturaData.value ? `${coberturaData.value.cobertura_general}%` : '—',
    icon: 'mdi-chart-donut',
    color: coberturaData.value && coberturaData.value.cobertura_general >= 80 ? 'success' : 'error',
    sub: null,
  },
])

const cobertura = computed(() => {
  if (!coberturaData.value) return null
  return {
    porcentaje: coberturaData.value.cobertura_general,
    total: coberturaData.value.total_planificadas,
    finalizadas: coberturaData.value.total_finalizadas,
    sin_cubrir: coberturaData.value.total_sin_cubrir,
  }
})

const coberturaColor = computed(() => {
  if (!cobertura.value) return ''
  if (cobertura.value.porcentaje >= 80) return 'text-success'
  if (cobertura.value.porcentaje >= 50) return 'text-warning'
  return 'text-error'
})

const coberturaBarColor = computed(() => {
  if (!cobertura.value) return 'primary'
  if (cobertura.value.porcentaje >= 80) return 'success'
  if (cobertura.value.porcentaje >= 50) return 'warning'
  return 'error'
})

const guardiasHoy = computed(() => {
  return guardiasRaw.value.map((g) => {
    const asp = aspMap.value[g.asp_id]
    const turno = postaMap.value[g.turno_posta_id]
    return {
      id: g.id,
      asp_nombre: asp ? `${asp.nombre} ${asp.apellidos}` : `ASP #${g.asp_id}`,
      posta_nombre: turno?.posta_nombre || '—',
      horario: turno?.horario || '—',
      estado: g.estado,
      tardanza: g.tardanza_minutos || null,
    }
  })
})

const estadoSummary = computed(() => {
  const counts = {}
  for (const g of guardiasRaw.value) {
    counts[g.estado] = (counts[g.estado] || 0) + 1
  }
  return Object.entries(counts).map(([estado, count]) => ({
    estado,
    count,
    color: estadoColor(estado),
  }))
})

function estadoColor(estado) {
  const map = {
    programada: 'grey',
    activa: 'primary',
    finalizada: 'success',
    ausente: 'error',
  }
  return map[estado] || 'grey'
}

function buildPostaTurnoMap(turnos) {
  const map = {}
  for (const turno of turnos) {
    map[turno.id] = {
      posta_nombre: turno.posta_nombre,
      horario: `${String(turno.hora_inicio).slice(0, 5)} - ${String(turno.hora_fin).slice(0, 5)}`,
    }
  }
  return map
}

async function cargarDatos() {
  cargando.value = true
  error.value = ''
  try {
    const hoy = todayStr()

    const [aspRes, guardiasRes, coberturaRes, turnosRes, postasRes] = await Promise.allSettled([
      aspApi.listar({ page: 1, size: 1 }),
      guardiaApi.listar({ fecha: hoy, page: 1, size: 100 }),
      reporteApi.cobertura({ fecha_desde: hoy, fecha_hasta: hoy }),
      postaApi.listarTurnos({ page: 1, size: 100 }),
      postaApi.listar({ page: 1, size: 1, activa: true }),
    ])

    if (aspRes.status === 'fulfilled') {
      totalAsp.value = aspRes.value.data.total || 0
    }

    if (totalAsp.value > 0) {
      const pages = Math.ceil(totalAsp.value / 100)
      for (let p = 1; p <= pages; p++) {
        const pageRes = await aspApi.listar({ page: p, size: 100 }).catch(() => null)
        if (pageRes) {
          for (const a of pageRes.data.items || []) {
            aspMap.value[a.id] = a
          }
        }
      }
    }

    if (guardiasRes.status === 'fulfilled') {
      guardiasRaw.value = guardiasRes.value.data.items || []
    }

    if (coberturaRes.status === 'fulfilled') {
      coberturaData.value = coberturaRes.value.data
    }

    if (turnosRes.status === 'fulfilled') {
      postaMap.value = buildPostaTurnoMap(turnosRes.value.data.items || [])
    }

    if (postasRes.status === 'fulfilled') {
      totalPostas.value = postasRes.value.data.total || 0
    }
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al cargar datos del dashboard')
  } finally {
    cargando.value = false
  }
}

onMounted(cargarDatos)
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.mono {
  font-variant-numeric: tabular-nums;
}

.dashboard-guardias-mobile {
  display: flex;
  flex-direction: column;
}

.dashboard-guardia-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}
</style>
