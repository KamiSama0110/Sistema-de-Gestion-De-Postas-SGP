<template>
  <div>
    <div class="page-header">
      <div class="page-title-block">
        <div class="page-title-icon">
          <i class="pi pi-map-marker"></i>
        </div>
        <div>
          <h2 class="page-title">Postas</h2>
          <p class="page-subtitle">Gestion de postas y turnos</p>
        </div>
      </div>
      <Button label="Nueva posta" icon="pi pi-plus" @click="abrirModal()" />
    </div>

    <Card style="margin-bottom: 16px">
      <template #content>
        <div class="filtros">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText v-model="filtros.buscar" placeholder="Buscar por nombre..." @input="cargarPostas" />
          </IconField>
          <Select v-model="filtros.activa" :options="opcionesActiva" optionLabel="label" optionValue="value"
            placeholder="Estado" @change="cargarPostas" style="width: 170px" />
          <Select v-model="filtros.tipo" :options="opcionesTipo" optionLabel="label" optionValue="value"
            placeholder="Tipo" @change="cargarPostas" style="width: 190px" />
        </div>
      </template>
    </Card>

    <Card>
      <template #content>
        <div v-if="cargando" class="empty-state">
          Cargando...
        </div>

        <div v-else-if="postas.length === 0" class="empty-state">
          No hay postas registradas
        </div>
        <DataTable v-else :value="postas" :loading="cargando" stripedRows size="small"
          emptyMessage="No hay postas registradas">
          <Column field="nombre" header="Nombre" />
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
          <Column header="Turnos">
            <template #body="{ data }">
              {{ data.turnos?.length || 0 }}
            </template>
          </Column>
          <Column header="Estado">
            <template #body="{ data }">
              <Tag :value="data.activa ? 'Activa' : 'Inactiva'" :severity="data.activa ? 'success' : 'secondary'" />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <div class="actions">
                <Button icon="pi pi-eye" size="small" severity="info" text @click="abrirModalInfo(data)" />
                <Button icon="pi pi-pencil" size="small" severity="secondary" text @click="abrirModal(data)" />
                <Button icon="pi pi-clock" size="small" severity="info" text @click="abrirModalTurnos(data)" />
                <Button :icon="data.activa ? 'pi pi-times' : 'pi pi-check'" size="small"
                  :severity="data.activa ? 'danger' : 'success'" text @click="toggleEstado(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="modalVisible" :header="editando ? 'Editar posta' : 'Nueva posta'"
      :style="{ width: '620px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ error }}
        </Message>
        <div class="form-grid">
          <div class="field">
            <label>Nombre *</label>
            <InputText v-model="form.nombre" />
          </div>
          <div class="field">
            <label>Tipo *</label>
            <Select v-model="form.tipo" :options="opcionesTipo" optionLabel="label" optionValue="value" />
          </div>
          <div class="field">
            <label>Ubicacion</label>
            <InputText v-model="form.ubicacion" />
          </div>
          <div class="field" style="grid-column: span 2">
            <label>Descripcion</label>
            <Textarea v-model="form.descripcion" rows="2" autoResize />
          </div>
          <div class="field" style="grid-column: span 2">
            <label>Observaciones</label>
            <Textarea v-model="form.observaciones" rows="2" autoResize />
          </div>
        </div>

        <div v-if="!editando" class="turnos-section">
          <div class="turnos-header">
            <div>
              <h4>Turnos iniciales</h4>
              <p class="muted">Puedes registrar turnos ahora o despues desde el modulo de turnos.</p>
            </div>
          </div>
          <Message v-if="errorTurnoDraft" severity="warn" :closable="false" style="margin-bottom: 10px">
            {{ errorTurnoDraft }}
          </Message>
          <div class="turno-form">
            <div class="field">
              <label>Nombre *</label>
              <InputText v-model="turnoDraftForm.nombre" />
            </div>
            <div class="field">
              <label>Inicio *</label>
              <InputText v-model="turnoDraftForm.hora_inicio" type="time" />
            </div>
            <div class="field">
              <label>Fin *</label>
              <InputText v-model="turnoDraftForm.hora_fin" type="time" />
            </div>
            <div class="field">
              <label>ASP requeridos *</label>
              <InputText v-model="turnoDraftForm.asp_requeridos" type="number" min="1" />
            </div>
            <div class="turno-actions">
              <Button label="Agregar" icon="pi pi-plus" severity="secondary" @click="agregarTurnoDraft" />
            </div>
          </div>

          <DataTable v-if="turnosDraft.length" :value="turnosDraft" size="small" stripedRows>
            <Column field="nombre" header="Nombre" />
            <Column header="Horario">
              <template #body="{ data }">
                {{ formatHora(data.hora_inicio) }} - {{ formatHora(data.hora_fin) }}
              </template>
            </Column>
            <Column field="asp_requeridos" header="ASP" />
            <Column header="Acciones">
              <template #body="{ index }">
                <Button icon="pi pi-trash" size="small" severity="danger" text @click="eliminarTurnoDraft(index)" />
              </template>
            </Column>
          </DataTable>
        </div>

        <div v-else class="turnos-section">
          <div class="turnos-header">
            <div>
              <h4>Turnos</h4>
              <p class="muted">Gestiona los turnos desde el modulo de turnos de esta posta.</p>
            </div>
            <Button label="Gestionar turnos" icon="pi pi-clock" severity="info" text
              @click="abrirModalTurnos(editando)" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="cerrarModal" />
        <Button label="Guardar" icon="pi pi-check" :loading="guardando" @click="guardar" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalTurnosVisible" :header="'Turnos — ' + (postaSeleccionada?.nombre || '')"
      :style="{ width: '700px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="errorTurno" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorTurno }}
        </Message>
        <div class="turno-form">
          <div class="field">
            <label>Nombre *</label>
            <InputText v-model="formTurno.nombre" />
          </div>
          <div class="field">
            <label>Inicio *</label>
            <InputText v-model="formTurno.hora_inicio" type="time" />
          </div>
          <div class="field">
            <label>Fin *</label>
            <InputText v-model="formTurno.hora_fin" type="time" />
          </div>
          <div class="field">
            <label>ASP requeridos *</label>
            <InputText v-model="formTurno.asp_requeridos" type="number" min="1" />
          </div>
          <div class="turno-actions">
            <Button :label="editandoTurno ? 'Actualizar' : 'Agregar'" icon="pi pi-check" :loading="guardandoTurno"
              @click="guardarTurno" />
            <Button v-if="editandoTurno" label="Cancelar" severity="secondary" text @click="resetTurnoForm" />
          </div>
        </div>

        <DataTable :value="turnos" size="small" stripedRows emptyMessage="No hay turnos registrados">
          <Column field="nombre" header="Nombre" />
          <Column header="Horario">
            <template #body="{ data }">
              {{ formatHora(data.hora_inicio) }} - {{ formatHora(data.hora_fin) }}
            </template>
          </Column>
          <Column field="asp_requeridos" header="ASP" />
          <Column header="Cruza medianoche">
            <template #body="{ data }">
              <Tag :value="data.cruza_medianoche ? 'Si' : 'No'"
                :severity="data.cruza_medianoche ? 'warn' : 'secondary'" />
            </template>
          </Column>
          <Column header="Estado">
            <template #body="{ data }">
              <Tag :value="data.activo ? 'Activo' : 'Inactivo'" :severity="data.activo ? 'success' : 'secondary'" />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <div class="actions">
                <Button icon="pi pi-pencil" size="small" severity="secondary" text @click="editarTurno(data)" />
                <Button :icon="data.activo ? 'pi pi-times' : 'pi pi-check'" size="small"
                  :severity="data.activo ? 'danger' : 'success'" text @click="toggleEstadoTurno(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalTurnos" />
      </template>
    </Dialog>

    <Dialog v-model:visible="modalInfoVisible" :header="'Ficha tecnica — ' + (postaDetalle?.nombre || '')"
      :style="{ width: '680px' }" modal :closable="true">
      <div class="p-fluid">
        <Message v-if="errorInfo" severity="error" :closable="false" style="margin-bottom: 12px">
          {{ errorInfo }}
        </Message>
        <div v-if="cargandoInfo" class="empty-state">Cargando...</div>
        <div v-else-if="postaDetalle" class="info-grid">
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">Nombre</span>
              <span class="info-value">{{ postaDetalle.nombre }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Ubicacion</span>
              <span class="info-value">{{ postaDetalle.ubicacion || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Descripcion</span>
              <span class="info-value">{{ postaDetalle.descripcion || '—' }}</span>
            </div>
          </div>
          <div class="info-col">
            <div class="info-item">
              <span class="info-label">Tipo</span>
              <span class="info-value">{{ labelTipo(postaDetalle.tipo) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Estado</span>
              <span class="info-value">{{ postaDetalle.activa ? 'Activa' : 'Inactiva' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Observaciones</span>
              <span class="info-value">{{ postaDetalle.observaciones || '—' }}</span>
            </div>
          </div>
        </div>

        <div v-if="postaDetalle?.turnos?.length" class="info-section">
          <h4>Turnos</h4>
          <DataTable :value="postaDetalle.turnos" size="small" stripedRows>
            <Column field="nombre" header="Nombre" />
            <Column header="Horario">
              <template #body="{ data }">
                {{ formatHora(data.hora_inicio) }} - {{ formatHora(data.hora_fin) }}
              </template>
            </Column>
            <Column field="asp_requeridos" header="ASP" />
            <Column header="Cruza medianoche">
              <template #body="{ data }">
                {{ data.cruza_medianoche ? 'Si' : 'No' }}
              </template>
            </Column>
            <Column header="Estado">
              <template #body="{ data }">
                {{ data.activo ? 'Activo' : 'Inactivo' }}
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      <template #footer>
        <Button label="Cerrar" severity="secondary" text @click="cerrarModalInfo" />
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
import Select from 'primevue/select'
import Message from 'primevue/message'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import { useToast } from 'primevue/usetoast'
import { postaApi } from '../api/posta'
import { normalizeApiError } from '../utils/error'

const postas = ref([])
const cargando = ref(true)
const modalVisible = ref(false)
const modalTurnosVisible = ref(false)
const modalInfoVisible = ref(false)
const editando = ref(null)
const postaSeleccionada = ref(null)
const postaDetalle = ref(null)
const error = ref('')
const errorTurno = ref('')
const errorTurnoDraft = ref('')
const guardando = ref(false)
const guardandoTurno = ref(false)
const errorInfo = ref('')
const cargandoInfo = ref(false)
const toast = useToast()

const filtros = ref({ buscar: '', activa: null, tipo: null })

const opcionesActiva = [
  { label: 'Todas', value: null },
  { label: 'Activas', value: true },
  { label: 'Inactivas', value: false },
]
const opcionesTipo = [
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
  observaciones: '',
})
const form = ref(formVacio())

const turnoVacio = () => ({
  nombre: '',
  hora_inicio: '',
  hora_fin: '',
  asp_requeridos: 1,
})
const turnoDraftForm = ref(turnoVacio())
const turnosDraft = ref([])

const turnos = ref([])
const formTurno = ref(turnoVacio())
const editandoTurno = ref(null)

function labelTipo(tipo) {
  return opcionesTipo.find(o => o.value === tipo)?.label || '—'
}

function normalizarHora(value) {
  if (!value) return ''
  const parts = String(value).split(':')
  if (parts.length < 2) return value
  const horas = parts[0].padStart(2, '0')
  const minutos = parts[1].padStart(2, '0')
  return `${horas}:${minutos}`
}

function formatHora(value) {
  return normalizarHora(value)
}

async function cargarPostas() {
  cargando.value = true
  try {
    const params = {}
    if (filtros.value.buscar) params.buscar = filtros.value.buscar
    if (filtros.value.activa !== null) params.activa = filtros.value.activa
    if (filtros.value.tipo) params.tipo = filtros.value.tipo
    const res = await postaApi.listar(params)
    postas.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function abrirModal(posta = null) {
  editando.value = posta
  form.value = posta
    ? {
      nombre: posta.nombre,
      tipo: posta.tipo,
      ubicacion: posta.ubicacion || '',
      descripcion: posta.descripcion || '',
      observaciones: posta.observaciones || '',
    }
    : formVacio()
  turnosDraft.value = []
  turnoDraftForm.value = turnoVacio()
  error.value = ''
  errorTurnoDraft.value = ''
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
    if (editando.value) {
      await postaApi.actualizar(editando.value.id, form.value)
      toast.add({ severity: 'success', summary: 'Posta actualizada', detail: 'La posta se actualizo correctamente', life: 3000 })
    } else {
      const datos = {
        ...form.value,
        turnos: turnosDraft.value.map(t => ({
          ...t,
          asp_requeridos: Number(t.asp_requeridos),
        })),
      }
      await postaApi.crear(datos)
      toast.add({ severity: 'success', summary: 'Posta creada', detail: 'La posta se creo correctamente', life: 3000 })
    }
    cerrarModal()
    await cargarPostas()
  } catch (e) {
    error.value = normalizeApiError(e, 'Error al guardar')
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
  }
}

function agregarTurnoDraft() {
  errorTurnoDraft.value = ''
  if (!turnoDraftForm.value.nombre || !turnoDraftForm.value.hora_inicio || !turnoDraftForm.value.hora_fin) {
    errorTurnoDraft.value = 'Completa nombre y horarios del turno'
    return
  }
  turnosDraft.value.push({
    ...turnoDraftForm.value,
    hora_inicio: normalizarHora(turnoDraftForm.value.hora_inicio),
    hora_fin: normalizarHora(turnoDraftForm.value.hora_fin),
    asp_requeridos: Number(turnoDraftForm.value.asp_requeridos) || 1,
  })
  turnoDraftForm.value = turnoVacio()
}

function eliminarTurnoDraft(index) {
  turnosDraft.value.splice(index, 1)
}

async function abrirModalTurnos(posta) {
  postaSeleccionada.value = posta
  await cargarTurnos(posta.id)
  errorTurno.value = ''
  resetTurnoForm()
  modalTurnosVisible.value = true
}

function cerrarModalTurnos() {
  modalTurnosVisible.value = false
  postaSeleccionada.value = null
}

async function abrirModalInfo(posta) {
  postaDetalle.value = null
  errorInfo.value = ''
  cargandoInfo.value = true
  modalInfoVisible.value = true
  try {
    const res = await postaApi.obtener(posta.id)
    postaDetalle.value = res.data
  } catch (e) {
    errorInfo.value = normalizeApiError(e, 'Error al cargar informacion')
  } finally {
    cargandoInfo.value = false
  }
}

function cerrarModalInfo() {
  modalInfoVisible.value = false
  postaDetalle.value = null
}

async function cargarTurnos(postaId) {
  const res = await postaApi.obtener(postaId)
  turnos.value = res.data.turnos || []
  postaSeleccionada.value = res.data
}

function editarTurno(turno) {
  editandoTurno.value = turno
  formTurno.value = {
    nombre: turno.nombre,
    hora_inicio: normalizarHora(turno.hora_inicio),
    hora_fin: normalizarHora(turno.hora_fin),
    asp_requeridos: turno.asp_requeridos,
  }
}

function resetTurnoForm() {
  editandoTurno.value = null
  formTurno.value = turnoVacio()
}

async function guardarTurno() {
  errorTurno.value = ''
  if (!formTurno.value.nombre || !formTurno.value.hora_inicio || !formTurno.value.hora_fin) {
    errorTurno.value = 'Completa nombre y horarios del turno'
    return
  }
  guardandoTurno.value = true
  try {
    const payload = {
      ...formTurno.value,
      hora_inicio: normalizarHora(formTurno.value.hora_inicio),
      hora_fin: normalizarHora(formTurno.value.hora_fin),
      asp_requeridos: Number(formTurno.value.asp_requeridos) || 1,
    }
    if (editandoTurno.value) {
      await postaApi.actualizarTurno(editandoTurno.value.id, payload)
      toast.add({ severity: 'success', summary: 'Turno actualizado', detail: 'El turno se actualizo correctamente', life: 3000 })
    } else {
      await postaApi.agregarTurno(postaSeleccionada.value.id, payload)
      toast.add({ severity: 'success', summary: 'Turno agregado', detail: 'El turno se agrego correctamente', life: 3000 })
    }
    await cargarTurnos(postaSeleccionada.value.id)
    await cargarPostas()
    resetTurnoForm()
  } catch (e) {
    errorTurno.value = normalizeApiError(e, 'Error al guardar turno')
  } finally {
    guardandoTurno.value = false
  }
}

async function toggleEstadoTurno(turno) {
  const accion = turno.activo ? 'desactivar' : 'activar'
  const confirmado = window.confirm(`Confirmas ${accion} el turno "${turno.nombre}"?`)
  if (!confirmado) return
  errorTurno.value = ''
  try {
    await postaApi.cambiarEstadoTurno(turno.id, !turno.activo)
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado del turno se actualizo', life: 3000 })
    await cargarTurnos(postaSeleccionada.value.id)
    await cargarPostas()
  } catch (e) {
    errorTurno.value = normalizeApiError(e, 'Error al cambiar estado del turno')
  }
}

onMounted(cargarPostas)
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

.actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 20px;
}

.turnos-section {
  margin-top: 18px;
}

.turnos-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.turnos-header h4 {
  margin: 0 0 2px;
}

.muted {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}

.turno-form {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  align-items: end;
  margin-bottom: 12px;
}

.turno-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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

.info-section {
  margin-top: 14px;
}

.info-section h4 {
  margin: 0 0 8px;
}

.span-2 {
  grid-column: span 2;
}
</style>

<style>
.p-dialog .p-inputtext,
.p-dialog .p-textarea,
.p-dialog .p-select {
  width: 100%;
}
</style>
