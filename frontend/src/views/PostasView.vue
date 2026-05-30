<template>
  <div class="postas-page">
    <div class="page-header postas-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-building"></i>
        </div>
        <div>
          <h2 class="page-title">Postas</h2>
          <p class="page-subtitle">Ubicaciones de vigilancia</p>
        </div>
      </div>

      <Button type="button" @click="abrirModal()">
        <i class="pi pi-plus button-icon"></i>
        Nueva Posta
      </Button>
    </div>

    <Card class="panel-card filters-card">
      <template #content>
        <div class="filters-row">
          <div class="filter-group search-group">
            <label for="search">Buscar</label>
            <div class="search-field">
              <i class="pi pi-search search-icon"></i>
              <InputText id="search" v-model="search" placeholder="Buscar por nombre, ubicación o descripción..." class="search-input" />
            </div>
          </div>

          <div class="filter-group state-group">
            <label for="filterEstado">Estado</label>
            <Select id="filterEstado" v-model="filterEstado" :options="estadoOptions" optionLabel="label" optionValue="value" placeholder="Todos" class="state-select" />
          </div>

          <Button v-if="hasActiveFilters" class="clear-button" severity="secondary" text @click="clearFilters">
            <i class="pi pi-times button-icon"></i>
            Limpiar
          </Button>
        </div>
      </template>
    </Card>

    <Card class="panel-card table-card">
      <template #content>
        <div v-if="cargando" class="empty-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="postas.length === 0" class="empty-state">
          <i class="pi pi-building empty-icon"></i>
          <div class="empty-copy">
            <p class="empty-title">No hay postas registradas</p>
            <p class="empty-subtitle">Comience agregando una nueva posta</p>
          </div>
        </div>

        <div v-else class="table-shell">
          <table class="postas-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Ubicacion</th>
                <th>Descripcion</th>
                <th>Estado</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="posta in postasFiltradas" :key="posta.id">
                <td class="name-cell">
                  <span class="name-main">{{ posta.nombre }}</span>
                </td>
                <td>
                  <Tag :value="labelTipo(posta.tipo)" severity="secondary" />
                </td>
                <td class="location-cell">{{ posta.ubicacion || '—' }}</td>
                <td class="description-cell">{{ posta.descripcion || '—' }}</td>
                <td>
                  <Tag :value="posta.activa ? 'Activa' : 'Inactiva'" :severity="posta.activa ? 'success' : 'secondary'" />
                </td>
                <td class="actions-col">
                  <div class="actions">
                    <Button
                      type="button"
                      icon="pi pi-pencil"
                      size="small"
                      severity="secondary"
                      text
                      title="Editar posta"
                      aria-label="Editar posta"
                      @click="abrirModal(posta)"
                    />
                    <Button
                      type="button"
                      icon="pi pi-clock"
                      size="small"
                      severity="info"
                      text
                      title="Ver turnos"
                      aria-label="Ver turnos"
                      @click="irATurnos(posta)"
                    />
                    <Button
                      type="button"
                      :icon="posta.activa ? 'pi pi-times' : 'pi pi-check'"
                      size="small"
                      :severity="posta.activa ? 'danger' : 'success'"
                      text
                      :title="posta.activa ? 'Desactivar posta' : 'Activar posta'"
                      :aria-label="posta.activa ? 'Desactivar posta' : 'Activar posta'"
                      @click="toggleEstado(posta)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar Posta' : 'Nueva Posta'" modal :style="{ width: '620px' }">
      <form class="form-layout" @submit.prevent="guardar">
        <Message v-if="formError" severity="error" :closable="false" class="form-message">
          {{ formError }}
        </Message>

        <section class="form-section">
          <div class="section-head">
            <h3>Datos de la posta</h3>
            <p>Nombre, tipo y ubicación de la posta.</p>
          </div>

          <div class="form-grid">
            <div class="field">
              <label for="nombre">Nombre *</label>
              <InputText id="nombre" v-model="form.nombre" :class="{ invalid: Boolean(fieldErrors.nombre) }" placeholder="Posta Central" />
              <small v-if="fieldErrors.nombre" class="field-error">{{ fieldErrors.nombre }}</small>
            </div>

            <div class="field">
              <label for="tipo">Tipo *</label>
              <Select id="tipo" v-model="form.tipo" :options="tipos" optionLabel="label" optionValue="value" placeholder="Seleccione un tipo" :class="{ invalid: Boolean(fieldErrors.tipo) }" />
              <small v-if="fieldErrors.tipo" class="field-error">{{ fieldErrors.tipo }}</small>
            </div>

            <div class="field span-2">
              <label for="ubicacion">Ubicacion</label>
              <InputText id="ubicacion" v-model="form.ubicacion" :class="{ invalid: Boolean(fieldErrors.ubicacion) }" placeholder="Av. Principal #123" />
              <small v-if="fieldErrors.ubicacion" class="field-error">{{ fieldErrors.ubicacion }}</small>
            </div>

            <div class="field span-2">
              <label for="descripcion">Descripcion</label>
              <Textarea id="descripcion" v-model="form.descripcion" rows="3" autoResize :class="{ invalid: Boolean(fieldErrors.descripcion) }" placeholder="Descripcion de la posta..." />
              <small v-if="fieldErrors.descripcion" class="field-error">{{ fieldErrors.descripcion }}</small>
            </div>
          </div>
        </section>
      </form>

      <template #footer>
          <div class="dialog-footer">
            <Button type="button" label="Cancelar" severity="secondary" text @click="cerrarModal" />
            <Button type="submit" :loading="guardando" label="Guardar" icon="pi pi-check" @click="guardar" />
          </div>
        </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { postaApi } from '../api/posta'
import { normalizeApiError } from '../utils/error'

const router = useRouter()
const toast = useToast()

const postas = ref([])
const cargando = ref(true)
const modalVisible = ref(false)
const editando = ref(null)
const guardando = ref(false)
const formError = ref('')
const fieldErrors = ref({})
const search = ref('')
const filterEstado = ref('')

const estadoOptions = [
  { label: 'Activas', value: 'true' },
  { label: 'Inactivas', value: 'false' },
]

const tipos = [
  { label: 'Interior', value: 'interior' },
  { label: 'Perimetral', value: 'perimetral' },
  { label: 'Movil', value: 'movil' },
  { label: 'Punto critico', value: 'punto_critico' },
]

const formVacio = () => ({
  nombre: '',
  tipo: 'interior',
  ubicacion: '',
  descripcion: '',
})

const form = ref(formVacio())

const postasFiltradas = computed(() => {
  const query = search.value.trim().toLowerCase()

  return postas.value.filter((posta) => {
    const matchesSearch =
      !query ||
      [posta.nombre, posta.ubicacion, posta.descripcion, labelTipo(posta.tipo)]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))

    const matchesEstado =
      !filterEstado.value || String(posta.activa) === filterEstado.value

    return matchesSearch && matchesEstado
  })
})

const hasActiveFilters = computed(() => Boolean(search.value.trim() || filterEstado.value))

function clearFilters() {
  search.value = ''
  filterEstado.value = ''
}

function labelTipo(tipo) {
  return tipos.find((opcion) => opcion.value === tipo)?.label || '—'
}

function irATurnos(posta) {
  router.push({ name: 'turnos', query: { posta: String(posta.id) } })
}

async function cargarPostas() {
  cargando.value = true
  try {
    const res = await postaApi.listar()
    postas.value = res.data
  } catch (e) {
    console.error(e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las postas', life: 3000 })
  } finally {
    cargando.value = false
  }
}

function abrirModal(posta = null) {
  editando.value = posta
  form.value = posta
    ? {
        nombre: posta.nombre ?? '',
        tipo: posta.tipo ?? 'interior',
        ubicacion: posta.ubicacion ?? '',
        descripcion: posta.descripcion ?? '',
      }
    : formVacio()
  formError.value = ''
  fieldErrors.value = {}
  modalVisible.value = true
}

function cerrarModal() {
  modalVisible.value = false
  editando.value = null
}

async function guardar() {
  formError.value = ''
  fieldErrors.value = {}
  guardando.value = true

  try {
    if (!form.value.nombre?.trim()) {
      fieldErrors.value.nombre = 'Nombre es requerido'
      return
    }

    if (!form.value.tipo) {
      fieldErrors.value.tipo = 'Tipo es requerido'
      return
    }

    const payload = {
      nombre: form.value.nombre.trim(),
      tipo: form.value.tipo,
      ubicacion: form.value.ubicacion?.trim() || null,
      descripcion: form.value.descripcion?.trim() || null,
    }

    if (editando.value) {
      await postaApi.actualizar(editando.value.id, payload)
      toast.add({ severity: 'success', summary: 'Posta actualizada', detail: 'La posta se actualizo correctamente', life: 3000 })
    } else {
      await postaApi.crear(payload)
      toast.add({ severity: 'success', summary: 'Posta creada', detail: 'La posta se creo correctamente', life: 3000 })
    }

    cerrarModal()
    await cargarPostas()
  } catch (e) {
    const apiError = e?.errors
    if (apiError) {
      fieldErrors.value = Object.fromEntries(
        Object.entries(apiError).map(([key, messages]) => [key, Array.isArray(messages) ? messages[0] : String(messages)]),
      )
      formError.value = 'Revisa los campos marcados'
      return
    }

    formError.value = normalizeApiError(e, 'Error al guardar')
  } finally {
    guardando.value = false
  }
}

async function toggleEstado(posta) {
  try {
    await postaApi.cambiarEstado(posta.id, !posta.activa)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado de la posta se actualizo', life: 3000 })
    await cargarPostas()
  } catch (e) {
    console.error(e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estado', life: 3000 })
  }
}

onMounted(cargarPostas)
</script>

<style scoped>
.postas-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  --bg: #f3f6fb;
  --surface: #ffffff;
  --surface-2: #eef2f7;
  --border: #e2e8f0;
  --text: #0f172a;
  --text-muted: #64748b;
  background: linear-gradient(180deg, #f8fbff 0%, #f3f6fb 100%);
}

.postas-header { align-items: center; gap: 1rem; flex-wrap: wrap; }
.page-title-block { display: flex; align-items: center; gap: 0.875rem; min-width: 0; }
.page-title-icon { width: 2.625rem; height: 2.625rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; background: var(--brand-50); color: var(--brand-600); font-size: 1.25rem; flex-shrink: 0; }
.page-title-icon :deep(i) { color: inherit; }
.page-title { margin: 0; font-size: 1.6rem; line-height: 1.2; font-weight: 700; color: var(--text); }
.page-subtitle { margin: 0.2rem 0 0; font-size: 0.875rem; color: var(--text-muted); }
.button-icon { margin-right: 0.5rem; }
.panel-card { border: 1px solid color-mix(in srgb, var(--border) 75%, transparent); box-shadow: 0 16px 50px rgba(15, 23, 42, 0.05); }
.filters-row { display: flex; gap: 0.75rem; align-items: flex-end; flex-wrap: wrap; }
.filter-group { display: flex; flex-direction: column; gap: 0.35rem; }
.filter-group label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.search-group { flex: 1 1 320px; }
.state-group { min-width: 200px; }
.search-field { position: relative; }
.search-icon { position: absolute; left: 0.9rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.search-input { width: 100%; padding-left: 2.4rem; }
.state-select { width: 100%; }
.clear-button { margin-left: auto; }
.table-shell { overflow-x: auto; }
.postas-table { width: 100%; border-collapse: collapse; }
.postas-table thead th { padding: 0.9rem 1rem; text-align: left; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent); }
.postas-table tbody td { padding: 0.95rem 1rem; border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent); vertical-align: middle; }
.postas-table tbody tr:hover { background: color-mix(in srgb, var(--surface) 86%, transparent); }
.name-cell { min-width: 14rem; }
.name-main { display: block; font-weight: 600; color: var(--text); }
.location-cell, .description-cell { color: var(--text-muted); }
.description-cell { max-width: 24rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.actions-col { width: 9rem; text-align: center; }
.actions { display: flex; justify-content: center; gap: 0.25rem; }
.empty-state { min-height: 16rem; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.75rem; color: var(--text-muted); }
.empty-icon { font-size: 2rem; color: var(--brand-500); }
.empty-copy { text-align: center; }
.empty-title { margin: 0; font-weight: 600; color: var(--text); }
.empty-subtitle { margin: 0.25rem 0 0; font-size: 0.875rem; }
.spinner { width: 1.8rem; height: 1.8rem; border-radius: 9999px; border: 3px solid var(--brand-500); border-top-color: transparent; animation: spin 0.85s linear infinite; }
.form-layout { display: flex; flex-direction: column; gap: 1rem; }
.form-message { margin-bottom: 0.25rem; }
.form-section { display: flex; flex-direction: column; gap: 0.85rem; }
.section-head h3 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--text); }
.section-head p { margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-muted); }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem 1rem; }
.span-2 { grid-column: span 2; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
.field-error { color: #dc2626; font-size: 0.75rem; }
.invalid :deep(.p-inputtext), .invalid :deep(.p-select), .invalid :deep(.p-textarea) { border-color: #dc2626; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.25rem; }

.postas-page :deep(.p-inputtext),
.postas-page :deep(.p-select),
.postas-page :deep(.p-textarea) {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border);
}

.postas-page :deep(.p-inputtext::placeholder),
.postas-page :deep(.p-textarea::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 80%, transparent);
}

.postas-page :deep(.p-select-label) {
  color: var(--text);
}

.postas-page :deep(.p-dialog) {
  color: var(--text);
}

.postas-page :deep(.p-dialog .p-dialog-header),
.postas-page :deep(.p-dialog .p-dialog-content),
.postas-page :deep(.p-dialog .p-dialog-footer) {
  background: var(--surface);
  color: var(--text);
}

.postas-page :deep(.p-dialog) {
  border: 1px solid var(--border);
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.12);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 960px) {
  .postas-header { align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
  .span-2 { grid-column: auto; }
}

@media (max-width: 640px) {
  .page-title { font-size: 1.35rem; }
  .dialog-footer { flex-wrap: wrap; }
  .dialog-footer > * { flex: 1 1 140px; }
  .actions { justify-content: flex-start; }
}
</style>
