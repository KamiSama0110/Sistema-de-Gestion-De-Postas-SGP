<template>
  <div class="reportes-cuadros-page mx-auto">
    <v-alert
      v-if="error"
      role="alert"
      type="error"
      variant="tonal"
      density="compact"
      class="mb-4"
      closable
      @click:close="error = ''"
    >
      {{ error }}
    </v-alert>

    <v-card rounded="lg" class="pa-sm-5 pa-3 mb-4">
      <v-tabs
        v-model="tab"
        color="primary"
        show-arrows
        density="comfortable"
        slider-transition="grow"
        :slider-transition-duration="300"
        class="mb-4"
      >
        <v-tab v-for="r in reportes" :key="r.id" :value="r.id" :prepend-icon="r.icon">
          {{ r.label }}
        </v-tab>
      </v-tabs>

      <Transition name="fade-slide" mode="out-in">
        <div
          :key="reporteActivo.selector"
          :class="mobile ? 'd-flex flex-column ga-3' : 'd-flex flex-wrap align-center ga-3'"
        >
          <template v-if="reporteActivo.selector === 'mes'">
            <v-select
              v-model="anio"
              :items="anios"
              label="Año"
              hide-details
              density="comfortable"
              :style="mobile ? undefined : 'max-width: 140px'"
            />
            <v-select
              v-model="mes"
              :items="meses"
              item-title="label"
              item-value="value"
              label="Mes"
              hide-details
              density="comfortable"
              :style="mobile ? undefined : 'max-width: 220px'"
            />
          </template>

          <template v-else>
            <v-menu v-model="menuDesde" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  v-bind="menuProps"
                  :model-value="desde"
                  label="Desde"
                  readonly
                  append-inner-icon="mdi-calendar"
                  hide-details
                  density="comfortable"
                  :style="mobile ? undefined : 'max-width: 180px'"
                />
              </template>
              <v-date-picker v-model="desdePicker" :max="hasta || undefined" color="primary" />
            </v-menu>

            <v-menu v-model="menuHasta" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  v-bind="menuProps"
                  :model-value="hasta"
                  label="Hasta"
                  readonly
                  append-inner-icon="mdi-calendar"
                  hide-details
                  density="comfortable"
                  :style="mobile ? undefined : 'max-width: 180px'"
                />
              </template>
              <v-date-picker v-model="hastaPicker" :min="desde || undefined" color="primary" />
            </v-menu>
          </template>

          <template v-if="reporteActivo.id === 'incidencias'">
            <v-select
              v-model="severidadFiltro"
              :items="SEVERIDADES"
              item-title="title"
              item-value="value"
              label="Severidad"
              clearable
              hide-details
              density="comfortable"
              :style="mobile ? undefined : 'max-width: 170px'"
            />
            <v-select
              v-model="tipoFiltro"
              :items="TIPOS_INCIDENCIA"
              item-title="title"
              item-value="value"
              label="Tipo"
              clearable
              hide-details
              density="comfortable"
              :style="mobile ? undefined : 'max-width: 200px'"
            />
          </template>

          <v-spacer v-if="!mobile" />

          <v-btn
            v-if="datos && !estaVacio"
            variant="tonal"
            color="error"
            prepend-icon="mdi-file-pdf-box"
            :class="mobile ? 'w-100' : ''"
            @click="exportarPDF"
          >
            PDF
          </v-btn>
        </div>
      </Transition>
    </v-card>

    <div class="resultados-contenedor" aria-live="polite">
      <Transition name="fade-slide" mode="out-in">
        <div :key="fase">
      <SkeletonList v-if="fase === 'cargando'" :filas="8" :avatar="false" />

      <v-alert v-else-if="fase === 'sinPlan'" type="info" variant="tonal" class="mb-4">
        <v-alert-title>{{ mensajeSinPlan }}</v-alert-title>
        Genere el plan de guardias y apruébelo para poder consultar este reporte.
      </v-alert>

      <v-card v-else-if="fase === 'listo'" rounded="lg" class="pa-sm-5 pa-3">
        <v-progress-linear v-if="cargando" indeterminate color="primary" class="mb-3" height="3" />
        <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-4">
          <div class="text-subtitle-2 font-weight-bold">{{ reporteActivo.label }}</div>
          <v-chip size="small" variant="tonal" color="primary" label>
            {{ periodoLabel }}
          </v-chip>
        </div>

        <div v-if="!estaVacio" class="d-flex flex-wrap ga-2 mb-5">
            <v-chip
              v-for="c in resumenChips"
              :key="c.label"
              size="small"
              variant="tonal"
              :color="c.color"
              label
            >
              {{ c.label }}: {{ c.value }}
            </v-chip>
          </div>

          <v-row v-if="tab === 'cumplimiento'" dense class="mb-4">
            <v-col cols="12" md="6">
              <div class="text-body-2 font-weight-medium mb-2">Guardias del plan</div>
              <GraficoBarras :items="barrasEstados" />
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-body-2 font-weight-medium mb-2">Porcentajes</div>
              <GraficoBarras :items="barrasPorcentajes" />
            </v-col>
          </v-row>

          <v-row v-if="tab === 'incidencias'" dense class="mb-4">
            <v-col cols="12" md="6">
              <div class="text-body-2 font-weight-medium mb-2">Por severidad</div>
              <GraficoBarras :items="barrasSeveridad" />
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-body-2 font-weight-medium mb-2">Por tipo</div>
              <GraficoBarras :items="barrasTipo" />
            </v-col>
          </v-row>

          <div v-if="tab === 'guardias_por_cuadro'" class="mb-4">
            <div class="text-body-2 font-weight-medium mb-2">Guardias por cuadro</div>
            <GraficoBarras :items="barrasCuadros" />
          </div>

          <template v-if="tab === 'dias_sin_cubrir'">
            <div class="d-flex flex-wrap align-center ga-2 mb-4">
              <span class="text-body-2 text-medium-emphasis">Feriados del mes:</span>
              <v-chip
                v-for="f in datos.feriados"
                :key="f.fecha"
                size="small"
                variant="tonal"
                color="info"
                label
              >
                {{ f.fecha }} — {{ f.descripcion }}
              </v-chip>
              <span v-if="!datos.feriados?.length" class="text-body-2 text-medium-emphasis">
                Ninguno
              </span>
            </div>
          </template>

          <div class="tabla-contenedor">
            <ReporteResultados :columnas="columnas" :filas="filas" />
          </div>

          <div v-if="tab === 'incidencias' && totalPaginas > 1" class="d-flex align-center justify-center ga-2 mt-4">
            <v-btn
              icon
              size="small"
              variant="text"
              :disabled="pagina === 1 || cargando"
              aria-label="Página anterior"
              @click="cambiarPagina(-1)"
            >
              <v-icon icon="mdi-chevron-left" />
            </v-btn>
            <span class="text-body-2 text-medium-emphasis">{{ pagina }}/{{ totalPaginas }}</span>
            <v-btn
              icon
              size="small"
              variant="text"
              :disabled="pagina >= totalPaginas || cargando"
              aria-label="Página siguiente"
              @click="cambiarPagina(1)"
            >
              <v-icon icon="mdi-chevron-right" />
            </v-btn>
          </div>
      </v-card>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { jsPDF } from 'jspdf'
import { applyPlugin } from 'jspdf-autotable'
import { reporteCuadroApi } from '../api/reporteCuadro'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { TIPOS_INCIDENCIA, SEVERIDADES, tipoLabel, severidadLabel, severidadColor } from '../utils/incidencia'
import { formatFechaHora } from '../utils/formatters'
import SkeletonList from '../components/SkeletonList.vue'
import GraficoBarras from '../components/GraficoBarras.vue'
import ReporteResultados from '../components/ReporteResultados.vue'

applyPlugin(jsPDF)

const { mobile } = useDisplay()
const toast = useToast()

const reportes = [
  { id: 'cumplimiento', label: 'Cumplimiento mensual', icon: 'mdi-chart-donut', selector: 'mes' },
  { id: 'guardias_por_cuadro', label: 'Guardias por cuadro', icon: 'mdi-account-group', selector: 'rango' },
  { id: 'incidencias', label: 'Incidencias', icon: 'mdi-alert-circle-outline', selector: 'rango' },
  { id: 'dias_sin_cubrir', label: 'Días sin cubrir', icon: 'mdi-calendar-remove-outline', selector: 'mes' },
  { id: 'incumplimientos', label: 'Incumplimientos', icon: 'mdi-close-octagon-outline', selector: 'rango' },
]

const meses = [
  { value: 1, label: 'Enero' },
  { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' },
  { value: 4, label: 'Abril' },
  { value: 5, label: 'Mayo' },
  { value: 6, label: 'Junio' },
  { value: 7, label: 'Julio' },
  { value: 8, label: 'Agosto' },
  { value: 9, label: 'Septiembre' },
  { value: 10, label: 'Octubre' },
  { value: 11, label: 'Noviembre' },
  { value: 12, label: 'Diciembre' },
]

const anioActual = new Date().getFullYear()
const anios = Array.from({ length: 11 }, (_, i) => anioActual - 5 + i)

const PLAN_ESTADOS = {
  borrador: { label: 'Borrador', color: 'grey' },
  pendiente_aprobacion: { label: 'Pendiente de aprobación', color: 'warning' },
  aprobado: { label: 'Aprobado', color: 'success' },
  rechazado: { label: 'Rechazado', color: 'error' },
}

const tab = ref('cumplimiento')
const anio = ref(anioActual)
const mes = ref(new Date().getMonth() + 1)
const desde = ref(primerDiaMes())
const hasta = ref(hoyYMD())
const menuDesde = ref(false)
const menuHasta = ref(false)
const severidadFiltro = ref(null)
const tipoFiltro = ref(null)
const pagina = ref(1)
const tamanoPagina = 20
const cargando = ref(false)
const error = ref('')
const sinPlanAprobado = ref(false)
const mensajeSinPlan = ref('No hay un plan aprobado para ese mes')
const datos = ref(null)

const reporteActivo = computed(() => reportes.find((r) => r.id === tab.value) || reportes[0])

const desdePicker = computed({
  get() {
    return ymdToDate(desde.value)
  },
  set(val) {
    if (!val) return
    desde.value = dateToYMD(val)
    menuDesde.value = false
  },
})

const hastaPicker = computed({
  get() {
    return ymdToDate(hasta.value)
  },
  set(val) {
    if (!val) return
    hasta.value = dateToYMD(val)
    menuHasta.value = false
  },
})

function dateToYMD(d) {
  if (!d) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function ymdToDate(s) {
  if (!s) return null
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function hoyYMD() {
  return dateToYMD(new Date())
}

function primerDiaMes() {
  const hoy = new Date()
  return dateToYMD(new Date(hoy.getFullYear(), hoy.getMonth(), 1))
}

function pct(valor) {
  return valor != null ? `${Number(valor).toFixed(1)}%` : '—'
}

function siNo(valor) {
  return valor ? 'Sí' : 'No'
}

function planEstadoLabel(valor) {
  return PLAN_ESTADOS[valor]?.label || valor
}

function planEstadoColor(valor) {
  return PLAN_ESTADOS[valor]?.color || 'grey'
}

const periodoLabel = computed(() => {
  if (reporteActivo.value.selector === 'mes') {
    const nombre = meses.find((m) => m.value === mes.value)?.label || ''
    return `${nombre} ${anio.value}`
  }
  return `${desde.value} — ${hasta.value}`
})

const estaVacio = computed(() => {
  const d = datos.value
  if (!d) return true
  if (tab.value === 'cumplimiento') return !d.plan_id
  if (tab.value === 'dias_sin_cubrir') return !d.dias?.length
  return !d.items?.length
})

const fase = computed(() => {
  if (!datos.value) {
    if (cargando.value) return 'cargando'
    if (sinPlanAprobado.value) return 'sinPlan'
    return 'inicial'
  }
  return 'listo'
})

const totalPaginas = computed(() => Math.max(1, Math.ceil((datos.value?.total || 0) / tamanoPagina)))

const resumenChips = computed(() => {
  const d = datos.value
  if (!d) return []
  if (tab.value === 'cumplimiento') {
    return [
      { label: 'Slots', value: d.slots_totales, color: 'primary' },
      { label: 'Cubiertos', value: d.cubiertos, color: 'success' },
      { label: 'Sin cubrir', value: d.sin_cubrir, color: 'error' },
      { label: 'Cobertura', value: pct(d.porcentaje_cobertura), color: d.porcentaje_cobertura >= 80 ? 'success' : 'warning' },
      {
        label: 'Cumplimiento',
        value: pct(d.porcentaje_cumplimiento),
        color: d.porcentaje_cumplimiento >= 80 ? 'success' : 'warning',
      },
    ]
  }
  if (tab.value === 'guardias_por_cuadro') {
    const total = (d.items || []).reduce((s, i) => s + i.total, 0)
    return [
      { label: 'Cuadros', value: d.items?.length || 0, color: 'primary' },
      { label: 'Guardias', value: total, color: 'primary' },
    ]
  }
  if (tab.value === 'incidencias') {
    return [
      { label: 'Total', value: d.total, color: 'warning' },
      { label: 'Requieren seguimiento', value: d.requieren_seguimiento, color: 'error' },
    ]
  }
  if (tab.value === 'dias_sin_cubrir') {
    return [
      { label: 'Slots', value: d.slots_totales, color: 'primary' },
      { label: 'Sin cubrir', value: d.sin_cubrir, color: 'error' },
      { label: 'Feriados', value: d.feriados?.length || 0, color: 'info' },
      { label: 'Plan', value: planEstadoLabel(d.estado_plan), color: planEstadoColor(d.estado_plan) },
    ]
  }
  return [
    { label: 'Total', value: d.total, color: 'error' },
    { label: 'Justificadas', value: d.justificadas, color: 'success' },
    { label: 'Injustificadas', value: d.injustificadas, color: 'error' },
  ]
})

const barrasEstados = computed(() => {
  const d = datos.value
  if (!d) return []
  return [
    { label: 'Planificadas', value: d.planificadas, color: 'info' },
    { label: 'Activas', value: d.activas, color: 'success' },
    { label: 'Finalizadas', value: d.finalizadas, color: 'primary' },
    { label: 'Incumplidas just.', value: d.incumplidas_justificadas, color: 'warning' },
    { label: 'Incumplidas inj.', value: d.incumplidas_injustificadas, color: 'error' },
    { label: 'Canceladas', value: d.canceladas, color: 'grey' },
  ]
})

const barrasPorcentajes = computed(() => {
  const d = datos.value
  if (!d) return []
  const cobertura = Number(d.porcentaje_cobertura ?? 0)
  const cumplimiento = Number(d.porcentaje_cumplimiento ?? 0)
  return [
    { label: 'Cobertura', value: cobertura, porcentaje: cobertura, color: 'primary' },
    { label: 'Cumplimiento', value: cumplimiento, porcentaje: cumplimiento, color: 'success' },
  ]
})

const barrasSeveridad = computed(() => {
  const d = datos.value
  if (!d) return []
  return SEVERIDADES.map((s) => ({
    label: s.title,
    value: d.por_severidad?.[s.value] || 0,
    color: s.color,
  }))
})

const barrasTipo = computed(() => {
  const d = datos.value
  if (!d) return []
  return TIPOS_INCIDENCIA.map((t) => ({
    label: t.title,
    value: d.por_tipo?.[t.value] || 0,
    color: 'primary',
  }))
})

const barrasCuadros = computed(() => {
  const d = datos.value
  if (!d) return []
  return (d.items || []).map((i) => ({
    label: i.cuadro_nombre,
    value: i.total,
    color: 'primary',
  }))
})

const feriadosMap = computed(() => {
  const mapa = new Map()
  ;(datos.value?.feriados || []).forEach((f) => mapa.set(f.fecha, f.descripcion))
  return mapa
})

function marcaDia(row) {
  const partes = []
  if (row.cancelada) partes.push('Cancelada')
  const feriado = feriadosMap.value.get(row.fecha)
  if (feriado) partes.push(`Feriado: ${feriado}`)
  if (!partes.length) partes.push('Sin cubrir')
  return partes.join(' · ')
}

const columnas = computed(() => {
  const cols = {
    cumplimiento: [
      { key: 'concepto', label: 'Concepto', primary: true },
      { key: 'valor', label: 'Valor', align: 'right' },
    ],
    guardias_por_cuadro: [
      { key: 'cuadro_nombre', label: 'Cuadro', primary: true },
      { key: 'total', label: 'Total', align: 'right' },
      { key: 'planificadas', label: 'Planificadas', align: 'right' },
      { key: 'activas', label: 'Activas', align: 'right' },
      { key: 'finalizadas', label: 'Finalizadas', align: 'right' },
      { key: 'incumplidas', label: 'Incumplidas', align: 'right' },
      { key: 'canceladas', label: 'Canceladas', align: 'right' },
      { key: 'ultima_guardia', label: 'Última guardia' },
    ],
    incidencias: [
      { key: 'cuadro_nombre', label: 'Cuadro', primary: true },
      { key: 'fecha_hora', label: 'Fecha' },
      { key: 'tipo', label: 'Tipo', fn: tipoLabel },
      { key: 'severidad', label: 'Severidad', fn: severidadLabel, colorFn: severidadColor },
      { key: 'descripcion', label: 'Descripción', wrap: true },
    ],
    dias_sin_cubrir: [
      { key: 'fecha', label: 'Fecha', primary: true },
      { key: 'franja_nombre', label: 'Franja' },
      { key: 'marca', label: 'Detalle' },
    ],
    incumplimientos: [
      { key: 'cuadro_nombre', label: 'Cuadro', primary: true },
      { key: 'fecha', label: 'Fecha' },
      { key: 'franja_nombre', label: 'Franja' },
      { key: 'motivo', label: 'Motivo', wrap: true },
      { key: 'justificada', label: 'Justificada', fn: siNo },
    ],
  }
  return cols[tab.value] || []
})

const filasCumplimiento = computed(() => {
  const d = datos.value
  if (!d) return []
  return [
    { concepto: 'Slots del plan', valor: d.slots_totales },
    { concepto: 'Cubiertos', valor: d.cubiertos },
    { concepto: 'Sin cubrir', valor: d.sin_cubrir },
    { concepto: 'Planificadas', valor: d.planificadas },
    { concepto: 'Activas', valor: d.activas },
    { concepto: 'Finalizadas', valor: d.finalizadas },
    { concepto: 'Incumplidas', valor: d.incumplidas },
    { concepto: 'Incumplidas justificadas', valor: d.incumplidas_justificadas },
    { concepto: 'Incumplidas injustificadas', valor: d.incumplidas_injustificadas },
    { concepto: 'Canceladas', valor: d.canceladas },
    { concepto: 'Porcentaje de cobertura', valor: pct(d.porcentaje_cobertura) },
    { concepto: 'Porcentaje de cumplimiento', valor: pct(d.porcentaje_cumplimiento) },
  ]
})

const filas = computed(() => {
  const d = datos.value
  if (!d) return []
  if (tab.value === 'cumplimiento') return filasCumplimiento.value
  if (tab.value === 'guardias_por_cuadro') {
    return (d.items || []).map((i) => ({ ...i, ultima_guardia: i.ultima_guardia || '—' }))
  }
  if (tab.value === 'incidencias') {
    return (d.items || []).map((i) => ({ ...i, fecha_hora: formatFechaHora(i.fecha_hora) }))
  }
  if (tab.value === 'dias_sin_cubrir') {
    return (d.dias || []).map((row) => ({ ...row, marca: marcaDia(row) }))
  }
  return (d.items || []).map((i) => ({ ...i, justificada: siNo(i.justificada), motivo: i.motivo || '—' }))
})

function paramsRango() {
  return {
    fecha_desde: desde.value,
    fecha_hasta: hasta.value,
  }
}

function validar() {
  error.value = ''
  if (reporteActivo.value.selector === 'mes') {
    if (!anio.value || !mes.value) {
      error.value = 'Seleccione el año y el mes'
      return false
    }
    return true
  }
  if (!desde.value || !hasta.value) {
    error.value = 'Seleccione las fechas desde y hasta'
    return false
  }
  const d = ymdToDate(desde.value)
  const h = ymdToDate(hasta.value)
  if (d > h) {
    error.value = 'La fecha desde no puede ser posterior a la fecha hasta'
    return false
  }
  if ((h - d) / 86400000 > 366) {
    error.value = 'El rango no puede superar los 366 días'
    return false
  }
  return true
}

async function generar() {
  if (!validar()) {
    datos.value = null
    sinPlanAprobado.value = false
    return
  }
  cargando.value = true
  error.value = ''
  sinPlanAprobado.value = false
  try {
    let res
    if (tab.value === 'cumplimiento') {
      res = await reporteCuadroApi.cumplimiento({ anio: anio.value, mes: mes.value })
    } else if (tab.value === 'dias_sin_cubrir') {
      res = await reporteCuadroApi.diasSinCubrir({ anio: anio.value, mes: mes.value })
    } else if (tab.value === 'guardias_por_cuadro') {
      res = await reporteCuadroApi.guardiasPorCuadro(paramsRango())
    } else if (tab.value === 'incidencias') {
      res = await reporteCuadroApi.incidencias({
        ...paramsRango(),
        page: pagina.value,
        size: tamanoPagina,
        ...(severidadFiltro.value ? { severidad: severidadFiltro.value } : {}),
        ...(tipoFiltro.value ? { tipo: tipoFiltro.value } : {}),
      })
    } else {
      res = await reporteCuadroApi.incumplimientos(paramsRango())
    }
    datos.value = res.data
  } catch (e) {
    datos.value = null
    if (e.response?.status === 404) {
      sinPlanAprobado.value = true
      mensajeSinPlan.value =
        e.response?.data?.detail || 'No hay un plan aprobado para ese mes'
    } else {
      error.value = normalizeApiError(e, 'Error al generar el reporte')
    }
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  generar()
}

function regenerar() {
  datos.value = null
  error.value = ''
  sinPlanAprobado.value = false
  pagina.value = 1
  generar()
}

watch(tab, regenerar)

watch([anio, mes], () => {
  if (reporteActivo.value.selector === 'mes') regenerar()
})

watch([desde, hasta], () => {
  if (reporteActivo.value.selector === 'rango') regenerar()
})

watch([severidadFiltro, tipoFiltro], () => {
  if (tab.value !== 'incidencias') return
  pagina.value = 1
  generar()
})

onMounted(() => {
  generar()
})

function exportarPDF() {
  if (!datos.value) return
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  const pageH = doc.internal.pageSize.getHeight()

  const primary = [21, 101, 192]
  const dark = [28, 27, 31]
  const grey = [117, 117, 117]
  const lightBg = [245, 245, 245]
  const fechaGeneracion = new Date().toLocaleDateString('es-AR')

  function drawHeader() {
    doc.setFillColor(...primary)
    doc.rect(0, 0, pageW, 28, 'F')
    doc.setTextColor(255, 255, 255)
    doc.setFontSize(18)
    doc.setFont('helvetica', 'bold')
    doc.text('SGP', 14, 11)
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text('Sistema de Gestion de Postas', 14, 17)
    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text(`Reporte: ${reporteActivo.value.label}`, 14, 25)
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text(periodoLabel.value, pageW - 14, 25, { align: 'right' })
    doc.setFontSize(8)
    doc.text(`Generado: ${fechaGeneracion}`, pageW - 14, 20, { align: 'right' })
  }

  function drawFooter(pageNum) {
    doc.setFillColor(...lightBg)
    doc.rect(0, pageH - 10, pageW, 10, 'F')
    doc.setFontSize(7)
    doc.setTextColor(...grey)
    doc.text('SGP - Sistema de Gestion de Postas', 14, pageH - 4)
    doc.text(`Pagina ${pageNum}`, pageW - 14, pageH - 4, { align: 'right' })
  }

  function drawSummaryBoxes(items, startY) {
    if (!items.length) return startY
    const boxW = (pageW - 28) / items.length
    items.forEach((item, i) => {
      const x = 14 + i * boxW
      doc.setFillColor(...lightBg)
      doc.roundedRect(x, startY, boxW - 4, 14, 2, 2, 'F')
      doc.setFontSize(7)
      doc.setTextColor(...grey)
      doc.text(item.label, x + 4, startY + 5)
      doc.setFontSize(11)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(...dark)
      doc.text(String(item.value), x + 4, startY + 11)
    })
    return startY + 18
  }

  drawHeader()
  drawFooter(1)

  const y = drawSummaryBoxes(
    resumenChips.value.map((c) => ({ label: c.label, value: c.value })),
    34,
  )

  const head = [columnas.value.map((c) => c.label)]
  const body = filas.value.map((fila) =>
    columnas.value.map((col) => {
      const valor = col.fn ? col.fn(fila[col.key]) : fila[col.key]
      return valor == null || valor === '' ? '—' : String(valor)
    }),
  )

  if (body.length) {
    doc.autoTable({
      startY: y,
      head,
      body,
      headStyles: {
        fillColor: primary,
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: 8,
        cellPadding: 3,
      },
      bodyStyles: {
        fontSize: 8,
        textColor: dark,
        cellPadding: 2.5,
      },
      alternateRowStyles: {
        fillColor: [248, 250, 252],
      },
      styles: {
        lineColor: [226, 232, 240],
        lineWidth: 0.2,
      },
      margin: { left: 14, right: 14 },
    })
  } else {
    doc.setFontSize(10)
    doc.setTextColor(...grey)
    doc.text('Sin datos para el período seleccionado', 14, y + 8)
  }

  const totalPages = doc.internal.getNumberOfPages()
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i)
    drawFooter(i)
  }

  const nombrePeriodo =
    reporteActivo.value.selector === 'mes'
      ? `${anio.value}-${String(mes.value).padStart(2, '0')}`
      : `${desde.value}_${hasta.value}`
  doc.save(`reporte_${tab.value}_${nombrePeriodo}.pdf`)
  toast.success('PDF exportado')
}
</script>

<style scoped>
.reportes-cuadros-page {
  width: 100%;
}

.tabla-contenedor {
  overflow-x: auto;
}

.resultados-contenedor {
  min-height: 320px;
}
</style>
