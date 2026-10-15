<template>
  <div class="planes-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">Nuevo plan</v-btn>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <div class="d-flex flex-wrap ga-2 justify-center">
          <v-select
            v-model="filtroAnio"
            :items="aniosItems"
            label="Año"
            variant="solo-filled"
            density="compact"
            hide-details
            bg-color="grey-lighten-4"
            class="planes-filtro"
          />
          <v-select
            v-model="filtroEstado"
            :items="estadosFiltro"
            label="Estado"
            variant="solo-filled"
            density="compact"
            hide-details
            bg-color="grey-lighten-4"
            class="planes-filtro"
          />
        </div>
        <div v-if="total > 0" class="text-body-2 text-medium-emphasis text-center">
          {{ total }} plan{{ total !== 1 ? 'es' : '' }}
        </div>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="6" :avatar="false" />

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && planes.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-calendar-month-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-1 text-medium-emphasis">No hay planes para mostrar</p>
          </div>

          <!-- Mobile: card list -->
          <div v-else-if="!cargando && planes.length > 0 && mobile" key="mobile-list" class="planes-mobile-list">
            <div v-for="plan in planes" :key="plan.id" class="planes-mobile-card pa-4 mb-3">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-3">
                  <v-avatar :color="planEstadoColor(plan.estado)" size="36" rounded="lg">
                    <v-icon icon="mdi-calendar-month-outline" size="18" color="white" />
                  </v-avatar>
                  <div>
                    <div class="text-body-1 font-weight-medium">
                      {{ mesLabel(plan.mes) }} {{ plan.anio }}
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      {{ plan.cantidad_guardias }} guardia{{ plan.cantidad_guardias !== 1 ? 's' : '' }}
                    </div>
                  </div>
                </div>
                <v-chip :color="planEstadoColor(plan.estado)" variant="tonal" size="x-small" label class="font-weight-bold">
                  {{ planEstadoLabel(plan.estado) }}
                </v-chip>
              </div>
              <div class="d-flex align-center justify-space-between">
                <v-chip
                  v-if="plan.generado_automaticamente"
                  size="x-small"
                  variant="tonal"
                  color="secondary"
                  prepend-icon="mdi-robot-outline"
                  label
                >
                  Automático
                </v-chip>
                <span v-else />
                <v-btn
                  size="x-small"
                  variant="text"
                  color="primary"
                  prepend-icon="mdi-eye-outline"
                  class="text-none"
                  @click="verDetalle(plan)"
                >
                  Ver
                </v-btn>
              </div>
            </div>
          </div>

          <!-- Desktop: table -->
          <v-table v-else-if="!cargando && planes.length > 0" key="table" density="comfortable">
            <thead>
              <tr>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Mes</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Automático</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Guardias</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="plan in planes" :key="plan.id">
                <td class="font-weight-medium text-body-1">{{ mesLabel(plan.mes) }} {{ plan.anio }}</td>
                <td>
                  <v-chip :color="planEstadoColor(plan.estado)" variant="tonal" size="small" label class="font-weight-bold">
                    {{ planEstadoLabel(plan.estado) }}
                  </v-chip>
                </td>
                <td class="text-center">
                  <v-icon
                    :icon="plan.generado_automaticamente ? 'mdi-robot-outline' : 'mdi-minus'"
                    :color="plan.generado_automaticamente ? 'secondary' : 'grey-lighten-1'"
                    size="18"
                  />
                </td>
                <td class="text-center text-body-1">{{ plan.cantidad_guardias }}</td>
                <td class="text-center">
                  <v-tooltip text="Ver detalle" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="primary" aria-label="Ver detalle" v-bind="tipProps" @click="verDetalle(plan)">
                        <v-icon icon="mdi-eye-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                </td>
              </tr>
            </tbody>
          </v-table>
        </Transition>
      </div>

      <div v-if="totalPaginas > 1" class="d-flex align-center justify-center ga-2 mt-4">
        <v-btn icon size="small" variant="text" :disabled="pagina === 1" aria-label="Página anterior" @click="cambiarPagina(-1)">
          <v-icon icon="mdi-chevron-left" />
        </v-btn>
        <span class="text-body-2 text-medium-emphasis">{{ pagina }}/{{ totalPaginas }}</span>
        <v-btn icon size="small" variant="text" :disabled="pagina >= totalPaginas" aria-label="Página siguiente" @click="cambiarPagina(1)">
          <v-icon icon="mdi-chevron-right" />
        </v-btn>
      </div>
    </v-card>

    <!-- Dialog nuevo plan -->
    <v-dialog v-model="dialogForm" :max-width="mobile ? undefined : 480" :fullscreen="mobile" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Nuevo plan</v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            v-if="planExistenteId"
            role="alert"
            type="warning"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            <div class="d-flex flex-column ga-2">
              <span>{{ errores._global }}</span>
              <v-btn
                size="small"
                variant="tonal"
                color="primary"
                prepend-icon="mdi-arrow-right"
                class="text-none align-self-start"
                @click="irAPlanExistente"
              >
                Ver plan existente
              </v-btn>
            </div>
          </v-alert>
          <v-alert
            v-else-if="errores._global"
            role="alert"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ errores._global }}
          </v-alert>

          <v-form @submit.prevent="guardar">
            <v-select
              v-model="form.mes"
              label="Mes *"
              :items="mesesItems"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.mes"
              class="mb-1"
            />
            <v-select
              v-model="form.anio"
              label="Año *"
              :items="aniosItems"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.anio"
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarForm">Cancelar</v-btn>
          <v-tooltip :disabled="formValido" location="top">
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="primary"
                  :disabled="!formValido"
                  :loading="guardando"
                  class="text-none text-body-1"
                  @click="guardar"
                >
                  Crear
                </v-btn>
              </span>
            </template>
            <span>Seleccione el mes y el año</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { planCuadroApi } from '../api/planCuadro'
import { extractFieldErrors, normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const router = useRouter()
const toast = useToast()
const { mobile } = useDisplay()

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
const mesesItems = MESES.map((label, i) => ({ title: label, value: i + 1 }))
const estadosInfo = [
  { label: 'Borrador', value: 'borrador', color: 'grey' },
  { label: 'Pendiente de aprobación', value: 'pendiente_aprobacion', color: 'warning' },
  { label: 'Aprobado', value: 'aprobado', color: 'success' },
  { label: 'Rechazado', value: 'rechazado', color: 'error' },
]
const estadoMap = Object.fromEntries(estadosInfo.map((e) => [e.value, e]))

const anioActual = new Date().getFullYear()
const aniosItems = Array.from({ length: 6 }, (_, i) => anioActual - 2 + i)

const filtroAnio = ref(anioActual)
const filtroEstado = ref(null)
const estadosFiltro = [
  { title: 'Todos los estados', value: null },
  ...estadosInfo.map((e) => ({ title: e.label, value: e.value })),
]

const planes = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => (mobile.value ? 10 : 20))
const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))

const dialogForm = ref(false)
const guardando = ref(false)
const form = ref({ mes: new Date().getMonth() + 1, anio: anioActual })
const errores = ref({})
const planExistenteId = ref(null)

const formValido = computed(() => !!form.value.mes && !!form.value.anio)

function mesLabel(mes) {
  return MESES[mes - 1] || mes
}

function planEstadoColor(estado) {
  return estadoMap[estado]?.color || 'grey'
}

function planEstadoLabel(estado) {
  return estadoMap[estado]?.label || estado
}

async function cargarPlanes() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtroAnio.value) params.anio = filtroAnio.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    const res = await planCuadroApi.listar(params)
    planes.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar planes'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarPlanes().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function verDetalle(plan) {
  router.push(`/planes-cuadro/${plan.id}`)
}

function abrirCrear() {
  form.value = { mes: new Date().getMonth() + 1, anio: anioActual }
  errores.value = {}
  planExistenteId.value = null
  dialogForm.value = true
}

function cerrarForm() {
  dialogForm.value = false
  errores.value = {}
  planExistenteId.value = null
}

async function guardar() {
  if (!formValido.value) return
  guardando.value = true
  errores.value = {}
  planExistenteId.value = null
  try {
    const res = await planCuadroApi.crear({ anio: form.value.anio, mes: form.value.mes })
    toast.success('Plan creado correctamente')
    cerrarForm()
    router.push(`/planes-cuadro/${res.data.id}`)
  } catch (e) {
    const status = e?.response?.status
    const fieldErrors = extractFieldErrors(e)
    if (status === 409) {
      errores.value = { _global: normalizeApiError(e, 'Ya existe un plan para ese mes') }
      try {
        const res = await planCuadroApi.listar({ anio: form.value.anio, mes: form.value.mes, size: 1 })
        planExistenteId.value = res.data.items?.[0]?.id || null
      } catch {
        planExistenteId.value = null
      }
    } else if (Object.keys(fieldErrors).some((k) => k !== '_global')) {
      errores.value = fieldErrors
    } else {
      errores.value = { _global: normalizeApiError(e, 'Error al crear el plan') }
    }
  } finally {
    guardando.value = false
  }
}

function irAPlanExistente() {
  const id = planExistenteId.value
  cerrarForm()
  if (id) router.push(`/planes-cuadro/${id}`)
}

watch(filtroAnio, () => { pagina.value = 1; cargarPlanes() })
watch(filtroEstado, () => { pagina.value = 1; cargarPlanes() })
watch(mobile, () => { pagina.value = 1; cargarPlanes() })

onMounted(cargarPlanes)
</script>

<style scoped>
.planes-page {
  width: 100%;
}

.planes-filtro {
  min-width: 180px;
  max-width: 220px;
}

.planes-mobile-list {
  display: flex;
  flex-direction: column;
}

.planes-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@media (max-width: 599px) {
  .planes-filtro {
    min-width: 0;
    max-width: 100%;
    flex: 1 1 140px;
  }
}
</style>
