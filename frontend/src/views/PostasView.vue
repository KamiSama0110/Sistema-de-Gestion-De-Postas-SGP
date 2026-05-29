<template>
  <div class="postas-page">
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-building"></i>
        </div>
        <div>
          <h2 class="page-title">Postas</h2>
          <p class="page-subtitle">Ubicaciones de vigilancia</p>
        </div>
      </div>

      <Button label="Nueva Posta" icon="pi pi-plus" @click="abrirModal()" />
    </div>

    <Card class="panel-card">
      <template #content>
        <div v-if="cargando" class="empty-state">
          <div class="empty-state__inner">
            <div class="spinner"></div>
            <p>Cargando...</p>
          </div>
        </div>

        <div v-else-if="postas.length === 0" class="empty-state">
          <div class="empty-state__inner">
            <i class="pi pi-building empty-icon"></i>
            <p class="empty-title">No hay postas registradas</p>
            <p class="empty-subtitle">Comience agregando una nueva posta</p>
          </div>
        </div>

        <DataTable
          v-else
          :value="postas"
          stripedRows
          size="small"
          responsiveLayout="scroll"
          emptyMessage="No hay postas registradas"
        >
          <Column field="nombre" header="Nombre">
            <template #body="{ data }">
              <span class="table-strong">{{ data.nombre }}</span>
            </template>
          </Column>
          <Column header="Tipo">
            <template #body="{ data }">
              {{ labelTipo(data.tipo) }}
            </template>
          </Column>
          <Column header="Ubicacion">
            <template #body="{ data }">
              {{ data.ubicacion || '—' }}
            </template>
          </Column>
          <Column header="Descripcion">
            <template #body="{ data }">
              <span class="descripcion-cell">{{ data.descripcion || '—' }}</span>
            </template>
          </Column>
          <Column header="Estado">
            <template #body="{ data }">
              <Tag :value="data.activa ? 'Activa' : 'Inactiva'" :severity="data.activa ? 'success' : 'secondary'" />
            </template>
          </Column>
          <Column header="Acciones" bodyClass="actions-column">
            <template #body="{ data }">
              <div class="actions">
                <Button icon="pi pi-pencil" size="small" severity="secondary" text @click="abrirModal(data)" />
                <Button icon="pi pi-clock" size="small" severity="info" text title="Ver turnos" aria-label="Ver turnos" @click="irATurnos(data)" />
                <Button
                  :icon="data.activa ? 'pi pi-times' : 'pi pi-check'"
                  size="small"
                  :severity="data.activa ? 'danger' : 'success'"
                  text
                  @click="toggleEstado(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar Posta' : 'Nueva Posta'" :style="{ width: '620px' }" modal>
      <div class="p-fluid">
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div class="form-grid">
          <div class="field">
            <label for="nombre">Nombre *</label>
            <InputText id="nombre" v-model="form.nombre" placeholder="Posta Central" />
            <small v-if="fieldErrors.nombre" class="field-error">{{ fieldErrors.nombre }}</small>
          </div>

          <div class="field">
            <label for="tipo">Tipo *</label>
            <Select id="tipo" v-model="form.tipo" :options="tipos" optionLabel="label" optionValue="value" placeholder="Seleccione un tipo" />
            <small v-if="fieldErrors.tipo" class="field-error">{{ fieldErrors.tipo }}</small>
          </div>

          <div class="field">
            <label for="ubicacion">Ubicacion</label>
            <InputText id="ubicacion" v-model="form.ubicacion" placeholder="Av. Principal #123" />
            <small v-if="fieldErrors.ubicacion" class="field-error">{{ fieldErrors.ubicacion }}</small>
          </div>

          <div class="field span-2">
            <label for="descripcion">Descripcion</label>
            <Textarea id="descripcion" v-model="form.descripcion" rows="3" autoResize placeholder="Descripcion de la posta..." />
            <small v-if="fieldErrors.descripcion" class="field-error">{{ fieldErrors.descripcion }}</small>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModal" />
        <Button label="Guardar" icon="pi pi-check" :loading="guardando" @click="guardar" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
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
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

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

.table-strong {
  font-weight: 600;
}

.descripcion-cell {
  display: inline-block;
  max-width: 24rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

.actions-column {
  text-align: right;
}

.empty-state {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 3rem;
  color: var(--brand-500);
}

.empty-title {
  margin: 0;
  font-weight: 600;
  color: var(--text-color);
}

.empty-subtitle {
  margin: 0;
  font-size: 0.92rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  border: 4px solid var(--surface-border);
  border-top-color: var(--brand-600);
  animation: spin 0.8s linear infinite;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.span-2 {
  grid-column: span 2;
}

.form-error {
  margin: 0 0 0.75rem;
  color: var(--red-600, #dc2626);
  font-size: 0.9rem;
  font-weight: 500;
}

.field-error {
  color: var(--red-600, #dc2626);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }

  .descripcion-cell {
    max-width: 14rem;
  }
}
</style>
