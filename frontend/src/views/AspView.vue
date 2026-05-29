<template>
  <div>
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-users"></i>
        </div>
        <div>
          <h2 class="page-title">Agentes de Seguridad y Proteccion</h2>
          <p class="page-subtitle">Gestion de ASP registrados</p>
        </div>
      </div>
      <Button label="Nuevo ASP" icon="pi pi-plus" @click="abrirModal()" />
    </div>

    <!-- Filtros -->
    <Card style="margin-bottom: 16px">
      <template #content>
        <div class="filtros">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText v-model="filtros.buscar" placeholder="Buscar por nombre o CI..." @input="cargarAsp" />
          </IconField>
          <Select v-model="filtros.estado" :options="opcionesEstado" optionLabel="label" optionValue="value"
            placeholder="Todos los estados" @change="cargarAsp" style="width: 200px" />
        </div>
      </template>
    </Card>

    <Card>
      <template #content>
        <div v-if="cargando" class="empty-state">
          Cargando...
        </div>

        <div v-else-if="asp.length === 0" class="empty-state">
          No hay ASP registrados
        </div>
        <DataTable v-else :value="asp" :loading="cargando" stripedRows size="small" emptyMessage="No hay ASP registrados">
          <Column field="ci" header="CI" />
          <Column header="Nombre">
            <template #body="{ data }">
              {{ data.nombre }} {{ data.apellidos }}
            </template>
          </Column>
          <Column header="Cargo">
            <template #body="{ data }">
              {{ nombreCargo(data.cargo_id) }}
            </template>
          </Column>
          <Column field="estado" header="Estado">
            <template #body="{ data }">
              <Tag :value="data.estado" :severity="severidadEstado(data.estado)" />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <div class="actions">
                <Button icon="pi pi-eye" size="small" severity="info" text @click="abrirModalInfo(data)" />
                <Button icon="pi pi-pencil" size="small" severity="secondary" text @click="abrirModal(data)" />
                <Button icon="pi pi-sync" size="small" severity="warn" text @click="abrirModalEstado(data)" />
              </div>
            </template>
          </Column>
        </DataTable>

        <div class="paginacion" v-if="total > filtros.size">
          <Button icon="pi pi-chevron-left" size="small" severity="secondary" text :disabled="filtros.page === 1"
            @click="cambiarPagina(-1)" />
          <span>Pagina {{ filtros.page }} de {{ totalPaginas }}</span>
          <Button icon="pi pi-chevron-right" size="small" severity="secondary" text
            :disabled="filtros.page >= totalPaginas" @click="cambiarPagina(1)" />
        </div>
      </template>
    </Card>

    <!-- Modal crear/editar -->
    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar ASP' : 'Nuevo ASP'" :style="{ width: '560px' }"
      modal>
      <div class="p-fluid">
        <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ error }}
        </Message>
        <div class="form-grid">
          <div class="field">
            <label>CI *</label>
            <InputText v-model="form.ci" maxlength="11" />
          </div>
          <div class="field">
            <label>Cargo *</label>
            <Select v-model="form.cargo_id" :options="cargos" optionLabel="nombre" optionValue="id"
              placeholder="Seleccionar cargo" />
          </div>
          <div class="field">
            <label>Nombre *</label>
            <InputText v-model="form.nombre" />
          </div>
          <div class="field">
            <label>Apellidos *</label>
            <InputText v-model="form.apellidos" />
          </div>
          <div class="field">
            <label>Fecha de nacimiento *</label>
            <DatePicker v-model="form.fecha_nacimiento" dateFormat="yy-mm-dd" showIcon />
          </div>
          <div class="field">
            <label>Fecha de ingreso *</label>
            <DatePicker v-model="form.fecha_ingreso" dateFormat="yy-mm-dd" showIcon />
          </div>
          <div class="field">
            <label>Sexo *</label>
            <Select v-model="form.sexo" :options="opcionesSexo" optionLabel="label" optionValue="value" />
          </div>
          <div class="field">
            <label>Escolaridad *</label>
            <Select v-model="form.nivel_escolaridad" :options="opcionesEscolaridad" optionLabel="label"
              optionValue="value" />
          </div>
          <div class="field">
            <label>Telefono</label>
            <InputText v-model="form.telefono" />
          </div>
          <div class="field">
            <label>Direccion</label>
            <InputText v-model="form.direccion" />
          </div>
          <div class="field" style="grid-column: span 2">
            <label>Observaciones</label>
            <Textarea v-model="form.observaciones" rows="2" autoResize />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModal" />
        <Button label="Guardar" icon="pi pi-check" :loading="guardando" @click="guardar" />
      </template>
    </Dialog>

    <!-- Modal cambiar estado -->
    <Dialog v-model:visible="modalEstadoVisible" :header="'Cambiar estado — ' + (aspSeleccionado?.nombre || '')"
      :style="{ width: '400px' }" modal>
      <div class="p-fluid">
        <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ error }}
        </Message>
        <div class="field">
          <label>Nuevo estado</label>
          <Select v-model="formEstado.estado" :options="opcionesEstado.filter(o => o.value)" optionLabel="label"
            optionValue="value" />
        </div>
        <div class="field" style="margin-top: 14px">
          <label>Observacion</label>
          <Textarea v-model="formEstado.observacion" rows="2" autoResize />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModalEstado" />
        <Button label="Confirmar" icon="pi pi-check" :loading="guardando" @click="guardarEstado" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalInfoVisible" :header="'Ficha tecnica — ' + (aspDetalle?.nombre || '')"
      :style="{ width: '620px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="errorInfo" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorInfo }}
        </Message>
        <div v-if="cargandoInfo" class="empty-state">Cargando...</div>
        <div v-else-if="aspDetalle" class="info-grid">
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">CI</span>
              <span class="info-value">{{ aspDetalle.ci }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Nombre</span>
              <span class="info-value">{{ aspDetalle.nombre }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Fecha de nacimiento</span>
              <span class="info-value">{{ formatFecha(aspDetalle.fecha_nacimiento) || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Sexo</span>
              <span class="info-value">{{ aspDetalle.sexo }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Telefono</span>
              <span class="info-value">{{ aspDetalle.telefono || '—' }}</span>
            </div>
          </div>
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">Cargo</span>
              <span class="info-value">{{ nombreCargo(aspDetalle.cargo_id) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Apellidos</span>
              <span class="info-value">{{ aspDetalle.apellidos }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Fecha de ingreso</span>
              <span class="info-value">{{ formatFecha(aspDetalle.fecha_ingreso) || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Escolaridad</span>
              <span class="info-value">{{ aspDetalle.nivel_escolaridad }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Direccion</span>
              <span class="info-value">{{ aspDetalle.direccion || '—' }}</span>
            </div>
          </div>
          <div class="info-item span-2">
            <span class="info-label">Observaciones</span>
            <span class="info-value">{{ aspDetalle.observaciones || '—' }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalInfo" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import { aspApi } from '../api/asp'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'

const asp = ref([])
const cargos = ref([])
const cargando = ref(true)
const total = ref(0)
const modalVisible = ref(false)
const modalEstadoVisible = ref(false)
const modalInfoVisible = ref(false)
const editando = ref(null)
const aspSeleccionado = ref(null)
const aspDetalle = ref(null)
const error = ref('')
const guardando = ref(false)
const errorInfo = ref('')
const cargandoInfo = ref(false)
const toast = useToast()

const filtros = ref({ buscar: '', estado: '', page: 1, size: 20 })
const totalPaginas = computed(() => Math.ceil(total.value / filtros.value.size))

const opcionesEstado = [
  { label: 'Todos los estados', value: '' },
  { label: 'Activo', value: 'activo' },
  { label: 'Suspendido', value: 'suspendido' },
  { label: 'Baja temporal', value: 'baja_temporal' },
  { label: 'Baja definitiva', value: 'baja_definitiva' },
]
const opcionesSexo = [
  { label: 'Masculino', value: 'masculino' },
  { label: 'Femenino', value: 'femenino' },
]
const opcionesEscolaridad = [
  { label: 'Primaria', value: 'primaria' },
  { label: 'Secundaria', value: 'secundaria' },
  { label: 'Preuniversitario', value: 'preuniversitario' },
  { label: 'Tecnico medio', value: 'tecnico_medio' },
  { label: 'Universitario', value: 'universitario' },
]

function nombreCargo(id) {
  return cargos.value.find(c => c.id === id)?.nombre || '—'
}

function severidadEstado(estado) {
  const map = {
    activo: 'success',
    suspendido: 'warn',
    baja_temporal: 'warn',
    baja_definitiva: 'danger',
  }
  return map[estado] || 'secondary'
}

const formVacio = () => ({
  ci: '', nombre: '', apellidos: '',
  fecha_nacimiento: null, sexo: 'masculino',
  nivel_escolaridad: 'tecnico_medio',
  fecha_ingreso: null, cargo_id: null,
  telefono: '', direccion: '', observaciones: '',
})
const form = ref(formVacio())
const formEstado = ref({ estado: 'activo', observacion: '' })

async function cargarAsp() {
  cargando.value = true
  try {
    const params = { page: filtros.value.page, size: filtros.value.size }
    if (filtros.value.buscar) params.buscar = filtros.value.buscar
    if (filtros.value.estado) params.estado = filtros.value.estado
    const res = await aspApi.listar(params)
    asp.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(dir) {
  filtros.value.page += dir
  cargarAsp()
}

async function abrirModal(a = null) {
  editando.value = a
  error.value = ''
  if (!a) {
    form.value = formVacio()
    modalVisible.value = true
    return
  }
  try {
    const res = await aspApi.obtener(a.id)
    const aspData = res.data
    form.value = {
      ci: aspData.ci,
      nombre: aspData.nombre,
      apellidos: aspData.apellidos,
      fecha_nacimiento: parseDateOnly(aspData.fecha_nacimiento),
      sexo: aspData.sexo,
      nivel_escolaridad: aspData.nivel_escolaridad,
      fecha_ingreso: parseDateOnly(aspData.fecha_ingreso),
      cargo_id: aspData.cargo_id,
      telefono: aspData.telefono || '',
      direccion: aspData.direccion || '',
      observaciones: aspData.observaciones || '',
    }
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al cargar ASP')
  } finally {
    modalVisible.value = true
  }
}

function cerrarModal() {
  modalVisible.value = false
  editando.value = null
}

function abrirModalEstado(a) {
  aspSeleccionado.value = a
  formEstado.value = { estado: a.estado, observacion: '' }
  error.value = ''
  modalEstadoVisible.value = true
}

function cerrarModalEstado() {
  modalEstadoVisible.value = false
  aspSeleccionado.value = null
}

async function abrirModalInfo(item) {
  aspDetalle.value = null
  errorInfo.value = ''
  cargandoInfo.value = true
  modalInfoVisible.value = true
  try {
    const res = await aspApi.obtener(item.id)
    aspDetalle.value = res.data
  } catch (e) {
    errorInfo.value = normalizeApiError(e, 'Error al cargar informacion')
  } finally {
    cargandoInfo.value = false
  }
}

function cerrarModalInfo() {
  modalInfoVisible.value = false
  aspDetalle.value = null
}

function formatFecha(fecha) {
  if (!fecha) return null
  if (typeof fecha === 'string') return fecha.split('T')[0]
  const year = fecha.getFullYear()
  const month = String(fecha.getMonth() + 1).padStart(2, '0')
  const day = String(fecha.getDate()).padStart(2, '0')
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

function limpiarOpcionales(payload, campos) {
  campos.forEach(campo => {
    const valor = payload[campo]
    if (valor == null) {
      delete payload[campo]
      return
    }
    if (typeof valor === 'string' && valor.trim() === '') {
      delete payload[campo]
    }
  })
  return payload
}

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const datos = {
      ...form.value,
      fecha_nacimiento: formatFecha(form.value.fecha_nacimiento),
      fecha_ingreso: formatFecha(form.value.fecha_ingreso),
    }
    limpiarOpcionales(datos, ['telefono', 'direccion', 'observaciones'])
    if (editando.value) {
      await aspApi.actualizar(editando.value.id, datos)
      toast.add({ severity: 'success', summary: 'ASP actualizado', detail: 'El ASP se actualizo correctamente', life: 3000 })
    } else {
      await aspApi.crear(datos)
      toast.add({ severity: 'success', summary: 'ASP creado', detail: 'El ASP se creo correctamente', life: 3000 })
    }
    cerrarModal()
    await cargarAsp()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al guardar')
  } finally {
    guardando.value = false
  }
}

async function guardarEstado() {
  error.value = ''
  guardando.value = true
  try {
    const datos = limpiarOpcionales({ ...formEstado.value }, ['observacion'])
    await aspApi.cambiarEstado(aspSeleccionado.value.id, datos)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del ASP se actualizo', life: 3000 })
    cerrarModalEstado()
    await cargarAsp()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al cambiar estado')
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  const res = await cargoApi.listar(true)
  cargos.value = res.data
  await cargarAsp()
})
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
  gap: 10px;
  align-items: center;
}

.field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
}

.info-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--surface-border);
  background: var(--surface-ground);
}

.info-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--brand-700);
  margin-bottom: 6px;
}

.info-value {
  display: block;
  font-weight: 600;
  color: var(--text-color);
}

.span-2 {
  grid-column: span 2;
}

@media (max-width: 960px) {
  .filtros {
    flex-direction: column;
    align-items: stretch;
  }

  .filtros :deep(.p-iconfield),
  .filtros :deep(.p-select),
  .filtros :deep(.p-inputtext) {
    width: 100%;
  }

  .form-grid,
  .info-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }
}

@media (max-width: 640px) {
  .actions {
    width: 100%;
  }

  .actions > * {
    flex: 1 1 auto;
  }
}
</style>

<style>
.p-dialog .p-inputtext,
.p-dialog .p-textarea,
.p-dialog .p-select,
.p-dialog .p-datepicker {
  width: 100%;
}
</style>
