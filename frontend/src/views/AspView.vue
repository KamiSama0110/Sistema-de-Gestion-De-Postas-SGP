<template>
  <div class="asp-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nuevo ASP
      </v-btn>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-column flex-sm-row align-sm-center justify-sm-space-between mb-4 ga-3">
        <v-text-field
          v-model="buscar"
          prepend-inner-icon="mdi-magnify"
          placeholder="Buscar por nombre, apellidos o CI..."
          variant="solo-filled"
          density="compact"
          hide-details
          clearable
          bg-color="grey-lighten-4"
          class="asp-search"
          @update:model-value="onBuscar"
        />
        <div class="d-flex flex-column flex-sm-row align-sm-center ga-3">
          <div class="d-flex flex-wrap ga-2 justify-center">
            <v-btn
              :variant="filtroEstado === 'activo' ? 'flat' : 'outlined'"
              :color="filtroEstado === 'activo' ? 'primary' : 'default'"
              size="small"
              class="text-none"
              @click="cambiarFiltro('activo')"
            >
              Activos
            </v-btn>
            <v-btn
              v-for="est in estadosDisponibles"
              :key="est.value"
              :variant="filtroEstado === est.value ? 'flat' : 'outlined'"
              :color="filtroEstado === est.value ? est.color : 'default'"
              size="small"
              class="text-none"
              @click="cambiarFiltro(est.value)"
            >
              {{ est.label }}
            </v-btn>
            <v-btn
              :variant="filtroEstado === 'todos' ? 'flat' : 'outlined'"
              :color="filtroEstado === 'todos' ? 'primary' : 'default'"
              size="small"
              class="text-none"
              @click="cambiarFiltro('todos')"
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
        <SkeletonList v-if="cargando" :filas="6" />

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && asps.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-account-group-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-1 text-medium-emphasis">No hay ASP para mostrar</p>
          </div>

          <!-- Mobile: card list -->
          <div v-else-if="!cargando && asps.length > 0 && mobile" key="mobile-list" class="asp-mobile-list">
          <div v-for="asp in asps" :key="asp.id" class="asp-mobile-card pa-4 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="estadoColor(asp.estado)" size="36" rounded="lg">
                  <span class="text-white text-body-2 font-weight-bold">{{ asp.nombre.charAt(0) }}{{ asp.apellidos.charAt(0) }}</span>
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ asp.nombre }} {{ asp.apellidos }}</div>
                  <div class="text-body-2 text-medium-emphasis mono">{{ asp.ci }}</div>
                </div>
              </div>
              <v-chip :color="estadoColor(asp.estado)" variant="elevated" size="x-small" label class="font-weight-bold">
                {{ estadoLabel(asp.estado) }}
              </v-chip>
            </div>
            <div class="d-flex align-center justify-space-between">
              <span class="text-body-2 text-medium-emphasis">{{ cargoMap[asp.cargo_id] || '—' }}</span>
              <div class="d-flex ga-1">
                <v-btn icon size="x-small" variant="text" aria-label="Ver ficha" @click="abrirFicha(asp)">
                  <v-icon icon="mdi-eye-outline" size="16" />
                </v-btn>
                <v-btn icon size="x-small" variant="text" color="primary" aria-label="Editar ASP" @click="abrirEditar(asp)">
                  <v-icon icon="mdi-pencil-outline" size="16" />
                </v-btn>
                <v-btn icon size="x-small" variant="text" color="warning" aria-label="Cambiar estado" @click="abrirEstado(asp)">
                  <v-icon icon="mdi-swap-horizontal" size="16" />
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: table -->
        <v-table v-else-if="!cargando && asps.length > 0" key="table" density="comfortable">
          <thead>
            <tr>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">CI</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Nombre</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Apellidos</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Cargo</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asp in asps" :key="asp.id">
              <td class="mono text-body-1">{{ asp.ci }}</td>
              <td class="font-weight-medium text-body-1">{{ asp.nombre }}</td>
              <td class="text-body-1">{{ asp.apellidos }}</td>
              <td class="text-medium-emphasis text-body-1">{{ cargoMap[asp.cargo_id] || '—' }}</td>
              <td>
                <v-chip
                  :color="estadoColor(asp.estado)"
                  variant="elevated"
                  size="small"
                  label
                  class="font-weight-bold"
                >
                  {{ estadoLabel(asp.estado) }}
                </v-chip>
              </td>
              <td class="text-center">
                <v-tooltip text="Ver ficha" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" aria-label="Ver ficha" v-bind="tipProps" @click="abrirFicha(asp)">
                      <v-icon icon="mdi-eye-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="Editar ASP" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="primary" aria-label="Editar ASP" v-bind="tipProps" @click="abrirEditar(asp)">
                      <v-icon icon="mdi-pencil-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="Cambiar estado" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="warning" aria-label="Cambiar estado" v-bind="tipProps" @click="abrirEstado(asp)">
                      <v-icon icon="mdi-swap-horizontal" size="18" />
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

    <!-- Dialog ficha ASP -->
    <v-dialog v-model="dialogFicha" :max-width="mobile ? undefined : 600" :fullscreen="mobile">
      <v-card rounded="lg" v-if="fichaAsp">
        <v-card-title class="d-flex align-center justify-space-between pa-6 pb-2">
          <span class="text-h6 font-weight-bold">{{ fichaAsp.nombre }} {{ fichaAsp.apellidos }}</span>
          <v-chip :color="estadoColor(fichaAsp.estado)" variant="elevated" size="small" label class="font-weight-bold">
            {{ estadoLabel(fichaAsp.estado) }}
          </v-chip>
        </v-card-title>
        <v-card-text class="pa-6 pt-4">
          <div class="ficha-section mb-5">
            <div class="ficha-section-title mb-3">Datos personales</div>
            <div class="ficha-grid">
              <div class="ficha-item">
                <span class="ficha-label">CI</span>
                <span class="ficha-value mono">{{ fichaAsp.ci }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Sexo</span>
                <span class="ficha-value">{{ fichaAsp.sexo === 'masculino' ? 'Masculino' : 'Femenino' }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Fecha de nacimiento</span>
                <span class="ficha-value">{{ formatFecha(fichaAsp.fecha_nacimiento) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Teléfono</span>
                <span class="ficha-value">{{ fichaAsp.telefono || '—' }}</span>
              </div>
              <div class="ficha-item ficha-full">
                <span class="ficha-label">Dirección</span>
                <span class="ficha-value">{{ fichaAsp.direccion || '—' }}</span>
              </div>
            </div>
          </div>

          <v-divider class="mb-5" />

          <div class="ficha-section mb-5">
            <div class="ficha-section-title mb-3">Datos laborales</div>
            <div class="ficha-grid">
              <div class="ficha-item">
                <span class="ficha-label">Cargo</span>
                <span class="ficha-value">{{ cargoMap[fichaAsp.cargo_id] || '—' }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Escolaridad</span>
                <span class="ficha-value">{{ escolaridadLabel(fichaAsp.nivel_escolaridad) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Fecha de ingreso</span>
                <span class="ficha-value">{{ formatFecha(fichaAsp.fecha_ingreso) }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Estado</span>
                <span class="ficha-value font-weight-bold" :class="`text-${estadoColor(fichaAsp.estado)}`">{{ estadoLabel(fichaAsp.estado) }}</span>
              </div>
            </div>
          </div>

          <div v-if="fichaAsp.observaciones" class="ficha-section mb-4">
            <v-divider class="mb-5" />
            <div class="ficha-section-title mb-3">Observaciones</div>
            <p class="text-body-1">{{ fichaAsp.observaciones }}</p>
          </div>

          <v-divider class="mb-4" />
          <div class="d-flex flex-column flex-sm-row ga-2 flex-sm-wrap text-caption text-medium-emphasis">
            <span>Creado: {{ formatFechaHora(fichaAsp.creado_en) }}</span>
            <span>Actualizado: {{ formatFechaHora(fichaAsp.actualizado_en) }}</span>
          </div>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogFicha = false">Cerrar</v-btn>
          <v-btn color="primary" variant="tonal" class="text-none text-body-1" @click="dialogFicha = false; abrirEditar(fichaAsp)">
            Editar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog crear/editar -->
    <v-dialog v-model="dialogForm" :max-width="mobile ? undefined : 640" :fullscreen="mobile" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ tituloForm }}
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
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.ci"
                  label="CI *"
                  placeholder="00000000000"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.ci"
                  maxlength="11"
                  counter="11"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.sexo"
                  label="Sexo *"
                  :items="sexoItems"
                  item-title="label"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.sexo"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.nombre"
                  label="Nombre *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.nombre"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.apellidos"
                  label="Apellidos *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.apellidos"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-menu v-model="menuNacimiento" :close-on-content-click="false" location="bottom start">
                  <template #activator="{ props: menuProps }">
                    <v-text-field
                      :model-value="displayFecha(form.fecha_nacimiento)"
                      label="Fecha de nacimiento *"
                      readonly
                      append-inner-icon="mdi-calendar"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="errores.fecha_nacimiento"
                      v-bind="menuProps"
                      class="mb-1"
                    />
                  </template>
                  <v-date-picker v-model="nacimientoDate" color="primary" />
                </v-menu>
              </v-col>
              <v-col cols="12" sm="6">
                <v-menu v-model="menuIngreso" :close-on-content-click="false" location="bottom start">
                  <template #activator="{ props: menuProps }">
                    <v-text-field
                      :model-value="displayFecha(form.fecha_ingreso)"
                      label="Fecha de ingreso *"
                      readonly
                      append-inner-icon="mdi-calendar"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="errores.fecha_ingreso"
                      v-bind="menuProps"
                      class="mb-1"
                    />
                  </template>
                  <v-date-picker v-model="ingresoDate" color="primary" />
                </v-menu>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.cargo_id"
                  label="Cargo *"
                  :items="cargosList"
                  item-title="nombre"
                  item-value="id"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.cargo_id"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.nivel_escolaridad"
                  label="Nivel de escolaridad *"
                  :items="escolaridadItems"
                  item-title="label"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.nivel_escolaridad"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.telefono"
                  label="Teléfono (opcional)"
                  placeholder="+53XXXXXXXX"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.telefono"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.direccion"
                  label="Dirección (opcional)"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.direccion"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-textarea
              v-model="form.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.observaciones"
              rows="2"
              auto-grow
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
            <span>Complete todos los campos obligatorios</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog cambiar estado -->
    <v-dialog v-model="dialogEstado" :max-width="mobile ? undefined : 420" :fullscreen="mobile" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Cambiar estado
        </v-card-title>
        <v-card-text class="pa-5">
          <p v-if="aspEstado" class="text-body-1 mb-4">
            <strong>{{ aspEstado.nombre }} {{ aspEstado.apellidos }}</strong> — CI: {{ aspEstado.ci }}
          </p>
          <p class="text-body-2 text-medium-emphasis mb-3">
            Estado actual: <strong :class="`text-${estadoColor(aspEstado?.estado)}`">{{ estadoLabel(aspEstado?.estado) }}</strong>
          </p>
          <v-select
            v-model="estadoForm.estado"
            label="Nuevo estado"
            :items="transicionesPermitidas"
            item-title="label"
            item-value="value"
            variant="outlined"
            density="comfortable"
            :error-messages="erroresEstado.estado"
            class="mb-2"
          />
          <v-textarea
            v-model="estadoForm.observacion"
            label="Observación (opcional)"
            variant="outlined"
            density="comfortable"
            rows="2"
            auto-grow
          />
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarEstado">Cancelar</v-btn>
          <v-tooltip :disabled="!!estadoForm.estado" location="top">
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="primary"
                  :disabled="!estadoForm.estado"
                  :loading="guardandoEstado"
                  class="text-none text-body-1"
                  @click="confirmarEstado"
                >
                  Confirmar
                </v-btn>
              </span>
            </template>
            <span>Seleccione un estado destino</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { aspApi } from '../api/asp'
import { cargoApi } from '../api/cargo'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const toast = useToast()
const { mobile } = useDisplay()

const asps = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => mobile.value ? 10 : 20)
const buscar = ref('')
const filtroEstado = ref('todos')
const cargoMap = ref({})
const cargosList = ref([])

const dialogForm = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref(emptyForm())
const errores = ref({})

const menuNacimiento = ref(false)
const menuIngreso = ref(false)

function dateToYMD(d) {
  if (!d) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function ymdToDate(s) {
  if (!s) return null
  const [y, m, d] = s.split('-').map(Number)
  return new Date(y, m - 1, d)
}

const nacimientoDate = computed({
  get() { return ymdToDate(form.value.fecha_nacimiento) },
  set(val) {
    form.value.fecha_nacimiento = dateToYMD(val)
    menuNacimiento.value = false
  },
})

const ingresoDate = computed({
  get() { return ymdToDate(form.value.fecha_ingreso) },
  set(val) {
    form.value.fecha_ingreso = dateToYMD(val)
    menuIngreso.value = false
  },
})

const dialogFicha = ref(false)
const fichaAsp = ref(null)

const dialogEstado = ref(false)
const aspEstado = ref(null)
const guardandoEstado = ref(false)
const estadoForm = ref({ estado: null, observacion: '' })
const erroresEstado = ref({})

const sexoItems = [
  { label: 'Masculino', value: 'masculino' },
  { label: 'Femenino', value: 'femenino' },
]

const escolaridadItems = [
  { label: 'Primaria', value: 'primaria' },
  { label: 'Secundaria', value: 'secundaria' },
  { label: 'Preuniversitario', value: 'preuniversitario' },
  { label: 'Técnico Medio', value: 'tecnico_medio' },
  { label: 'Universitario', value: 'universitario' },
]

const estadosDisponibles = [
  { label: 'Suspendidos', value: 'suspendido', color: 'warning' },
  { label: 'Baja Temporal', value: 'baja_temporal', color: 'orange' },
  { label: 'Baja Definitiva', value: 'baja_definitiva', color: 'error' },
]

const TRANSICIONES = {
  activo: ['baja_temporal', 'baja_definitiva', 'suspendido'],
  suspendido: ['activo'],
  baja_temporal: ['activo'],
  baja_definitiva: [],
}

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))
const tituloForm = computed(() => (editando.value ? 'Editar ASP' : 'Nuevo ASP'))

const transicionesPermitidas = computed(() => {
  if (!aspEstado.value) return []
  const destinos = TRANSICIONES[aspEstado.value.estado] || []
  return destinos.map((v) => ({ label: estadoLabel(v), value: v }))
})

const formValido = computed(() => {
  const f = form.value
  return (
    f.ci.trim().length === 11
    && /^\d{11}$/.test(f.ci.trim())
    && f.nombre.trim().length > 0
    && f.apellidos.trim().length > 0
    && !!f.fecha_nacimiento
    && !!f.sexo
    && !!f.nivel_escolaridad
    && !!f.fecha_ingreso
    && !!f.cargo_id
  )
})

function emptyForm() {
  return {
    ci: '',
    nombre: '',
    apellidos: '',
    fecha_nacimiento: '',
    sexo: null,
    nivel_escolaridad: null,
    telefono: '',
    direccion: '',
    fecha_ingreso: '',
    cargo_id: null,
    observaciones: '',
  }
}

function estadoColor(estado) {
  const map = { activo: 'success', suspendido: 'warning', baja_temporal: 'orange', baja_definitiva: 'error' }
  return map[estado] || 'grey'
}

function estadoLabel(estado) {
  const map = { activo: 'Activo', suspendido: 'Suspendido', baja_temporal: 'Baja Temporal', baja_definitiva: 'Baja Definitiva' }
  return map[estado] || estado
}

function escolaridadLabel(val) {
  const map = {
    primaria: 'Primaria', secundaria: 'Secundaria', preuniversitario: 'Preuniversitario',
    tecnico_medio: 'Técnico Medio', universitario: 'Universitario',
  }
  return map[val] || val
}

function displayFecha(f) {
  if (!f) return ''
  const [y, m, d] = f.split('-')
  return `${d}/${m}/${y}`
}

function formatFecha(f) {
  if (!f) return '—'
  const d = new Date(f + 'T00:00:00')
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatFechaHora(f) {
  if (!f) return '—'
  const d = new Date(f)
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function calcularEdad(fechaNac) {
  const hoy = new Date()
  const nac = new Date(fechaNac + 'T00:00:00')
  let edad = hoy.getFullYear() - nac.getFullYear()
  const mes = hoy.getMonth() - nac.getMonth()
  if (mes < 0 || (mes === 0 && hoy.getDate() < nac.getDate())) edad--
  return edad
}

function mapBackendErrors(e) {
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    const msg = detail.replace(/^Value error,\s*/i, '')
    const field = inferFieldFromMessage(msg)
    return field ? { [field]: msg } : { _global: msg }
  }
  if (Array.isArray(detail)) {
    const knownFields = ['ci', 'nombre', 'apellidos', 'sexo', 'fecha_nacimiento', 'fecha_ingreso', 'nivel_escolaridad', 'cargo_id', 'telefono', 'direccion', 'observaciones']
    const fields = {}
    for (const item of detail) {
      const rawField = item?.loc?.[item.loc.length - 1]
      const msg = (item?.msg || '').replace(/^Value error,\s*/i, '')
      if (!msg) continue
      const field = knownFields.includes(rawField) ? rawField : inferFieldFromMessage(msg)
      if (field) {
        fields[field] = msg
      } else {
        fields._global = (fields._global ? fields._global + '. ' : '') + msg
      }
    }
    if (Object.keys(fields).length) return fields
  }
  const fallback = normalizeApiError(e, '')
  return fallback ? { _global: fallback } : {}
}

function inferFieldFromMessage(msg) {
  const lower = msg.toLowerCase()
  if (lower.includes('ci') || lower.includes('dígito') || lower.includes('septimo')) return 'ci'
  if (lower.includes('nacimiento')) return 'fecha_nacimiento'
  if (lower.includes('ingreso')) return 'fecha_ingreso'
  if (lower.includes('sexo')) return 'sexo'
  if (lower.includes('telefono') || lower.includes('teléfono')) return 'telefono'
  if (lower.includes('nombre') || lower.includes('vacio') || lower.includes('vacío')) return 'nombre'
  if (lower.includes('apellido')) return 'apellidos'
  if (lower.includes('escolaridad')) return 'nivel_escolaridad'
  if (lower.includes('direccion') || lower.includes('dirección')) return 'direccion'
  if (lower.includes('observacion')) return 'observaciones'
  return null
}

function debounce(fn, ms) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

const onBuscar = debounce(() => {
  pagina.value = 1
  cargarAsps()
}, 300)

async function cargarCargos() {
  try {
    const res = await cargoApi.listar(true, 1, 100)
    const items = res.data.items || []
    cargosList.value = items
    const map = {}
    for (const c of items) {
      map[c.id] = c.nombre
    }
    cargoMap.value = map
  } catch {
    toast.error('Error al cargar cargos')
  }
}

async function cargarAsps() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtroEstado.value !== 'todos') params.estado = filtroEstado.value
    if (buscar.value && buscar.value.trim()) params.buscar = buscar.value.trim()
    const res = await aspApi.listar(params)
    asps.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar ASP'))
  } finally {
    cargando.value = false
  }
}

function cambiarFiltro(valor) {
  filtroEstado.value = valor
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarAsps().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

async function abrirFicha(asp) {
  dialogFicha.value = true
  fichaAsp.value = null
  try {
    const res = await aspApi.obtener(asp.id)
    fichaAsp.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar ficha'))
    dialogFicha.value = false
  }
}

function abrirCrear() {
  editando.value = null
  form.value = emptyForm()
  errores.value = {}
  dialogForm.value = true
}

async function abrirEditar(asp) {
  editando.value = asp
  try {
    const res = await aspApi.obtener(asp.id)
    const full = res.data
    form.value = {
      ci: full.ci,
      nombre: full.nombre,
      apellidos: full.apellidos,
      fecha_nacimiento: full.fecha_nacimiento || '',
      sexo: full.sexo,
      nivel_escolaridad: full.nivel_escolaridad,
      telefono: full.telefono || '',
      direccion: full.direccion || '',
      fecha_ingreso: full.fecha_ingreso || '',
      cargo_id: full.cargo_id,
      observaciones: full.observaciones || '',
    }
  } catch (e) {
    form.value = {
      ci: asp.ci,
      nombre: asp.nombre,
      apellidos: asp.apellidos,
      fecha_nacimiento: '',
      sexo: null,
      nivel_escolaridad: null,
      telefono: '',
      direccion: '',
      fecha_ingreso: '',
      cargo_id: asp.cargo_id,
      observaciones: '',
    }
    toast.error(normalizeApiError(e, 'No se pudieron cargar todos los datos'))
  }
  errores.value = {}
  dialogForm.value = true
}

function cerrarForm() {
  dialogForm.value = false
  errores.value = {}
}

function abrirEstado(asp) {
  aspEstado.value = asp
  estadoForm.value = { estado: null, observacion: '' }
  erroresEstado.value = {}
  dialogEstado.value = true
}

function cerrarEstado() {
  dialogEstado.value = false
  aspEstado.value = null
  erroresEstado.value = {}
}

function validar() {
  const e = {}
  const f = form.value
  if (!f.ci.trim()) e.ci = 'El CI es requerido'
  else if (!/^\d{11}$/.test(f.ci.trim())) e.ci = 'El CI debe tener 11 dígitos numéricos'
  if (!f.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (!f.apellidos.trim()) e.apellidos = 'Los apellidos son requeridos'
  if (!f.sexo) e.sexo = 'El sexo es requerido'
  if (!f.nivel_escolaridad) e.nivel_escolaridad = 'El nivel de escolaridad es requerido'
  if (!f.cargo_id) e.cargo_id = 'El cargo es requerido'

  if (!f.fecha_nacimiento) {
    e.fecha_nacimiento = 'La fecha de nacimiento es requerida'
  } else {
    const edad = calcularEdad(f.fecha_nacimiento)
    if (edad < 18) e.fecha_nacimiento = 'El ASP debe tener al menos 18 años'
    else if (edad > 100) e.fecha_nacimiento = 'La fecha de nacimiento no es válida'
  }

  if (!f.fecha_ingreso) {
    e.fecha_ingreso = 'La fecha de ingreso es requerida'
  } else if (f.fecha_nacimiento && !e.fecha_nacimiento) {
    const ingreso = new Date(f.fecha_ingreso + 'T00:00:00')
    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)
    if (ingreso > hoy) {
      e.fecha_ingreso = 'La fecha de ingreso no puede ser futura'
    } else {
      const nac = new Date(f.fecha_nacimiento + 'T00:00:00')
      const minIngreso = new Date(nac)
      minIngreso.setFullYear(minIngreso.getFullYear() + 18)
      if (ingreso < minIngreso) {
        e.fecha_ingreso = 'Debe haber al menos 18 años entre nacimiento e ingreso'
      }
    }
  }

  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = {
      ci: form.value.ci.trim(),
      nombre: form.value.nombre.trim(),
      apellidos: form.value.apellidos.trim(),
      fecha_nacimiento: form.value.fecha_nacimiento,
      sexo: form.value.sexo,
      nivel_escolaridad: form.value.nivel_escolaridad,
      fecha_ingreso: form.value.fecha_ingreso,
      cargo_id: form.value.cargo_id,
    }
    if (form.value.telefono.trim()) payload.telefono = form.value.telefono.trim()
    if (form.value.direccion.trim()) payload.direccion = form.value.direccion.trim()
    if (form.value.observaciones.trim()) payload.observaciones = form.value.observaciones.trim()

    if (editando.value) {
      await aspApi.actualizar(editando.value.id, payload)
      toast.success('ASP actualizado correctamente')
    } else {
      await aspApi.crear(payload)
      toast.success('ASP creado correctamente')
    }
    cerrarForm()
    await cargarAsps()
  } catch (e) {
    const fieldErrors = mapBackendErrors(e)
    if (Object.keys(fieldErrors).length > 0 && !fieldErrors._global) {
      errores.value = { ...errores.value, ...fieldErrors }
    } else {
      toast.error(fieldErrors._global || normalizeApiError(e, 'Error al guardar'))
    }
  } finally {
    guardando.value = false
  }
}

function validarEstado() {
  const e = {}
  if (!estadoForm.value.estado) e.estado = 'Seleccioná un estado destino'
  erroresEstado.value = e
  return Object.keys(e).length === 0
}

async function confirmarEstado() {
  if (!validarEstado()) return
  guardandoEstado.value = true
  try {
    const payload = { estado: estadoForm.value.estado }
    if (estadoForm.value.observacion.trim()) payload.observacion = estadoForm.value.observacion.trim()
    await aspApi.cambiarEstado(aspEstado.value.id, payload)
    toast.success('Estado actualizado correctamente')
    cerrarEstado()
    await cargarAsps()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  } finally {
    guardandoEstado.value = false
  }
}

watch(filtroEstado, () => {
  pagina.value = 1
  cargarAsps()
})
watch(mobile, () => { pagina.value = 1; cargarAsps() })

onMounted(() => {
  cargarCargos()
  cargarAsps()
})
</script>

<style scoped>
.asp-page {
  width: 100%;
}

.asp-search {
  flex-grow: 1;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.ficha-section-title {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(0, 0, 0, 0.45);
}

.ficha-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}

.ficha-full {
  grid-column: 1 / -1;
}

.ficha-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ficha-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.45);
}

.ficha-value {
  font-size: 0.9375rem;
  color: rgba(0, 0, 0, 0.87);
  line-height: 1.4;
}

.asp-mobile-list {
  display: flex;
  flex-direction: column;
}

.asp-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@media (max-width: 599px) {
  .asp-search {
    max-width: 100%;
  }

  .ficha-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
