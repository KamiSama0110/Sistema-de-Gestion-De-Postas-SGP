<template>
  <div class="plan-detalle-page mx-auto">
    <!-- No encontrado -->
    <v-card v-if="noEncontrado" rounded="lg" class="pa-8 text-center">
      <v-icon icon="mdi-file-question-outline" size="56" color="grey-lighten-1" class="mb-3" />
      <h2 class="text-h6 font-weight-bold mb-1">Plan no encontrado</h2>
      <p class="text-body-2 text-medium-emphasis mb-6">
        El plan solicitado no existe o fue eliminado.
      </p>
      <v-btn color="primary" variant="tonal" prepend-icon="mdi-arrow-left" class="text-none" @click="volver">
        Volver a la lista
      </v-btn>
    </v-card>

    <template v-else>
      <div class="d-flex align-center ga-2 mb-4">
        <v-btn icon size="small" variant="text" aria-label="Volver" @click="volver">
          <v-icon icon="mdi-arrow-left" />
        </v-btn>
        <span class="text-body-2 text-medium-emphasis">Planificación de cuadros</span>
      </div>

      <!-- Cabecera -->
      <v-card rounded="lg" class="pa-sm-5 pa-3 mb-4">
        <div v-if="cargando && !plan" class="py-6 d-flex justify-center">
          <v-progress-circular indeterminate color="primary" />
        </div>
        <template v-else-if="plan">
          <div class="d-flex flex-wrap align-center justify-space-between ga-3 mb-4">
            <div class="d-flex align-center ga-3">
              <div>
                <h1 class="text-h5 font-weight-bold">{{ mesLabel(plan.mes) }} {{ plan.anio }}</h1>
                <div class="d-flex align-center ga-2 mt-1">
                  <v-chip :color="planEstadoColor(plan.estado)" variant="tonal" size="small" label class="font-weight-bold">
                    {{ planEstadoLabel(plan.estado) }}
                  </v-chip>
                  <v-chip
                    v-if="plan.generado_automaticamente"
                    size="small"
                    variant="tonal"
                    color="secondary"
                    prepend-icon="mdi-robot-outline"
                    label
                  >
                    Automático
                  </v-chip>
                </div>
              </div>
            </div>
            <div class="d-flex flex-wrap ga-2">
              <v-btn
                v-for="a in acciones"
                :key="a.key"
                :color="a.color"
                :variant="a.variant"
                :prepend-icon="a.icon"
                size="small"
                class="text-none"
                @click="ejecutarAccion(a.key)"
              >
                {{ a.label }}
              </v-btn>
            </div>
          </div>

          <p v-if="plan.observaciones" class="text-body-2 text-medium-emphasis mb-4 pre-wrap">
            {{ plan.observaciones }}
          </p>

          <div v-if="resumen" class="cobertura">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="text-body-2 font-weight-medium">Cobertura</span>
              <span class="text-body-2 text-medium-emphasis">
                {{ resumen.cubiertos }} / {{ resumen.slots_totales }} slots
              </span>
            </div>
            <v-progress-linear
              :model-value="coberturaPct"
              :color="coberturaPct >= 100 ? 'success' : 'primary'"
              height="10"
              rounded
              :aria-label="`Cobertura ${coberturaPct}%`"
            />
            <div class="d-flex flex-wrap ga-2 mt-3">
              <v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-check-circle-outline" label>
                {{ resumen.cubiertos }} cubiertas
              </v-chip>
              <v-chip size="small" variant="tonal" color="error" prepend-icon="mdi-alert-circle-outline" label>
                {{ resumen.sin_cubrir }} sin cubrir
              </v-chip>
              <v-chip size="small" variant="tonal" color="secondary" prepend-icon="mdi-calendar-star-outline" label>
                {{ resumen.feriados }} feriados
              </v-chip>
            </div>
          </div>
        </template>
      </v-card>

      <!-- Calendario -->
      <v-card rounded="lg" class="pa-sm-5 pa-3">
        <div class="d-flex flex-wrap align-center justify-space-between ga-2 mb-4">
          <h2 class="text-subtitle-1 font-weight-bold">Calendario</h2>
          <div class="d-flex flex-wrap align-center ga-3 text-body-2 text-medium-emphasis">
            <span class="d-flex align-center ga-1">
              <v-icon icon="mdi-square-rounded" size="12" color="primary" /> Asignada
            </span>
            <span class="d-flex align-center ga-1">
              <v-icon icon="mdi-square-rounded-outline" size="12" color="error" /> Sin cubrir
            </span>
            <span class="d-flex align-center ga-1">
              <v-icon icon="mdi-calendar-star" size="14" color="grey" /> Feriado
            </span>
          </div>
        </div>

        <div v-if="cargando && !calendario" class="py-10">
          <SkeletonList :filas="6" :avatar="false" />
        </div>

        <div v-else-if="calendario" aria-live="polite">
          <!-- Desktop: grilla -->
          <div v-if="!mobile" class="cal-grid">
            <div v-for="d in DIAS_SEMANA" :key="d" class="cal-head">{{ d }}</div>
            <div
              v-for="(celda, i) in celdas"
              :key="i"
              class="cal-cell"
              :class="{ 'cal-cell--empty': !celda, 'cal-cell--feriado': celda && celda.es_feriado }"
            >
              <template v-if="celda">
                <div class="cal-daynum">{{ diaNumero(celda.fecha) }}</div>
                <div v-if="celda.es_feriado" class="cal-feriado">
                  <v-icon icon="mdi-calendar-remove-outline" size="14" />
                  <span class="text-truncate">{{ celda.feriado_descripcion || 'Feriado' }}</span>
                </div>
                <template v-else>
                  <v-chip
                    v-for="f in franjasAplicables(celda)"
                    :key="f.franja_id"
                    :color="f.guardia ? guardiaEstadoColor(f.guardia.estado) : 'error'"
                    :variant="f.guardia ? 'tonal' : 'outlined'"
                    size="x-small"
                    label
                    class="cal-chip"
                    :class="{ 'cal-chip--ro': !esInteractivo(celda, f) }"
                    @click="abrirSlot(celda, f)"
                  >
                    {{ chipTexto(f) }}
                  </v-chip>
                </template>
              </template>
            </div>
          </div>

          <!-- Mobile: lista por día -->
          <div v-else class="cal-mobile-list">
            <div
              v-for="dia in diasConActividad"
              :key="dia.fecha"
              class="cal-mobile-day pa-3 mb-2"
              :class="{ 'cal-mobile-day--feriado': dia.es_feriado }"
            >
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-body-2 font-weight-medium">
                  {{ diaSemanaLabel(dia.dia_semana) }} {{ diaNumero(dia.fecha) }}
                </span>
                <span class="text-caption text-medium-emphasis">{{ mesLabel(plan.mes).slice(0, 3) }}</span>
              </div>
              <div v-if="dia.es_feriado" class="d-flex align-center ga-1 text-body-2 text-medium-emphasis">
                <v-icon icon="mdi-calendar-remove-outline" size="16" />
                {{ dia.feriado_descripcion || 'Feriado' }}
              </div>
              <div v-else class="d-flex flex-column ga-1">
                <v-chip
                  v-for="f in franjasAplicables(dia)"
                  :key="f.franja_id"
                  :color="f.guardia ? guardiaEstadoColor(f.guardia.estado) : 'error'"
                  :variant="f.guardia ? 'tonal' : 'outlined'"
                  size="small"
                  label
                  class="cal-chip align-self-start"
                  :class="{ 'cal-chip--ro': !esInteractivo(dia, f) }"
                  @click="abrirSlot(dia, f)"
                >
                  {{ f.nombre }}: {{ chipTexto(f) }}
                </v-chip>
              </div>
            </div>
          </div>
        </div>
      </v-card>
    </template>

    <!-- Dialog de slot (asignar / gestionar) -->
    <v-dialog v-model="dialogSlot" :max-width="xs ? undefined : 520" :fullscreen="xs" scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ slotFranja?.nombre }} · {{ formatFechaCorta(slotDia?.fecha) }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            v-if="errorSlot"
            role="alert"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ errorSlot }}
          </v-alert>

          <!-- Guardia asignada: ver / gestionar -->
          <template v-if="slotGuardia && !modoCambio">
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="guardiaEstadoColor(slotGuardia.estado)" size="40" rounded="lg">
                  <v-icon icon="mdi-account-tie-outline" size="20" color="white" />
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ slotGuardia.cuadro_nombre }}</div>
                  <div class="text-body-2 text-medium-emphasis">Cuadro asignado</div>
                </div>
              </div>
              <v-chip :color="guardiaEstadoColor(slotGuardia.estado)" variant="tonal" size="small" label class="font-weight-bold">
                {{ guardiaEstadoLabel(slotGuardia.estado) }}
              </v-chip>
            </div>

            <p v-if="!puedeEditarGuardiaActual" class="text-body-2 text-medium-emphasis mt-4">
              Esta guardia no se puede modificar con el estado actual del plan.
            </p>

            <v-btn
              color="primary"
              variant="tonal"
              size="small"
              prepend-icon="mdi-shield-account-outline"
              class="text-none mt-4"
              @click="irAGuardiasCuadro"
            >
              Operar en Guardias de cuadro
            </v-btn>
          </template>

          <!-- Asignar / cambiar cuadro -->
          <template v-else>
            <div v-if="cargandoCandidatos" class="d-flex justify-center py-8">
              <v-progress-circular indeterminate color="primary" />
            </div>
            <template v-else-if="candidatos">
              <div class="text-subtitle-2 font-weight-bold mb-1">Elegibles</div>
              <div v-if="candidatos.elegibles.length" class="mb-4">
                <v-list density="compact" class="py-0">
                  <v-list-item
                    v-for="c in candidatos.elegibles"
                    :key="c.cuadro_id"
                    :title="c.cuadro_nombre"
                    rounded="lg"
                    :disabled="guardandoSlot"
                    @click="seleccionarCandidato(c)"
                  >
                    <template #append>
                      <v-icon icon="mdi-chevron-right" />
                    </template>
                  </v-list-item>
                </v-list>
              </div>
              <p v-else class="text-body-2 text-medium-emphasis mb-4">
                No hay cuadros elegibles para esta franja.
              </p>

              <div class="text-subtitle-2 font-weight-bold mb-1">Descartados</div>
              <div v-if="candidatos.descartados.length">
                <v-list density="compact" class="py-0">
                  <v-list-item
                    v-for="d in candidatos.descartados"
                    :key="d.cuadro_id"
                    :title="d.cuadro_nombre"
                    :subtitle="d.motivo"
                    disabled
                  />
                </v-list>
              </div>
              <p v-else class="text-body-2 text-medium-emphasis">Ninguno.</p>
            </template>
          </template>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-btn v-if="modoCambio" variant="text" class="text-none text-body-1" @click="modoCambio = false">
            Volver
          </v-btn>
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogSlot = false">Cerrar</v-btn>
          <template v-if="slotGuardia && !modoCambio && puedeEditarGuardiaActual">
            <v-btn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-swap-horizontal"
              class="text-none text-body-1"
              @click="activarCambio"
            >
              Cambiar cuadro
            </v-btn>
            <v-btn color="error" variant="tonal" prepend-icon="mdi-trash-can-outline" class="text-none text-body-1" @click="dialogConfirmQuitar = true">
              Quitar
            </v-btn>
          </template>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmar quitar -->
    <v-dialog v-model="dialogConfirmQuitar" max-width="400">
      <v-card rounded="lg" class="pa-sm-5 pa-3">
        <v-card-title class="text-h6 font-weight-bold">Quitar guardia</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          ¿Seguro que desea quitar la guardia de
          <strong class="text-high-emphasis">{{ slotGuardia?.cuadro_nombre }}</strong>
          el {{ formatFechaCorta(slotDia?.fecha) }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogConfirmQuitar = false">Cancelar</v-btn>
          <v-btn color="error" :loading="guardandoSlot" class="text-none text-body-1" @click="quitarGuardia">Quitar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog generar -->
    <v-dialog v-model="dialogGenerar" :max-width="xs ? undefined : 520" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Generar automáticamente</v-card-title>
        <v-card-text class="pa-5">
          <v-alert v-if="errorGenerar" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorGenerar }}
          </v-alert>
          <v-radio-group v-model="genModo" hide-details class="mb-2">
            <v-radio value="completar" label="Completar (conserva lo asignado)" />
            <v-radio value="reemplazar" label="Reemplazar (borra las planificadas y regenera)" />
          </v-radio-group>
          <v-alert v-if="genModo === 'reemplazar'" type="warning" variant="tonal" density="compact" class="mb-3">
            Se eliminarán todas las guardias planificadas de este plan.
          </v-alert>
          <v-checkbox
            v-if="genModo === 'reemplazar'"
            v-model="genConfirmado"
            color="primary"
            density="comfortable"
            hide-details
            label="Confirmo que quiero reemplazar las guardias planificadas"
            class="mb-3"
          />
          <v-text-field
            v-model="genSemilla"
            label="Semilla (opcional)"
            type="number"
            variant="outlined"
            density="comfortable"
            hint="Misma semilla da el mismo resultado"
            persistent-hint
            class="mb-1"
          />
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogGenerar = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :disabled="genModo === 'reemplazar' && !genConfirmado"
            :loading="generando"
            class="text-none text-body-1"
            @click="confirmarGenerar"
          >
            Generar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Resultado de generación -->
    <v-dialog v-model="dialogResultado" :max-width="xs ? undefined : 560" :fullscreen="xs" scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Resumen de generación</v-card-title>
        <v-card-text v-if="resultadoGeneracion" class="pa-5">
          <div class="d-flex flex-wrap ga-2 mb-4">
            <v-chip size="small" variant="tonal" color="success" label>
              {{ resultadoGeneracion.cubiertos }} / {{ resultadoGeneracion.slots_totales }} cubiertos
            </v-chip>
            <v-chip size="small" variant="tonal" color="primary" label>
              {{ resultadoGeneracion.creadas }} creadas
            </v-chip>
            <v-chip size="small" variant="tonal" color="error" label>
              {{ resultadoGeneracion.sin_cubrir.length }} sin cubrir
            </v-chip>
          </div>

          <template v-if="resultadoGeneracion.advertencias.length">
            <div class="text-subtitle-2 font-weight-bold mb-1">Advertencias</div>
            <v-alert
              v-for="(a, i) in resultadoGeneracion.advertencias"
              :key="i"
              type="warning"
              variant="tonal"
              density="compact"
              class="mb-2"
            >
              {{ a }}
            </v-alert>
          </template>

          <div class="text-subtitle-2 font-weight-bold mb-1">Cuadros sin asignar</div>
          <div v-if="resultadoGeneracion.cuadros_sin_asignar.length" class="mb-4">
            <v-list density="compact" class="py-0">
              <v-list-item
                v-for="c in resultadoGeneracion.cuadros_sin_asignar"
                :key="c.cuadro_id"
                :title="c.nombre"
                :subtitle="c.motivo"
              />
            </v-list>
          </div>
          <p v-else class="text-body-2 text-medium-emphasis mb-4">Todos los cuadros recibieron al menos una guardia.</p>

          <div class="text-subtitle-2 font-weight-bold mb-1">Franjas sin cubrir</div>
          <div v-if="resultadoGeneracion.sin_cubrir.length" class="d-flex flex-wrap ga-2">
            <v-chip v-for="s in resultadoGeneracion.sin_cubrir" :key="`${s.fecha}-${s.franja_id}`" size="small" variant="outlined" color="error" label>
              {{ formatFechaCorta(s.fecha) }} · {{ s.franja_nombre }}
            </v-chip>
          </div>
          <p v-else class="text-body-2 text-medium-emphasis">Todas las franjas quedaron cubiertas.</p>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn color="primary" class="text-none text-body-1" @click="dialogResultado = false">Entendido</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog rechazar -->
    <v-dialog v-model="dialogRechazar" :max-width="xs ? undefined : 440" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Rechazar plan</v-card-title>
        <v-card-text class="pa-5">
          <v-alert v-if="errorRechazar" role="alert" type="error" variant="tonal" density="compact" class="mb-4">
            {{ errorRechazar }}
          </v-alert>
          <v-textarea
            v-model="motivoRechazo"
            label="Motivo (opcional)"
            variant="outlined"
            density="comfortable"
            rows="3"
            auto-grow
          />
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogRechazar = false">Cancelar</v-btn>
          <v-btn color="error" :loading="procesando" class="text-none text-body-1" @click="confirmarRechazar">Rechazar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmar eliminar -->
    <v-dialog v-model="dialogConfirmEliminar" max-width="400">
      <v-card rounded="lg" class="pa-sm-5 pa-3">
        <v-card-title class="text-h6 font-weight-bold">Eliminar plan</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          ¿Seguro que desea eliminar el plan de {{ mesLabel(plan?.mes) }} {{ plan?.anio }}? Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogConfirmEliminar = false">Cancelar</v-btn>
          <v-btn color="error" :loading="procesando" class="text-none text-body-1" @click="confirmarEliminar">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { planCuadroApi } from '../api/planCuadro'
import { guardiaCuadroApi } from '../api/guardiaCuadro'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { mobile, xs } = useDisplay()

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const DIAS_SEMANA_LARGO = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

const planEstados = {
  borrador: { color: 'grey', label: 'Borrador' },
  pendiente_aprobacion: { color: 'warning', label: 'Pendiente de aprobación' },
  aprobado: { color: 'success', label: 'Aprobado' },
  rechazado: { color: 'error', label: 'Rechazado' },
}
const guardiaEstados = {
  planificada: { color: 'info', label: 'Planificada' },
  activa: { color: 'success', label: 'Activa' },
  finalizada: { color: 'grey', label: 'Finalizada' },
  incumplida: { color: 'error', label: 'Incumplida' },
  cancelada: { color: 'error', label: 'Cancelada' },
}

const planId = Number(route.params.id)

const plan = ref(null)
const calendario = ref(null)
const cargando = ref(true)
const noEncontrado = ref(false)

const dialogSlot = ref(false)
const slotDia = ref(null)
const slotFranja = ref(null)
const modoCambio = ref(false)
const candidatos = ref(null)
const cargandoCandidatos = ref(false)
const guardandoSlot = ref(false)
const errorSlot = ref(null)

const dialogConfirmQuitar = ref(false)

const dialogGenerar = ref(false)
const genModo = ref('completar')
const genSemilla = ref('')
const genConfirmado = ref(false)
const generando = ref(false)
const errorGenerar = ref(null)
const dialogResultado = ref(false)
const resultadoGeneracion = ref(null)

const dialogRechazar = ref(false)
const motivoRechazo = ref('')
const errorRechazar = ref(null)

const dialogConfirmEliminar = ref(false)
const procesando = ref(false)

function mesLabel(mes) {
  return MESES[(mes || 1) - 1] || mes
}

function planEstadoColor(estado) {
  return planEstados[estado]?.color || 'grey'
}

function planEstadoLabel(estado) {
  return planEstados[estado]?.label || estado
}

function guardiaEstadoColor(estado) {
  return guardiaEstados[estado]?.color || 'grey'
}

function guardiaEstadoLabel(estado) {
  return guardiaEstados[estado]?.label || estado
}

function diaSemanaLabel(dia) {
  return DIAS_SEMANA_LARGO[dia] || ''
}

function diaNumero(fecha) {
  if (!fecha) return ''
  return Number(fecha.split('-')[2])
}

function formatFechaCorta(f) {
  if (!f) return ''
  const [y, m, d] = f.split('-')
  return `${d}/${m}/${y}`
}

function hoyYMD() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${dd}`
}

const resumen = computed(() => calendario.value?.resumen || null)
const coberturaPct = computed(() => {
  if (!resumen.value || !resumen.value.slots_totales) return 0
  return Math.round((resumen.value.cubiertos / resumen.value.slots_totales) * 100)
})

const celdas = computed(() => {
  const dias = calendario.value?.dias || []
  if (!dias.length) return []
  const leading = dias[0].dia_semana
  return [...Array(leading).fill(null), ...dias]
})

const diasConActividad = computed(() => calendario.value?.dias || [])

const slotGuardia = computed(() => slotFranja.value?.guardia || null)

const puedeAsignar = computed(
  () => ['borrador', 'pendiente_aprobacion'].includes(plan.value?.estado),
)

const puedeEditarGuardiaActual = computed(() => {
  if (!slotGuardia.value || !slotDia.value) return false
  return puedeEditarGuardia(slotGuardia.value, slotDia.value.fecha)
})

const acciones = computed(() => {
  const e = plan.value?.estado
  if (e === 'borrador') {
    return [
      { key: 'generar', label: 'Generar automáticamente', icon: 'mdi-robot-outline', color: 'primary', variant: 'flat' },
      { key: 'enviar', label: 'Enviar a aprobación', icon: 'mdi-send-outline', color: 'primary', variant: 'tonal' },
      { key: 'eliminar', label: 'Eliminar', icon: 'mdi-trash-can-outline', color: 'error', variant: 'text' },
    ]
  }
  if (e === 'pendiente_aprobacion') {
    return [
      { key: 'aprobar', label: 'Aprobar', icon: 'mdi-check-bold', color: 'success', variant: 'flat' },
      { key: 'rechazar', label: 'Rechazar', icon: 'mdi-close-thick', color: 'error', variant: 'tonal' },
    ]
  }
  if (e === 'rechazado') {
    return [
      { key: 'reabrir', label: 'Reabrir', icon: 'mdi-backup-restore', color: 'primary', variant: 'tonal' },
    ]
  }
  return []
})

function franjasAplicables(dia) {
  return (dia.franjas || []).filter((f) => f.aplica)
}

function chipTexto(f) {
  if (!f.guardia) return 'Sin cubrir'
  if (f.guardia.estado === 'cancelada') return 'Cancelada'
  return f.guardia.cuadro_nombre
}

function puedeEditarGuardia(guardia, fecha) {
  if (!plan.value) return false
  if (['borrador', 'pendiente_aprobacion'].includes(plan.value.estado)) return true
  if (plan.value.estado !== 'aprobado') return false
  return guardia.estado === 'planificada' && fecha > hoyYMD()
}

function esInteractivo(dia, franja) {
  if (franja.guardia) return puedeEditarGuardia(franja.guardia, dia.fecha)
  return puedeAsignar.value
}

function volver() {
  router.push('/planes-cuadro')
}

async function cargarPlan() {
  try {
    const res = await planCuadroApi.obtener(planId)
    plan.value = res.data
    noEncontrado.value = false
  } catch (e) {
    if (e?.response?.status === 404) {
      noEncontrado.value = true
    } else {
      toast.error(normalizeApiError(e, 'Error al cargar el plan'))
    }
  }
}

async function cargarCalendario() {
  try {
    const res = await planCuadroApi.calendario(planId)
    calendario.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar el calendario'))
  }
}

async function recargar() {
  await Promise.all([cargarPlan(), cargarCalendario()])
}

function abrirSlot(dia, franja) {
  if (dia.es_feriado || !franja.aplica) return
  if (!franja.guardia && !puedeAsignar.value) return
  slotDia.value = dia
  slotFranja.value = franja
  modoCambio.value = false
  candidatos.value = null
  errorSlot.value = null
  dialogSlot.value = true
  if (!franja.guardia) cargarCandidatos()
}

function irAGuardiasCuadro() {
  dialogSlot.value = false
  router.push({ path: '/operativo-cuadro', query: { plan_id: planId } })
}

async function cargarCandidatos() {
  cargandoCandidatos.value = true
  candidatos.value = null
  try {
    const res = await planCuadroApi.candidatos(planId, {
      fecha: slotDia.value.fecha,
      franja_id: slotFranja.value.franja_id,
    })
    candidatos.value = res.data
  } catch (e) {
    errorSlot.value = normalizeApiError(e, 'Error al cargar los cuadros elegibles')
  } finally {
    cargandoCandidatos.value = false
  }
}

function activarCambio() {
  modoCambio.value = true
  candidatos.value = null
  errorSlot.value = null
  cargarCandidatos()
}

async function seleccionarCandidato(c) {
  guardandoSlot.value = true
  errorSlot.value = null
  try {
    if (slotFranja.value.guardia) {
      await guardiaCuadroApi.actualizar(slotFranja.value.guardia.id, { cuadro_id: c.cuadro_id })
      toast.success('Cuadro cambiado correctamente')
    } else {
      await guardiaCuadroApi.crear(planId, {
        cuadro_id: c.cuadro_id,
        franja_id: slotFranja.value.franja_id,
        fecha: slotDia.value.fecha,
      })
      toast.success('Guardia asignada correctamente')
    }
    dialogSlot.value = false
    await recargar()
  } catch (e) {
    errorSlot.value = normalizeApiError(e, 'No se pudo asignar el cuadro')
  } finally {
    guardandoSlot.value = false
  }
}

async function quitarGuardia() {
  guardandoSlot.value = true
  try {
    await guardiaCuadroApi.eliminar(slotFranja.value.guardia.id)
    toast.success('Guardia quitada')
    dialogConfirmQuitar.value = false
    dialogSlot.value = false
    await recargar()
  } catch (e) {
    dialogConfirmQuitar.value = false
    errorSlot.value = normalizeApiError(e, 'No se pudo quitar la guardia')
  } finally {
    guardandoSlot.value = false
  }
}

function abrirGenerar() {
  genModo.value = 'completar'
  genSemilla.value = ''
  genConfirmado.value = false
  errorGenerar.value = null
  dialogGenerar.value = true
}

async function confirmarGenerar() {
  generando.value = true
  errorGenerar.value = null
  try {
    const datos = { modo: genModo.value }
    if (String(genSemilla.value).trim() !== '') datos.semilla = Number(genSemilla.value)
    const res = await planCuadroApi.generar(planId, datos)
    resultadoGeneracion.value = res.data
    dialogGenerar.value = false
    dialogResultado.value = true
    await recargar()
  } catch (e) {
    errorGenerar.value = normalizeApiError(e, 'No se pudo generar el plan')
  } finally {
    generando.value = false
  }
}

async function ejecutarAccion(key) {
  if (key === 'generar') return abrirGenerar()
  if (key === 'rechazar') {
    motivoRechazo.value = ''
    errorRechazar.value = null
    dialogRechazar.value = true
    return
  }
  if (key === 'eliminar') {
    dialogConfirmEliminar.value = true
    return
  }
  procesando.value = true
  try {
    if (key === 'enviar') {
      await planCuadroApi.enviar(planId)
      toast.success('Plan enviado a aprobación')
    } else if (key === 'aprobar') {
      await planCuadroApi.aprobar(planId)
      toast.success('Plan aprobado')
    } else if (key === 'reabrir') {
      await planCuadroApi.reabrir(planId)
      toast.success('Plan reabierto')
    }
    await recargar()
  } catch (e) {
    toast.error(normalizeApiError(e, 'No se pudo completar la acción'))
  } finally {
    procesando.value = false
  }
}

async function confirmarRechazar() {
  procesando.value = true
  errorRechazar.value = null
  try {
    const datos = {}
    if (motivoRechazo.value.trim()) datos.motivo = motivoRechazo.value.trim()
    await planCuadroApi.rechazar(planId, datos)
    toast.success('Plan rechazado')
    dialogRechazar.value = false
    await recargar()
  } catch (e) {
    errorRechazar.value = normalizeApiError(e, 'No se pudo rechazar el plan')
  } finally {
    procesando.value = false
  }
}

async function confirmarEliminar() {
  procesando.value = true
  try {
    await planCuadroApi.eliminar(planId)
    toast.success('Plan eliminado')
    dialogConfirmEliminar.value = false
    router.push('/planes-cuadro')
  } catch (e) {
    dialogConfirmEliminar.value = false
    toast.error(normalizeApiError(e, 'No se pudo eliminar el plan'))
  } finally {
    procesando.value = false
  }
}

onMounted(async () => {
  cargando.value = true
  await Promise.all([cargarPlan(), cargarCalendario()])
  cargando.value = false
})
</script>

<style scoped>
.plan-detalle-page {
  width: 100%;
}

.pre-wrap {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
}

.cal-head {
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 0;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.6;
}

.cal-cell {
  min-height: 100px;
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 10px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgb(var(--v-theme-surface));
}

.cal-cell--empty {
  border: none;
  background: transparent;
}

.cal-cell--feriado {
  background: repeating-linear-gradient(45deg, #f4f4f5, #f4f4f5 7px, #e9e9eb 7px, #e9e9eb 14px);
}

.cal-daynum {
  font-size: 12px;
  font-weight: 700;
}

.cal-feriado {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.6;
}

.cal-chip {
  justify-content: flex-start;
  min-width: 0;
}

.cal-chip--ro {
  cursor: default;
}

.cal-mobile-list {
  display: flex;
  flex-direction: column;
}

.cal-mobile-day {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.cal-mobile-day--feriado {
  background: repeating-linear-gradient(45deg, #f4f4f5, #f4f4f5 7px, #e9e9eb 7px, #e9e9eb 14px);
}
</style>
