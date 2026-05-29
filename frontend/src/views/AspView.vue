<template>
  <div class="asp-page">
    <div class="page-header asp-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-users"></i>
        </div>
        <div>
          <h2 class="page-title">Personal ASP</h2>
          <p class="page-subtitle">Gestion del personal de seguridad</p>
        </div>
      </div>

      <Button type="button" @click="openCreateDialog">
        <i class="pi pi-plus button-icon"></i>
        Nuevo ASP
      </Button>
    </div>

    <Card class="panel-card filters-card">
      <template #content>
        <div class="filters-row">
          <div class="filter-group search-group">
            <label for="search">Buscar</label>
            <div class="search-field">
              <i class="pi pi-search search-icon"></i>
              <InputText
                id="search"
                v-model="search"
                placeholder="Buscar por nombre, CI..."
                class="search-input"
              />
            </div>
          </div>

          <div class="filter-group state-group">
            <label for="filterEstado">Estado</label>
            <Select
              id="filterEstado"
              v-model="filterEstado"
              :options="estadoOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Todos"
              class="state-select"
            />
          </div>

          <Button
            v-if="hasActiveFilters"
            class="clear-button"
            severity="secondary"
            text
            @click="clearFilters"
          >
            <i class="pi pi-times button-icon"></i>
            Limpiar
          </Button>
        </div>
      </template>
    </Card>

    <Card class="panel-card table-card">
      <template #content>
        <div v-if="isLoading" class="empty-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="asps.length === 0" class="empty-state">
          <i class="pi pi-users empty-icon"></i>
          <div class="empty-copy">
            <p class="empty-title">No hay personal registrado</p>
            <p class="empty-subtitle">{{ hasActiveFilters ? 'Intente con otros filtros' : 'Comience agregando un nuevo ASP' }}</p>
          </div>
        </div>

        <div v-else class="table-shell">
          <table class="asp-table">
            <thead>
              <tr>
                <th>CI</th>
                <th>Nombre</th>
                <th>Cargo</th>
                <th>Estado</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asp in asps" :key="asp.id">
                <td class="mono">{{ asp.ci }}</td>
                <td>
                  <div class="name-cell">
                    <span class="name-main">{{ asp.nombre }} {{ asp.apellidos }}</span>
                  </div>
                </td>
                <td>{{ getCargoNombre(asp.cargo_id) }}</td>
                <td>
                  <Tag :value="getEstadoLabel(asp.estado)" :severity="getEstadoSeverity(asp.estado)" />
                </td>
                <td class="actions-col">
                  <div class="actions">
                    <Button
                      icon="pi pi-eye"
                      size="small"
                      severity="info"
                      text
                      title="Ver datos completos"
                      aria-label="Ver datos completos"
                      @click="openInfoDialog(asp)"
                    />
                    <Button
                      icon="pi pi-pencil"
                      size="small"
                      severity="secondary"
                      text
                      title="Editar ASP"
                      aria-label="Editar ASP"
                      @click="openEditDialog(asp)"
                    />
                    <Button
                      icon="pi pi-sync"
                      size="small"
                      severity="warn"
                      text
                      :title="`Cambiar estado de ${asp.nombre}`"
                      :aria-label="`Cambiar estado de ${asp.nombre}`"
                      @click="openStateDialog(asp)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1" class="pagination-bar">
          <Button icon="pi pi-chevron-left" severity="secondary" text :disabled="currentPage === 1" @click="changePage(-1)" />
          <span>Página {{ currentPage }} de {{ totalPages }}</span>
          <Button icon="pi pi-chevron-right" severity="secondary" text :disabled="currentPage >= totalPages" @click="changePage(1)" />
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="isFormOpen" :header="editingASP ? 'Editar ASP' : 'Nuevo ASP'" modal :style="{ width: '860px' }">
      <form class="form-layout" @submit.prevent="handleSubmit">
        <Message v-if="Object.keys(formErrors).length" severity="error" :closable="false" class="form-message">
          Corrige los campos marcados antes de guardar.
        </Message>

        <section class="form-section">
          <div class="section-head">
            <h3>Datos principales</h3>
            <p>Identificación y relación laboral</p>
          </div>

          <div class="form-grid">
            <div class="field">
              <label for="ci">CI *</label>
              <InputText id="ci" v-model="formData.ci" :class="{ invalid: hasError('ci') }" maxlength="11" />
              <small v-if="hasError('ci')" class="field-error">{{ formErrors.ci }}</small>
            </div>

            <div class="field">
              <label for="cargo_id">Cargo *</label>
              <Select
                id="cargo_id"
                v-model="formData.cargo_id"
                :options="cargos"
                optionLabel="nombre"
                optionValue="id"
                placeholder="Seleccionar cargo"
                :class="{ invalid: hasError('cargo_id') }"
              />
              <small v-if="hasError('cargo_id')" class="field-error">{{ formErrors.cargo_id }}</small>
            </div>

            <div class="field">
              <label for="nombre">Nombre *</label>
              <InputText id="nombre" v-model="formData.nombre" :class="{ invalid: hasError('nombre') }" />
              <small v-if="hasError('nombre')" class="field-error">{{ formErrors.nombre }}</small>
            </div>

            <div class="field">
              <label for="apellidos">Apellidos *</label>
              <InputText id="apellidos" v-model="formData.apellidos" :class="{ invalid: hasError('apellidos') }" />
              <small v-if="hasError('apellidos')" class="field-error">{{ formErrors.apellidos }}</small>
            </div>

            <div class="field">
              <label for="fecha_nacimiento">Fecha de nacimiento *</label>
              <DatePicker
                id="fecha_nacimiento"
                v-model="formData.fecha_nacimiento"
                dateFormat="yy-mm-dd"
                showIcon
                :class="{ invalid: hasError('fecha_nacimiento') }"
              />
              <small v-if="hasError('fecha_nacimiento')" class="field-error">{{ formErrors.fecha_nacimiento }}</small>
            </div>

            <div class="field">
              <label for="fecha_ingreso">Fecha de ingreso *</label>
              <DatePicker
                id="fecha_ingreso"
                v-model="formData.fecha_ingreso"
                dateFormat="yy-mm-dd"
                showIcon
                :class="{ invalid: hasError('fecha_ingreso') }"
              />
              <small v-if="hasError('fecha_ingreso')" class="field-error">{{ formErrors.fecha_ingreso }}</small>
            </div>
          </div>
        </section>

        <section class="form-section">
          <div class="section-head">
            <h3>Datos complementarios</h3>
            <p>Información personal y de contacto</p>
          </div>

          <div class="form-grid">
            <div class="field">
              <label for="sexo">Sexo *</label>
              <Select
                id="sexo"
                v-model="formData.sexo"
                :options="sexoOptions"
                optionLabel="label"
                optionValue="value"
                :class="{ invalid: hasError('sexo') }"
              />
              <small v-if="hasError('sexo')" class="field-error">{{ formErrors.sexo }}</small>
            </div>

            <div class="field">
              <label for="nivel_escolaridad">Escolaridad *</label>
              <Select
                id="nivel_escolaridad"
                v-model="formData.nivel_escolaridad"
                :options="escolaridadOptions"
                optionLabel="label"
                optionValue="value"
                :class="{ invalid: hasError('nivel_escolaridad') }"
              />
              <small v-if="hasError('nivel_escolaridad')" class="field-error">{{ formErrors.nivel_escolaridad }}</small>
            </div>

            <div class="field">
              <label for="telefono">Telefono</label>
              <InputText id="telefono" v-model="formData.telefono" :class="{ invalid: hasError('telefono') }" />
              <small v-if="hasError('telefono')" class="field-error">{{ formErrors.telefono }}</small>
            </div>

            <div class="field">
              <label for="direccion">Direccion</label>
              <InputText id="direccion" v-model="formData.direccion" :class="{ invalid: hasError('direccion') }" />
              <small v-if="hasError('direccion')" class="field-error">{{ formErrors.direccion }}</small>
            </div>

            <div class="field span-2">
              <label for="observaciones">Observaciones</label>
              <Textarea id="observaciones" v-model="formData.observaciones" rows="3" autoResize />
            </div>
          </div>
        </section>

        <div class="dialog-footer">
          <Button type="button" label="Cancelar" severity="secondary" text @click="closeFormDialog" />
          <Button type="submit" :loading="isSaving" label="Guardar" icon="pi pi-check" />
        </div>
      </form>
    </Dialog>

    <Dialog
      v-model:visible="isInfoOpen"
      :header="`Ficha tecnica — ${aspDetail?.nombre || ''}`"
      modal
      :style="{ width: '720px' }"
      @hide="closeInfoDialog"
    >
      <div class="detail-layout">
        <Message v-if="infoError" severity="error" :closable="false" class="form-message">
          {{ infoError }}
        </Message>

        <div v-if="isLoadingInfo" class="empty-state compact-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="aspDetail" class="detail-grid">
          <div class="detail-card">
            <span class="detail-label">CI</span>
            <span class="detail-value mono">{{ aspDetail.ci }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Nombre</span>
            <span class="detail-value">{{ aspDetail.nombre }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Apellidos</span>
            <span class="detail-value">{{ aspDetail.apellidos }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Cargo</span>
            <span class="detail-value">{{ getCargoNombre(aspDetail.cargo_id) }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Fecha de nacimiento</span>
            <span class="detail-value">{{ formatDate(aspDetail.fecha_nacimiento) || '—' }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Fecha de ingreso</span>
            <span class="detail-value">{{ formatDate(aspDetail.fecha_ingreso) || '—' }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Sexo</span>
            <span class="detail-value">{{ aspDetail.sexo }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Escolaridad</span>
            <span class="detail-value">{{ aspDetail.nivel_escolaridad }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Telefono</span>
            <span class="detail-value">{{ aspDetail.telefono || '—' }}</span>
          </div>
          <div class="detail-card">
            <span class="detail-label">Estado</span>
            <Tag :value="getEstadoLabel(aspDetail.estado)" :severity="getEstadoSeverity(aspDetail.estado)" />
          </div>
          <div class="detail-card span-2">
            <span class="detail-label">Direccion</span>
            <span class="detail-value">{{ aspDetail.direccion || '—' }}</span>
          </div>
          <div class="detail-card span-2">
            <span class="detail-label">Observaciones</span>
            <span class="detail-value">{{ aspDetail.observaciones || '—' }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <Button type="button" label="Cerrar" severity="secondary" text @click="closeInfoDialog" />
      </template>
    </Dialog>

    <Dialog v-model:visible="isStateOpen" :header="`Cambiar estado — ${changingASP?.nombre || ''}`" modal :style="{ width: '420px' }">
      <div class="form-layout compact-layout">
        <Message v-if="stateError" severity="error" :closable="false" class="form-message">
          {{ stateError }}
        </Message>

        <div class="field">
          <label for="estado">Nuevo estado *</label>
          <Select
            id="estado"
            v-model="stateForm.estado"
            :options="stateOptions.filter((option) => option.value)"
            optionLabel="label"
            optionValue="value"
          />
        </div>

        <div class="field">
          <label for="observacion">Observacion</label>
          <Textarea id="observacion" v-model="stateForm.observacion" rows="3" autoResize />
        </div>

        <div class="dialog-footer">
          <Button type="button" label="Cancelar" severity="secondary" text @click="closeStateDialog" />
          <Button type="button" label="Confirmar" icon="pi pi-check" :loading="isChangingState" @click="saveState" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import DatePicker from 'primevue/datepicker'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { aspApi } from '../api/asp'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'

const toast = useToast()

const asps = ref([])
const cargos = ref([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)
const search = ref('')
const filterEstado = ref('')

const isFormOpen = ref(false)
const isStateOpen = ref(false)
const isInfoOpen = ref(false)
const editingASP = ref(null)
const changingASP = ref(null)
const aspDetail = ref(null)
const isLoadingInfo = ref(false)
const infoError = ref('')
const formErrors = ref({})
const formMessage = ref('')
const isSaving = ref(false)
const stateError = ref('')
const isChangingState = ref(false)

const estadoOptions = [
  { label: 'Todos', value: '' },
  { label: 'Activo', value: 'activo' },
  { label: 'Suspendido', value: 'suspendido' },
  { label: 'Baja temporal', value: 'baja_temporal' },
  { label: 'Baja definitiva', value: 'baja_definitiva' },
]

const stateOptions = [
  { label: 'Todos', value: '' },
  { label: 'Activo', value: 'activo' },
  { label: 'Suspendido', value: 'suspendido' },
  { label: 'Baja temporal', value: 'baja_temporal' },
  { label: 'Baja definitiva', value: 'baja_definitiva' },
]

const sexoOptions = [
  { label: 'Masculino', value: 'masculino' },
  { label: 'Femenino', value: 'femenino' },
]

const escolaridadOptions = [
  { label: 'Primaria', value: 'primaria' },
  { label: 'Secundaria', value: 'secundaria' },
  { label: 'Preuniversitario', value: 'preuniversitario' },
  { label: 'Tecnico medio', value: 'tecnico_medio' },
  { label: 'Universitario', value: 'universitario' },
]

const formData = reactive({
  ci: '',
  nombre: '',
  apellidos: '',
  fecha_nacimiento: null,
  sexo: 'masculino',
  nivel_escolaridad: 'tecnico_medio',
  telefono: '',
  direccion: '',
  fecha_ingreso: null,
  cargo_id: null,
  observaciones: '',
})

const stateForm = reactive({
  estado: 'activo',
  observacion: '',
})

const hasActiveFilters = computed(() => Boolean(search.value || filterEstado.value))

function hasError(field) {
  return Boolean(formErrors.value[field])
}

function getCargoNombre(id) {
  return cargos.value.find((cargo) => cargo.id === id)?.nombre || '—'
}

function getEstadoLabel(estado) {
  const labels = {
    activo: 'Activo',
    suspendido: 'Suspendido',
    baja_temporal: 'Baja temporal',
    baja_definitiva: 'Baja definitiva',
  }
  return labels[estado] || estado
}

function getEstadoSeverity(estado) {
  const severities = {
    activo: 'success',
    suspendido: 'warn',
    baja_temporal: 'warn',
    baja_definitiva: 'danger',
  }
  return severities[estado] || 'secondary'
}

function formatDate(value) {
  if (!value) return null
  if (typeof value === 'string') return value.split('T')[0]
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseDateOnly(value) {
  if (!value) return null
  if (value instanceof Date) return value
  if (typeof value !== 'string') return null
  const [year, month, day] = value.split('T')[0].split('-').map(Number)
  if (!year || !month || !day) return null
  return new Date(year, month - 1, day, 12, 0, 0)
}

function clearFormErrors() {
  formErrors.value = {}
  formMessage.value = ''
}

function resetForm() {
  formData.ci = ''
  formData.nombre = ''
  formData.apellidos = ''
  formData.fecha_nacimiento = null
  formData.sexo = 'masculino'
  formData.nivel_escolaridad = 'tecnico_medio'
  formData.telefono = ''
  formData.direccion = ''
  formData.fecha_ingreso = null
  formData.cargo_id = null
  formData.observaciones = ''
}

function openCreateDialog() {
  editingASP.value = null
  resetForm()
  clearFormErrors()
  isFormOpen.value = true
}

async function openEditDialog(asp) {
  editingASP.value = asp
  clearFormErrors()

  try {
    const response = await aspApi.obtener(asp.id)
    const item = response.data
    formData.ci = item.ci || ''
    formData.nombre = item.nombre || ''
    formData.apellidos = item.apellidos || ''
    formData.fecha_nacimiento = parseDateOnly(item.fecha_nacimiento)
    formData.sexo = item.sexo || 'masculino'
    formData.nivel_escolaridad = item.nivel_escolaridad || 'tecnico_medio'
    formData.telefono = item.telefono || ''
    formData.direccion = item.direccion || ''
    formData.fecha_ingreso = parseDateOnly(item.fecha_ingreso)
    formData.cargo_id = item.cargo_id || null
    formData.observaciones = item.observaciones || ''
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cargar ASP'), life: 3000 })
    editingASP.value = null
    return
  }

  isFormOpen.value = true
}

function closeFormDialog() {
  isFormOpen.value = false
  editingASP.value = null
  clearFormErrors()
}

function openStateDialog(asp) {
  changingASP.value = asp
  stateForm.estado = asp.estado
  stateForm.observacion = ''
  stateError.value = ''
  isStateOpen.value = true
}

async function openInfoDialog(asp) {
  infoError.value = ''
  aspDetail.value = null
  isLoadingInfo.value = true
  isInfoOpen.value = true

  try {
    const response = await aspApi.obtener(asp.id)
    aspDetail.value = response.data
  } catch (error) {
    infoError.value = normalizeApiError(error, 'Error al cargar informacion')
  } finally {
    isLoadingInfo.value = false
  }
}

function closeStateDialog() {
  isStateOpen.value = false
  changingASP.value = null
  stateError.value = ''
}

function closeInfoDialog() {
  isInfoOpen.value = false
  aspDetail.value = null
  infoError.value = ''
  isLoadingInfo.value = false
}

function validateForm() {
  const errors = {}

  if (!formData.ci || !/^\d{11}$/.test(formData.ci)) {
    errors.ci = 'El CI debe tener exactamente 11 digitos'
  }

  if (!formData.nombre || formData.nombre.trim().length < 2) {
    errors.nombre = 'Nombre requerido'
  }

  if (!formData.apellidos || formData.apellidos.trim().length < 2) {
    errors.apellidos = 'Apellidos requeridos'
  }

  if (!formData.fecha_nacimiento) {
    errors.fecha_nacimiento = 'Fecha de nacimiento requerida'
  } else {
    const birthDate = new Date(formatDate(formData.fecha_nacimiento))
    const today = new Date()
    const eighteenYearsAgo = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate())
    if (birthDate > eighteenYearsAgo) {
      errors.fecha_nacimiento = 'Debe ser mayor de 18 anos'
    }
  }

  if (!formData.fecha_ingreso) {
    errors.fecha_ingreso = 'Fecha de ingreso requerida'
  }

  if (!formData.sexo) {
    errors.sexo = 'Sexo requerido'
  }

  if (!formData.nivel_escolaridad) {
    errors.nivel_escolaridad = 'Escolaridad requerida'
  }

  if (!formData.cargo_id) {
    errors.cargo_id = 'Cargo requerido'
  }

  if (formData.telefono && !/^\d{8}$/.test(formData.telefono)) {
    errors.telefono = 'El telefono debe tener 8 digitos'
  }

  if (formData.direccion && formData.direccion.trim().length < 3) {
    errors.direccion = 'Direccion demasiado corta'
  }

  formErrors.value = errors
  return Object.keys(errors).length === 0
}

function buildPayload() {
  return {
    ci: formData.ci.trim(),
    nombre: formData.nombre.trim(),
    apellidos: formData.apellidos.trim(),
    fecha_nacimiento: formatDate(formData.fecha_nacimiento),
    sexo: formData.sexo,
    nivel_escolaridad: formData.nivel_escolaridad,
    telefono: formData.telefono.trim() || null,
    direccion: formData.direccion.trim() || null,
    fecha_ingreso: formatDate(formData.fecha_ingreso),
    cargo_id: formData.cargo_id,
    observaciones: formData.observaciones.trim() || null,
  }
}

async function handleSubmit() {
  if (!validateForm()) return

  isSaving.value = true
  try {
    const payload = buildPayload()

    if (editingASP.value) {
      await aspApi.actualizar(editingASP.value.id, payload)
      toast.add({ severity: 'success', summary: 'ASP actualizado', detail: 'El ASP se actualizo correctamente', life: 3000 })
    } else {
      await aspApi.crear(payload)
      toast.add({ severity: 'success', summary: 'ASP creado', detail: 'El ASP se creo correctamente', life: 3000 })
    }

    closeFormDialog()
    await fetchASPs()
  } catch (error) {
    const message = normalizeApiError(error, 'Error al guardar')
    const details = error?.response?.data?.errors

    if (details && typeof details === 'object') {
      const mappedErrors = {}
      Object.entries(details).forEach(([key, values]) => {
        mappedErrors[key] = Array.isArray(values) ? values[0] : String(values)
      })
      formErrors.value = mappedErrors
    } else {
      formMessage.value = message
      toast.add({ severity: 'error', summary: 'Error', detail: message, life: 3000 })
    }
  } finally {
    isSaving.value = false
  }
}

async function saveState() {
  if (!changingASP.value) return

  isChangingState.value = true
  stateError.value = ''

  try {
    await aspApi.cambiarEstado(changingASP.value.id, {
      estado: stateForm.estado,
      observacion: stateForm.observacion?.trim() || null,
    })

    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del ASP se actualizo', life: 3000 })
    closeStateDialog()
    await fetchASPs()
  } catch (error) {
    stateError.value = normalizeApiError(error, 'Error al cambiar estado')
  } finally {
    isChangingState.value = false
  }
}

async function fetchCargos() {
  try {
    const response = await cargoApi.listar(true)
    cargos.value = response.data || []
  } catch (error) {
    console.error(error)
  }
}

async function fetchASPs() {
  isLoading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: 20,
    }

    if (search.value.trim()) {
      params.buscar = search.value.trim()
    }

    if (filterEstado.value) {
      params.estado = filterEstado.value
    }

    const response = await aspApi.listar(params)
    asps.value = response.data.items || []
    total.value = response.data.total || 0
    totalPages.value = Math.max(1, Math.ceil(total.value / response.data.size))
  } catch (error) {
    console.error(error)
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cargar el personal'), life: 3000 })
  } finally {
    isLoading.value = false
  }
}

function changePage(delta) {
  const nextPage = currentPage.value + delta
  if (nextPage < 1 || nextPage > totalPages.value) return
  currentPage.value = nextPage
  fetchASPs()
}

function clearFilters() {
  search.value = ''
  filterEstado.value = ''
  currentPage.value = 1
  fetchASPs()
}

watch([search, filterEstado], () => {
  currentPage.value = 1
  fetchASPs()
})

onMounted(async () => {
  await fetchCargos()
  await fetchASPs()
})
</script>

<style scoped>
.asp-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.asp-header {
  align-items: center;
}

.page-title-block {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.page-title-icon {
  width: 2.625rem;
  height: 2.625rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-50);
  color: var(--brand-600);
  font-size: 1.25rem;
}

.page-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text);
}

.page-subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.button-icon {
  margin-right: 0.5rem;
}

.panel-card {
  border: 1px solid color-mix(in srgb, var(--border) 75%, transparent);
  box-shadow: 0 16px 50px rgba(15, 23, 42, 0.05);
}

.filters-row {
  display: flex;
  gap: 1rem;
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.search-group {
  flex: 1 1 280px;
}

.state-group {
  width: min(18rem, 100%);
}

.filter-group label,
.field label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.search-field {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.4rem;
}

.state-select {
  width: 100%;
}

.clear-button {
  align-self: end;
}

.table-shell {
  overflow-x: auto;
}

.asp-table {
  width: 100%;
  border-collapse: collapse;
}

.asp-table thead th {
  padding: 0.9rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
}

.asp-table tbody td {
  padding: 0.95rem 1rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  vertical-align: middle;
}

.asp-table tbody tr:hover {
  background: color-mix(in srgb, var(--surface) 86%, transparent);
}

.mono {
  font-variant-numeric: tabular-nums;
}

.name-main {
  display: block;
  font-weight: 600;
  color: var(--text);
}

.actions-col {
  width: 10rem;
  text-align: center;
}

.actions {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding-top: 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.empty-state {
  min-height: 16rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
}

.compact-state {
  min-height: 9rem;
}

.empty-icon {
  font-size: 2rem;
}

.empty-title {
  margin: 0;
  font-weight: 600;
  color: var(--text);
}

.empty-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
}

.spinner {
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 9999px;
  border: 3px solid var(--brand-500);
  border-top-color: transparent;
  animation: spin 0.85s linear infinite;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.compact-layout {
  gap: 1rem;
}

.form-message {
  margin-bottom: 0.25rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.section-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}

.section-head p {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field span,
.field :deep(.p-inputtext),
.field :deep(.p-select),
.field :deep(.p-datepicker) {
  width: 100%;
}

.field-error {
  color: #dc2626;
  font-size: 0.75rem;
}

.invalid :deep(.p-inputtext),
.invalid :deep(.p-select),
.invalid :deep(.p-datepicker-input) {
  border-color: #dc2626;
}

.span-2 {
  grid-column: span 2;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.25rem;
}

.detail-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.detail-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.9rem 1rem;
  border-radius: 0.9rem;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  background: color-mix(in srgb, var(--surface) 72%, transparent);
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.detail-value {
  color: var(--text);
  font-weight: 600;
  word-break: break-word;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .asp-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }
}

@media (max-width: 640px) {
  .filters-row {
    align-items: stretch;
  }

  .search-group,
  .state-group,
  .clear-button {
    width: 100%;
  }

  .page-title {
    font-size: 1.35rem;
  }

  .dialog-footer {
    flex-wrap: wrap;
  }

  .dialog-footer > * {
    flex: 1 1 140px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }
}
</style>
