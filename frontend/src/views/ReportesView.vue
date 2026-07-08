<template>
  <div class="reportes-page">
    <div class="page-header reportes-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div>
          <h2 class="page-title">Reportes</h2>
          <p class="page-subtitle">Metricas operativas del sistema</p>
        </div>
      </div>

    </div>

    <Card class="panel-card filters-card">
      <template #content>
        <div class="filters-top">
          <div class="filters-summary">
            <span class="filters-summary-label">Reporte seleccionado</span>
            <span class="filters-summary-value">
              <Tag :value="reporteActual.label" severity="info" />
            </span>
            <span class="muted">Ajusta el periodo y aplica filtros adicionales si el reporte lo requiere.</span>
          </div>

          <div class="filter-state-box">
            <label>Periodo de analisis</label>
            <div class="report-filters-grid">
              <div class="report-filter-item">
                <span class="report-filter-label">Tipo de reporte</span>
                <Select
                  v-model="tipoReporte"
                  :options="opcionesReporte"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Tipo de reporte"
                  class="report-type-select"
                />
              </div>

              <div class="report-filter-item">
                <span class="report-filter-label">Desde</span>
                <DatePicker v-model="filtros.fecha_desde" dateFormat="yy-mm-dd" showIcon placeholder="Desde" class="report-date-input" />
              </div>

              <div class="report-filter-item">
                <span class="report-filter-label">Hasta</span>
                <DatePicker v-model="filtros.fecha_hasta" dateFormat="yy-mm-dd" showIcon placeholder="Hasta" class="report-date-input" />
              </div>

              <div v-if="tipoReporte === 'incidencias'" class="report-filter-item">
                <span class="report-filter-label">Severidad</span>
                <Select
                  v-model="filtros.severidad"
                  :options="opcionesSeveridad"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Severidad"
                  class="report-type-select"
                />
              </div>

              <div v-if="tipoReporte === 'incidencias'" class="report-filter-item">
                <span class="report-filter-label">Posta</span>
                <Select
                  v-model="filtros.posta_id"
                  :options="opcionesPosta"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Posta"
                  class="report-type-select"
                />
              </div>

              <div v-if="tipoReporte === 'tardanzas'" class="report-filter-item">
                <span class="report-filter-label">ASP</span>
                <Select
                  v-model="filtros.asp_id"
                  :options="opcionesAsp"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="ASP"
                  class="report-type-select"
                />
              </div>

              <div class="report-filter-item report-filter-action">
                <span class="report-filter-label">Accion</span>
                <Button label="Generar" icon="pi pi-search" :loading="cargando" @click="generarReporte" />
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
      {{ error }}
    </Message>

    <Card v-if="reporte" class="panel-card report-card">
      <template #content>
        <div class="section-head report-section-head">
          <div>
            <h3>{{ reporteActual.label }}</h3>
            <p>{{ reporteDescripcion }}</p>
          </div>
          <div class="report-head-actions">
            <Tag :value="reporteActual.label" severity="success" />
            <Button
              label="Exportar PDF"
              icon="pi pi-file-pdf"
              severity="primary"
              class="report-export-button"
              :disabled="!puedeExportar"
              @click="exportarPdf"
            />
          </div>
        </div>

        <div v-if="!reporteEsActual" class="stale-report-state">
          <i class="pi pi-info-circle stale-report-icon"></i>
          <div>
            <p class="stale-report-title">Este reporte cambió de filtros o de tipo</p>
            <p class="stale-report-text">Presiona Generar para actualizar los datos y habilitar la exportación.</p>
          </div>
        </div>

        <div v-else-if="reporteSinDatos" class="empty-report-state">
          <i class="pi pi-folder-open empty-report-icon"></i>
          <div>
            <p class="empty-report-title">No hay datos para este reporte</p>
            <p class="empty-report-text">El periodo o los filtros seleccionados no devolvieron resultados. Ajusta los criterios y vuelve a generar.</p>
          </div>
        </div>

        <div v-else-if="tipoReporte === 'cobertura'">
          <div class="summary-grid">
            <div class="summary-card">
              <p class="summary-label">Cobertura general</p>
              <h3>{{ reporte.cobertura_general }}%</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Planificadas</p>
              <h3>{{ reporte.total_planificadas }}</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Finalizadas</p>
              <h3>{{ reporte.total_finalizadas }}</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Sin cubrir</p>
              <h3>{{ reporte.total_sin_cubrir }}</h3>
            </div>
          </div>
          <div class="table-shell report-table-shell">
            <DataTable :value="reporte.por_posta" size="small" stripedRows>
              <Column field="posta_nombre" header="Posta" />
              <Column field="planificadas" header="Planificadas" />
              <Column field="finalizadas" header="Finalizadas" />
              <Column field="ausentes" header="Ausentes" />
              <Column field="porcentaje_cobertura" header="Cobertura %" />
            </DataTable>
          </div>
        </div>

        <div v-else-if="tipoReporte === 'ausentismo'">
          <div class="summary-grid">
            <div class="summary-card">
              <p class="summary-label">Planificadas</p>
              <h3>{{ reporte.total_planificadas }}</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Ausencias</p>
              <h3>{{ reporte.total_ausencias }}</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Porcentaje</p>
              <h3>{{ reporte.porcentaje_ausentismo }}%</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Sin cubrir</p>
              <h3>{{ reporte.guardias_sin_cubrir }}</h3>
            </div>
          </div>
          <div class="table-shell report-table-shell">
            <DataTable :value="reporte.por_asp" size="small" stripedRows>
              <Column field="asp_nombre" header="ASP" />
              <Column field="total_ausencias" header="Ausencias" />
              <Column field="justificadas" header="Justificadas" />
              <Column field="injustificadas" header="Injustificadas" />
            </DataTable>
          </div>
        </div>

        <div v-else-if="tipoReporte === 'horas'">
          <div class="table-shell report-table-shell">
            <DataTable :value="reporte.por_asp" size="small" stripedRows>
              <Column field="asp_nombre" header="ASP" />
              <Column field="total_guardias" header="Guardias" />
              <Column field="total_horas" header="Horas" />
            </DataTable>
          </div>
        </div>

        <div v-else-if="tipoReporte === 'incidencias'">
          <div class="summary-grid">
            <div class="summary-card">
              <p class="summary-label">Total novedades</p>
              <h3>{{ reporte.total_incidencias }}</h3>
            </div>
          </div>
          <div class="table-shell report-table-shell">
            <DataTable :value="reporte.items" size="small" stripedRows>
              <Column field="fecha" header="Fecha" />
              <Column field="posta_nombre" header="Posta" />
              <Column field="asp_nombre" header="ASP" />
              <Column field="tipo" header="Tipo" />
              <Column field="severidad" header="Severidad" />
              <Column field="descripcion" header="Descripcion" />
            </DataTable>
          </div>
        </div>

        <div v-else-if="tipoReporte === 'tardanzas'">
          <div class="summary-grid">
            <div class="summary-card">
              <p class="summary-label">Guardias</p>
              <h3>{{ reporte.total_guardias }}</h3>
            </div>
            <div class="summary-card">
              <p class="summary-label">Tardanzas</p>
              <h3>{{ reporte.total_tardanzas }}</h3>
            </div>
          </div>
          <div class="table-shell report-table-shell">
            <DataTable :value="reporte.por_asp" size="small" stripedRows>
              <Column field="asp_nombre" header="ASP" />
              <Column field="total_tardanzas" header="Tardanzas" />
              <Column field="promedio_minutos" header="Promedio" />
              <Column field="max_minutos" header="Max" />
            </DataTable>
          </div>
        </div>
      </template>
    </Card>

    <Card v-else class="panel-card empty-report-card">
      <template #content>
        <div class="empty-state">
          <i class="pi pi-chart-line empty-icon"></i>
          <div>
            <p class="empty-title">Aun no hay un reporte generado</p>
            <p class="empty-subtitle">Selecciona un periodo y presiona Generar para ver los resultados</p>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { reporteApi } from '../api/reporte'
import { postaApi } from '../api/posta'
import { aspApi } from '../api/asp'
import { normalizeApiError } from '../utils/error'

const tipoReporte = ref('cobertura')
const reporte = ref(null)
const cargando = ref(false)
const error = ref('')

const filtros = ref({
  fecha_desde: null,
  fecha_hasta: null,
  severidad: '',
  posta_id: null,
  asp_id: null,
})

const postas = ref([])
const asps = ref([])

const opcionesReporte = [
  { label: 'Cobertura', value: 'cobertura' },
  { label: 'Ausentismo', value: 'ausentismo' },
  { label: 'Horas por ASP', value: 'horas' },
  { label: 'Novedades', value: 'incidencias' },
  { label: 'Tardanzas', value: 'tardanzas' },
]

const opcionesSeveridad = [
  { label: 'Todas', value: '' },
  { label: 'Baja', value: 'baja' },
  { label: 'Media', value: 'media' },
  { label: 'Alta', value: 'alta' },
  { label: 'Critica', value: 'critica' },
]

const opcionesPosta = computed(() => [
  { label: 'Todas', value: null },
  ...postas.value.map(p => ({ label: p.nombre, value: p.id })),
])

const opcionesAsp = computed(() => [
  { label: 'Todos', value: null },
  ...asps.value.map(a => ({ label: `${a.nombre} ${a.apellidos}`, value: a.id })),
])

const reporteActual = computed(() => opcionesReporte.find(o => o.value === tipoReporte.value) || opcionesReporte[0])
const reporteGeneradoClave = ref('')

function buildReporteClave() {
  return JSON.stringify({
    tipo: tipoReporte.value,
    fecha_desde: formatFecha(filtros.value.fecha_desde),
    fecha_hasta: formatFecha(filtros.value.fecha_hasta),
    severidad: filtros.value.severidad || '',
    posta_id: filtros.value.posta_id ?? null,
    asp_id: filtros.value.asp_id ?? null,
  })
}

const reporteEsActual = computed(() => Boolean(reporte.value) && reporteGeneradoClave.value === buildReporteClave())
const reporteSinDatos = computed(() => {
  if (!reporteEsActual.value || !reporte.value) return false

  if (tipoReporte.value === 'cobertura') return (reporte.value.total_planificadas || 0) === 0
  if (tipoReporte.value === 'ausentismo') return (reporte.value.total_planificadas || 0) === 0
  if (tipoReporte.value === 'horas') return (reporte.value.por_asp || []).length === 0
  if (tipoReporte.value === 'incidencias') return (reporte.value.total_incidencias || 0) === 0
  if (tipoReporte.value === 'tardanzas') return (reporte.value.total_guardias || 0) === 0

  return false
})

const puedeExportar = computed(() => reporteEsActual.value && !reporteSinDatos.value && Boolean(buildPdfTable()))

const reporteDescripcion = computed(() => {
  const descripciones = {
    cobertura: 'Mide la cobertura por posta y el volumen de guardias completadas.',
    ausentismo: 'Resume ausencias por ASP y su nivel de justificacion.',
    horas: 'Compara la carga de guardias y las horas acumuladas por ASP.',
    incidencias: 'Lista las novedades relevantes ocurridas en el periodo seleccionado.',
    tardanzas: 'Muestra el retraso acumulado y su promedio por ASP.',
  }

  return descripciones[tipoReporte.value] || ''
})

function formatFecha(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.split('T')[0]
  const d = new Date(value)
  return d.toISOString().split('T')[0]
}

function formatNumero(value, decimals = 0) {
  if (value === null || value === undefined || value === '') return '-'
  const number = Number(value)
  if (Number.isNaN(number)) return String(value)
  return decimals > 0 ? number.toFixed(decimals) : String(Math.round(number))
}

function getFiltroDescripcionPdf() {
  const partes = [
    `Reporte: ${reporteActual.value.label}`,
    `Periodo: ${filtros.value.fecha_desde ? formatFecha(filtros.value.fecha_desde) : '-'}  -  ${filtros.value.fecha_hasta ? formatFecha(filtros.value.fecha_hasta) : '-'}`,
  ]

  if (tipoReporte.value === 'incidencias') {
    partes.push(`Severidad: ${filtros.value.severidad || 'Todas'}`)
    const posta = opcionesPosta.value.find((item) => item.value === filtros.value.posta_id)
    partes.push(`Posta: ${posta?.label || 'Todas'}`)
  }

  if (tipoReporte.value === 'tardanzas') {
    const asp = opcionesAsp.value.find((item) => item.value === filtros.value.asp_id)
    partes.push(`ASP: ${asp?.label || 'Todos'}`)
  }

  return partes
}

function buildPdfTable() {
  if (!reporte.value) return null

  if (tipoReporte.value === 'cobertura') {
    return {
      title: 'Cobertura por posta',
      head: [['Posta', 'Planificadas', 'Finalizadas', 'Ausentes', 'Cobertura %']],
      body: (reporte.value.por_posta || []).map((item) => [
        item.posta_nombre,
        formatNumero(item.planificadas),
        formatNumero(item.finalizadas),
        formatNumero(item.ausentes),
        `${formatNumero(item.porcentaje_cobertura, 2)}%`,
      ]),
    }
  }

  if (tipoReporte.value === 'ausentismo') {
    return {
      title: 'Ausentismo por ASP',
      head: [['ASP', 'Ausencias', 'Justificadas', 'Injustificadas']],
      body: (reporte.value.por_asp || []).map((item) => [
        item.asp_nombre,
        formatNumero(item.total_ausencias),
        formatNumero(item.justificadas),
        formatNumero(item.injustificadas),
      ]),
    }
  }

  if (tipoReporte.value === 'horas') {
    return {
      title: 'Horas por ASP',
      head: [['ASP', 'Guardias', 'Horas']],
      body: (reporte.value.por_asp || []).map((item) => [
        item.asp_nombre,
        formatNumero(item.total_guardias),
        formatNumero(item.total_horas, 2),
      ]),
    }
  }

  if (tipoReporte.value === 'incidencias') {
    return {
      title: 'Novedades',
      head: [['Fecha', 'Posta', 'ASP', 'Tipo', 'Severidad', 'Descripcion']],
      body: (reporte.value.items || []).map((item) => [
        formatFecha(item.fecha),
        item.posta_nombre,
        item.asp_nombre,
        item.tipo,
        item.severidad,
        item.descripcion,
      ]),
    }
  }

  if (tipoReporte.value === 'tardanzas') {
    return {
      title: 'Tardanzas por ASP',
      head: [['ASP', 'Tardanzas', 'Promedio', 'Maximo']],
      body: (reporte.value.por_asp || []).map((item) => [
        item.asp_nombre,
        formatNumero(item.total_tardanzas),
        formatNumero(item.promedio_minutos, 2),
        formatNumero(item.max_minutos),
      ]),
    }
  }

  return null
}

function exportarPdf() {
  if (!puedeExportar.value) return

  const table = buildPdfTable()
  if (!table) return

  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const marginLeft = 14
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const colors = {
    band: [15, 23, 42],
    accent: [217, 119, 6],
    ink: [17, 24, 39],
    muted: [100, 116, 139],
    border: [203, 213, 225],
    soft: [248, 250, 252],
    white: [255, 255, 255],
  }

  const drawHeader = () => {
    doc.setFillColor(...colors.band)
    doc.rect(0, 0, pageWidth, 24, 'F')
    doc.setFillColor(...colors.accent)
    doc.circle(marginLeft + 7, 12, 5.5, 'F')
    doc.setTextColor(...colors.white)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.text('SISTEMA DE GESTION DE POSTAS', marginLeft + 17, 10)
    doc.setFontSize(15)
    doc.text('Reporte operativo', marginLeft + 17, 16)
  }

  const drawFooter = () => {
    const totalPages = doc.getNumberOfPages()
    for (let pageNumber = 1; pageNumber <= totalPages; pageNumber += 1) {
      doc.setPage(pageNumber)
      doc.setDrawColor(...colors.border)
      doc.line(marginLeft, pageHeight - 14, pageWidth - marginLeft, pageHeight - 14)
      doc.setTextColor(...colors.muted)
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(9)
      doc.text(`Pagina ${pageNumber} de ${totalPages}`, pageWidth - marginLeft, pageHeight - 8, { align: 'right' })
      doc.text(`Generado: ${new Date().toLocaleString()}`, marginLeft, pageHeight - 8)
    }
  }

  let currentY = 33
  doc.setTextColor(...colors.ink)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(18)
  doc.text(`Reporte ${reporteActual.value.label}`, marginLeft, currentY)

  currentY += 7
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(...colors.muted)
  doc.text(reporteDescripcion.value, marginLeft, currentY)

  currentY += 9
  doc.setFillColor(...colors.soft)
  doc.setDrawColor(...colors.border)
  doc.roundedRect(marginLeft, currentY, pageWidth - (marginLeft * 2), 22, 2, 2, 'FD')
  doc.setTextColor(...colors.ink)
  doc.setFontSize(9)
  getFiltroDescripcionPdf().forEach((linea, index) => {
    const columnWidth = (pageWidth - (marginLeft * 2) - 8) / 2
    const x = marginLeft + 4 + (index % 2) * (columnWidth + 4)
    const y = currentY + 7 + Math.floor(index / 2) * 7
    doc.text(linea, x, y)
  })

  let summaryLines = []
  if (tipoReporte.value === 'cobertura') {
    summaryLines = [
      ['Cobertura general', `${formatNumero(reporte.value.cobertura_general, 2)}%`],
      ['Planificadas', formatNumero(reporte.value.total_planificadas)],
      ['Finalizadas', formatNumero(reporte.value.total_finalizadas)],
      ['Sin cubrir', formatNumero(reporte.value.total_sin_cubrir)],
    ]
  } else if (tipoReporte.value === 'ausentismo') {
    summaryLines = [
      ['Planificadas', formatNumero(reporte.value.total_planificadas)],
      ['Ausencias', formatNumero(reporte.value.total_ausencias)],
      ['Porcentaje', `${formatNumero(reporte.value.porcentaje_ausentismo, 2)}%`],
      ['Sin cubrir', formatNumero(reporte.value.guardias_sin_cubrir)],
    ]
  } else if (tipoReporte.value === 'horas') {
    summaryLines = [['Cantidad de ASP', String((reporte.value.por_asp || []).length)]]
  } else if (tipoReporte.value === 'incidencias') {
    summaryLines = [['Total novedades', formatNumero(reporte.value.total_incidencias)]]
  } else if (tipoReporte.value === 'tardanzas') {
    summaryLines = [
      ['Guardias', formatNumero(reporte.value.total_guardias)],
      ['Tardanzas', formatNumero(reporte.value.total_tardanzas)],
    ]
  }

  if (summaryLines.length) {
    currentY += 28
    summaryLines.forEach(([label, value], index) => {
      const cardWidth = (pageWidth - (marginLeft * 2) - 8) / 2
      const x = marginLeft + (index % 2) * (cardWidth + 4)
      const y = currentY + Math.floor(index / 2) * 14
      doc.setFillColor(...colors.white)
      doc.setDrawColor(...colors.border)
      doc.roundedRect(x, y, cardWidth, 12, 2, 2, 'FD')
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(8)
      doc.setTextColor(...colors.muted)
      doc.text(label, x + 3, y + 4)
      doc.setFont('helvetica', 'bold')
      doc.setFontSize(11)
      doc.setTextColor(...colors.ink)
      doc.text(value, x + 3, y + 9)
    })
    currentY += Math.ceil(summaryLines.length / 2) * 14 + 4
  }

  autoTable(doc, {
    head: table.head,
    body: table.body,
    startY: currentY,
    theme: 'grid',
    styles: {
      fontSize: 9,
      cellPadding: 2,
      overflow: 'linebreak',
      valign: 'middle',
    },
    headStyles: {
      fillColor: colors.band,
      textColor: 255,
      fontStyle: 'bold',
    },
    alternateRowStyles: {
      fillColor: colors.soft,
    },
    margin: { left: marginLeft, right: marginLeft },
    didDrawPage: () => {
      drawHeader()
    },
  })

  drawFooter()

  const safeDate = `${new Date().toISOString().slice(0, 10)}`
  const filename = `reporte_${tipoReporte.value}_${safeDate}.pdf`
  doc.save(filename)
}

async function cargarCatalogos() {
  const [postasRes, aspRes] = await Promise.all([
    postaApi.listar({}),
    aspApi.listar({ page: 1, size: 100 }),
  ])
  postas.value = postasRes.data || []
  asps.value = aspRes.data.items || []
}

async function generarReporte() {
  error.value = ''
  reporte.value = null
  if (!filtros.value.fecha_desde || !filtros.value.fecha_hasta) {
    error.value = 'Selecciona un rango de fechas'
    return
  }
  cargando.value = true
  try {
    const params = {
      fecha_desde: formatFecha(filtros.value.fecha_desde),
      fecha_hasta: formatFecha(filtros.value.fecha_hasta),
    }
    if (tipoReporte.value === 'incidencias') {
      if (filtros.value.severidad) params.severidad = filtros.value.severidad
      if (filtros.value.posta_id) params.posta_id = filtros.value.posta_id
    }
    if (tipoReporte.value === 'tardanzas') {
      if (filtros.value.asp_id) params.asp_id = filtros.value.asp_id
    }

    if (tipoReporte.value === 'cobertura') {
      const res = await reporteApi.cobertura(params)
      reporte.value = res.data
    } else if (tipoReporte.value === 'ausentismo') {
      const res = await reporteApi.ausentismo(params)
      reporte.value = res.data
    } else if (tipoReporte.value === 'horas') {
      const res = await reporteApi.horasAsp(params)
      reporte.value = res.data
    } else if (tipoReporte.value === 'incidencias') {
      const res = await reporteApi.incidencias(params)
      reporte.value = res.data
    } else if (tipoReporte.value === 'tardanzas') {
      const res = await reporteApi.tardanzas(params)
      reporte.value = res.data
    }
    reporteGeneradoClave.value = buildReporteClave()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al generar reporte')
  } finally {
    cargando.value = false
  }
}

onMounted(cargarCatalogos)
</script>

<style scoped>
.reportes-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title-icon {
  width: 42px;
  height: 42px;
  background: color-mix(in srgb, var(--primary) 14%, transparent);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--primary);
}

.filters-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.filters-summary {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 220px;
}

.filters-summary-label,
.summary-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin: 0;
}

.filters-summary-value {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.muted {
  color: var(--text-muted);
  font-size: 13px;
}

.filter-state-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.filter-state-box label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}

.report-filters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: end;
  width: 100%;
  overflow-x: visible;
}

.report-filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1 1 190px;
  min-width: 160px;
}

.report-filter-item :deep(.p-select),
.report-filter-item :deep(.p-datepicker),
.report-filter-item :deep(.p-button) {
  width: 100%;
  height: 42px;
}

.report-filter-item :deep(.p-inputtext) {
  height: 42px;
}

.report-filter-item :deep(.p-datepicker .p-inputtext) {
  height: 42px;
}

.report-filter-item :deep(.p-select-label),
.report-filter-item :deep(.p-select-trigger),
.report-filter-item :deep(.p-datepicker-trigger) {
  height: 42px;
}

.report-filter-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.report-filter-action {
  justify-content: flex-end;
  flex: 0 0 160px;
  min-width: 160px;
  align-items: stretch;
}

.report-filter-action :deep(.p-button) {
  height: 42px;
}

.report-type-select,
.report-date-input {
  width: 100%;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  background: var(--surface-2);
  box-shadow: 0 1px 0 color-mix(in srgb, var(--border) 30%, transparent);
}

.summary-card h3 {
  margin: 6px 0 0;
  font-size: 20px;
}

.section-head {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.report-section-head {
  align-items: center;
}

.report-head-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.report-export-button {
  border-radius: 9999px;
  padding-inline: 1rem;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
}

.report-export-button :deep(.p-button-icon) {
  font-size: 0.9rem;
}

.report-export-button:disabled {
  opacity: 0.72;
}

.stale-report-state {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  margin-top: 18px;
  border-radius: 14px;
  border: 1px dashed color-mix(in srgb, var(--primary) 28%, var(--border));
  background: color-mix(in srgb, var(--primary) 6%, var(--surface-2));
}

.stale-report-icon {
  margin-top: 2px;
  font-size: 1.1rem;
  color: var(--primary);
}

.stale-report-title {
  margin: 0 0 4px;
  font-weight: 700;
  color: var(--text);
}

.stale-report-text {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.empty-report-state {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  margin-top: 18px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--surface-border) 75%, transparent);
  background: color-mix(in srgb, var(--surface-2) 78%, white);
}

.empty-report-icon {
  margin-top: 2px;
  font-size: 1.1rem;
  color: var(--text-muted);
}

.empty-report-title {
  margin: 0 0 4px;
  font-weight: 700;
  color: var(--text);
}

.empty-report-text {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.section-head h3 {
  margin: 0;
  font-size: 18px;
}

.section-head p {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.table-shell {
  overflow-x: auto;
}

.report-table-shell {
  margin-top: 8px;
}

.empty-report-card :deep(.p-card-body) {
  padding: 8px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 24px 12px;
  text-align: left;
}

.empty-icon {
  font-size: 24px;
  color: var(--text-muted);
}

.empty-title {
  margin: 0;
  font-weight: 600;
  color: var(--text);
  font-size: 15px;
}

.empty-subtitle {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 960px) {
  .report-filters-grid {
    flex-wrap: wrap;
    overflow-x: visible;
  }

  .report-filters-grid :deep(.p-select),
  .report-filters-grid :deep(.p-datepicker),
  .report-filters-grid :deep(.p-button) {
    width: 100%;
    flex: 1 1 100%;
  }

  .section-head {
    flex-direction: column;
  }

  .report-section-head {
    align-items: stretch;
  }

  .report-head-actions {
    width: 100%;
  }

  .report-head-actions :deep(.p-button) {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .empty-state {
    flex-direction: column;
    text-align: center;
  }
}
</style>
