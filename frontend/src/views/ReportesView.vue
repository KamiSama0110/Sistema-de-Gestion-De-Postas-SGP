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
          <Tag :value="reporteActual.label" severity="success" />
        </div>

        <div v-if="tipoReporte === 'cobertura'">
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
              <p class="summary-label">Total incidencias</p>
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
  { label: 'Incidencias', value: 'incidencias' },
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

const reporteDescripcion = computed(() => {
  const descripciones = {
    cobertura: 'Mide la cobertura por posta y el volumen de guardias completadas.',
    ausentismo: 'Resume ausencias por ASP y su nivel de justificacion.',
    horas: 'Compara la carga de guardias y las horas acumuladas por ASP.',
    incidencias: 'Lista los eventos relevantes ocurridos en el periodo seleccionado.',
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
