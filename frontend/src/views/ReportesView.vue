<template>
  <div class="reportes-page mx-auto">
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

    <v-card rounded="lg" class="pa-sm-5 pa-3 mb-6">
      <div class="d-flex align-center ga-2 mb-4">
        <v-icon icon="mdi-chart-box-outline" color="primary" />
        <div class="text-subtitle-1 font-weight-bold">Reportes</div>
      </div>

      <v-row dense align="center">
        <v-col cols="12" sm="auto">
          <v-select
            v-model="tipoReporte"
            :items="reportTypes"
            item-title="label"
            item-value="value"
            label="Tipo de reporte"
            prepend-inner-icon="mdi-chart-bar"
            hide-details
          />
        </v-col>

        <v-col cols="12" sm>
          <v-menu v-model="menuDesde" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="fechaDesdeFmt"
                label="Desde"
                readonly
                append-inner-icon="mdi-calendar"
                hide-details
                v-bind="menuProps"
              />
            </template>
            <v-date-picker
              v-model="fechaDesdeDate"
              :max="fechaHastaDate || undefined"
              color="primary"
            />
          </v-menu>
        </v-col>

        <v-col cols="12" sm>
          <v-menu v-model="menuHasta" :close-on-content-click="false" location="bottom start">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="fechaHastaFmt"
                label="Hasta"
                readonly
                append-inner-icon="mdi-calendar"
                hide-details
                v-bind="menuProps"
              />
            </template>
            <v-date-picker
              v-model="fechaHastaDate"
              :min="fechaDesdeDate || undefined"
              color="primary"
            />
          </v-menu>
        </v-col>

        <v-col cols="12" sm="auto">
          <v-btn
            color="primary"
            prepend-icon="mdi-magnify"
            :disabled="!fechaDesdeDate || !fechaHastaDate"
            @click="generarReporte"
            :loading="cargando"
            block
          >
            Generar
          </v-btn>
        </v-col>

        <v-col v-if="reportData && !isEmpty" cols="12" sm="auto">
          <v-btn
            variant="tonal"
            prepend-icon="mdi-file-pdf-box"
            color="error"
            @click="exportarPDF"
            block
          >
            PDF
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <div v-if="cargando" class="d-flex align-center justify-center" style="min-height: 200px">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <Transition name="fade-up" mode="out-in">
      <div v-if="!cargando && reportData" key="report">
        <v-card rounded="lg" class="pa-sm-5 pa-3">
          <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-4">
            <div class="d-flex align-center ga-3">
              <div class="text-subtitle-2 font-weight-bold">{{ reportLabel }}</div>
              <v-chip size="small" variant="tonal" color="primary" label>
                {{ fechaDesdeFmt }} — {{ fechaHastaFmt }}
              </v-chip>
            </div>
          </div>

          <div v-if="isEmpty" class="text-center py-8">
            <v-icon icon="mdi-file-document-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-2 text-medium-emphasis">No hay datos para el período seleccionado</p>
          </div>

          <template v-else>
            <div class="d-flex flex-wrap ga-2 mb-4">
              <v-chip
                v-for="s in summaryChips"
                :key="s.label"
                size="small"
                variant="tonal"
                :color="s.color"
                label
              >
                {{ s.label }}: {{ s.value }}
              </v-chip>
            </div>

            <v-table v-if="!mobile" density="comfortable">
              <thead>
                <tr>
                  <th
                    v-for="col in tableColumns"
                    :key="col.key"
                    class="text-caption font-weight-bold text-medium-emphasis"
                    :class="col.align === 'right' ? 'text-right' : ''"
                  >
                    {{ col.label }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in tableRows" :key="idx">
                  <td
                    v-for="col in tableColumns"
                    :key="col.key"
                    :class="[col.align === 'right' ? 'text-right' : '', col.primary ? 'font-weight-medium' : '']"
                  >
                    <template v-if="col.colorFn">
                      <v-chip
                        :color="col.colorFn(row[col.key])"
                        size="x-small"
                        variant="tonal"
                        label
                      >
                        {{ row[col.key] }}
                      </v-chip>
                    </template>
                    <template v-else>
                      {{ row[col.key] }}
                    </template>
                  </td>
                </tr>
              </tbody>
            </v-table>

            <div v-else class="reportes-mobile-list">
              <div
                v-for="(row, idx) in tableRows"
                :key="idx"
                class="reportes-mobile-card pa-3 mb-2"
              >
                <div class="d-flex align-center justify-space-between mb-1">
                  <div class="text-body-2 font-weight-medium">{{ row[tableColumns[0].key] }}</div>
                  <v-chip
                    v-if="severityColor(row)"
                    :color="severityColor(row)"
                    size="x-small"
                    variant="tonal"
                    label
                  >
                    {{ row.severidad || row.estado || '' }}
                  </v-chip>
                </div>
                <div class="d-flex flex-wrap ga-3 text-caption text-medium-emphasis">
                  <span v-for="col in tableColumns.slice(1)" :key="col.key">
                    {{ col.label }}: {{ row[col.key] }}
                  </span>
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
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { jsPDF } from 'jspdf'
import { applyPlugin } from 'jspdf-autotable'
import { reporteApi } from '../api/reporte'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'

applyPlugin(jsPDF)

const { mobile } = useDisplay()
const toast = useToast()

const tipoReporte = ref('cobertura')
const fechaDesdeDate = ref(null)
const fechaHastaDate = ref(null)
const menuDesde = ref(false)
const menuHasta = ref(false)
const cargando = ref(false)
const error = ref('')
const reportData = ref(null)

const reportTypes = [
  { value: 'cobertura', label: 'Cobertura' },
  { value: 'ausentismo', label: 'Ausentismo' },
  { value: 'horas_asp', label: 'Horas por ASP' },
  { value: 'incidencias', label: 'Incidencias' },
  { value: 'tardanzas', label: 'Tardanzas' },
]

function toISODate(d) {
  if (!d) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function fmtDate(d) {
  if (!d) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${day}/${m}/${y}`
}

const fechaDesdeFmt = computed(() => fmtDate(fechaDesdeDate.value))
const fechaHastaFmt = computed(() => fmtDate(fechaHastaDate.value))

watch(fechaDesdeDate, () => { menuDesde.value = false })
watch(fechaHastaDate, () => { menuHasta.value = false })
watch(tipoReporte, () => {
  if (fechaDesdeDate.value && fechaHastaDate.value) generarReporte()
})

const reportLabel = computed(() => {
  return reportTypes.find(r => r.value === tipoReporte.value)?.label || ''
})

const apiMap = {
  cobertura: reporteApi.cobertura,
  ausentismo: reporteApi.ausentismo,
  horas_asp: reporteApi.horasAsp,
  incidencias: reporteApi.incidencias,
  tardanzas: reporteApi.tardanzas,
}

const isEmpty = computed(() => {
  if (!reportData.value) return true
  const d = reportData.value
  if (d.por_posta?.length) return false
  if (d.por_asp?.length) return false
  if (d.items?.length) return false
  return true
})

function formatNum(n) {
  return n != null ? Number(n).toLocaleString('es-AR') : '—'
}

function formatPercent(n) {
  return n != null ? `${Number(n).toFixed(1)}%` : '—'
}

const summaryChips = computed(() => {
  const d = reportData.value
  if (!d) return []
  const base = [
    { label: 'Desde', value: d.fecha_desde, color: 'grey' },
    { label: 'Hasta', value: d.fecha_hasta, color: 'grey' },
  ]
  if (tipoReporte.value === 'cobertura') {
    base.push({ label: 'Cobertura', value: formatPercent(d.cobertura_general), color: d.cobertura_general >= 80 ? 'success' : 'error' })
    base.push({ label: 'Planificadas', value: formatNum(d.total_planificadas), color: 'primary' })
    base.push({ label: 'Finalizadas', value: formatNum(d.total_finalizadas), color: 'success' })
    base.push({ label: 'Sin cubrir', value: formatNum(d.total_sin_cubrir), color: 'error' })
  } else if (tipoReporte.value === 'ausentismo') {
    base.push({ label: 'Ausentismo', value: formatPercent(d.porcentaje_ausentismo), color: 'error' })
    base.push({ label: 'Ausencias', value: formatNum(d.total_ausencias), color: 'warning' })
    base.push({ label: 'Sin cubrir', value: formatNum(d.guardias_sin_cubrir), color: 'error' })
  } else if (tipoReporte.value === 'incidencias') {
    base.push({ label: 'Total', value: formatNum(d.total_incidencias), color: 'warning' })
  } else if (tipoReporte.value === 'tardanzas') {
    base.push({ label: 'Total guardias', value: formatNum(d.total_guardias), color: 'primary' })
    base.push({ label: 'Tardanzas', value: formatNum(d.total_tardanzas), color: 'warning' })
  }
  return base
})

const tableColumns = computed(() => {
  const cols = {
    cobertura: [
      { key: 'posta_nombre', label: 'Posta', primary: true },
      { key: 'planificadas', label: 'Planificadas', align: 'right' },
      { key: 'finalizadas', label: 'Finalizadas', align: 'right' },
      { key: 'ausentes', label: 'Ausentes', align: 'right' },
      { key: 'porcentaje_cobertura', label: 'Cobertura', align: 'right' },
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
      { key: 'total_horas', label: 'Horas', align: 'right' },
    ],
    incidencias: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'posta_nombre', label: 'Posta' },
      { key: 'fecha', label: 'Fecha' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'severidad', label: 'Severidad', colorFn: severityColor },
    ],
    tardanzas: [
      { key: 'asp_nombre', label: 'ASP', primary: true },
      { key: 'total_tardanzas', label: 'Tardanzas', align: 'right' },
      { key: 'promedio_minutos', label: 'Promedio (min)', align: 'right' },
      { key: 'max_minutos', label: 'Máx (min)', align: 'right' },
    ],
  }
  return cols[tipoReporte.value] || []
})

const tableRows = computed(() => {
  const d = reportData.value
  if (!d) return []
  if (tipoReporte.value === 'cobertura') {
    return (d.por_posta || []).map(r => ({
      ...r,
      porcentaje_cobertura: formatPercent(r.porcentaje_cobertura),
    }))
  }
  if (tipoReporte.value === 'horas_asp') {
    return (d.por_asp || []).map(r => ({
      ...r,
      total_horas: formatNum(r.total_horas),
    }))
  }
  if (tipoReporte.value === 'tardanzas') {
    return (d.por_asp || []).map(r => ({
      ...r,
      promedio_minutos: formatNum(r.promedio_minutos),
      max_minutos: formatNum(r.max_minutos),
    }))
  }
  if (tipoReporte.value === 'incidencias') {
    return (d.items || []).map(r => ({
      ...r,
      fecha: r.fecha,
    }))
  }
  return d.por_asp || []
})

function severityColor(row) {
  const s = row.severidad
  if (!s) return null
  const map = { critica: 'error', alta: 'error', media: 'warning', baja: 'grey' }
  return map[s] || 'grey'
}

async function generarReporte() {
  if (!fechaDesdeDate.value || !fechaHastaDate.value) return
  cargando.value = true
  error.value = ''
  reportData.value = null
  try {
    const params = {
      fecha_desde: toISODate(fechaDesdeDate.value),
      fecha_hasta: toISODate(fechaHastaDate.value),
    }
    const fn = apiMap[tipoReporte.value]
    const res = await fn(params)
    reportData.value = res.data
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al generar reporte')
  } finally {
    cargando.value = false
  }
}

function exportarPDF() {
  if (!reportData.value) return
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const d = reportData.value
  const pageW = doc.internal.pageSize.getWidth()
  const pageH = doc.internal.pageSize.getHeight()

  const primary = [21, 101, 192]
  const dark = [28, 27, 31]
  const grey = [117, 117, 117]
  const lightBg = [245, 245, 245]

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
    doc.text(`Reporte: ${reportLabel.value}`, 14, 25)
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text(`${fechaDesdeFmt.value} - ${fechaHastaFmt.value}`, pageW - 14, 25, { align: 'right' })
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

  const tableOpts = {
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
  }

  let pageNum = 1
  drawHeader()
  drawFooter(pageNum)
  let y = 34

  if (tipoReporte.value === 'cobertura') {
    y = drawSummaryBoxes([
      { label: 'Cobertura', value: formatPercent(d.cobertura_general) },
      { label: 'Planificadas', value: String(d.total_planificadas) },
      { label: 'Finalizadas', value: String(d.total_finalizadas) },
      { label: 'Sin cubrir', value: String(d.total_sin_cubrir) },
    ], y)

    if (d.por_posta?.length) {
      doc.autoTable({
        startY: y,
        head: [['Posta', 'Planificadas', 'Finalizadas', 'Ausentes', 'Cobertura']],
        body: d.por_posta.map(r => [
          r.posta_nombre, r.planificadas, r.finalizadas, r.ausentes, formatPercent(r.porcentaje_cobertura),
        ]),
        ...tableOpts,
        columnStyles: {
          0: { cellWidth: 'auto' },
          1: { halign: 'right' },
          2: { halign: 'right' },
          3: { halign: 'right' },
          4: { halign: 'right' },
        },
      })
    }
  } else if (tipoReporte.value === 'ausentismo') {
    y = drawSummaryBoxes([
      { label: 'Ausentismo', value: formatPercent(d.porcentaje_ausentismo) },
      { label: 'Ausencias', value: String(d.total_ausencias) },
      { label: 'Sin cubrir', value: String(d.guardias_sin_cubrir) },
    ], y)

    if (d.por_asp?.length) {
      doc.autoTable({
        startY: y,
        head: [['ASP', 'Total', 'Justificadas', 'Injustificadas']],
        body: d.por_asp.map(r => [r.asp_nombre, r.total_ausencias, r.justificadas, r.injustificadas]),
        ...tableOpts,
        columnStyles: {
          0: { cellWidth: 'auto' },
          1: { halign: 'right' },
          2: { halign: 'right' },
          3: { halign: 'right' },
        },
      })
    }
  } else if (tipoReporte.value === 'horas_asp') {
    if (d.por_asp?.length) {
      doc.autoTable({
        startY: y,
        head: [['ASP', 'Guardias', 'Horas']],
        body: d.por_asp.map(r => [r.asp_nombre, r.total_guardias, formatNum(r.total_horas)]),
        ...tableOpts,
        columnStyles: {
          0: { cellWidth: 'auto' },
          1: { halign: 'right' },
          2: { halign: 'right' },
        },
      })
    }
  } else if (tipoReporte.value === 'incidencias') {
    y = drawSummaryBoxes([
      { label: 'Total incidencias', value: String(d.total_incidencias) },
    ], y)

    if (d.items?.length) {
      doc.autoTable({
        startY: y,
        head: [['ASP', 'Posta', 'Fecha', 'Tipo', 'Severidad', 'Descripcion']],
        body: d.items.map(r => [r.asp_nombre, r.posta_nombre, r.fecha, r.tipo, r.severidad, r.descripcion]),
        ...tableOpts,
        styles: { ...tableOpts.styles, fontSize: 7 },
        columnStyles: {
          0: { cellWidth: 30 },
          1: { cellWidth: 30 },
          2: { cellWidth: 20 },
          3: { cellWidth: 20 },
          4: { cellWidth: 18 },
          5: { cellWidth: 'auto' },
        },
      })
    }
  } else if (tipoReporte.value === 'tardanzas') {
    y = drawSummaryBoxes([
      { label: 'Total guardias', value: String(d.total_guardias) },
      { label: 'Tardanzas', value: String(d.total_tardanzas) },
    ], y)

    if (d.por_asp?.length) {
      doc.autoTable({
        startY: y,
        head: [['ASP', 'Tardanzas', 'Promedio (min)', 'Max (min)']],
        body: d.por_asp.map(r => [r.asp_nombre, r.total_tardanzas, formatNum(r.promedio_minutos), formatNum(r.max_minutos)]),
        ...tableOpts,
        columnStyles: {
          0: { cellWidth: 'auto' },
          1: { halign: 'right' },
          2: { halign: 'right' },
          3: { halign: 'right' },
        },
      })
    }
  }

  const totalPages = doc.internal.getNumberOfPages()
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i)
    drawFooter(i)
  }

  doc.save(`reporte_${tipoReporte.value}_${toISODate(fechaDesdeDate.value)}_${toISODate(fechaHastaDate.value)}.pdf`)
  toast.success('PDF exportado')
}
</script>

<style scoped>
.reportes-page {
  width: 100%;
}

.reportes-mobile-list {
  display: flex;
  flex-direction: column;
}

.reportes-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}
</style>
