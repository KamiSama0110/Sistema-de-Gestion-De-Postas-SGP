<template>
  <div class="turnos-page">
    <div class="page-header turnos-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div>
          <h2 class="page-title">Turnos</h2>
          <p class="page-subtitle">Horarios de trabajo por posta</p>
        </div>
      </div>

      <div class="header-actions">
        <Button type="button" severity="secondary" outlined @click="openFilterDialog">
          <i class="pi pi-filter button-icon"></i>
          Filtro
        </Button>
        <Button type="button" severity="secondary" text :disabled="!hasActiveFilters" @click="clearFilters">
          <i class="pi pi-times button-icon"></i>
          Limpiar
        </Button>
        <Button type="button" @click="openCreateDialog">
          <i class="pi pi-plus button-icon"></i>
          Nuevo Turno
        </Button>
      </div>
    </div>

    <Card class="panel-card filters-card">
      <template #content>
        <div class="filters-top">
          <div class="filters-summary">
            <span class="filters-summary-label">Filtros actuales</span>
            <span v-if="!hasActiveFilters" class="muted">Sin filtros aplicados</span>
            <span v-else class="filters-summary-value">
              <Tag v-if="filterPosta" :value="filterPosta.label" severity="info" />
              <Tag v-if="filterActivo" :value="filterActivo === 'true' ? 'Activos' : 'Inactivos'" :severity="filterActivo === 'true' ? 'success' : 'secondary'" />
            </span>
          </div>

          <div class="filter-state-box">
            <label for="filterActivo">Estado</label>
            <Select id="filterActivo" v-model="filterActivo" :options="stateOptions" optionLabel="label" optionValue="value" placeholder="Todos" />
          </div>
        </div>
      </template>
    </Card>

    <Card class="panel-card table-card">
      <template #content>
        <div v-if="isLoading" class="empty-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="turnosFiltrados.length === 0" class="empty-state">
          <i class="pi pi-clock empty-icon"></i>
          <div>
            <p class="empty-title">No hay turnos registrados</p>
            <p class="empty-subtitle">Comience agregando un nuevo turno</p>
          </div>
        </div>

        <div v-else class="table-shell">
          <table class="turnos-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Posta</th>
                <th>Horario</th>
                <th>ASP</th>
                <th>Cruza medianoche</th>
                <th>Estado</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="turno in turnosFiltrados" :key="turno.id">
                <td><span class="name-main">{{ turno.nombre }}</span></td>
                <td><span class="cell-muted">{{ getPostaNombre(turno.posta_id) }}</span></td>
                <td class="mono">{{ formatTime(turno.hora_inicio) }} - {{ formatTime(turno.hora_fin) }}</td>
                <td>{{ turno.asp_requeridos }}</td>
                <td>
                  <Tag :value="turno.cruza_medianoche ? 'Si' : 'No'" :severity="turno.cruza_medianoche ? 'warn' : 'secondary'" />
                </td>
                <td>
                  <Tag :value="turno.activo ? 'Activo' : 'Inactivo'" :severity="turno.activo ? 'success' : 'secondary'" />
                </td>
                <td class="actions-col">
                  <div class="actions">
                    <Button type="button" icon="pi pi-pencil" size="small" severity="secondary" text title="Editar turno" aria-label="Editar turno" @click="openEditDialog(turno)" />
                    <Button
                      type="button"
                      :icon="turno.activo ? 'pi pi-times' : 'pi pi-check'"
                      size="small"
                      :severity="turno.activo ? 'danger' : 'success'"
                      text
                      :title="turno.activo ? 'Desactivar turno' : 'Activar turno'"
                      :aria-label="turno.activo ? 'Desactivar turno' : 'Activar turno'"
                      @click="toggleEstado(turno)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="isFilterDialogOpen" header="Filtrar turnos" modal :style="{ width: '920px' }">
      <div class="dialog-shell">
        <div class="section-head">
          <h3>Buscar posta</h3>
          <p>Filtra la lista y elige una posta para aplicar el filtro.</p>
        </div>

        <div class="filter-grid">
          <div class="field span-2">
            <label for="filterSearch">Buscar posta</label>
            <div class="search-inline">
              <div class="search-field search-field-flex">
                <i class="pi pi-search search-icon"></i>
                <InputText id="filterSearch" v-model="filterSearch" class="search-input" placeholder="Buscar por nombre de posta..." @keyup.enter="loadFilterPostas" />
              </div>
              <Button type="button" severity="secondary" outlined @click="loadFilterPostas">
                <i class="pi pi-search button-icon"></i>
                Buscar
              </Button>
            </div>
          </div>
        </div>

        <div class="selected-posta-banner">
          <span class="selected-posta-label">Posta seleccionada</span>
          <span v-if="filterDraftPosta" class="selected-posta-value">{{ filterDraftPosta.label }}</span>
          <span v-else class="muted">Todas</span>
        </div>

        <div class="results-shell">
          <table class="results-table">
            <thead>
              <tr>
                <th>Posta</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Turnos</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="posta in filterPostas" :key="posta.value" :class="{ selected: filterDraftPosta?.value === posta.value }">
                <td><span class="name-main">{{ posta.label }}</span></td>
                <td>{{ posta.tipo }}</td>
                <td><Tag :value="posta.activa ? 'Activa' : 'Inactiva'" :severity="posta.activa ? 'success' : 'secondary'" /></td>
                <td>{{ posta.total_turnos ?? 0 }}</td>
                <td class="actions-col">
                  <Button type="button" size="small" severity="secondary" text :label="filterDraftPosta?.value === posta.value ? 'Elegida' : 'Elegir'" @click="selectFilterPosta(posta)" />
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="filterPostas.length === 0" class="empty-state compact-empty">
            <i class="pi pi-search empty-icon"></i>
            <div>
              <p class="empty-title">No hay postas para mostrar</p>
              <p class="empty-subtitle">Prueba con otro criterio de búsqueda</p>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <Button type="button" label="Limpiar" severity="secondary" text @click="resetFilterDialog" />
          <div class="dialog-actions">
            <Button type="button" label="Cerrar" severity="secondary" outlined @click="closeFilterDialog" />
            <Button type="button" label="Aplicar" icon="pi pi-check" @click="applyFilters" />
          </div>
        </div>
      </div>
    </Dialog>

    <Dialog v-model:visible="isFormOpen" :header="editingTurno ? 'Editar Turno' : 'Nuevo Turno'" modal :style="{ width: '980px' }">
      <form class="wizard-layout" @submit.prevent="handlePrimaryAction">
        <Message v-if="formError" severity="error" :closable="false" class="form-message">{{ formError }}</Message>

        <div class="wizard-steps">
          <div v-for="step in steps" :key="step.id" class="wizard-step" :class="{ active: wizardStep === step.id, done: wizardStep > step.id }">
            <span class="wizard-step-index">{{ step.id }}</span>
            <div>
              <strong>{{ step.title }}</strong>
              <small>{{ step.description }}</small>
            </div>
          </div>
        </div>

        <section v-if="wizardStep === 1" class="form-section">
          <div class="section-head">
            <h3>Seleccionar posta</h3>
            <p>Busca la posta antes de continuar con el horario.</p>
          </div>

          <div v-if="editingTurno" class="selected-posta-card">
            <span class="selected-posta-label">Posta asignada</span>
            <strong>{{ form.posta?.label || 'No disponible' }}</strong>
            <p>La posta no se puede cambiar al editar.</p>
          </div>

          <template v-else>
            <div class="filter-grid">
              <div class="field span-2">
                <label for="wizardSearch">Buscar</label>
                <div class="search-inline">
                  <div class="search-field search-field-flex">
                    <i class="pi pi-search search-icon"></i>
                    <InputText id="wizardSearch" v-model="wizardSearch" class="search-input" placeholder="Buscar por nombre de posta..." @keyup.enter="loadWizardPostas" />
                  </div>
                  <Button type="button" severity="secondary" outlined @click="loadWizardPostas">
                    <i class="pi pi-search button-icon"></i>
                    Buscar
                  </Button>
                </div>
              </div>
            </div>

            <small v-if="fieldErrors.posta_id" class="field-error">{{ fieldErrors.posta_id }}</small>

            <div class="results-shell wizard-results-shell">
              <table class="results-table">
                <thead>
                  <tr>
                    <th>Posta</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Turnos</th>
                    <th class="actions-col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="posta in wizardPostas" :key="posta.value" :class="{ selected: form.posta?.value === posta.value }">
                    <td><span class="name-main">{{ posta.label }}</span></td>
                    <td>{{ posta.tipo }}</td>
                    <td><Tag :value="posta.activa ? 'Activa' : 'Inactiva'" :severity="posta.activa ? 'success' : 'secondary'" /></td>
                    <td>{{ posta.total_turnos ?? 0 }}</td>
                    <td class="actions-col">
                      <Button type="button" size="small" severity="secondary" text :label="form.posta?.value === posta.value ? 'Elegida' : 'Elegir'" @click="selectWizardPosta(posta)" />
                    </td>
                  </tr>
                </tbody>
              </table>

              <div v-if="wizardPostas.length === 0" class="empty-state compact-empty">
                <i class="pi pi-search empty-icon"></i>
                <div>
                  <p class="empty-title">No hay postas para mostrar</p>
                  <p class="empty-subtitle">Prueba con otro criterio de búsqueda</p>
                </div>
              </div>
            </div>
          </template>
        </section>

        <section v-else-if="wizardStep === 2" class="form-section">
          <div class="section-head">
            <h3>Horario</h3>
            <p>Define el tramo horario y la cantidad de ASP requeridos.</p>
          </div>

          <div class="form-grid">
            <div class="field">
              <label for="hora_inicio">Hora inicio *</label>
              <InputText id="hora_inicio" v-model="form.hora_inicio" type="time" :class="{ invalid: Boolean(fieldErrors.hora_inicio) }" />
              <small v-if="fieldErrors.hora_inicio" class="field-error">{{ fieldErrors.hora_inicio }}</small>
            </div>

            <div class="field">
              <label for="hora_fin">Hora fin *</label>
              <InputText id="hora_fin" v-model="form.hora_fin" type="time" :class="{ invalid: Boolean(fieldErrors.hora_fin) }" />
              <small v-if="fieldErrors.hora_fin" class="field-error">{{ fieldErrors.hora_fin }}</small>
            </div>

            <div class="field span-2">
              <label for="asp_requeridos">ASP requeridos *</label>
              <InputText id="asp_requeridos" v-model="form.asp_requeridos" type="number" min="1" :class="{ invalid: Boolean(fieldErrors.asp_requeridos) }" />
              <small v-if="fieldErrors.asp_requeridos" class="field-error">{{ fieldErrors.asp_requeridos }}</small>
            </div>
          </div>
        </section>

        <section v-else class="form-section">
          <div class="section-head">
            <h3>Datos finales</h3>
            <p>Completa el nombre, la descripción y el estado inicial.</p>
          </div>

          <div class="form-grid">
            <div class="field span-2">
              <label for="nombre">Nombre *</label>
              <InputText id="nombre" v-model="form.nombre" :class="{ invalid: Boolean(fieldErrors.nombre) }" placeholder="Turno Mañana" />
              <small v-if="fieldErrors.nombre" class="field-error">{{ fieldErrors.nombre }}</small>
            </div>

            <div class="field span-2">
              <label for="descripcion">Descripcion</label>
              <Textarea id="descripcion" v-model="form.descripcion" rows="4" autoResize placeholder="Descripcion del turno..." />
            </div>

            <div v-if="editingTurno" class="field span-2 checkbox-row">
              <input id="activo" v-model="form.activo" type="checkbox" />
              <label for="activo">Turno activo</label>
            </div>
          </div>
        </section>

        <div class="dialog-footer wizard-footer">
          <Button type="button" label="Cancelar" severity="secondary" text @click="closeFormDialog" />
          <div class="dialog-actions">
            <Button type="button" label="Volver" severity="secondary" outlined :disabled="wizardStep === 1" @click="previousStep" />
            <Button type="submit" :loading="isSaving" :label="wizardStep === steps.length ? (editingTurno ? 'Actualizar' : 'Crear') : 'Siguiente'" icon="pi pi-check" />
          </div>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { postaApi } from '../api/posta'
import { normalizeApiError } from '../utils/error'

const toast = useToast()
const route = useRoute()

const postas = ref([])
const isLoading = ref(true)
const isFormOpen = ref(false)
const isFilterDialogOpen = ref(false)
const editingTurno = ref(null)
const isSaving = ref(false)
const filterPosta = ref(null)
const filterActivo = ref('')
const filterDraftPosta = ref(null)
const filterSearch = ref('')
const filterPostas = ref([])
const wizardSearch = ref('')
const wizardPostas = ref([])
const wizardStep = ref(1)
const formError = ref('')
const fieldErrors = ref({})

const form = reactive({
  posta: null,
  nombre: '',
  hora_inicio: '',
  hora_fin: '',
  asp_requeridos: 1,
  descripcion: '',
  activo: true,
})

const steps = [
  { id: 1, title: 'Posta', description: 'Selecciona la posta' },
  { id: 2, title: 'Horario', description: 'Define el rango horario' },
  { id: 3, title: 'Datos', description: 'Completa el nombre y estado' },
]

const stateOptions = [
  { label: 'Todos', value: '' },
  { label: 'Activo', value: 'true' },
  { label: 'Inactivo', value: 'false' },
]

const hasActiveFilters = computed(() => Boolean(filterPosta.value || filterActivo.value))

function toPostaOption(posta) {
  return {
    label: posta.nombre,
    value: posta.id,
    tipo: posta.tipo,
    activa: posta.activa,
    total_turnos: Array.isArray(posta.turnos) ? posta.turnos.length : 0,
  }
}

function findPostaOptionById(id) {
  const posta = postas.value.find((item) => item.id === id)
  return posta ? toPostaOption(posta) : null
}

function syncPostaFromRoute() {
  const postaId = Number(route.query.posta)
  if (!Number.isFinite(postaId) || postaId <= 0) return
  const opcion = findPostaOptionById(postaId)
  if (opcion) {
    filterPosta.value = opcion
  }
}

function resetForm() {
  form.posta = null
  form.nombre = ''
  form.hora_inicio = ''
  form.hora_fin = ''
  form.asp_requeridos = 1
  form.descripcion = ''
  form.activo = true
  formError.value = ''
  fieldErrors.value = {}
  wizardStep.value = 1
}

async function loadPostasInto(target) {
  try {
    const params = {}
    const query = target === 'filter' ? filterSearch.value.trim() : wizardSearch.value.trim()
    if (query) params.buscar = query
    const response = await postaApi.listar(params)
    const items = (response.data || []).map(toPostaOption)
    if (target === 'filter') {
      filterPostas.value = items
    } else {
      wizardPostas.value = items
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cargar las postas'), life: 3000 })
  }
}

function loadFilterPostas() {
  return loadPostasInto('filter')
}

function loadWizardPostas() {
  return loadPostasInto('wizard')
}

async function openCreateDialog() {
  editingTurno.value = null
  resetForm()
  wizardSearch.value = ''
  isFormOpen.value = true
  await loadPostasInto('wizard')
}

function openEditDialog(turno) {
  editingTurno.value = turno
  form.posta = findPostaOptionById(turno.posta_id)
  form.nombre = turno.nombre || ''
  form.hora_inicio = formatTimeForInput(turno.hora_inicio)
  form.hora_fin = formatTimeForInput(turno.hora_fin)
  form.asp_requeridos = turno.asp_requeridos ?? 1
  form.descripcion = turno.descripcion || ''
  form.activo = turno.activo
  formError.value = ''
  fieldErrors.value = {}
  wizardStep.value = 1
  isFormOpen.value = true
}

function closeFormDialog() {
  isFormOpen.value = false
  editingTurno.value = null
  resetForm()
  wizardSearch.value = ''
  wizardPostas.value = []
}

function formatTime(value) {
  if (!value) return '—'
  return String(value).slice(0, 5)
}

function formatTimeForInput(value) {
  if (!value) return ''
  return String(value).slice(0, 5)
}

function getPostaNombre(postaId) {
  return postas.value.find((posta) => posta.id === postaId)?.nombre || '—'
}

function openFilterDialog() {
  filterDraftPosta.value = filterPosta.value
  filterSearch.value = ''
  isFilterDialogOpen.value = true
  loadPostasInto('filter')
}

function closeFilterDialog() {
  isFilterDialogOpen.value = false
}

function resetFilterDialog() {
  filterDraftPosta.value = null
  filterSearch.value = ''
  loadPostasInto('filter')
}

function selectFilterPosta(posta) {
  filterDraftPosta.value = posta
}

function applyFilters() {
  filterPosta.value = filterDraftPosta.value
  closeFilterDialog()
}

function clearFilters() {
  filterPosta.value = null
  filterActivo.value = ''
  filterDraftPosta.value = null
  filterSearch.value = ''
  filterPostas.value = []
}

function selectWizardPosta(posta) {
  form.posta = posta
  if (fieldErrors.value.posta_id) {
    const { posta_id, ...rest } = fieldErrors.value
    fieldErrors.value = rest
  }
}

function previousStep() {
  if (wizardStep.value > 1) wizardStep.value -= 1
}

function validateStep(step) {
  const errors = {}

  if (step === 1 && !editingTurno.value && !form.posta?.value) {
    errors.posta_id = 'Posta requerida'
  }
  if (step === 2) {
    if (!form.hora_inicio) errors.hora_inicio = 'Hora de inicio requerida'
    if (!form.hora_fin) errors.hora_fin = 'Hora de fin requerida'
    if (!form.asp_requeridos || Number(form.asp_requeridos) < 1) errors.asp_requeridos = 'Debe requerir al menos 1 ASP'
  }
  if (step === 3 && (!form.nombre || form.nombre.trim().length < 2)) {
    errors.nombre = 'Nombre es requerido (min. 2 caracteres)'
  }

  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

function validateAllSteps() {
  const errors = {}
  if (!editingTurno.value && !form.posta?.value) errors.posta_id = 'Posta requerida'
  if (!form.hora_inicio) errors.hora_inicio = 'Hora de inicio requerida'
  if (!form.hora_fin) errors.hora_fin = 'Hora de fin requerida'
  if (!form.asp_requeridos || Number(form.asp_requeridos) < 1) errors.asp_requeridos = 'Debe requerir al menos 1 ASP'
  if (!form.nombre || form.nombre.trim().length < 2) errors.nombre = 'Nombre es requerido (min. 2 caracteres)'
  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

function getPostaTurnos() {
  const items = []
  postas.value.forEach((posta) => {
    ;(posta.turnos || []).forEach((turno) => {
      items.push({ ...turno, posta_nombre: posta.nombre })
    })
  })
  return items
}

const turnosFiltrados = computed(() => {
  const selectedPostaId = filterPosta.value?.value || ''
  return getPostaTurnos().filter((turno) => {
    const matchPosta = !selectedPostaId || turno.posta_id === selectedPostaId
    const matchActivo = !filterActivo.value || String(turno.activo) === filterActivo.value
    return matchPosta && matchActivo
  })
})

async function fetchPostas() {
  try {
    const response = await postaApi.listar({})
    postas.value = response.data || []
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cargar los turnos'), life: 3000 })
  }
}

async function handlePrimaryAction() {
  if (wizardStep.value < steps.length) {
    if (validateStep(wizardStep.value)) wizardStep.value += 1
    return
  }
  await saveTurno()
}

function buildPayload() {
  return {
    nombre: form.nombre.trim(),
    hora_inicio: form.hora_inicio,
    hora_fin: form.hora_fin,
    asp_requeridos: Number(form.asp_requeridos),
  }
}

async function saveTurno() {
  if (!validateAllSteps()) return

  isSaving.value = true
  formError.value = ''

  try {
    const payload = buildPayload()
    if (editingTurno.value) {
      await postaApi.actualizarTurno(editingTurno.value.id, payload)
      toast.add({ severity: 'success', summary: 'Turno actualizado', detail: 'El turno se actualizo correctamente', life: 3000 })
    } else {
      await postaApi.agregarTurno(form.posta.value, payload)
      toast.add({ severity: 'success', summary: 'Turno creado', detail: 'El turno se creo correctamente', life: 3000 })
    }
    closeFormDialog()
    await fetchPostas()
  } catch (error) {
    const apiErrors = error?.response?.data?.errors
    if (apiErrors && typeof apiErrors === 'object') {
      const mapped = {}
      Object.entries(apiErrors).forEach(([key, values]) => {
        mapped[key] = Array.isArray(values) ? values[0] : String(values)
      })
      fieldErrors.value = mapped
    } else {
      formError.value = normalizeApiError(error, 'Error al guardar')
    }
  } finally {
    isSaving.value = false
  }
}

async function toggleEstado(turno) {
  try {
    await postaApi.cambiarEstadoTurno(turno.id, !turno.activo)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del turno se actualizo', life: 3000 })
    await fetchPostas()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cambiar estado'), life: 3000 })
  }
}

onMounted(async () => {
  await Promise.all([fetchPostas(), loadPostasInto('filter')])
  syncPostaFromRoute()
  isLoading.value = false
})

watch(
  () => route.query.posta,
  () => {
    syncPostaFromRoute()
  }
)
</script>

<style scoped>
.turnos-page { display: flex; flex-direction: column; gap: 1rem; }
.turnos-header { align-items: center; gap: 1rem; flex-wrap: wrap; }
.page-title-block { display: flex; align-items: center; gap: 0.875rem; }
.page-title-icon { width: 2.625rem; height: 2.625rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; background: var(--brand-50); color: var(--brand-600); font-size: 1.25rem; }
.page-title { margin: 0; font-size: 1.6rem; line-height: 1.2; font-weight: 700; color: var(--text); }
.page-subtitle { margin: 0.2rem 0 0; font-size: 0.875rem; color: var(--text-muted); }
.header-actions { display: flex; gap: 0.75rem; align-items: center; margin-left: auto; flex-wrap: wrap; }
.button-icon { margin-right: 0.5rem; }
.panel-card { border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); box-shadow: 0 16px 50px rgba(15, 23, 42, 0.05); }
.filters-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.filters-summary { display: flex; flex-direction: column; gap: 0.4rem; }
.filters-summary-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.filters-summary-value { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.muted { color: var(--text-muted); }
.filter-state-box { display: flex; flex-direction: column; gap: 0.35rem; min-width: 220px; }
.dialog-shell { display: flex; flex-direction: column; gap: 1rem; }
.section-head h3 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--text); }
.section-head p { margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-muted); }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.search-inline { display: flex; align-items: center; gap: 0.75rem; }
.search-field-flex { flex: 1 1 auto; }
.search-field { position: relative; }
.search-icon { position: absolute; left: 0.9rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.search-input { width: 100%; padding-left: 2.4rem; }
.search-inline .p-button { flex: 0 0 auto; }
.filter-grid, .form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem 1rem; }
.span-2 { grid-column: span 2; }
.selected-posta-banner, .selected-posta-card { border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); background: color-mix(in srgb, var(--surface) 92%, transparent); border-radius: 1rem; padding: 0.9rem 1rem; }
.selected-posta-card { display: flex; flex-direction: column; gap: 0.35rem; }
.selected-posta-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); }
.selected-posta-value { font-size: 0.95rem; font-weight: 600; color: var(--text); }
.selected-posta-card p { margin: 0; color: var(--text-muted); font-size: 0.85rem; }
.wizard-layout { display: flex; flex-direction: column; gap: 1rem; }
.wizard-steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; }
.wizard-step { display: flex; align-items: center; gap: 0.75rem; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); border-radius: 1rem; padding: 0.85rem 1rem; background: color-mix(in srgb, var(--surface) 92%, transparent); }
.wizard-step.active { border-color: color-mix(in srgb, var(--brand-500) 35%, var(--border)); background: color-mix(in srgb, var(--brand-50) 50%, var(--surface)); }
.wizard-step.done { border-color: color-mix(in srgb, var(--brand-500) 22%, var(--border)); }
.wizard-step-index { width: 2rem; height: 2rem; border-radius: 9999px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; background: var(--brand-50); color: var(--brand-600); flex: 0 0 auto; }
.wizard-step strong { display: block; font-size: 0.95rem; color: var(--text); }
.wizard-step small { display: block; margin-top: 0.15rem; color: var(--text-muted); }
.results-shell { overflow: hidden; border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); border-radius: 1rem; }
.wizard-results-shell { max-height: 320px; overflow: auto; }
.results-table { width: 100%; border-collapse: collapse; }
.results-table thead th { padding: 0.85rem 1rem; text-align: left; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent); background: color-mix(in srgb, var(--surface) 95%, transparent); }
.results-table tbody td { padding: 0.9rem 1rem; border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent); vertical-align: middle; }
.results-table tbody tr:hover, .results-table tbody tr.selected { background: color-mix(in srgb, var(--brand-50) 42%, var(--surface)); }
.empty-state { min-height: 16rem; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.75rem; color: var(--text-muted); }
.compact-empty { min-height: 10rem; }
.empty-icon { font-size: 2rem; }
.empty-title { margin: 0; font-weight: 600; color: var(--text); }
.empty-subtitle { margin: 0.25rem 0 0; font-size: 0.875rem; }
.spinner { width: 1.8rem; height: 1.8rem; border-radius: 9999px; border: 3px solid var(--brand-500); border-top-color: transparent; animation: spin 0.85s linear infinite; }
.form-section { display: flex; flex-direction: column; gap: 0.85rem; }
.field-error { font-size: 0.75rem; color: #dc2626; }
.invalid :deep(.p-inputtext), .invalid :deep(.p-select), .invalid :deep(.p-datepicker-input) { border-color: #dc2626; }
.checkbox-row { display: flex; align-items: center; gap: 0.55rem; }
.dialog-footer { display: flex; justify-content: space-between; gap: 0.75rem; padding-top: 0.25rem; align-items: center; }
.dialog-actions { display: flex; gap: 0.75rem; align-items: center; }
.actions-col { width: 9rem; text-align: center; }
.actions { display: flex; justify-content: center; gap: 0.25rem; }
.name-main { display: block; font-weight: 600; color: var(--text); }
.cell-muted { color: var(--text-muted); }
.mono { font-variant-numeric: tabular-nums; }
.table-shell { overflow-x: auto; }
.turnos-table { width: 100%; border-collapse: collapse; }
.turnos-table thead th { padding: 0.9rem 1rem; text-align: left; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent); }
.turnos-table tbody td { padding: 0.95rem 1rem; border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent); vertical-align: middle; }
.turnos-table tbody tr:hover { background: color-mix(in srgb, var(--surface) 86%, transparent); }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 960px) {
  .turnos-header { align-items: flex-start; }
  .header-actions { margin-left: 0; width: 100%; }
  .filters-top { align-items: stretch; }
  .filter-state-box { min-width: 0; width: 100%; }
  .filter-grid, .form-grid, .wizard-steps { grid-template-columns: 1fr; }
  .span-2 { grid-column: auto; }
  .search-inline { flex-direction: column; align-items: stretch; }
  .search-inline > * { width: 100%; }
}
@media (max-width: 640px) {
  .header-actions, .dialog-actions { width: 100%; flex-direction: column; }
  .header-actions > *, .dialog-actions > * { width: 100%; }
  .page-title { font-size: 1.35rem; }
  .dialog-footer { flex-wrap: wrap; }
  .dialog-footer > * { flex: 1 1 160px; }
}
</style>
