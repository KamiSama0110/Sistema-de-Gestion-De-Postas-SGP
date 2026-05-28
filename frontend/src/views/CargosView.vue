<template>
  <div>
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-id-card"></i>
        </div>
        <div>
          <h2 class="page-title">Cargos</h2>
          <p class="page-subtitle">Gestión de cargos laborales</p>
        </div>
      </div>
      <Button label="Nuevo cargo" icon="pi pi-plus" @click="abrirModal()" />
    </div>

    <Card>
      <template #content>
        <div v-if="cargando" class="empty-state">
          Cargando...
        </div>

        <div v-else-if="cargos.length === 0" class="empty-state">
          No hay cargos registrados
        </div>

        <DataTable v-else :value="cargos" stripedRows size="small">
          <Column field="nombre" header="Nombre" />
          <Column field="descripcion" header="Descripción">
            <template #body="{ data }">
              {{ data.descripcion || '—' }}
            </template>
          </Column>
          <Column field="activo" header="Estado">
            <template #body="{ data }">
              <Tag :value="data.activo ? 'Activo' : 'Inactivo'" :severity="data.activo ? 'success' : 'secondary'" />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <div class="actions">
                <Button icon="pi pi-pencil" size="small" severity="secondary" text @click="abrirModal(data)" />
                <Button :icon="data.activo ? 'pi pi-times' : 'pi pi-check'" size="small"
                  :severity="data.activo ? 'danger' : 'success'" text @click="toggleEstado(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar cargo' : 'Nuevo cargo'"
      :style="{ width: '440px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ error }}
        </Message>
        <div class="field">
          <label>Nombre *</label>
          <InputText v-model="form.nombre" />
        </div>
        <div class="field" style="margin-top: 14px">
          <label>Descripcion</label>
          <Textarea v-model="form.descripcion" rows="3" autoResize />
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
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'

const cargos = ref([])
const cargando = ref(true)
const modalVisible = ref(false)
const editando = ref(null)
const error = ref('')
const guardando = ref(false)
const form = ref({ nombre: '', descripcion: '' })
const toast = useToast()

async function cargarCargos() {
  cargando.value = true
  try {
    const res = await cargoApi.listar(false)
    cargos.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function abrirModal(cargo = null) {
  editando.value = cargo
  form.value = cargo
    ? { nombre: cargo.nombre, descripcion: cargo.descripcion || '' }
    : { nombre: '', descripcion: '' }
  error.value = ''
  modalVisible.value = true
}

function cerrarModal() {
  modalVisible.value = false
  editando.value = null
}

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const datos = { ...form.value }
    if (typeof datos.descripcion === 'string' && datos.descripcion.trim() === '') {
      delete datos.descripcion
    }
    if (editando.value) {
      await cargoApi.actualizar(editando.value.id, datos)
      toast.add({ severity: 'success', summary: 'Cargo actualizado', detail: 'El cargo se actualizo correctamente', life: 3000 })
    } else {
      await cargoApi.crear(datos)
      toast.add({ severity: 'success', summary: 'Cargo creado', detail: 'El cargo se creo correctamente', life: 3000 })
    }
    cerrarModal()
    await cargarCargos()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al guardar')
  } finally {
    guardando.value = false
  }
}

async function toggleEstado(cargo) {
  try {
    await cargoApi.cambiarEstado(cargo.id, !cargo.activo)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del cargo se actualizo', life: 3000 })
    await cargarCargos()
  } catch (e) {
    console.error(e)
  }
}

onMounted(cargarCargos)
</script>

<style scoped>
.field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 6px;
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
</style>

<style>
.p-dialog .p-inputtext,
.p-dialog .p-textarea {
  width: 100%;
}
</style>
