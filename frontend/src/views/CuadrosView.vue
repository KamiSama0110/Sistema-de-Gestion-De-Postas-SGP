<template>
  <div class="cuadros-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nuevo Cuadro
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
          class="cuadros-search"
          @update:model-value="onBuscar"
        />
        <div v-if="total > 0" class="text-body-2 text-medium-emphasis text-center">
          {{ total }} resultado{{ total !== 1 ? 's' : '' }}
        </div>
      </div>

      <div class="d-flex flex-wrap align-center justify-center ga-2 mb-4">
        <v-btn
          v-for="op in filtrosSexo"
          :key="op.value"
          :variant="filtroSexo === op.value ? 'flat' : 'outlined'"
          :color="filtroSexo === op.value ? 'primary' : 'default'"
          size="small"
          class="text-none"
          @click="filtroSexo = op.value"
        >
          {{ op.label }}
        </v-btn>
        <v-divider vertical class="mx-1" />
        <v-btn
          v-for="op in filtrosActivo"
          :key="op.value"
          :variant="filtroActivo === op.value ? 'flat' : 'outlined'"
          :color="filtroActivo === op.value ? 'primary' : 'default'"
          size="small"
          class="text-none"
          @click="filtroActivo = op.value"
        >
          {{ op.label }}
        </v-btn>
        <v-divider vertical class="mx-1" />
        <v-btn
          :variant="filtroVieDom ? 'flat' : 'outlined'"
          :color="filtroVieDom ? 'secondary' : 'default'"
          prepend-icon="mdi-calendar-weekend-outline"
          size="small"
          class="text-none"
          @click="filtroVieDom = !filtroVieDom"
        >
          Sin vie-dom
        </v-btn>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="6" />

        <Transition name="fade-up" mode="out-in">
          <div v-if="!cargando && cuadros.length === 0" key="empty" class="text-center py-12">
            <v-icon icon="mdi-account-tie-outline" size="48" color="grey-lighten-1" class="mb-2" />
            <p class="text-body-1 text-medium-emphasis">No hay cuadros para mostrar</p>
          </div>

          <!-- Mobile: card list -->
          <div v-else-if="!cargando && cuadros.length > 0 && mobile" key="mobile-list" class="cuadros-mobile-list">
            <div v-for="cuadro in cuadros" :key="cuadro.id" class="cuadros-mobile-card pa-4 mb-3">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-3">
                  <v-avatar :color="cuadro.activo ? 'primary' : 'grey'" size="36" rounded="lg">
                    <span class="text-white text-body-2 font-weight-bold">
                      {{ cuadro.nombre.charAt(0) }}{{ cuadro.apellidos.charAt(0) }}
                    </span>
                  </v-avatar>
                  <div>
                    <div class="text-body-1 font-weight-medium">{{ cuadro.nombre }} {{ cuadro.apellidos }}</div>
                    <div class="text-body-2 text-medium-emphasis mono">{{ cuadro.ci || '—' }}</div>
                  </div>
                </div>
                <v-chip :color="cuadro.activo ? 'success' : 'grey'" variant="elevated" size="x-small" label class="font-weight-bold">
                  {{ cuadro.activo ? 'Activo' : 'Inactivo' }}
                </v-chip>
              </div>
              <div class="text-body-2 text-medium-emphasis mb-2">
                {{ cuadro.cargo }} · {{ cuadro.area }}
              </div>
              <div class="d-flex align-center justify-space-between">
                <div class="d-flex ga-1">
                  <v-chip size="x-small" variant="tonal" label>
                    {{ cuadro.sexo === 'masculino' ? 'Masculino' : 'Femenino' }}
                  </v-chip>
                  <v-chip v-if="cuadro.sin_guardia_vie_dom" size="x-small" variant="tonal" color="secondary" label>
                    Sin vie-dom
                  </v-chip>
                </div>
                <div class="d-flex ga-1">
                  <v-btn icon size="x-small" variant="text" color="primary" aria-label="Editar cuadro" @click="abrirEditar(cuadro)">
                    <v-icon icon="mdi-pencil-outline" size="16" />
                  </v-btn>
                  <v-btn icon size="x-small" variant="text" aria-label="Cuenta de acceso" @click="abrirCuenta(cuadro)">
                    <v-icon icon="mdi-account-key-outline" size="16" />
                  </v-btn>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    :color="cuadro.activo ? 'error' : 'success'"
                    aria-label="Cambiar estado"
                    @click="toggleEstado(cuadro)"
                  >
                    <v-icon :icon="cuadro.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="16" />
                  </v-btn>
                </div>
              </div>
            </div>
          </div>

          <!-- Desktop: table -->
          <v-table v-else-if="!cargando && cuadros.length > 0" key="table" density="comfortable">
            <thead>
              <tr>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Nombre</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">CI</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Cargo</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Área</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Sexo</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Sin vie-dom</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
                <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cuadro in cuadros" :key="cuadro.id">
                <td class="font-weight-medium text-body-1">{{ cuadro.nombre }} {{ cuadro.apellidos }}</td>
                <td class="mono text-body-1">{{ cuadro.ci || '—' }}</td>
                <td class="text-medium-emphasis text-body-1">{{ cuadro.cargo }}</td>
                <td class="text-medium-emphasis text-body-1">{{ cuadro.area }}</td>
                <td class="text-body-1">{{ cuadro.sexo === 'masculino' ? 'Masculino' : 'Femenino' }}</td>
                <td class="text-center">
                  <v-icon
                    :icon="cuadro.sin_guardia_vie_dom ? 'mdi-check-circle-outline' : 'mdi-minus'"
                    :color="cuadro.sin_guardia_vie_dom ? 'secondary' : 'grey-lighten-1'"
                    size="18"
                  />
                </td>
                <td>
                  <v-chip
                    :color="cuadro.activo ? 'success' : 'grey'"
                    variant="elevated"
                    size="small"
                    label
                    class="font-weight-bold"
                  >
                    {{ cuadro.activo ? 'Activo' : 'Inactivo' }}
                  </v-chip>
                </td>
                <td class="text-center">
                  <v-tooltip text="Editar cuadro" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" color="primary" aria-label="Editar cuadro" v-bind="tipProps" @click="abrirEditar(cuadro)">
                        <v-icon icon="mdi-pencil-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip text="Cuenta de acceso" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn icon size="small" variant="text" aria-label="Cuenta de acceso" v-bind="tipProps" @click="abrirCuenta(cuadro)">
                        <v-icon icon="mdi-account-key-outline" size="18" />
                      </v-btn>
                    </template>
                  </v-tooltip>
                  <v-tooltip :text="cuadro.activo ? 'Desactivar cuadro' : 'Activar cuadro'" location="top">
                    <template #activator="{ props: tipProps }">
                      <v-btn
                        icon
                        size="small"
                        variant="text"
                        :color="cuadro.activo ? 'error' : 'success'"
                        aria-label="Cambiar estado"
                        v-bind="tipProps"
                        @click="toggleEstado(cuadro)"
                      >
                        <v-icon :icon="cuadro.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="18" />
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

    <!-- Dialog crear/editar -->
    <v-dialog v-model="dialogForm" :max-width="xs ? undefined : 680" :fullscreen="xs" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editando ? 'Editar Cuadro' : 'Nuevo Cuadro' }}
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
                  v-model="form.nombre"
                  label="Nombre *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.nombre"
                  maxlength="100"
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
                  maxlength="150"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  :model-value="form.ci"
                  label="CI *"
                  placeholder="00000000000"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.ci"
                  maxlength="11"
                  counter="11"
                  inputmode="numeric"
                  class="mb-1"
                  @update:model-value="onCIInput"
                  @keydown="bloquearTeclaCI"
                  @paste="bloquearPasteCI"
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
                  v-model="form.cargo"
                  label="Cargo *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.cargo"
                  maxlength="100"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.area"
                  label="Área *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.area"
                  maxlength="100"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-text-field
              v-model="form.telefono"
              label="Teléfono (opcional)"
              placeholder="+53XXXXXXXX"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.telefono"
              class="mb-1"
            />
            <v-switch
              v-model="form.sin_guardia_vie_dom"
              color="primary"
              label="No se le asigna guardia de viernes a domingo"
              density="comfortable"
              hide-details
              class="mb-1"
            />
            <v-textarea
              v-model="form.observaciones"
              label="Observaciones (opcional)"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.observaciones"
              rows="2"
              auto-grow
              class="mt-3"
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

    <!-- Dialog cuenta de acceso -->
    <v-dialog v-model="dialogCuenta" :max-width="xs ? undefined : 460" :fullscreen="xs" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          Cuenta de acceso
        </v-card-title>
        <v-card-text class="pa-5">
          <p v-if="cuentaCuadro" class="text-body-2 text-medium-emphasis mb-4">
            <strong class="text-high-emphasis">{{ cuentaCuadro.nombre }} {{ cuentaCuadro.apellidos }}</strong>
          </p>

          <div v-if="cargandoCuenta" class="d-flex justify-center py-6">
            <v-progress-circular indeterminate color="primary" />
          </div>

          <template v-else-if="cuenta && cuenta.existe">
            <v-alert type="info" variant="tonal" density="compact" class="mb-4" icon="mdi-account-check-outline">
              Usuario: <strong>{{ cuenta.username }}</strong>
            </v-alert>
            <v-form @submit.prevent="cambiarPassword">
              <v-text-field
                v-model="cuentaForm.password_nueva"
                label="Nueva contraseña"
                :type="mostrarPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                :error-messages="erroresCuenta.password_nueva"
                hint="Mínimo 8 caracteres"
                persistent-hint
                autocomplete="new-password"
                @update:model-value="erroresCuenta.password_nueva = null"
              >
                <template #append-inner>
                  <v-btn
                    :icon="mostrarPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                    :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    variant="text"
                    size="small"
                    density="comfortable"
                    @click="mostrarPassword = !mostrarPassword"
                  />
                </template>
              </v-text-field>
            </v-form>
          </template>

          <template v-else>
            <v-alert type="warning" variant="tonal" density="compact" class="mb-4" icon="mdi-account-off-outline">
              Este cuadro no tiene cuenta de acceso.
            </v-alert>
            <v-form @submit.prevent="crearCuenta">
              <v-text-field
                v-model="cuentaForm.username"
                label="Usuario"
                variant="outlined"
                density="comfortable"
                :error-messages="erroresCuenta.username"
                hint="Mínimo 3 caracteres"
                persistent-hint
                autocomplete="off"
                class="mb-3"
                @update:model-value="erroresCuenta.username = null"
              />
              <v-text-field
                v-model="cuentaForm.password"
                label="Contraseña"
                :type="mostrarPassword ? 'text' : 'password'"
                variant="outlined"
                density="comfortable"
                :error-messages="erroresCuenta.password"
                hint="Mínimo 8 caracteres"
                persistent-hint
                autocomplete="new-password"
                @update:model-value="erroresCuenta.password = null"
              >
                <template #append-inner>
                  <v-btn
                    :icon="mostrarPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                    :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    variant="text"
                    size="small"
                    density="comfortable"
                    @click="mostrarPassword = !mostrarPassword"
                  />
                </template>
              </v-text-field>
            </v-form>
          </template>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarCuenta">Cerrar</v-btn>
          <v-btn
            v-if="!cargandoCuenta && cuenta && cuenta.existe"
            color="primary"
            :disabled="!passwordNuevaValida"
            :loading="guardandoCuenta"
            class="text-none text-body-1"
            @click="cambiarPassword"
          >
            Cambiar contraseña
          </v-btn>
          <v-btn
            v-else-if="!cargandoCuenta && cuenta && !cuenta.existe"
            color="primary"
            :disabled="!cuentaValida"
            :loading="guardandoCuenta"
            class="text-none text-body-1"
            @click="crearCuenta"
          >
            Crear cuenta
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { cuadroApi } from '../api/cuadro'
import { extractFieldErrors, normalizeApiError } from '../utils/error'
import { soloDigitos } from '../utils/formatters'
import { useToast } from '../composables/useToast'
import SkeletonList from '../components/SkeletonList.vue'

const toast = useToast()
const { mobile, xs } = useDisplay()

const cuadros = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => (mobile.value ? 10 : 20))
const buscar = ref('')
const filtroSexo = ref(null)
const filtroActivo = ref('todos')
const filtroVieDom = ref(false)

const sexoItems = [
  { label: 'Masculino', value: 'masculino' },
  { label: 'Femenino', value: 'femenino' },
]
const filtrosSexo = [
  { label: 'Ambos sexos', value: null },
  { label: 'Masculino', value: 'masculino' },
  { label: 'Femenino', value: 'femenino' },
]
const filtrosActivo = [
  { label: 'Todos', value: 'todos' },
  { label: 'Activos', value: 'activos' },
  { label: 'Inactivos', value: 'inactivos' },
]

const dialogForm = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref(emptyForm())
const errores = ref({})

const dialogCuenta = ref(false)
const cuentaCuadro = ref(null)
const cuenta = ref(null)
const cargandoCuenta = ref(false)
const guardandoCuenta = ref(false)
const cuentaForm = ref({ username: '', password: '', password_nueva: '' })
const erroresCuenta = ref({})
const mostrarPassword = ref(false)

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))

const formValido = computed(() => {
  const f = form.value
  return (
    f.nombre.trim().length > 0
    && f.apellidos.trim().length > 0
    && /^\d{11}$/.test(f.ci.trim())
    && f.cargo.trim().length > 0
    && f.area.trim().length > 0
    && !!f.sexo
  )
})

const cuentaValida = computed(
  () => cuentaForm.value.username.trim().length >= 3 && cuentaForm.value.password.length >= 8,
)
const passwordNuevaValida = computed(() => cuentaForm.value.password_nueva.length >= 8)

function emptyForm() {
  return {
    nombre: '',
    apellidos: '',
    ci: '',
    cargo: '',
    area: '',
    telefono: '',
    sexo: null,
    sin_guardia_vie_dom: false,
    observaciones: '',
  }
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
  cargarCuadros()
}, 300)

async function cargarCuadros() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (buscar.value && buscar.value.trim()) params.q = buscar.value.trim()
    if (filtroSexo.value) params.sexo = filtroSexo.value
    if (filtroActivo.value === 'activos') params.activo = true
    else if (filtroActivo.value === 'inactivos') params.activo = false
    if (filtroVieDom.value) params.sin_guardia_vie_dom = true
    const res = await cuadroApi.listar(params)
    cuadros.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar cuadros'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarCuadros().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function abrirCrear() {
  editando.value = null
  form.value = emptyForm()
  errores.value = {}
  dialogForm.value = true
}

function abrirEditar(cuadro) {
  editando.value = cuadro
  form.value = {
    nombre: cuadro.nombre,
    apellidos: cuadro.apellidos,
    ci: cuadro.ci || '',
    cargo: cuadro.cargo,
    area: cuadro.area,
    telefono: cuadro.telefono || '',
    sexo: cuadro.sexo,
    sin_guardia_vie_dom: cuadro.sin_guardia_vie_dom,
    observaciones: cuadro.observaciones || '',
  }
  errores.value = {}
  dialogForm.value = true
}

function cerrarForm() {
  dialogForm.value = false
  errores.value = {}
}

function onCIInput(valor) {
  form.value.ci = soloDigitos(valor, 11)
}

function bloquearTeclaCI(e) {
  if (e.ctrlKey || e.metaKey || e.altKey) return
  if (e.key.length === 1 && !/\d/.test(e.key)) e.preventDefault()
}

function bloquearPasteCI(e) {
  const texto = e.clipboardData?.getData('text') ?? ''
  if (/^\d*$/.test(texto)) return
  e.preventDefault()
  const digitos = soloDigitos(texto, 11)
  if (!digitos) return
  const el = e.target
  const inicio = el.selectionStart ?? el.value.length
  const fin = el.selectionEnd ?? inicio
  form.value.ci = soloDigitos(el.value.slice(0, inicio) + digitos + el.value.slice(fin), 11)
}

function validar() {
  const e = {}
  const f = form.value
  if (!f.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (!f.apellidos.trim()) e.apellidos = 'Los apellidos son requeridos'
  if (!f.ci.trim()) e.ci = 'El CI es requerido'
  else if (!/^\d{11}$/.test(f.ci.trim())) e.ci = 'El CI debe tener 11 dígitos numéricos'
  else if (f.sexo) {
    const septimo = Number(f.ci.trim()[6])
    if (f.sexo === 'masculino' && septimo % 2 !== 0) e.ci = 'El séptimo dígito del CI debe ser par para masculino'
    if (f.sexo === 'femenino' && septimo % 2 === 0) e.ci = 'El séptimo dígito del CI debe ser impar para femenino'
  }
  if (!f.cargo.trim()) e.cargo = 'El cargo es requerido'
  if (!f.area.trim()) e.area = 'El área es requerida'
  if (!f.sexo) e.sexo = 'El sexo es requerido'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      apellidos: form.value.apellidos.trim(),
      ci: form.value.ci.trim(),
      cargo: form.value.cargo.trim(),
      area: form.value.area.trim(),
      sexo: form.value.sexo,
      sin_guardia_vie_dom: form.value.sin_guardia_vie_dom,
    }
    if (form.value.telefono.trim()) payload.telefono = form.value.telefono.trim()
    if (form.value.observaciones.trim()) payload.observaciones = form.value.observaciones.trim()

    if (editando.value) {
      await cuadroApi.actualizar(editando.value.id, payload)
      toast.success('Cuadro actualizado correctamente')
    } else {
      await cuadroApi.crear(payload)
      toast.success('Cuadro creado correctamente')
    }
    cerrarForm()
    await cargarCuadros()
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    const hasFields = Object.keys(fieldErrors).some((k) => k !== '_global')
    if (hasFields) {
      errores.value = { ...errores.value, ...fieldErrors }
    } else {
      toast.error(fieldErrors._global || normalizeApiError(e, 'Error al guardar'))
    }
  } finally {
    guardando.value = false
  }
}

async function toggleEstado(cuadro) {
  try {
    await cuadroApi.cambiarEstado(cuadro.id, !cuadro.activo)
    toast.success(cuadro.activo ? 'Cuadro desactivado' : 'Cuadro activado')
    await cargarCuadros()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  }
}

async function abrirCuenta(cuadro) {
  cuentaCuadro.value = cuadro
  cuenta.value = null
  cuentaForm.value = { username: '', password: '', password_nueva: '' }
  erroresCuenta.value = {}
  mostrarPassword.value = false
  dialogCuenta.value = true
  cargandoCuenta.value = true
  try {
    const res = await cuadroApi.obtenerCuenta(cuadro.id)
    cuenta.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar la cuenta'))
    dialogCuenta.value = false
  } finally {
    cargandoCuenta.value = false
  }
}

function cerrarCuenta() {
  dialogCuenta.value = false
  mostrarPassword.value = false
}

async function crearCuenta() {
  if (!cuentaValida.value) {
    const e = {}
    if (cuentaForm.value.username.trim().length < 3) e.username = 'El usuario debe tener al menos 3 caracteres'
    if (cuentaForm.value.password.length < 8) e.password = 'La contraseña debe tener al menos 8 caracteres'
    erroresCuenta.value = e
    return
  }
  guardandoCuenta.value = true
  try {
    const res = await cuadroApi.crearCuenta(cuentaCuadro.value.id, {
      username: cuentaForm.value.username.trim(),
      password: cuentaForm.value.password,
    })
    cuenta.value = res.data
    cuentaForm.value.password = ''
    toast.success('Cuenta de acceso creada correctamente')
    cerrarCuenta()
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    if (fieldErrors.username || fieldErrors.password) {
      erroresCuenta.value = fieldErrors
    } else {
      toast.error(normalizeApiError(e, 'Error al crear la cuenta'))
    }
  } finally {
    guardandoCuenta.value = false
  }
}

async function cambiarPassword() {
  if (!passwordNuevaValida.value) {
    erroresCuenta.value = { password_nueva: 'La contraseña debe tener al menos 8 caracteres' }
    return
  }
  guardandoCuenta.value = true
  try {
    await cuadroApi.cambiarPassword(cuentaCuadro.value.id, cuentaForm.value.password_nueva)
    cuentaForm.value.password_nueva = ''
    toast.success('Contraseña actualizada correctamente')
    cerrarCuenta()
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    if (fieldErrors.password_nueva) {
      erroresCuenta.value = fieldErrors
    } else {
      toast.error(normalizeApiError(e, 'Error al cambiar la contraseña'))
    }
  } finally {
    guardandoCuenta.value = false
  }
}

watch(filtroSexo, () => { pagina.value = 1; cargarCuadros() })
watch(filtroActivo, () => { pagina.value = 1; cargarCuadros() })
watch(filtroVieDom, () => { pagina.value = 1; cargarCuadros() })
watch(mobile, () => { pagina.value = 1; cargarCuadros() })

onMounted(cargarCuadros)
</script>

<style scoped>
.cuadros-page {
  width: 100%;
}

.cuadros-search {
  flex-grow: 1;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.cuadros-mobile-list {
  display: flex;
  flex-direction: column;
}

.cuadros-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@media (max-width: 599px) {
  .cuadros-search {
    max-width: 100%;
  }
}
</style>
