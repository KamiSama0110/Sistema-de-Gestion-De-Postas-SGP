<template>
  <div class="turnos-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nuevo Turno
      </v-btn>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <v-text-field
          v-model="buscar"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por nombre..."
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="turnos-search"
          @update:model-value="onBuscar"
        />
        <div class="d-flex flex-column flex-sm-row align-sm-center ga-3">
          <div class="d-flex flex-wrap ga-2 justify-center">
            <v-select
              v-model="filtroPostaId"
              :items="postasList"
              item-title="nombre"
              item-value="id"
              label="Posta"
              variant="solo-filled"
              density="compact"
              hide-details
              clearable
              bg-color="grey-lighten-4"
              class="turnos-posta-select"
              @update:model-value="pagina = 1; cargarTurnos()"
            />
          </div>
          <div class="d-flex ga-2 justify-center">
            <v-btn
              :variant="filtroActivo === 'activos' ? 'flat' : 'outlined'"
              :color="filtroActivo === 'activos' ? 'success' : 'default'"
              size="small"
              class="text-none"
              @click="filtroActivo = 'activos'"
            >
              Activos
            </v-btn>
            <v-btn
              :variant="filtroActivo === 'todos' ? 'flat' : 'outlined'"
              :color="filtroActivo === 'todos' ? 'primary' : 'default'"
              size="small"
              class="text-none"
              @click="filtroActivo = 'todos'"
            >
              Todos
            </v-btn>
          </div>
          <div v-if="total > 0" class="text-body-2 text-medium-emphasis text-center">
            {{ total }} resultado{{ total !== 1 ? 's' : '' }}
          </div>
        </div>
      </div>

      <div aria-live="polite">
        <div v-if="cargando" class="d-flex align-center justify-center py-12">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && turnos.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-clock-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-1 text-medium-emphasis">No hay turnos para mostrar</p>
          </div>

          <!-- Mobile: card list -->
          <div v-else-if="!cargando && turnos.length > 0 && mobile" key="mobile-list" class="turnos-mobile-list">
          <div v-for="turno in turnos" :key="turno.id" class="turnos-mobile-card pa-4 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="turno.activo ? 'primary' : 'grey'" size="36" rounded="lg">
                  <v-icon icon="mdi-clock-outline" size="18" color="white" />
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ turno.nombre }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ turno.posta_nombre }}</div>
                </div>
              </div>
              <v-chip :color="turno.activo ? 'success' : 'grey'" variant="elevated" size="x-small" label class="font-weight-bold">
                {{ turno.activo ? 'Activo' : 'Inactivo' }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis mb-2">
              {{ turno.hora_inicio?.slice(0, 5) }} – {{ turno.hora_fin?.slice(0, 5) }}
              <span v-if="turno.cruza_medianoche" class="text-warning ms-1">(medianoche)</span>
              <span class="ms-2">{{ turno.asp_requeridos }} ASP{{ turno.asp_requeridos > 1 ? 's' : '' }}</span>
            </div>
            <div class="d-flex justify-end ga-1">
              <v-btn icon size="x-small" variant="text" color="primary" aria-label="Editar turno" @click="abrirEditar(turno)">
                <v-icon icon="mdi-pencil-outline" size="16" />
              </v-btn>
              <v-btn
                icon
                size="x-small"
                variant="text"
                :color="turno.activo ? 'error' : 'success'"
                aria-label="Cambiar estado"
                @click="toggleActivo(turno)"
              >
                <v-icon :icon="turno.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="16" />
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Desktop: table -->
        <v-table v-else-if="!cargando && turnos.length > 0" key="table" density="comfortable">
          <thead>
            <tr>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Nombre</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Posta</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Horario</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">ASP</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="turno in turnos" :key="turno.id">
              <td class="font-weight-medium text-body-1">{{ turno.nombre }}</td>
              <td class="text-medium-emphasis text-body-1">{{ turno.posta_nombre }}</td>
              <td class="text-body-1">
                {{ turno.hora_inicio?.slice(0, 5) }} – {{ turno.hora_fin?.slice(0, 5) }}
                <v-icon v-if="turno.cruza_medianoche" icon="mdi-weather-night" size="14" color="warning" class="ms-1" />
              </td>
              <td class="text-medium-emphasis text-body-1">{{ turno.asp_requeridos }}</td>
              <td>
                <v-chip
                  :color="turno.activo ? 'success' : 'grey'"
                  variant="elevated"
                  size="small"
                  label
                  class="font-weight-bold"
                >
                  {{ turno.activo ? 'Activo' : 'Inactivo' }}
                </v-chip>
              </td>
              <td class="text-center">
                <v-tooltip text="Editar turno" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="primary" aria-label="Editar turno" v-bind="tipProps" @click="abrirEditar(turno)">
                      <v-icon icon="mdi-pencil-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip :text="turno.activo ? 'Desactivar' : 'Activar'" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn
                      icon
                      size="small"
                      variant="text"
                      :color="turno.activo ? 'error' : 'success'"
                      aria-label="Cambiar estado"
                      v-bind="tipProps"
                      @click="toggleActivo(turno)"
                    >
                      <v-icon :icon="turno.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
              </td>
            </tr>
          </tbody>
        </v-table>
      </Transition>
      </div>

      <div v-if="totalPaginas > 1" class="d-flex align-center justify-center ga-2 mt-4">
        <v-btn icon size="small" variant="text" :disabled="pagina === 1" aria-label="Página anterior" @click="cambiarPagina(-1)">
          <v-icon icon="mdi-chevron-left" />
        </v-btn>
        <span class="text-body-2 text-medium-emphasis">{{ pagina }}/{{ totalPaginas }}</span>
        <v-btn icon size="small" variant="text" :disabled="pagina >= totalPaginas" aria-label="Página siguiente" @click="cambiarPagina(1)">
          <v-icon icon="mdi-chevron-right" />
        </v-btn>
      </div>
    </v-card>

    <!-- Dialog crear/editar turno -->
    <v-dialog v-model="dialogForm" :max-width="mobile ? undefined : 480" :fullscreen="mobile" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editando ? 'Editar Turno' : 'Nuevo Turno' }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
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
            <v-select
              v-if="!editando"
              v-model="form.posta_id"
              label="Posta *"
              :items="postasList"
              item-title="nombre"
              item-value="id"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.posta_id"
              class="mb-3"
            />
            <v-text-field
              v-model="form.nombre"
              label="Nombre *"
              placeholder="Ej: Turno A, Turno mañana..."
              variant="outlined"
              density="comfortable"
              :error-messages="errores.nombre"
              maxlength="50"
              counter="50"
              class="mb-3"
            />
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-menu v-model="menuHoraInicio" :close-on-content-click="false" location="bottom start">
                  <template #activator="{ props: menuProps }">
                    <v-text-field
                      :model-value="form.hora_inicio || ''"
                      label="Hora inicio *"
                      readonly
                      append-inner-icon="mdi-clock-outline"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="errores.hora_inicio"
                      v-bind="menuProps"
                      class="mb-1"
                    />
                  </template>
                  <v-card rounded="lg" class="pa-3">
                    <div class="d-flex ga-3 align-center mb-3">
                      <v-select
                        v-model="horaInicioHora"
                        :items="horasItems"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="hora-select"
                      />
                      <span class="text-h5 text-medium-emphasis">:</span>
                      <v-select
                        v-model="horaInicioMinuto"
                        :items="minutosItems"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="minuto-select"
                      />
                    </div>
                    <div class="d-flex justify-end">
                      <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuHoraInicio = false">Listo</v-btn>
                    </div>
                  </v-card>
                </v-menu>
              </v-col>
              <v-col cols="12" sm="6">
                <v-menu v-model="menuHoraFin" :close-on-content-click="false" location="bottom start">
                  <template #activator="{ props: menuProps }">
                    <v-text-field
                      :model-value="form.hora_fin || ''"
                      label="Hora fin *"
                      readonly
                      append-inner-icon="mdi-clock-outline"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="errores.hora_fin"
                      v-bind="menuProps"
                      class="mb-1"
                    />
                  </template>
                  <v-card rounded="lg" class="pa-3">
                    <div class="d-flex ga-3 align-center mb-3">
                      <v-select
                        v-model="horaFinHora"
                        :items="horasItems"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="hora-select"
                      />
                      <span class="text-h5 text-medium-emphasis">:</span>
                      <v-select
                        v-model="horaFinMinuto"
                        :items="minutosItems"
                        variant="outlined"
                        density="compact"
                        hide-details
                        class="minuto-select"
                      />
                    </div>
                    <div class="d-flex justify-end">
                      <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="menuHoraFin = false">Listo</v-btn>
                    </div>
                  </v-card>
                </v-menu>
              </v-col>
            </v-row>
            <v-text-field
              v-model.number="form.asp_requeridos"
              label="ASP requeridos *"
              type="number"
              min="1"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.asp_requeridos"
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarForm">Cancelar</v-btn>
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
            <span>Complete posta, nombre, horas y ASP requeridos</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { postaApi } from '../api/posta'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'

const toast = useToast()
const { mobile } = useDisplay()

const turnos = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => mobile.value ? 10 : 20)
const buscar = ref('')
const filtroPostaId = ref(null)
const filtroActivo = ref('activos')

const postasList = ref([])

const dialogForm = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref(emptyForm())
const errores = ref({})

const menuHoraInicio = ref(false)
const menuHoraFin = ref(false)

const horasItems = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutosItems = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))
const formValido = computed(() => {
  const f = form.value
  if (editando.value) {
    return f.nombre.trim().length > 0 && f.hora_inicio && f.hora_fin && f.asp_requeridos >= 1
  }
  return f.posta_id && f.nombre.trim().length > 0 && f.hora_inicio && f.hora_fin && f.asp_requeridos >= 1
})

function timeToParts(t) {
  if (!t) return { h: '08', m: '00' }
  const [h, m] = t.split(':')
  return { h: h || '08', m: m || '00' }
}

function partsToTime(h, m) {
  return `${h}:${m}`
}

const horaInicioHora = computed({
  get() { return timeToParts(form.value.hora_inicio).h },
  set(val) { form.value.hora_inicio = partsToTime(val, timeToParts(form.value.hora_inicio).m) },
})
const horaInicioMinuto = computed({
  get() { return timeToParts(form.value.hora_inicio).m },
  set(val) { form.value.hora_inicio = partsToTime(timeToParts(form.value.hora_inicio).h, val) },
})
const horaFinHora = computed({
  get() { return timeToParts(form.value.hora_fin).h },
  set(val) { form.value.hora_fin = partsToTime(val, timeToParts(form.value.hora_fin).m) },
})
const horaFinMinuto = computed({
  get() { return timeToParts(form.value.hora_fin).m },
  set(val) { form.value.hora_fin = partsToTime(timeToParts(form.value.hora_fin).h, val) },
})

function emptyForm() {
  return { posta_id: null, nombre: '', hora_inicio: '', hora_fin: '', asp_requeridos: 1 }
}

function debounce(fn, ms) {
  let timer
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms) }
}

const onBuscar = debounce(() => { pagina.value = 1; cargarTurnos() }, 300)

async function cargarPostasList() {
  try {
    const res = await postaApi.listar({ size: 100 })
    postasList.value = res.data.items || []
  } catch {
    postasList.value = []
  }
}

async function cargarTurnos() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtroPostaId.value) params.posta_id = filtroPostaId.value
    if (filtroActivo.value === 'activos') params.activo = true
    if (buscar.value?.trim()) params.buscar = buscar.value.trim()
    const res = await postaApi.listarTurnos(params)
    turnos.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar turnos'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarTurnos().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function abrirCrear() {
  editando.value = null
  form.value = emptyForm()
  errores.value = {}
  dialogForm.value = true
}

function abrirEditar(turno) {
  editando.value = turno
  form.value = {
    posta_id: turno.posta_id,
    nombre: turno.nombre,
    hora_inicio: turno.hora_inicio?.slice(0, 5) || '',
    hora_fin: turno.hora_fin?.slice(0, 5) || '',
    asp_requeridos: turno.asp_requeridos || 1,
  }
  errores.value = {}
  dialogForm.value = true
}

function cerrarForm() {
  dialogForm.value = false
  errores.value = {}
}

function validar() {
  const e = {}
  const f = form.value
  if (!editando.value && !f.posta_id) e.posta_id = 'Seleccione una posta'
  if (!f.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (!f.hora_inicio) e.hora_inicio = 'Requerido'
  if (!f.hora_fin) e.hora_fin = 'Requerido'
  if (f.hora_inicio && f.hora_fin && f.hora_inicio === f.hora_fin) {
    e.hora_fin = 'Debe ser diferente a hora inicio'
  }
  if (!f.asp_requeridos || f.asp_requeridos < 1) e.asp_requeridos = 'Mínimo 1'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      hora_inicio: form.value.hora_inicio,
      hora_fin: form.value.hora_fin,
      asp_requeridos: form.value.asp_requeridos,
    }
    if (editando.value) {
      await postaApi.actualizarTurno(editando.value.id, payload)
      toast.success('Turno actualizado')
    } else {
      await postaApi.agregarTurno(form.value.posta_id, payload)
      toast.success('Turno creado')
    }
    cerrarForm()
    await cargarTurnos()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      errores.value = { _global: detail }
    } else {
      const fieldErrors = {}
      if (Array.isArray(detail)) {
        for (const item of detail) {
          const msg = (item?.msg || '').replace(/^Value error,\s*/i, '')
          if (msg) {
            if (!fieldErrors._global) fieldErrors._global = msg
            else fieldErrors._global += '. ' + msg
          }
        }
      }
      if (fieldErrors._global) errores.value = fieldErrors
      else toast.error(normalizeApiError(e, 'Error al guardar turno'))
    }
  } finally {
    guardando.value = false
  }
}

async function toggleActivo(turno) {
  try {
    await postaApi.cambiarEstadoTurno(turno.id, !turno.activo)
    toast.success(turno.activo ? 'Turno desactivado' : 'Turno activado')
    await cargarTurnos()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  }
}

watch(filtroActivo, () => { pagina.value = 1; cargarTurnos() })
watch(mobile, () => { pagina.value = 1; cargarTurnos() })

onMounted(() => {
  Promise.all([cargarPostasList(), cargarTurnos()])
})
</script>

<style scoped>
.turnos-page {
  width: 100%;
}

.turnos-search {
  flex-grow: 1;
}

.turnos-posta-select {
  min-width: 180px;
  max-width: 240px;
}

.turnos-mobile-list {
  display: flex;
  flex-direction: column;
}

.turnos-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.hora-select,
.minuto-select {
  min-width: 70px;
}

@media (max-width: 599px) {
  .turnos-search {
    max-width: 100%;
  }

  .turnos-posta-select {
    min-width: 100%;
    max-width: 100%;
  }
}
</style>
