<template>
	<div>
		<div class="page-header">
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

		<Card style="margin-bottom: 16px">
			<template #content>
				<div class="filtros">
					<Select
						v-model="tipoReporte"
						:options="opcionesReporte"
						optionLabel="label"
						optionValue="value"
						placeholder="Tipo de reporte"
						style="min-width: 240px"
					/>
					<DatePicker v-model="filtros.fecha_desde" dateFormat="yy-mm-dd" showIcon placeholder="Desde" />
					<DatePicker v-model="filtros.fecha_hasta" dateFormat="yy-mm-dd" showIcon placeholder="Hasta" />
					<Select
						v-if="tipoReporte === 'incidencias'"
						v-model="filtros.severidad"
						:options="opcionesSeveridad"
						optionLabel="label"
						optionValue="value"
						placeholder="Severidad"
						style="width: 180px"
					/>
					<Select
						v-if="tipoReporte === 'incidencias'"
						v-model="filtros.posta_id"
						:options="opcionesPosta"
						optionLabel="label"
						optionValue="value"
						placeholder="Posta"
						style="min-width: 200px"
					/>
					<Select
						v-if="tipoReporte === 'tardanzas'"
						v-model="filtros.asp_id"
						:options="opcionesAsp"
						optionLabel="label"
						optionValue="value"
						placeholder="ASP"
						style="min-width: 220px"
					/>
					<Button label="Generar" icon="pi pi-search" :loading="cargando" @click="generarReporte" />
				</div>
			</template>
		</Card>

		<Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
			{{ error }}
		</Message>

		<Card v-if="reporte">
			<template #content>
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
					<DataTable :value="reporte.por_posta" size="small" stripedRows>
						<Column field="posta_nombre" header="Posta" />
						<Column field="planificadas" header="Planificadas" />
						<Column field="finalizadas" header="Finalizadas" />
						<Column field="ausentes" header="Ausentes" />
						<Column field="porcentaje_cobertura" header="Cobertura %" />
					</DataTable>
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
					<DataTable :value="reporte.por_asp" size="small" stripedRows>
						<Column field="asp_nombre" header="ASP" />
						<Column field="total_ausencias" header="Ausencias" />
						<Column field="justificadas" header="Justificadas" />
						<Column field="injustificadas" header="Injustificadas" />
					</DataTable>
				</div>

				<div v-else-if="tipoReporte === 'horas'">
					<DataTable :value="reporte.por_asp" size="small" stripedRows>
						<Column field="asp_nombre" header="ASP" />
						<Column field="total_guardias" header="Guardias" />
						<Column field="total_horas" header="Horas" />
					</DataTable>
				</div>

				<div v-else-if="tipoReporte === 'incidencias'">
					<div class="summary-grid">
						<div class="summary-card">
							<p class="summary-label">Total incidencias</p>
							<h3>{{ reporte.total_incidencias }}</h3>
						</div>
					</div>
					<DataTable :value="reporte.items" size="small" stripedRows>
						<Column field="fecha" header="Fecha" />
						<Column field="posta_nombre" header="Posta" />
						<Column field="asp_nombre" header="ASP" />
						<Column field="tipo" header="Tipo" />
						<Column field="severidad" header="Severidad" />
						<Column field="descripcion" header="Descripcion" />
					</DataTable>
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
					<DataTable :value="reporte.por_asp" size="small" stripedRows>
						<Column field="asp_nombre" header="ASP" />
						<Column field="total_tardanzas" header="Tardanzas" />
						<Column field="promedio_minutos" header="Promedio" />
						<Column field="max_minutos" header="Max" />
					</DataTable>
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
.filtros {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	align-items: center;
}
.summary-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
	gap: 12px;
	margin-bottom: 16px;
}
.summary-card {
	border: 1px solid var(--border);
	border-radius: 10px;
	padding: 12px;
	background: var(--surface-2);
}
.summary-label {
	margin: 0;
	color: var(--text-muted);
	font-size: 12px;
}
.summary-card h3 {
	margin: 6px 0 0;
	font-size: 20px;
}

@media (max-width: 960px) {
	.filtros {
		flex-direction: column;
		align-items: stretch;
	}

	.filtros :deep(.p-select),
	.filtros :deep(.p-datepicker),
	.filtros :deep(.p-button) {
		width: 100%;
	}
}

@media (max-width: 640px) {
	.summary-grid {
		grid-template-columns: 1fr;
	}
}
</style>
