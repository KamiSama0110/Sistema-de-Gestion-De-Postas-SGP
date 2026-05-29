<template>
  <div class="cargo-page">
    <div class="page-header cargo-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-id-card"></i>
        </div>
        <div>
          <h2 class="page-title">Cargos</h2>
          <p class="page-subtitle">Catalogo de cargos del personal</p>
        </div>
      </div>

      <Button type="button" @click="openCreateDialog">
        <i class="pi pi-plus button-icon"></i>
        Nuevo Cargo
      </Button>
    </div>

    <Card class="panel-card table-card">
      <template #content>
        <div v-if="isLoading" class="empty-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>

        <div v-else-if="cargos.length === 0" class="empty-state">
          <i class="pi pi-file-empty empty-icon"></i>
          <div class="empty-copy">
            <p class="empty-title">No hay cargos registrados</p>
            <p class="empty-subtitle">Comience agregando un nuevo cargo</p>
          </div>
        </div>

        <div v-else class="table-shell">
          <table class="cargo-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripcion</th>
                <th>Estado</th>
                <th class="actions-col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cargo in cargos" :key="cargo.id">
                <td class="name-cell">
                  <span class="name-main">{{ cargo.nombre }}</span>
                </td>
                <td class="description-cell">{{ cargo.descripcion || '—' }}</td>
                <td>
                  <Tag :value="cargo.activo ? 'Activo' : 'Inactivo'" :severity="cargo.activo ? 'success' : 'secondary'" />
                </td>
                <td class="actions-col">
                  <div class="actions">
                    <Button
                      type="button"
                      icon="pi pi-pencil"
                      size="small"
                      severity="secondary"
                      text
                      title="Editar cargo"
                      aria-label="Editar cargo"
                      @click="openEditDialog(cargo)"
                    />
                    <Button
                      type="button"
                      :icon="cargo.activo ? 'pi pi-times' : 'pi pi-check'"
                      size="small"
                      :severity="cargo.activo ? 'danger' : 'success'"
                      text
                      :title="cargo.activo ? 'Desactivar cargo' : 'Activar cargo'"
                      :aria-label="cargo.activo ? 'Desactivar cargo' : 'Activar cargo'"
                      @click="toggleState(cargo)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="isFormOpen" :header="editingCargo ? 'Editar Cargo' : 'Nuevo Cargo'" modal :style="{ width: '460px' }">
      <form class="form-layout" @submit.prevent="handleSubmit">
        <Message v-if="formError" severity="error" :closable="false" class="form-message">
          {{ formError }}
        </Message>

        <div class="field">
          <label for="nombre">Nombre *</label>
          <InputText id="nombre" v-model="form.nombre" :class="{ invalid: Boolean(fieldErrors.nombre) }" placeholder="Vigilante" />
          <small v-if="fieldErrors.nombre" class="field-error">{{ fieldErrors.nombre }}</small>
        </div>

        <div class="field">
          <label for="descripcion">Descripcion</label>
          <Textarea id="descripcion" v-model="form.descripcion" rows="4" autoResize placeholder="Descripcion del cargo..." />
        </div>

        <div class="dialog-footer">
          <Button type="button" label="Cancelar" severity="secondary" text @click="closeFormDialog" />
          <Button type="submit" :loading="isSaving" :label="editingCargo ? 'Actualizar' : 'Crear'" icon="pi pi-check" />
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'

const toast = useToast()

const cargos = ref([])
const isLoading = ref(true)
const isFormOpen = ref(false)
const editingCargo = ref(null)
const isSaving = ref(false)
const formError = ref('')
const fieldErrors = ref({})

const form = reactive({
  nombre: '',
  descripcion: '',
})

function resetForm() {
  form.nombre = ''
  form.descripcion = ''
  formError.value = ''
  fieldErrors.value = {}
}

function openCreateDialog() {
  editingCargo.value = null
  resetForm()
  isFormOpen.value = true
}

function openEditDialog(cargo) {
  editingCargo.value = cargo
  form.nombre = cargo.nombre || ''
  form.descripcion = cargo.descripcion || ''
  formError.value = ''
  fieldErrors.value = {}
  isFormOpen.value = true
}

function closeFormDialog() {
  isFormOpen.value = false
  editingCargo.value = null
  resetForm()
}

function validateForm() {
  const errors = {}

  if (!form.nombre || form.nombre.trim().length < 2) {
    errors.nombre = 'Nombre es requerido (min. 2 caracteres)'
  }

  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

async function fetchCargos() {
  isLoading.value = true
  try {
    const response = await cargoApi.listar(false)
    cargos.value = response.data || []
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cargar los cargos'), life: 3000 })
  } finally {
    isLoading.value = false
  }
}

async function handleSubmit() {
  if (!validateForm()) return

  isSaving.value = true
  formError.value = ''

  try {
    const payload = {
      nombre: form.nombre.trim(),
      descripcion: form.descripcion.trim() || null,
    }

    if (editingCargo.value) {
      await cargoApi.actualizar(editingCargo.value.id, payload)
      toast.add({ severity: 'success', summary: 'Cargo actualizado', detail: 'El cargo se actualizo correctamente', life: 3000 })
    } else {
      await cargoApi.crear(payload)
      toast.add({ severity: 'success', summary: 'Cargo creado', detail: 'El cargo se creo correctamente', life: 3000 })
    }

    closeFormDialog()
    await fetchCargos()
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

async function toggleState(cargo) {
  try {
    await cargoApi.cambiarEstado(cargo.id, !cargo.activo)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del cargo se actualizo', life: 3000 })
    await fetchCargos()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: normalizeApiError(error, 'Error al cambiar estado'), life: 3000 })
  }
}

onMounted(fetchCargos)
</script>

<style scoped>
.cargo-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cargo-header {
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
  line-height: 1.2;
  font-weight: 700;
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

.table-shell {
  overflow-x: auto;
}

.cargo-table {
  width: 100%;
  border-collapse: collapse;
}

.cargo-table thead th {
  padding: 0.9rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
}

.cargo-table tbody td {
  padding: 0.95rem 1rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  vertical-align: middle;
}

.cargo-table tbody tr:hover {
  background: color-mix(in srgb, var(--surface) 86%, transparent);
}

.name-main {
  display: block;
  font-weight: 600;
  color: var(--text);
}

.description-cell {
  color: var(--text-muted);
}

.actions-col {
  width: 8rem;
  text-align: center;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
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

.form-message {
  margin-bottom: 0.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.field-error {
  color: #dc2626;
  font-size: 0.75rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.25rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .cargo-header {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: 1.35rem;
  }

  .dialog-footer {
    flex-wrap: wrap;
  }

  .dialog-footer > * {
    flex: 1 1 140px;
  }

  .actions {
    justify-content: flex-start;
  }
}
</style>
