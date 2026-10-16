<template>
  <div class="config-page mx-auto">
    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <v-tabs v-model="tab" color="primary" class="mb-2">
        <v-tab value="franjas" prepend-icon="mdi-clock-outline">Franjas</v-tab>
        <v-tab value="feriados" prepend-icon="mdi-calendar-star-outline">Feriados</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <!-- Pestaña Franjas -->
        <v-window-item value="franjas">
          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            icon="mdi-information-outline"
            class="mb-4"
          >
            El sexo y los días de cada franja no se editan. Solo puede ajustar el horario y si
            está activa.
          </v-alert>

          <div aria-live="polite">
            <SkeletonList v-if="cargandoFranjas" :filas="2" />

            <div v-else-if="franjas.length === 0" class="text-center py-12">
              <v-icon icon="mdi-clock-outline" size="48" color="grey-lighten-1" class="mb-2" />
              <p class="text-body-1 text-medium-emphasis">No hay franjas configuradas</p>
            </div>

            <v-row v-else>
              <v-col v-for="franja in franjas" :key="franja.id" cols="12" md="6">
                <v-card variant="outlined" rounded="lg" class="pa-4 h-100">
                  <div class="d-flex align-center justify-space-between mb-3">
                    <span class="text-subtitle-1 font-weight-bold text-capitalize">{{ franja.nombre }}</span>
                    <v-chip
                      size="small"
                      variant="tonal"
                      :color="franja.sexo_permitido === 'masculino' ? 'primary' : 'secondary'"
                    >
                      {{ franja.sexo_permitido === 'masculino' ? 'Masculino' : 'Femenino' }}
                    </v-chip>
                  </div>

                  <div class="mb-3">
                    <div class="text-caption text-medium-emphasis mb-1">Días</div>
                    <div class="d-flex flex-wrap ga-1">
                      <v-chip
                        v-for="dia in franja.dias_semana"
                        :key="dia"
                        size="x-small"
                        variant="tonal"
                        label
                      >
                        {{ DIAS[dia] }}
                      </v-chip>
                    </div>
                  </div>

                  <v-row dense>
                    <v-col cols="6">
                      <v-menu v-model="franja._menuInicio" :close-on-content-click="false" location="bottom start">
                        <template #activator="{ props: menuProps }">
                          <v-text-field
                            :model-value="franja._hora_inicio"
                            label="Hora de inicio"
                            readonly
                            append-inner-icon="mdi-clock-outline"
                            variant="outlined"
                            density="comfortable"
                            hide-details="auto"
                            :error-messages="franja._error ? [franja._error] : []"
                            v-bind="menuProps"
                          />
                        </template>
                        <v-card rounded="lg" class="pa-3">
                          <div class="d-flex ga-3 align-center mb-3">
                            <v-select
                              :model-value="horaPart(franja._hora_inicio, 'h')"
                              :items="horasItems"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="hora-select"
                              @update:model-value="setHoraPart(franja, 'inicio', $event, 'h')"
                            />
                            <span class="text-h5 text-medium-emphasis">:</span>
                            <v-select
                              :model-value="horaPart(franja._hora_inicio, 'm')"
                              :items="minutosItems"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="minuto-select"
                              @update:model-value="setHoraPart(franja, 'inicio', $event, 'm')"
                            />
                          </div>
                          <div class="d-flex justify-end">
                            <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="franja._menuInicio = false">Listo</v-btn>
                          </div>
                        </v-card>
                      </v-menu>
                    </v-col>
                    <v-col cols="6">
                      <v-menu v-model="franja._menuFin" :close-on-content-click="false" location="bottom start">
                        <template #activator="{ props: menuProps }">
                          <v-text-field
                            :model-value="franja._hora_fin"
                            label="Hora de fin"
                            readonly
                            append-inner-icon="mdi-clock-outline"
                            variant="outlined"
                            density="comfortable"
                            hide-details="auto"
                            :error-messages="franja._error ? [franja._error] : []"
                            v-bind="menuProps"
                          />
                        </template>
                        <v-card rounded="lg" class="pa-3">
                          <div class="d-flex ga-3 align-center mb-3">
                            <v-select
                              :model-value="horaPart(franja._hora_fin, 'h')"
                              :items="horasItems"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="hora-select"
                              @update:model-value="setHoraPart(franja, 'fin', $event, 'h')"
                            />
                            <span class="text-h5 text-medium-emphasis">:</span>
                            <v-select
                              :model-value="horaPart(franja._hora_fin, 'm')"
                              :items="minutosItems"
                              variant="outlined"
                              density="compact"
                              hide-details
                              class="minuto-select"
                              @update:model-value="setHoraPart(franja, 'fin', $event, 'm')"
                            />
                          </div>
                          <div class="d-flex justify-end">
                            <v-btn size="small" variant="tonal" color="primary" class="text-none" @click="franja._menuFin = false">Listo</v-btn>
                          </div>
                        </v-card>
                      </v-menu>
                    </v-col>
                  </v-row>

                  <v-switch
                    v-model="franja._activa"
                    color="primary"
                    label="Activa"
                    density="comfortable"
                    hide-details
                    class="mt-2"
                  />

                  <div class="d-flex justify-end ga-2 mt-3">
                    <v-btn
                      variant="text"
                      class="text-none"
                      :disabled="!franjaDirty(franja)"
                      @click="resetFranja(franja)"
                    >
                      Descartar
                    </v-btn>
                    <v-btn
                      color="primary"
                      class="text-none"
                      :disabled="!franjaDirty(franja)"
                      :loading="franja._saving"
                      @click="guardarFranja(franja)"
                    >
                      Guardar
                    </v-btn>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </div>
        </v-window-item>

        <!-- Pestaña Feriados -->
        <v-window-item value="feriados">
          <div class="d-flex flex-column flex-sm-row align-sm-center ga-3 pt-3 mb-4">
            <v-select
              v-model="anio"
              :items="anios"
              label="Año"
              variant="outlined"
              density="comfortable"
              hide-details
              class="config-anio"
            />
            <v-spacer />
            <div class="d-flex flex-wrap ga-2 justify-center">
              <v-btn
                variant="tonal"
                color="primary"
                prepend-icon="mdi-calendar-sync-outline"
                class="text-none"
                @click="previsualizarSugeridos"
              >
                Cargar feriados sugeridos
              </v-btn>
              <v-btn color="primary" prepend-icon="mdi-plus" class="text-none" @click="abrirCrearFeriado">
                Nuevo feriado
              </v-btn>
            </div>
          </div>

          <div aria-live="polite">
            <SkeletonList v-if="cargandoFeriados" :filas="4" />

            <Transition name="fade-up" mode="out-in">
              <div v-if="!cargandoFeriados && feriados.length === 0" key="empty" class="text-center py-12">
                <v-icon icon="mdi-calendar-remove-outline" size="48" color="grey-lighten-1" class="mb-2" />
                <p class="text-body-1 text-medium-emphasis">No hay feriados para {{ anio }}</p>
              </div>

              <!-- Mobile -->
              <div v-else-if="!cargandoFeriados && feriados.length > 0 && mobile" key="mobile-list" class="feriados-mobile-list">
                <div v-for="feriado in feriados" :key="feriado.id" class="feriados-mobile-card pa-4 mb-3">
                  <div class="d-flex align-center justify-space-between">
                    <div>
                      <div class="text-body-1 font-weight-medium">{{ formatFechaFeriado(feriado.fecha) }}</div>
                      <div class="text-body-2 text-medium-emphasis">{{ feriado.descripcion }}</div>
                    </div>
                    <div class="d-flex ga-1">
                      <v-btn icon size="x-small" variant="text" color="primary" aria-label="Editar feriado" @click="abrirEditarFeriado(feriado)">
                        <v-icon icon="mdi-pencil-outline" size="16" />
                      </v-btn>
                      <v-btn icon size="x-small" variant="text" color="error" aria-label="Eliminar feriado" @click="confirmarEliminar(feriado)">
                        <v-icon icon="mdi-trash-can-outline" size="16" />
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Desktop -->
              <v-table v-else-if="!cargandoFeriados && feriados.length > 0" key="table" density="comfortable">
                <thead>
                  <tr>
                    <th class="text-body-1 font-weight-bold text-medium-emphasis">Fecha</th>
                    <th class="text-body-1 font-weight-bold text-medium-emphasis">Descripción</th>
                    <th class="text-body-1 font-weight-bold text-medium-emphasis text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="feriado in feriados" :key="feriado.id">
                    <td class="mono text-body-1">{{ formatFechaFeriado(feriado.fecha) }}</td>
                    <td class="text-body-1">{{ feriado.descripcion }}</td>
                    <td class="text-right">
                      <v-tooltip text="Editar feriado" location="top">
                        <template #activator="{ props: tipProps }">
                          <v-btn icon size="small" variant="text" color="primary" aria-label="Editar feriado" v-bind="tipProps" @click="abrirEditarFeriado(feriado)">
                            <v-icon icon="mdi-pencil-outline" size="18" />
                          </v-btn>
                        </template>
                      </v-tooltip>
                      <v-tooltip text="Eliminar feriado" location="top">
                        <template #activator="{ props: tipProps }">
                          <v-btn icon size="small" variant="text" color="error" aria-label="Eliminar feriado" v-bind="tipProps" @click="confirmarEliminar(feriado)">
                            <v-icon icon="mdi-trash-can-outline" size="18" />
                          </v-btn>
                        </template>
                      </v-tooltip>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </Transition>
          </div>
        </v-window-item>
      </v-window>
    </v-card>

    <!-- Dialog crear/editar feriado -->
    <v-dialog v-model="dialogFeriado" :max-width="xs ? undefined : 480" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editandoFeriado ? 'Editar feriado' : 'Nuevo feriado' }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            role="alert"
            v-if="erroresFeriado._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresFeriado._global = null"
          >
            {{ erroresFeriado._global }}
          </v-alert>
          <v-form @submit.prevent="guardarFeriado">
            <v-menu v-model="menuFechaFeriado" :close-on-content-click="false" location="bottom start">
              <template #activator="{ props: menuProps }">
                <v-text-field
                  :model-value="displayFecha(formFeriado.fecha)"
                  label="Fecha *"
                  readonly
                  append-inner-icon="mdi-calendar"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="erroresFeriado.fecha"
                  v-bind="menuProps"
                  class="mb-3"
                />
              </template>
              <v-date-picker v-model="fechaFeriadoDate" color="primary" />
            </v-menu>
            <v-textarea
              v-model="formFeriado.descripcion"
              label="Descripción *"
              variant="outlined"
              density="comfortable"
              :error-messages="erroresFeriado.descripcion"
              rows="2"
              auto-grow
              maxlength="200"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarDialogFeriado">Cancelar</v-btn>
          <v-btn
            color="primary"
            :disabled="!formFeriadoValido"
            :loading="guardandoFeriado"
            class="text-none text-body-1"
            @click="guardarFeriado"
          >
            {{ editandoFeriado ? 'Actualizar' : 'Crear' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog eliminar feriado -->
    <v-dialog v-model="dialogEliminar" max-width="420" persistent>
      <v-card rounded="lg" class="pa-sm-5 pa-3">
        <v-card-title class="d-flex align-center ga-2 text-subtitle-1 font-weight-bold">
          <v-icon color="error">mdi-trash-can-outline</v-icon>
          Eliminar feriado
        </v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          ¿Seguro que deseas eliminar
          <strong class="text-high-emphasis">{{ feriadoEliminar ? formatFechaFeriado(feriadoEliminar.fecha) : '' }}</strong>?
          Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" class="text-none" @click="dialogEliminar = false">Cancelar</v-btn>
          <v-btn color="error" :loading="eliminandoFeriado" class="text-none" @click="eliminarFeriado">
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog sugeridos: vista previa -->
    <v-dialog v-model="dialogSugeridos" :max-width="xs ? undefined : 520" :fullscreen="xs" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Feriados sugeridos {{ anio }}
        </v-card-title>
        <v-card-text class="pa-5">
          <p class="text-body-2 text-medium-emphasis mb-3">
            Se cargarán las siguientes fechas. Las que ya existan se omitirán.
          </p>
          <div v-if="cargandoSugeridos" class="d-flex justify-center py-6">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <v-list v-else density="compact" class="sugeridos-list">
            <v-list-item v-for="s in sugeridos" :key="String(s.fecha)" class="px-0">
              <template #prepend>
                <v-icon icon="mdi-calendar-star-outline" color="primary" size="18" />
              </template>
              <v-list-item-title class="text-body-2">
                {{ formatFechaFeriado(s.fecha) }} · {{ s.descripcion }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogSugeridos = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :disabled="cargandoSugeridos || sugeridos.length === 0"
            :loading="guardandoSugeridos"
            class="text-none text-body-1"
            @click="cargarSugeridos"
          >
            Confirmar ({{ sugeridos.length }})
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { franjaApi } from '../api/franja'
import { feriadoApi } from '../api/feriado'
import { extractFieldErrors, normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const toast = useToast()
const { mobile, xs } = useDisplay()

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const horasItems = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutosItems = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

function horaPart(t, part) {
  const [h, m] = (t || '08:00').split(':')
  return part === 'h' ? (h || '08') : (m || '00')
}

function setHoraPart(franja, campo, val, part) {
  const key = campo === 'inicio' ? '_hora_inicio' : '_hora_fin'
  let [h, m] = (franja[key] || '08:00').split(':')
  if (part === 'h') h = val
  else m = val
  franja[key] = `${h}:${m}`
  franja._error = null
}

function dateToYMD(d) {
  if (!d) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function ymdToDate(s) {
  if (!s) return null
  const [y, m, d] = String(s).split('-').map(Number)
  return new Date(y, m - 1, d)
}

function displayFecha(f) {
  if (!f) return ''
  const [y, m, d] = String(f).split('T')[0].split('-')
  return `${d}/${m}/${y}`
}

const tab = ref('franjas')

// --- Franjas ---
const franjas = ref([])
const cargandoFranjas = ref(true)

async function cargarFranjas() {
  cargandoFranjas.value = true
  try {
    const res = await franjaApi.listar()
    franjas.value = (res.data || []).map((f) => ({
      ...f,
      _hora_inicio: f.hora_inicio,
      _hora_fin: f.hora_fin,
      _activa: f.activa,
      _saving: false,
      _error: null,
      _menuInicio: false,
      _menuFin: false,
    }))
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar franjas'))
  } finally {
    cargandoFranjas.value = false
  }
}

function franjaDirty(franja) {
  return (
    franja._hora_inicio !== franja.hora_inicio
    || franja._hora_fin !== franja.hora_fin
    || franja._activa !== franja.activa
  )
}

function resetFranja(franja) {
  franja._hora_inicio = franja.hora_inicio
  franja._hora_fin = franja.hora_fin
  franja._activa = franja.activa
  franja._error = null
}

async function guardarFranja(franja) {
  franja._error = null
  if (franja._hora_inicio === franja._hora_fin) {
    franja._error = 'La hora de inicio y fin deben ser distintas'
    return
  }
  const payload = {}
  if (franja._hora_inicio !== franja.hora_inicio) payload.hora_inicio = franja._hora_inicio
  if (franja._hora_fin !== franja.hora_fin) payload.hora_fin = franja._hora_fin
  if (franja._activa !== franja.activa) payload.activa = franja._activa

  franja._saving = true
  try {
    const res = await franjaApi.actualizar(franja.id, payload)
    const updated = res.data
    franja.hora_inicio = updated.hora_inicio
    franja.hora_fin = updated.hora_fin
    franja.activa = updated.activa
    resetFranja(franja)
    toast.success('Franja actualizada correctamente')
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    franja._error =
      fieldErrors.hora_fin || fieldErrors.hora_inicio || normalizeApiError(e, 'Error al guardar la franja')
  } finally {
    franja._saving = false
  }
}

// --- Feriados ---
const anioActual = new Date().getFullYear()
const anios = Array.from({ length: 7 }, (_, i) => anioActual - 2 + i)
const anio = ref(anioActual)

const feriados = ref([])
const cargandoFeriados = ref(true)

const dialogFeriado = ref(false)
const editandoFeriado = ref(null)
const guardandoFeriado = ref(false)
const formFeriado = ref({ fecha: '', descripcion: '' })
const erroresFeriado = ref({})

const menuFechaFeriado = ref(false)
const fechaFeriadoDate = computed({
  get() { return ymdToDate(formFeriado.value.fecha) },
  set(val) {
    formFeriado.value.fecha = dateToYMD(val)
    menuFechaFeriado.value = false
  },
})

const dialogEliminar = ref(false)
const feriadoEliminar = ref(null)
const eliminandoFeriado = ref(false)

const dialogSugeridos = ref(false)
const sugeridos = ref([])
const cargandoSugeridos = ref(false)
const guardandoSugeridos = ref(false)

const formFeriadoValido = computed(
  () => !!formFeriado.value.fecha && formFeriado.value.descripcion.trim().length > 0,
)

function formatFechaFeriado(value) {
  if (!value) return '—'
  const [y, m, d] = String(value).split('T')[0].split('-')
  return `${d}/${m}/${y}`
}

async function cargarFeriados() {
  cargandoFeriados.value = true
  try {
    const res = await feriadoApi.listar({ anio: anio.value, page: 1, size: 100 })
    feriados.value = res.data.items || []
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar feriados'))
  } finally {
    cargandoFeriados.value = false
  }
}

function abrirCrearFeriado() {
  editandoFeriado.value = null
  formFeriado.value = { fecha: '', descripcion: '' }
  erroresFeriado.value = {}
  menuFechaFeriado.value = false
  dialogFeriado.value = true
}

function abrirEditarFeriado(feriado) {
  editandoFeriado.value = feriado
  formFeriado.value = { fecha: String(feriado.fecha).split('T')[0], descripcion: feriado.descripcion }
  erroresFeriado.value = {}
  menuFechaFeriado.value = false
  dialogFeriado.value = true
}

function cerrarDialogFeriado() {
  dialogFeriado.value = false
  erroresFeriado.value = {}
  menuFechaFeriado.value = false
}

function validarFeriado() {
  const e = {}
  if (!formFeriado.value.fecha) e.fecha = 'La fecha es requerida'
  if (!formFeriado.value.descripcion.trim()) e.descripcion = 'La descripción es requerida'
  erroresFeriado.value = e
  return Object.keys(e).length === 0
}

async function guardarFeriado() {
  if (!validarFeriado()) return
  guardandoFeriado.value = true
  try {
    const payload = {
      fecha: formFeriado.value.fecha,
      descripcion: formFeriado.value.descripcion.trim(),
    }
    if (editandoFeriado.value) {
      await feriadoApi.actualizar(editandoFeriado.value.id, payload)
      toast.success('Feriado actualizado correctamente')
    } else {
      await feriadoApi.crear(payload)
      toast.success('Feriado creado correctamente')
    }
    cerrarDialogFeriado()
    // Si el feriado se guardó en otro año visible, cambiar el filtro; si no, recargar.
    const nuevoAnio = Number(formFeriado.value.fecha.split('-')[0])
    if (nuevoAnio && nuevoAnio !== anio.value && anios.includes(nuevoAnio)) {
      anio.value = nuevoAnio
    } else {
      await cargarFeriados()
    }
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    const hasFields = Object.keys(fieldErrors).some((k) => k !== '_global')
    if (hasFields) {
      erroresFeriado.value = { ...erroresFeriado.value, ...fieldErrors }
    } else {
      toast.error(fieldErrors._global || normalizeApiError(e, 'Error al guardar el feriado'))
    }
  } finally {
    guardandoFeriado.value = false
  }
}

function confirmarEliminar(feriado) {
  feriadoEliminar.value = feriado
  dialogEliminar.value = true
}

async function eliminarFeriado() {
  eliminandoFeriado.value = true
  try {
    await feriadoApi.eliminar(feriadoEliminar.value.id)
    toast.success('Feriado eliminado')
    dialogEliminar.value = false
    feriadoEliminar.value = null
    await cargarFeriados()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al eliminar el feriado'))
  } finally {
    eliminandoFeriado.value = false
  }
}

async function previsualizarSugeridos() {
  dialogSugeridos.value = true
  sugeridos.value = []
  cargandoSugeridos.value = true
  try {
    const res = await feriadoApi.sugeridos(anio.value)
    sugeridos.value = res.data.sugeridos || []
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al obtener los feriados sugeridos'))
    dialogSugeridos.value = false
  } finally {
    cargandoSugeridos.value = false
  }
}

async function cargarSugeridos() {
  guardandoSugeridos.value = true
  try {
    const res = await feriadoApi.cargarSugeridos(anio.value)
    const { creados, omitidos } = res.data
    toast.success(`Feriados cargados: ${creados} creados, ${omitidos} omitidos`)
    dialogSugeridos.value = false
    await cargarFeriados()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar los feriados sugeridos'))
  } finally {
    guardandoSugeridos.value = false
  }
}

watch(anio, cargarFeriados)

onMounted(() => {
  cargarFranjas()
  cargarFeriados()
})
</script>

<style scoped>
.config-page {
  width: 100%;
}

.config-anio {
  max-width: 180px;
}

.hora-select,
.minuto-select {
  min-width: 70px;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.feriados-mobile-list {
  display: flex;
  flex-direction: column;
}

.feriados-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.sugeridos-list {
  max-height: 320px;
  overflow-y: auto;
}

@media (max-width: 599px) {
  .config-anio {
    max-width: 100%;
  }
}
</style>
