<template>
  <div class="mis-guardias-page mx-auto">
    <!-- Próxima guardia -->
    <v-card v-if="proximaGuardia" rounded="lg" class="proxima-card mb-4 pa-sm-5 pa-3">
      <div class="d-flex flex-wrap align-center justify-space-between ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="primary" size="48" rounded="lg">
            <v-icon icon="mdi-shield-star-outline" color="white" size="24" />
          </v-avatar>
          <div>
            <div class="text-overline text-medium-emphasis">Próxima guardia</div>
            <div class="text-body-1 font-weight-bold">
              {{ fechaLarga(proximaGuardia.fecha) }}
            </div>
            <div class="text-body-2 text-medium-emphasis">
              {{ proximaGuardia.franja_nombre }}
              <span v-if="horarioDe(proximaGuardia)">· {{ horarioDe(proximaGuardia) }}</span>
            </div>
          </div>
        </div>
        <div class="d-flex flex-column align-end ga-1">
          <v-chip :color="estadoColor(proximaGuardia.estado)" variant="tonal" size="small" label class="font-weight-bold">
            {{ estadoLabel(proximaGuardia.estado) }}
          </v-chip>
          <span class="text-body-2 text-medium-emphasis">{{ textoFaltante(proximaGuardia.fecha) }}</span>
        </div>
      </div>
    </v-card>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 mb-4">
        <v-select
          v-model="mes"
          :items="mesesItems"
          label="Mes"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          class="filtro"
        />
        <v-select
          v-model="anio"
          :items="aniosItems"
          label="Año"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          class="filtro"
        />
        <v-spacer v-if="!mobile" />
        <div v-if="planId" class="text-body-2 text-medium-emphasis text-center">
          {{ guardiasMes.length }} guardia{{ guardiasMes.length !== 1 ? 's' : '' }}
        </div>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="4" :avatar="false" />

        <v-alert
          v-else-if="!planId"
          type="info"
          variant="tonal"
          density="comfortable"
          icon="mdi-calendar-remove-outline"
        >
          No hay un plan aprobado para {{ mesLabel(mes) }} {{ anio }}.
        </v-alert>

        <div v-else-if="guardiasMes.length === 0" class="text-center py-10">
          <v-icon icon="mdi-calendar-blank-outline" size="44" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-1 text-medium-emphasis mb-0">No tiene guardias asignadas en este mes</p>
        </div>

        <div v-else class="d-flex flex-column ga-3">
          <v-card
            v-for="g in guardiasMes"
            :key="g.id"
            rounded="lg"
            variant="outlined"
            class="pa-4"
          >
            <div class="d-flex flex-wrap align-center justify-space-between ga-2 mb-3">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="estadoColor(g.estado)" size="40" rounded="lg">
                  <v-icon icon="mdi-shield-account-outline" color="white" size="20" />
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ fechaLarga(g.fecha) }}</div>
                  <div class="text-body-2 text-medium-emphasis">
                    {{ g.franja_nombre }}
                    <span v-if="horarioDe(g)">· {{ horarioDe(g) }}</span>
                  </div>
                </div>
              </div>
              <v-chip :color="estadoColor(g.estado)" variant="tonal" size="small" label class="font-weight-bold">
                {{ estadoLabel(g.estado) }}
              </v-chip>
            </div>

            <div v-if="g.inicio_real || g.fin_real" class="text-body-2 text-medium-emphasis mb-2">
              <span v-if="g.inicio_real">Inicio: {{ formatFechaHora(g.inicio_real) }}</span>
              <span v-if="g.fin_real" class="ml-3">Fin: {{ formatFechaHora(g.fin_real) }}</span>
            </div>
            <p v-if="g.motivo_incumplimiento" class="text-body-2 text-medium-emphasis mb-2 texto-largo">
              <strong>Incumplimiento:</strong> {{ g.motivo_incumplimiento }}
            </p>
            <p v-if="g.motivo_cancelacion" class="text-body-2 text-medium-emphasis mb-2 texto-largo">
              <strong>Cancelación:</strong> {{ g.motivo_cancelacion }}
            </p>

            <div class="d-flex flex-wrap ga-2">
              <v-tooltip :disabled="puedeRegistrar(g)" location="top">
                <template #activator="{ props: tipProps }">
                  <span v-bind="tipProps">
                    <v-btn
                      color="secondary"
                      variant="tonal"
                      size="small"
                      prepend-icon="mdi-clipboard-plus-outline"
                      class="text-none"
                      :disabled="!puedeRegistrar(g)"
                      @click="registrarIncidencia(g)"
                    >
                      Registrar incidencia
                    </v-btn>
                  </span>
                </template>
                <span>Solo en guardias activas o finalizadas o dentro de las 24 horas antes o después de la fecha de guardia</span>
              </v-tooltip>

              <v-btn
                variant="text"
                size="small"
                prepend-icon="mdi-clipboard-text-outline"
                class="text-none"
                @click="verIncidencias(g)"
              >
                Ver incidencias
              </v-btn>
            </div>

            <v-alert
              v-if="fueraDeFecha(g)"
              type="warning"
              density="compact"
              variant="tonal"
              icon="mdi-account-alert-outline"
              class="mt-2 mb-0"
            >
              {{ AVISO_FUERA_FECHA }}
            </v-alert>
          </v-card>
        </div>
      </div>
    </v-card>

    <IncidenciaDialog
      v-model="dialogIncidencia"
      :guardia-id="guardiaAccion?.id"
      :modo="'cuadro'"
      :opciones="opciones"
      :aviso="avisoIncidencia"
      @saved="onIncidenciaSaved"
    />

    <IncidenciasGuardiaDialog
      v-model="dialogIncidencias"
      :guardia="guardiaAccion"
      modo="cuadro"
      :opciones="opciones"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { miGuardiaApi } from '../api/miGuardia'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { formatFechaHora, formatHora } from '../utils/formatters'
import IncidenciaDialog from '../components/IncidenciaDialog.vue'
import IncidenciasGuardiaDialog from '../components/IncidenciasGuardiaDialog.vue'
import {
  AVISO_FUERA_FECHA,
  puedeRegistrarIncidencia,
  requiereAvisoAdministrador,
} from '../utils/incidencia'

const toast = useToast()
const { mobile } = useDisplay()

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
const DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

const ahora = new Date()
const mes = ref(ahora.getMonth() + 1)
const anio = ref(ahora.getFullYear())
const mesesItems = MESES.map((label, i) => ({ title: label, value: i + 1 }))
const aniosItems = Array.from({ length: 6 }, (_, i) => anio.value - 2 + i)

const cargando = ref(true)
const planId = ref(null)
const guardiasMes = ref([])
const todas = ref([])
const opciones = ref({ postas: [], asp: [] })

const dialogIncidencia = ref(false)
const dialogIncidencias = ref(false)
const guardiaAccion = ref(null)

const estadosInfo = {
  planificada: { color: 'info', label: 'Planificada' },
  activa: { color: 'success', label: 'Activa' },
  finalizada: { color: 'grey', label: 'Finalizada' },
  incumplida: { color: 'error', label: 'Incumplida' },
  cancelada: { color: 'error', label: 'Cancelada' },
}

function mesLabel(m) {
  return MESES[m - 1] || m
}

function estadoColor(estado) {
  return estadosInfo[estado]?.color || 'grey'
}

function estadoLabel(estado) {
  return estadosInfo[estado]?.label || estado
}

function toDate(value) {
  if (!value) return null
  if (value instanceof Date) return value
  return new Date(`${String(value).slice(0, 10)}T12:00:00`)
}

function fechaLarga(value) {
  const d = toDate(value)
  if (!d || Number.isNaN(d.getTime())) return value || ''
  const dia = DIAS[(d.getDay() + 6) % 7]
  return `${dia} ${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
}

function horarioDe(g) {
  const f = g?.franja
  if (!f) return ''
  return `${formatHora(f.hora_inicio)} – ${formatHora(f.hora_fin)}`
}

function hoyYMD() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function textoFaltante(fecha) {
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  const f = toDate(fecha)
  if (!f) return ''
  f.setHours(0, 0, 0, 0)
  const dias = Math.round((f - hoy) / 86400000)
  if (dias < 0) return `Hace ${Math.abs(dias)} día${Math.abs(dias) !== 1 ? 's' : ''}`
  if (dias === 0) return 'Hoy'
  if (dias === 1) return 'Mañana'
  return `En ${dias} días`
}

function puedeRegistrar(g) {
  return puedeRegistrarIncidencia(g)
}

function fueraDeFecha(g) {
  return requiereAvisoAdministrador(g)
}

const proximaGuardia = computed(() => {
  const hoy = hoyYMD()
  return (
    todas.value
      .filter((g) => g.fecha >= hoy && ['planificada', 'activa'].includes(g.estado))
      .sort((a, b) => (a.fecha < b.fecha ? -1 : a.fecha > b.fecha ? 1 : 0))[0] || null
  )
})

async function cargarMes() {
  cargando.value = true
  try {
    const res = await miGuardiaApi.planificacion({ anio: anio.value, mes: mes.value })
    planId.value = res.data.plan_id
    guardiasMes.value = res.data.guardias || []
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar sus guardias'))
  } finally {
    cargando.value = false
  }
}

async function cargarTodas() {
  try {
    const res = await miGuardiaApi.misGuardias({ size: 100 })
    todas.value = res.data.items || []
  } catch {
    todas.value = []
  }
}

async function cargarOpciones() {
  try {
    const res = await miGuardiaApi.opcionesIncidencia()
    opciones.value = { postas: res.data.postas || [], asp: res.data.asp || [] }
  } catch {
    opciones.value = { postas: [], asp: [] }
  }
}

async function recargar() {
  await Promise.all([cargarMes(), cargarTodas()])
}

function registrarIncidencia(g) {
  guardiaAccion.value = g
  dialogIncidencia.value = true
}

const avisoIncidencia = computed(() =>
  guardiaAccion.value && fueraDeFecha(guardiaAccion.value) ? AVISO_FUERA_FECHA : '',
)

function verIncidencias(g) {
  guardiaAccion.value = g
  dialogIncidencias.value = true
}

async function onIncidenciaSaved() {
  await recargar()
}

watch([mes, anio], cargarMes)

onMounted(async () => {
  await Promise.all([cargarMes(), cargarTodas(), cargarOpciones()])
})
</script>

<style scoped>
.mis-guardias-page {
  width: 100%;
}

.proxima-card {
  border-left: 4px solid rgb(var(--v-theme-primary));
}

.texto-largo {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.filtro {
  min-width: 180px;
  max-width: 220px;
}

@media (max-width: 599px) {
  .filtro {
    min-width: 0;
    max-width: 100%;
    width: 100%;
    flex: none;
  }
}
</style>
