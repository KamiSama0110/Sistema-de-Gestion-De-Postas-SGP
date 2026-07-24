<template>
  <div class="cargos-page mx-auto">
    <div class="d-flex align-center justify-space-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nuevo Cargo
      </v-btn>
    </div>

    <v-card rounded="lg" class="pa-5">
      <div class="d-flex align-center justify-space-between mb-4">
        <div class="d-flex ga-2">
          <v-btn
            :variant="filtroActivos === 'activos' ? 'flat' : 'outlined'"
            :color="filtroActivos === 'activos' ? 'primary' : 'default'"
            size="small"
            class="text-none"
            @click="filtroActivos = 'activos'"
          >
            Activos
          </v-btn>
          <v-btn
            :variant="filtroActivos === 'todos' ? 'flat' : 'outlined'"
            :color="filtroActivos === 'todos' ? 'primary' : 'default'"
            size="small"
            class="text-none"
            @click="filtroActivos = 'todos'"
          >
            Todos
          </v-btn>
        </div>
        <div v-if="total > 0" class="text-body-1 text-medium-emphasis">
          {{ total }} cargo{{ total !== 1 ? 's' : '' }}
        </div>
      </div>

      <div v-if="cargando" class="d-flex align-center justify-center py-12">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <Transition name="fade-up" mode="out-in">
        <div v-if="!cargando && cargos.length === 0" key="empty" class="text-center py-12">
          <v-icon icon="mdi-card-account-details-outline" size="48" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-1 text-medium-emphasis">No hay cargos para mostrar</p>
        </div>

        <v-table v-else-if="!cargando && cargos.length > 0" key="table" density="comfortable">
        <thead>
          <tr>
            <th class="text-body-1 font-weight-bold text-medium-emphasis">Nombre</th>
            <th class="text-body-1 font-weight-bold text-medium-emphasis">Descripción</th>
            <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
            <th class="text-body-1 font-weight-bold text-medium-emphasis text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cargo in cargos" :key="cargo.id">
            <td class="font-weight-medium text-body-1">{{ cargo.nombre }}</td>
            <td class="text-medium-emphasis text-body-1">{{ cargo.descripcion || '—' }}</td>
            <td>
              <v-chip
                :color="cargo.activo ? 'success' : 'grey'"
                variant="elevated"
                size="small"
                label
                class="font-weight-bold"
              >
                {{ cargo.activo ? 'Activo' : 'Inactivo' }}
              </v-chip>
            </td>
            <td class="text-right">
              <v-tooltip text="Editar cargo" location="top">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    size="small"
                    variant="text"
                    color="primary"
                    v-bind="props"
                    @click="abrirEditar(cargo)"
                  >
                    <v-icon icon="mdi-pencil-outline" size="18" />
                  </v-btn>
                </template>
              </v-tooltip>
              <v-tooltip :text="cargo.activo ? 'Desactivar cargo' : 'Activar cargo'" location="top">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    size="small"
                    variant="text"
                    :color="cargo.activo ? 'error' : 'success'"
                    v-bind="props"
                    @click="toggleEstado(cargo)"
                  >
                    <v-icon :icon="cargo.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="18" />
                  </v-btn>
                </template>
              </v-tooltip>
            </td>
          </tr>
        </tbody>
      </v-table>
      </Transition>

      <div v-if="totalPaginas > 1" class="d-flex align-center justify-center ga-2 mt-4">
        <v-btn
          icon
          size="small"
          variant="text"
          :disabled="pagina === 1"
          aria-label="Página anterior"
          @click="cambiarPagina(-1)"
        >
          <v-icon icon="mdi-chevron-left" />
        </v-btn>
        <span class="text-body-1 text-medium-emphasis">Página {{ pagina }} de {{ totalPaginas }}</span>
        <v-btn
          icon
          size="small"
          variant="text"
          :disabled="pagina >= totalPaginas"
          aria-label="Página siguiente"
          @click="cambiarPagina(1)"
        >
          <v-icon icon="mdi-chevron-right" />
        </v-btn>
      </div>
    </v-card>

    <v-dialog v-model="dialogAbierto" max-width="480" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ tituloDialog }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-form @submit.prevent="guardar">
            <v-text-field
              v-model="form.nombre"
              label="Nombre"
              placeholder="Ej: ASP, Supervisor..."
              variant="outlined"
              density="comfortable"
              :error-messages="errores.nombre"
              maxlength="100"
              class="mb-3"
              autofocus
            />
            <v-textarea
              v-model="form.descripcion"
              label="Descripción (opcional)"
              placeholder="Describe las funciones de este cargo..."
              variant="outlined"
              density="comfortable"
              :error-messages="errores.descripcion"
              rows="3"
              auto-grow
              class="mb-2"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarDialog">Cancelar</v-btn>
          <v-btn color="primary" :loading="guardando" class="text-none text-body-1" @click="guardar">
            {{ editando ? 'Actualizar' : 'Crear' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'

const toast = useToast()

const cargos = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = 10
const filtroActivos = ref('activos')

const dialogAbierto = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref({ nombre: '', descripcion: '' })
const errores = ref({})
const tituloDialog = ref('Nuevo Cargo')

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina)))

async function cargarCargos() {
  cargando.value = true
  try {
    const soloActivos = filtroActivos.value === 'activos'
    const res = await cargoApi.listar(soloActivos, pagina.value, tamanoPagina)
    cargos.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar cargos'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarCargos()
}

function abrirCrear() {
  editando.value = null
  form.value = { nombre: '', descripcion: '' }
  errores.value = {}
  tituloDialog.value = 'Nuevo Cargo'
  dialogAbierto.value = true
}

function abrirEditar(cargo) {
  editando.value = cargo
  form.value = { nombre: cargo.nombre, descripcion: cargo.descripcion || '' }
  errores.value = {}
  tituloDialog.value = 'Editar Cargo'
  dialogAbierto.value = true
}

function cerrarDialog() {
  dialogAbierto.value = false
  errores.value = {}
}

function validar() {
  const e = {}
  if (!form.value.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (form.value.nombre.trim().length > 100) e.nombre = 'Máximo 100 caracteres'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = { nombre: form.value.nombre.trim() }
    if (form.value.descripcion.trim()) payload.descripcion = form.value.descripcion.trim()

    if (editando.value) {
      await cargoApi.actualizar(editando.value.id, payload)
      toast.success('Cargo actualizado correctamente')
    } else {
      await cargoApi.crear(payload)
      toast.success('Cargo creado correctamente')
    }
    cerrarDialog()
    await cargarCargos()
  } catch (e) {
    const msg = normalizeApiError(e, 'Error al guardar')
    toast.error(msg)
  } finally {
    guardando.value = false
  }
}

async function toggleEstado(cargo) {
  try {
    await cargoApi.cambiarEstado(cargo.id, !cargo.activo)
    toast.success(cargo.activo ? 'Cargo desactivado' : 'Cargo activado')
    await cargarCargos()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  }
}

watch(filtroActivos, () => {
  pagina.value = 1
  cargarCargos()
})

onMounted(cargarCargos)
</script>

<style scoped>
.cargos-page {
  width: 100%;
}
</style>
