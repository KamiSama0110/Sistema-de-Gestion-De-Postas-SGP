<template>
  <div class="postas-page mx-auto">
    <div class="d-flex align-center justify-end mb-6">
      <v-btn color="primary" prepend-icon="mdi-plus" @click="abrirCrear">
        Nueva Posta
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
          class="postas-search"
          @update:model-value="onBuscar"
        />
        <div class="d-flex flex-column flex-sm-row align-sm-center ga-3">
          <div class="d-flex flex-wrap ga-2 justify-center">
            <v-btn
              :variant="filtroTipo === 'todos' ? 'flat' : 'outlined'"
              :color="filtroTipo === 'todos' ? 'primary' : 'default'"
              size="small"
              class="text-none"
              @click="filtroTipo = 'todos'"
            >
              Todos
            </v-btn>
            <v-btn
              v-for="t in tipoItems"
              :key="t.value"
              :variant="filtroTipo === t.value ? 'flat' : 'outlined'"
              :color="filtroTipo === t.value ? t.color : 'default'"
              size="small"
              class="text-none"
              @click="filtroTipo = t.value"
            >
              {{ t.label }}
            </v-btn>
          </div>
          <div class="d-flex ga-2 justify-center">
            <v-btn
              :variant="filtroActiva === 'activas' ? 'flat' : 'outlined'"
              :color="filtroActiva === 'activas' ? 'success' : 'default'"
              size="small"
              class="text-none"
              @click="filtroActiva = 'activas'"
            >
              Activas
            </v-btn>
            <v-btn
              :variant="filtroActiva === 'todas' ? 'flat' : 'outlined'"
              :color="filtroActiva === 'todas' ? 'primary' : 'default'"
              size="small"
              class="text-none"
              @click="filtroActiva = 'todas'"
            >
              Todas
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
        <div v-if="!cargando && postas.length === 0" key="empty" class="text-center py-12">
          <v-icon icon="mdi-office-building-outline" size="48" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-1 text-medium-emphasis">No hay postas para mostrar</p>
        </div>

        <!-- Mobile: card list -->
        <div v-else-if="!cargando && postas.length > 0 && mobile" key="mobile-list" class="postas-mobile-list">
          <div v-for="posta in postas" :key="posta.id" class="postas-mobile-card pa-4 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center ga-3">
                <v-avatar :color="posta.activa ? 'primary' : 'grey'" size="36" rounded="lg">
                  <v-icon :icon="tipoIcon(posta.tipo)" size="18" color="white" />
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ posta.nombre }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ tipoLabel(posta.tipo) }}</div>
                </div>
              </div>
              <v-chip :color="posta.activa ? 'success' : 'grey'" variant="elevated" size="x-small" label class="font-weight-bold">
                {{ posta.activa ? 'Activa' : 'Inactiva' }}
              </v-chip>
            </div>
            <div class="d-flex align-center justify-space-between">
              <span class="text-body-2 text-medium-emphasis">{{ posta.total_turnos }} turno{{ posta.total_turnos !== 1 ? 's' : '' }}</span>
              <div class="d-flex ga-1">
                <v-btn icon size="x-small" variant="text" @click="abrirFicha(posta)">
                  <v-icon icon="mdi-eye-outline" size="16" />
                </v-btn>
                <v-btn icon size="x-small" variant="text" color="primary" @click="abrirEditar(posta)">
                  <v-icon icon="mdi-pencil-outline" size="16" />
                </v-btn>
                <v-btn
                  icon
                  size="x-small"
                  variant="text"
                  :color="posta.activa ? 'error' : 'success'"
                  @click="toggleActiva(posta)"
                >
                  <v-icon :icon="posta.activa ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="16" />
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: table -->
        <v-table v-else-if="!cargando && postas.length > 0" key="table" density="comfortable">
          <thead>
            <tr>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Nombre</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Tipo</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Turnos</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Estado</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="posta in postas" :key="posta.id">
              <td class="font-weight-medium text-body-1">{{ posta.nombre }}</td>
              <td>
                <v-chip size="small" variant="tonal" :color="tipoColor(posta.tipo)" label>
                  {{ tipoLabel(posta.tipo) }}
                </v-chip>
              </td>
              <td class="text-medium-emphasis text-body-1">{{ posta.total_turnos }}</td>
              <td>
                <v-chip
                  :color="posta.activa ? 'success' : 'grey'"
                  variant="elevated"
                  size="small"
                  label
                  class="font-weight-bold"
                >
                  {{ posta.activa ? 'Activa' : 'Inactiva' }}
                </v-chip>
              </td>
              <td class="text-center">
                <v-tooltip text="Ver detalle" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" v-bind="tipProps" @click="abrirFicha(posta)">
                      <v-icon icon="mdi-eye-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="Editar posta" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="primary" v-bind="tipProps" @click="abrirEditar(posta)">
                      <v-icon icon="mdi-pencil-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip :text="posta.activa ? 'Desactivar' : 'Activar'" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn
                      icon
                      size="small"
                      variant="text"
                      :color="posta.activa ? 'error' : 'success'"
                      v-bind="tipProps"
                      @click="toggleActiva(posta)"
                    >
                      <v-icon :icon="posta.activa ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
              </td>
            </tr>
          </tbody>
        </v-table>
      </Transition>

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

    <!-- Dialog ficha / detalle posta -->
    <v-dialog v-model="dialogFicha" :max-width="mobile ? undefined : 700" :fullscreen="mobile">
      <v-card rounded="lg" v-if="fichaPosta">
        <v-card-title class="d-flex align-center justify-space-between pa-6 pb-2">
          <div class="d-flex align-center ga-3">
            <v-avatar :color="fichaPosta.activa ? 'primary' : 'grey'" size="36" rounded="lg">
              <v-icon :icon="tipoIcon(fichaPosta.tipo)" size="18" color="white" />
            </v-avatar>
            <div>
              <span class="text-h6 font-weight-bold">{{ fichaPosta.nombre }}</span>
              <div class="text-body-2 text-medium-emphasis">{{ tipoLabel(fichaPosta.tipo) }}</div>
            </div>
          </div>
          <v-chip :color="fichaPosta.activa ? 'success' : 'grey'" variant="elevated" size="small" label class="font-weight-bold">
            {{ fichaPosta.activa ? 'Activa' : 'Inactiva' }}
          </v-chip>
        </v-card-title>
        <v-card-text class="pa-6 pt-4">
          <div class="ficha-section mb-5">
            <div class="ficha-section-title mb-3">Información general</div>
            <div class="ficha-grid">
              <div class="ficha-item">
                <span class="ficha-label">Nombre</span>
                <span class="ficha-value">{{ fichaPosta.nombre }}</span>
              </div>
              <div class="ficha-item">
                <span class="ficha-label">Tipo</span>
                <span class="ficha-value">{{ tipoLabel(fichaPosta.tipo) }}</span>
              </div>
              <div v-if="fichaPosta.descripcion" class="ficha-item ficha-full">
                <span class="ficha-label">Descripción</span>
                <span class="ficha-value">{{ fichaPosta.descripcion }}</span>
              </div>
              <div v-if="fichaPosta.ubicacion" class="ficha-item ficha-full">
                <span class="ficha-label">Ubicación</span>
                <span class="ficha-value">{{ fichaPosta.ubicacion }}</span>
              </div>
              <div v-if="fichaPosta.observaciones" class="ficha-item ficha-full">
                <span class="ficha-label">Observaciones</span>
                <span class="ficha-value">{{ fichaPosta.observaciones }}</span>
              </div>
            </div>
          </div>

          <v-divider class="mb-5" />

          <div class="ficha-section">
            <div class="d-flex align-center justify-space-between mb-3">
              <div class="ficha-section-title">Turnos</div>
              <v-btn
                size="small"
                variant="tonal"
                color="primary"
                prepend-icon="mdi-plus"
                class="text-none"
                @click="abrirTurno(null)"
              >
                Agregar turno
              </v-btn>
            </div>
            <div v-if="!fichaPosta.turnos || fichaPosta.turnos.length === 0" class="text-body-2 text-medium-emphasis py-4 text-center">
              No hay turnos configurados
            </div>
            <div v-else class="turnos-list">
              <div v-for="turno in fichaPosta.turnos" :key="turno.id" class="turno-item pa-3 mb-2">
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="text-body-1 font-weight-medium">{{ turno.nombre }}</div>
                    <div class="text-body-2 text-medium-emphasis">
                      {{ turno.hora_inicio?.slice(0, 5) }} – {{ turno.hora_fin?.slice(0, 5) }}
                      <span v-if="turno.cruza_medianoche" class="text-warning ms-1">(medianoche)</span>
                      <span class="ms-2">{{ turno.asp_requeridos }} ASP{{ turno.asp_requeridos > 1 ? 's' : '' }}</span>
                    </div>
                  </div>
                  <div class="d-flex ga-1 align-center">
                    <v-chip
                      :color="turno.activo ? 'success' : 'grey'"
                      variant="elevated"
                      size="x-small"
                      label
                      class="font-weight-bold"
                    >
                      {{ turno.activo ? 'Activo' : 'Inactivo' }}
                    </v-chip>
                    <v-btn icon size="x-small" variant="text" color="primary" @click="abrirTurno(turno)">
                      <v-icon icon="mdi-pencil-outline" size="16" />
                    </v-btn>
                    <v-btn
                      icon
                      size="x-small"
                      variant="text"
                      :color="turno.activo ? 'error' : 'success'"
                      @click="toggleTurnoActivo(turno)"
                    >
                      <v-icon :icon="turno.activo ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" size="16" />
                    </v-btn>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogFicha = false">Cerrar</v-btn>
          <v-btn color="primary" variant="tonal" class="text-none text-body-1" @click="dialogFicha = false; abrirEditar(fichaPosta)">
            Editar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog crear/editar posta -->
    <v-dialog v-model="dialogForm" :max-width="mobile ? undefined : 560" :fullscreen="mobile" persistent scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editando ? 'Editar Posta' : 'Nueva Posta' }}
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
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.nombre"
                  label="Nombre *"
                  placeholder="Ej: Posta Central..."
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.nombre"
                  maxlength="100"
                  counter="100"
                  class="mb-1"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.tipo"
                  label="Tipo *"
                  :items="tipoItems"
                  item-title="label"
                  item-value="value"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="errores.tipo"
                  class="mb-1"
                />
              </v-col>
            </v-row>
            <v-textarea
              v-model="form.descripcion"
              label="Descripción (opcional)"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.descripcion"
              rows="2"
              auto-grow
              class="mb-1"
            />
            <v-text-field
              v-model="form.ubicacion"
              label="Ubicación (opcional)"
              variant="outlined"
              density="comfortable"
              :error-messages="errores.ubicacion"
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
            <span>Complete nombre y tipo</span>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog crear/editar turno -->
    <v-dialog v-model="dialogTurno" :max-width="mobile ? undefined : 480" :fullscreen="mobile" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
          {{ editandoTurno ? 'Editar Turno' : 'Nuevo Turno' }}
        </v-card-title>
        <v-card-text class="pa-5">
          <v-alert
            v-if="erroresTurno._global"
            type="error"
            variant="tonal"
            density="compact"
            closable
            class="mb-4"
            @click:close="erroresTurno._global = null"
          >
            {{ erroresTurno._global }}
          </v-alert>
          <v-form @submit.prevent="guardarTurno">
            <v-text-field
              v-model="turnoForm.nombre"
              label="Nombre *"
              placeholder="Ej: Turno A, Turno mañana..."
              variant="outlined"
              density="comfortable"
              :error-messages="erroresTurno.nombre"
              maxlength="50"
              counter="50"
              class="mb-3"
            />
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-menu v-model="menuHoraInicio" :close-on-content-click="false" location="bottom start">
                  <template #activator="{ props: menuProps }">
                    <v-text-field
                      :model-value="turnoForm.hora_inicio || ''"
                      label="Hora inicio *"
                      readonly
                      append-inner-icon="mdi-clock-outline"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="erroresTurno.hora_inicio"
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
                      :model-value="turnoForm.hora_fin || ''"
                      label="Hora fin *"
                      readonly
                      append-inner-icon="mdi-clock-outline"
                      variant="outlined"
                      density="comfortable"
                      :error-messages="erroresTurno.hora_fin"
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
              v-model.number="turnoForm.asp_requeridos"
              label="ASP requeridos *"
              type="number"
              min="1"
              variant="outlined"
              density="comfortable"
              :error-messages="erroresTurno.asp_requeridos"
              class="mb-1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="cerrarTurno">Cancelar</v-btn>
          <v-tooltip :disabled="turnoFormValido" location="top">
            <template #activator="{ props: tipProps }">
              <span v-bind="tipProps">
                <v-btn
                  color="primary"
                  :disabled="!turnoFormValido"
                  :loading="guardandoTurno"
                  class="text-none text-body-1"
                  @click="guardarTurno"
                >
                  {{ editandoTurno ? 'Actualizar' : 'Crear' }}
                </v-btn>
              </span>
            </template>
            <span>Complete nombre, horas y ASP requeridos</span>
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

const postas = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => mobile.value ? 10 : 20)
const buscar = ref('')
const filtroTipo = ref('todos')
const filtroActiva = ref('activas')

const dialogForm = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref(emptyForm())
const errores = ref({})

const dialogFicha = ref(false)
const fichaPosta = ref(null)

const dialogTurno = ref(false)
const editandoTurno = ref(null)
const guardandoTurno = ref(false)
const turnoForm = ref(emptyTurnoForm())
const erroresTurno = ref({})

const menuHoraInicio = ref(false)
const menuHoraFin = ref(false)

const tipoItems = [
  { label: 'Interior', value: 'interior', color: 'blue' },
  { label: 'Perimetral', value: 'perimetral', color: 'orange' },
  { label: 'Móvil', value: 'movil', color: 'teal' },
  { label: 'Punto Crítico', value: 'punto_critico', color: 'red' },
]

const tipoMap = Object.fromEntries(tipoItems.map(t => [t.value, t]))

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))
const formValido = computed(() => {
  const f = form.value
  return f.nombre.trim().length > 0 && f.tipo
})
const turnoFormValido = computed(() => {
  const t = turnoForm.value
  return t.nombre.trim().length > 0 && t.hora_inicio && t.hora_fin && t.asp_requeridos >= 1
})

const horasItems = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutosItems = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']

function timeToParts(t) {
  if (!t) return { h: '08', m: '00' }
  const [h, m] = t.split(':')
  return { h: h || '08', m: m || '00' }
}

function partsToTime(h, m) {
  return `${h}:${m}`
}

const horaInicioHora = computed({
  get() { return timeToParts(turnoForm.value.hora_inicio).h },
  set(val) { turnoForm.value.hora_inicio = partsToTime(val, timeToParts(turnoForm.value.hora_inicio).m) },
})
const horaInicioMinuto = computed({
  get() { return timeToParts(turnoForm.value.hora_inicio).m },
  set(val) { turnoForm.value.hora_inicio = partsToTime(timeToParts(turnoForm.value.hora_inicio).h, val) },
})
const horaFinHora = computed({
  get() { return timeToParts(turnoForm.value.hora_fin).h },
  set(val) { turnoForm.value.hora_fin = partsToTime(val, timeToParts(turnoForm.value.hora_fin).m) },
})
const horaFinMinuto = computed({
  get() { return timeToParts(turnoForm.value.hora_fin).m },
  set(val) { turnoForm.value.hora_fin = partsToTime(timeToParts(turnoForm.value.hora_fin).h, val) },
})

function tipoLabel(tipo) { return tipoMap[tipo]?.label || tipo }
function tipoIcon(tipo) {
  const icons = { interior: 'mdi-home-outline', perimetral: 'mdi-fence-outline', movil: 'mdi-car-outline', punto_critico: 'mdi-alert-circle-outline' }
  return icons[tipo] || 'mdi-office-building-outline'
}
function tipoColor(tipo) { return tipoMap[tipo]?.color || 'grey' }

function emptyForm() { return { nombre: '', tipo: null, descripcion: '', ubicacion: '', observaciones: '' } }
function emptyTurnoForm() { return { nombre: '', hora_inicio: '', hora_fin: '', asp_requeridos: 1 } }

function debounce(fn, ms) {
  let timer
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms) }
}

const onBuscar = debounce(() => { pagina.value = 1; cargarPostas() }, 300)

async function cargarPostas() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtroTipo.value !== 'todos') params.tipo = filtroTipo.value
    if (filtroActiva.value === 'activas') params.activa = true
    if (buscar.value?.trim()) params.buscar = buscar.value.trim()
    const res = await postaApi.listar(params)
    postas.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar postas'))
  } finally {
    cargando.value = false
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarPostas().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

async function abrirFicha(posta) {
  dialogFicha.value = true
  fichaPosta.value = null
  try {
    const res = await postaApi.obtener(posta.id)
    fichaPosta.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar detalle'))
    dialogFicha.value = false
  }
}

function abrirCrear() {
  editando.value = null
  form.value = emptyForm()
  errores.value = {}
  dialogForm.value = true
}

function abrirEditar(posta) {
  editando.value = posta
  form.value = {
    nombre: posta.nombre,
    tipo: posta.tipo,
    descripcion: posta.descripcion || '',
    ubicacion: posta.ubicacion || '',
    observaciones: posta.observaciones || '',
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
  if (!form.value.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (!form.value.tipo) e.tipo = 'El tipo es requerido'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      tipo: form.value.tipo,
    }
    if (form.value.descripcion.trim()) payload.descripcion = form.value.descripcion.trim()
    if (form.value.ubicacion.trim()) payload.ubicacion = form.value.ubicacion.trim()
    if (form.value.observaciones.trim()) payload.observaciones = form.value.observaciones.trim()

    if (editando.value) {
      await postaApi.actualizar(editando.value.id, payload)
      toast.success('Posta actualizada correctamente')
    } else {
      await postaApi.crear(payload)
      toast.success('Posta creada correctamente')
    }
    cerrarForm()
    await cargarPostas()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string' && detail.toLowerCase().includes('nombre')) {
      errores.value = { nombre: detail }
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
      else toast.error(normalizeApiError(e, 'Error al guardar'))
    }
  } finally {
    guardando.value = false
  }
}

async function toggleActiva(posta) {
  try {
    await postaApi.cambiarEstado(posta.id, !posta.activa)
    toast.success(posta.activa ? 'Posta desactivada' : 'Posta activada')
    await cargarPostas()
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  }
}

function abrirTurno(turno) {
  editandoTurno.value = turno
  turnoForm.value = turno
    ? { nombre: turno.nombre, hora_inicio: turno.hora_inicio?.slice(0, 5) || '', hora_fin: turno.hora_fin?.slice(0, 5) || '', asp_requeridos: turno.asp_requeridos || 1 }
    : emptyTurnoForm()
  erroresTurno.value = {}
  dialogTurno.value = true
}

function cerrarTurno() {
  dialogTurno.value = false
  erroresTurno.value = {}
}

function validarTurno() {
  const e = {}
  if (!turnoForm.value.nombre.trim()) e.nombre = 'El nombre es requerido'
  if (!turnoForm.value.hora_inicio) e.hora_inicio = 'Requerido'
  if (!turnoForm.value.hora_fin) e.hora_fin = 'Requerido'
  if (turnoForm.value.hora_inicio && turnoForm.value.hora_fin && turnoForm.value.hora_inicio === turnoForm.value.hora_fin) {
    e.hora_fin = 'Debe ser diferente a hora inicio'
  }
  if (!turnoForm.value.asp_requeridos || turnoForm.value.asp_requeridos < 1) e.asp_requeridos = 'Mínimo 1'
  erroresTurno.value = e
  return Object.keys(e).length === 0
}

async function guardarTurno() {
  if (!validarTurno()) return
  guardandoTurno.value = true
  try {
    const payload = {
      nombre: turnoForm.value.nombre.trim(),
      hora_inicio: turnoForm.value.hora_inicio,
      hora_fin: turnoForm.value.hora_fin,
      asp_requeridos: turnoForm.value.asp_requeridos,
    }
    if (editandoTurno.value) {
      await postaApi.actualizarTurno(editandoTurno.value.id, payload)
      toast.success('Turno actualizado')
    } else {
      await postaApi.agregarTurno(fichaPosta.value.id, payload)
      toast.success('Turno creado')
    }
    cerrarTurno()
    const res = await postaApi.obtener(fichaPosta.value.id)
    fichaPosta.value = res.data
    await cargarPostas()
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      erroresTurno.value = { _global: detail }
    } else {
      toast.error(normalizeApiError(e, 'Error al guardar turno'))
    }
  } finally {
    guardandoTurno.value = false
  }
}

async function toggleTurnoActivo(turno) {
  try {
    await postaApi.cambiarEstadoTurno(turno.id, !turno.activo)
    toast.success(turno.activo ? 'Turno desactivado' : 'Turno activado')
    const res = await postaApi.obtener(fichaPosta.value.id)
    fichaPosta.value = res.data
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cambiar estado'))
  }
}

watch([filtroTipo, filtroActiva], () => { pagina.value = 1; cargarPostas() })
watch(mobile, () => { pagina.value = 1; cargarPostas() })

onMounted(cargarPostas)
</script>

<style scoped>
.postas-page {
  width: 100%;
}

.postas-search {
  flex-grow: 1;
}

.postas-mobile-list {
  display: flex;
  flex-direction: column;
}

.postas-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
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

.turnos-list {
  display: flex;
  flex-direction: column;
}

.turno-item {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 8px;
  background: rgb(var(--v-theme-surface));
}

.hora-select,
.minuto-select {
  min-width: 70px;
}

@media (max-width: 599px) {
  .postas-search {
    max-width: 100%;
  }

  .ficha-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
