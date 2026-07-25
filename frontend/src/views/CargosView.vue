<template>
  <div class="cargos-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nuevo Cargo
      </v-btn>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <v-text-field
          v-model="buscar"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por nombre o descripción..."
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="cargos-search"
          @update:model-value="onBuscar"
        />
        <div class="d-flex flex-column flex-sm-row align-sm-center ga-3">
          <div class="d-flex flex-wrap ga-2 justify-center">
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
          <div v-if="total > 0" class="text-body-2 text-medium-emphasis text-center">
            {{ total }} resultado{{ total !== 1 ? 's' : '' }}
          </div>
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

        <!-- Mobile: card list -->
        <div v-else-if="!cargando && cargos.length > 0 && mobile" key="mobile-list" class="cargos-mobile-list">
          <div v-for="cargo in cargos" :key="cargo.id" class="cargos-mobile-card pa-4 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="cargo.activo ? 'success' : 'grey'" size="36" rounded="lg">
                  <v-icon :icon="cargo.activo ? 'mdi-check' : 'mdi-minus'" size="18" color="white" />
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ cargo.nombre }}</div>
                  <div v-if="cargo.descripcion" class="text-body-2 text-medium-emphasis">{{ cargo.descripcion }}</div>
                </div>
              </div>
              <v-chip :color="cargo.activo ? 'success' : 'grey'" variant="elevated" size="x-small" label class="font-weight-bold">
                {{ cargo.activo ? 'Activo' : 'Inactivo' }}
              </v-chip>
            </div>
            <div class="d-flex justify-end ga-1">
              <v-btn icon size="x-small" variant="text" color="primary" @click="abrirEditar(cargo)">
                <v-icon icon="mdi-pencil-outline" size="16" />
              </v-btn>
              <v-btn
                icon
                size="x-small"
                variant="text"
                :color="cargo.activo ? 'error' : 'success'"
                @click="toggleEstado(cargo)"
              >
                <v-icon :icon="cargo.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="16" />
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Desktop: table -->
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
        <span class="text-body-2 text-medium-emphasis">{{ pagina }}/{{ totalPaginas }}</span>
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

    <v-dialog v-model="dialogAbierto" :max-width="mobile ? undefined : 480" :fullscreen="mobile" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ tituloDialog }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            v-if="errores._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="errores._global = null"
          >
            {{ errores._global }}
          </v-alert>
          <v-form @submit.prevent="guardar">
            <v-text-field
              v-model="form.nombre"
              label="Nombre *"
              placeholder="Ej: ASP, Supervisor..."
              variant="outlined"
              density="comfortable"
              :error-messages="errores.nombre"
              maxlength="100"
              counter="100"
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
          <v-tooltip :disabled="formValido" location="top">
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="primary"
                  :disabled="!formValido"
                  :loading="guardando"
                  class="text-none text-body-1"
                  @click="guardar"
                >
                  {{ editando ? 'Actualizar' : 'Crear' }}
                </v-btn>
              </span>
            </template>
            <span>Complete el nombre del cargo</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'

const toast = useToast()
const { mobile } = useDisplay()

const cargos = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => mobile.value ? 10 : 20)
const filtroActivos = ref('todos')
const buscar = ref('')

const dialogAbierto = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref({ nombre: '', descripcion: '' })
const errores = ref({})
const tituloDialog = ref('Nuevo Cargo')

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))
const formValido = computed(() => {
  const n = form.value.nombre.trim()
  return n.length > 0 && n.length <= 100
})

async function cargarCargos() {
  cargando.value = true
  try {
    const soloActivos = filtroActivos.value === 'activos'
    const res = await cargoApi.listar(soloActivos, pagina.value, tamanoPagina.value, buscar.value || null)
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
  cargarCargos().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
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
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string' && detail.toLowerCase().includes('nombre')) {
      errores.value = { nombre: detail }
    } else {
      const fieldErrors = {}
      const detailArr = e?.response?.data?.detail
      if (Array.isArray(detailArr)) {
        for (const item of detailArr) {
          const msg = (item?.msg || '').replace(/^Value error,\s*/i, '')
          if (msg) {
            if (!fieldErrors._global) fieldErrors._global = msg
            else fieldErrors._global += '. ' + msg
          }
        }
      }
      if (fieldErrors._global) {
        errores.value = fieldErrors
      } else {
        toast.error(normalizeApiError(e, 'Error al guardar'))
      }
    }
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
watch(mobile, () => { pagina.value = 1; cargarCargos() })

function debounce(fn, ms) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

const onBuscar = debounce(() => {
  pagina.value = 1
  cargarCargos()
}, 300)

onMounted(cargarCargos)
</script>

<style scoped>
.cargos-page {
  width: 100%;
}

.cargos-search {
  flex-grow: 1;
}

.cargos-mobile-list {
  display: flex;
  flex-direction: column;
}

.cargos-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}
</style>
