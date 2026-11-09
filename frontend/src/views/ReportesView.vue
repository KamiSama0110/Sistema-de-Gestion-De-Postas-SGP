<template>
  <div class="reportes-page mx-auto">
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

      <div :class="mobile ? 'd-flex flex-column ga-3' : 'd-flex flex-wrap align-center ga-3'">
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
    </v-card>

    <div class="resultados-contenedor" aria-live="polite">
      <Transition name="fade-slide" mode="out-in">
        <div :key="fase">
          <SkeletonList v-if="fase === 'cargando'" :filas="8" :avatar="false" />

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

            <div v-if="barras.length" class="mb-5">
              <div class="text-body-2 font-weight-medium mb-2">{{ barrasTitulo }}</div>
              <GraficoBarras :items="barras" />
            </div>

            <div class="tabla-contenedor">
              <ReporteResultados :columnas="columnas" :filas="filas" />
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
import { reporteApi } from '../api/reporte'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { SEVERIDADES, tipoLabel, severidadLabel, severidadColor } from '../utils/incidencia'
import SkeletonList from '../components/SkeletonList.vue'
import GraficoBarras from '../components/GraficoBarras.vue'
import ReporteResultados from '../components/ReporteResultados.vue'

applyPlugin(jsPDF)

const { mobile } = useDisplay()
const toast = useToast()

const reportes = [
  { id: 'cobertura', label: 'Cobertura', icon: 'mdi-shield-check-outline' },
  { id: 'ausentismo', label: 'Ausentismo', icon: 'mdi-account-off-outline' },
  { id: 'horas_asp', label: 'Horas por ASP', icon: 'mdi-clock-outline' },
  { id: 'incidencias', label: 'Incidencias', icon: 'mdi-alert-circle-outline' },
  { id: 'tardanzas', label: 'Tardanzas', icon: 'mdi-timer-outline' },
]

const apiMap = {
  cobertura: reporteApi.cobertura,
  ausentismo: reporteApi.ausentismo,
  horas_asp: reporteApi.horasAsp,
  incidencias: reporteApi.incidencias,
  tardanzas: reporteApi.tardanzas,
}

const tab = ref('cobertura')
const desde = ref(primerDiaMes())
const hasta = ref(hoyYMD())
const menuDesde = ref(false)
const menuHasta = ref(false)
const cargando = ref(false)
const error = ref('')
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

function num(valor) {
  return valor != null ? Number(valor).toLocaleString('es-AR') : '—'
}

const periodoLabel = computed(() => `${desde.value} — ${hasta.value}`)

const estaVacio = computed(() => {
  const d = datos.value
  if (!d) return true
  if (tab.value === 'incidencias') return !d.items?.length
  return !d.por_asp?.length && !d.por_posta?.length
})

const fase = computed(() => {
  if (!datos.value) {
    if (cargando.value) return 'cargando'
    return 'inicial'
  }
  return 'listo'
})

const resumenChips = computed(() => {
  const d = datos.value
  if (!d) return []
  if (tab.value === 'cobertura') {
    return [
      { label: 'Cobertura', value: pct(d.cobertura_general), color: d.cobertura_general >= 80 ? 'success' : 'warning' },
      { label: 'Planificadas', value: num(d.total_planificadas), color: 'primary' },
      { label: 'Finalizadas', value: num(d.total_finalizadas), color: 'success' },
      { label: 'Sin cubrir', value: num(d.total_sin_cubrir), color: 'error' },
    ]
  }
  if (tab.value === 'ausentismo') {
    return [
      { label: 'Ausentismo', value: pct(d.porcentaje_ausentismo), color: 'warning' },
      { label: 'Ausencias', value: num(d.total_ausencias), color: 'error' },
      { label: 'Sin cubrir', value: num(d.guardias_sin_cubrir), color: 'error' },
      { label: 'Planificadas', value: num(d.total_planificadas), color: 'primary' },
    ]
  }
  if (tab.value === 'horas_asp') {
    const guardias = (d.por_asp || []).reduce((s, a) => s + a.total_guardias, 0)
    const horas = (d.por_asp || []).reduce((s, a) => s + a.total_horas, 0)
    return [
      { label: 'ASP', value: d.por_asp?.length || 0, color: 'primary' },
      { label: 'Guardias', value: num(guardias), color: 'primary' },
      { label: 'Horas', value: num(horas), color: 'success' },
    ]
  }
  if (tab.value === 'incidencias') {
    return [{ label: 'Total', value: num(d.total_incidencias), color: 'warning' }]
  }
  return [
    { label: 'Total guardias', value: num(d.total_guardias), color: 'primary' },
    { label: 'Tardanzas', value: num(d.total_tardanzas), color: 'warning' },
  ]
})

const barrasTitulo = computed(() => {
  const titulos = {
    cobertura: 'Cobertura por posta',
    ausentismo: 'Ausencias por ASP',
    horas_asp: 'Horas por ASP',
    incidencias: 'Incidencias por severidad',
    tardanzas: 'Tardanzas por ASP',
  }
  return titulos[tab.value] || ''
})

const barras = computed(() => {
  const d = datos.value
  if (!d) return []
  if (tab.value === 'cobertura') {
    return (d.por_posta || []).map((p) => {
      const valor = Number(p.porcentaje_cobertura ?? 0)
      return {
        label: p.posta_nombre,
        value: valor,
        porcentaje: valor,
        color: valor >= 80 ? 'success' : 'warning',
      }
    })
  }
  if (tab.value === 'ausentismo') {
    return (d.por_asp || []).map((a) => ({
      label: a.asp_nombre,
      value: a.total_ausencias,
      color: 'error',
    }))
  }
  if (tab.value === 'horas_asp') {
    return (d.por_asp || []).map((a) => ({
      label: a.asp_nombre,
      value: a.total_horas,
      color: 'primary',
    }))
  }
  if (tab.value === 'incidencias') {
    const conteo = {}
    ;(d.items || []).forEach((i) => {
      conteo[i.severidad] = (conteo[i.severidad] || 0) + 1
    })
    return SEVERIDADES.map((s) => ({
      label: s.title,
      value: conteo[s.value] || 0,
      color: s.color,
    }))
  }
  return (d.por_asp || []).map((a) => ({
    label: a.asp_nombre,
    value: a.total_tardanzas,
    color: 'warning',
  }))
})

const columnas = computed(() => {
  const cols = {
    cobertura: [
      { key: 'posta_nombre', label: 'Posta', primary: true },
      { key: 'planificadas', label: 'Planificadas', align: 'right' },
      { key: 'finalizadas', label: 'Finalizadas', align: 'right' },
      { key: 'ausentes', label: 'Ausentes', align: 'right' },
      { key: 'porcentaje_cobertura', label: 'Cobertura', align: 'right', fn: pct },
    ],
    ausentismo: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'total_ausencias', label: 'Total', align: 'right' },
      { key: 'justificadas', label: 'Justificadas', align: 'right' },
      { key: 'injustificadas', label: 'Injustificadas', align: 'right' },
    ],
    horas_asp: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'total_guardias', label: 'Guardias', align: 'right' },
      { key: 'total_horas', label: 'Horas', align: 'right', fn: num },
    ],
    incidencias: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'posta_nombre', label: 'Posta' },
      { key: 'fecha', label: 'Fecha' },
      { key: 'tipo', label: 'Tipo', fn: tipoLabel },
      { key: 'severidad', label: 'Severidad', fn: severidadLabel, colorFn: severidadColor },
      { key: 'descripcion', label: 'Descripción', wrap: true },
    ],
    tardanzas: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'total_tardanzas', label: 'Tardanzas', align: 'right' },
      { key: 'promedio_minutos', label: 'Promedio (min)', align: 'right', fn: num },
      { key: 'max_minutos', label: 'Máx (min)', align: 'right', fn: num },
    ],
  }
  return cols[tab.value] || []
})

const filas = computed(() => {
  const d = datos.value
  if (!d) return []
  if (tab.value === 'cobertura') return d.por_posta || []
  if (tab.value === 'incidencias') return d.items || []
  return d.por_asp || []
})

function validar() {
  error.value = ''
  if (!desde.value || !hasta.value) {
    error.value = 'Seleccione las fechas desde y hasta'
    return false
  }
  if (ymdToDate(desde.value) > ymdToDate(hasta.value)) {
    error.value = 'La fecha desde no puede ser posterior a la fecha hasta'
    return false
  }
  return true
}

async function generar() {
  if (!validar()) {
    datos.value = null
    return
  }
  cargando.value = true
  error.value = ''
  try {
    const res = await apiMap[tab.value]({
      fecha_desde: desde.value,
      fecha_hasta: hasta.value,
    })
    datos.value = res.data
  } catch (e) {
    datos.value = null
    error.value = normalizeApiError(e, 'Error al generar el reporte')
  } finally {
    cargando.value = false
  }
}

function regenerar() {
  datos.value = null
  generar()
}

watch(tab, regenerar)

watch([desde, hasta], regenerar)

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

  doc.save(`reporte_${tab.value}_${desde.value}_${hasta.value}.pdf`)
  toast.success('PDF exportado')
}
</script>

<style scoped>
.reportes-page {
  width: 100%;
}

.tabla-contenedor {
  overflow-x: auto;
}

.resultados-contenedor {
  min-height: 320px;
}
</style>
