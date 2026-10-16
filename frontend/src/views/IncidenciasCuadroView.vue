<template>
  <div class="incidencias-page mx-auto">
    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="d-flex flex-wrap ga-3 mb-4">
        <v-text-field
          v-model="filtros.desde"
          label="Desde"
          type="date"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro"
        />
        <v-text-field
          v-model="filtros.hasta"
          label="Hasta"
          type="date"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro"
        />
        <v-select
          v-model="filtros.severidad"
          label="Severidad"
          :items="severidadItems"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro"
        />
        <v-select
          v-model="filtros.tipo"
          label="Tipo"
          :items="tipoItems"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro"
        />
        <v-autocomplete
          v-model="filtros.cuadro_id"
          label="Cuadro"
          :items="cuadroItems"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro filtro-auto"
        />
        <v-select
          v-model="filtros.requiere_seguimiento"
          label="Requiere seguimiento"
          :items="seguimientoItems"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="grey-lighten-4"
          clearable
          class="filtro"
        />
        <v-btn variant="text" color="primary" class="text-none" prepend-icon="mdi-filter-off-outline" @click="limpiarFiltros">
          Limpiar
        </v-btn>
        <v-spacer />
        <div v-if="total > 0" class="d-flex align-center text-body-2 text-medium-emphasis">
          {{ total }} incidencia{{ total !== 1 ? 's' : '' }}
        </div>
      </div>

      <div aria-live="polite">
        <SkeletonList v-if="cargando" :filas="6" :avatar="false" />

        <div v-else-if="incidencias.length === 0" class="text-center py-12">
          <v-icon icon="mdi-clipboard-text-outline" size="48" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-1 text-medium-emphasis mb-0">No hay incidencias para mostrar</p>
        </div>

        <!-- Mobile -->
        <div v-else-if="mobile" class="incidencias-mobile-list">
          <div v-for="inc in incidencias" :key="inc.id" class="incidencias-mobile-card pa-4 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center ga-2 flex-wrap">
                <v-chip :color="severidadColor(inc.severidad)" variant="tonal" size="x-small" label class="font-weight-bold">
                  {{ severidadLabel(inc.severidad) }}
                </v-chip>
                <span class="text-body-2 font-weight-medium">{{ tipoLabel(inc.tipo) }}</span>
              </div>
              <v-chip v-if="inc.requiere_seguimiento" color="warning" variant="tonal" size="x-small" label>Seguimiento</v-chip>
            </div>
            <div class="text-body-1 font-weight-medium">{{ inc.cuadro_nombre }}</div>
            <div class="text-body-2 text-medium-emphasis mb-1">{{ formatFechaHora(inc.fecha_hora) }}</div>
            <p class="text-body-2 mb-2 pre-wrap">{{ inc.descripcion }}</p>
            <div class="d-flex justify-end ga-1">
              <v-btn icon size="x-small" variant="text" color="primary" aria-label="Ver detalle" @click="abrirDetalle(inc)">
                <v-icon icon="mdi-eye-outline" size="16" />
              </v-btn>
              <v-btn icon size="x-small" variant="text" color="primary" aria-label="Editar" @click="abrirEditar(inc)">
                <v-icon icon="mdi-pencil-outline" size="16" />
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Desktop -->
        <v-table v-else density="comfortable">
          <thead>
            <tr>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Fecha y hora</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Cuadro</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Tipo</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Severidad</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Descripción</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Posta</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis">Custodio</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Seguim.</th>
              <th class="text-body-1 font-weight-bold text-medium-emphasis text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inc in incidencias" :key="inc.id">
              <td class="text-body-1">{{ formatFechaHora(inc.fecha_hora) }}</td>
              <td class="font-weight-medium text-body-1">{{ inc.cuadro_nombre }}</td>
              <td class="text-body-1">{{ tipoLabel(inc.tipo) }}</td>
              <td>
                <v-chip :color="severidadColor(inc.severidad)" variant="tonal" size="small" label class="font-weight-bold">
                  {{ severidadLabel(inc.severidad) }}
                </v-chip>
              </td>
              <td class="text-body-1 desc-cell">{{ inc.descripcion }}</td>
              <td class="text-medium-emphasis text-body-1">{{ inc.posta_nombre || '—' }}</td>
              <td class="text-medium-emphasis text-body-1">{{ inc.asp_nombre || '—' }}</td>
              <td class="text-center">
                <v-icon
                  :icon="inc.requiere_seguimiento ? 'mdi-check-circle-outline' : 'mdi-minus'"
                  :color="inc.requiere_seguimiento ? 'warning' : 'grey-lighten-1'"
                  size="18"
                />
              </td>
              <td class="text-center">
                <v-tooltip text="Ver detalle" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="primary" aria-label="Ver detalle" v-bind="tipProps" @click="abrirDetalle(inc)">
                      <v-icon icon="mdi-eye-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="Editar" location="top">
                  <template #activator="{ props: tipProps }">
                    <v-btn icon size="small" variant="text" color="primary" aria-label="Editar" v-bind="tipProps" @click="abrirEditar(inc)">
                      <v-icon icon="mdi-pencil-outline" size="18" />
                    </v-btn>
                  </template>
                </v-tooltip>
              </td>
            </tr>
          </tbody>
        </v-table>
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

    <!-- Detalle -->
    <v-dialog v-model="dialogDetalle" :max-width="xs ? undefined : 560" :fullscreen="xs" scrollable>
      <v-card rounded="lg">
        <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">Detalle de incidencia</v-card-title>
        <v-card-text v-if="detalle" class="pa-5">
          <div class="d-flex align-center ga-2 flex-wrap mb-3">
            <v-chip :color="severidadColor(detalle.severidad)" variant="tonal" size="small" label class="font-weight-bold">
              {{ severidadLabel(detalle.severidad) }}
            </v-chip>
            <v-chip size="small" variant="tonal" label>{{ tipoLabel(detalle.tipo) }}</v-chip>
            <v-chip v-if="detalle.requiere_seguimiento" color="warning" variant="tonal" size="small" label>Seguimiento</v-chip>
          </div>
          <p class="text-body-1 mb-4 pre-wrap">{{ detalle.descripcion }}</p>
          <v-row dense>
            <v-col cols="12" sm="6"><div class="detalle-label">Cuadro</div><div class="detalle-value">{{ detalle.cuadro_nombre }}</div></v-col>
            <v-col cols="12" sm="6"><div class="detalle-label">Fecha y hora</div><div class="detalle-value">{{ formatFechaHora(detalle.fecha_hora) }}</div></v-col>
            <v-col cols="12" sm="6"><div class="detalle-label">Posta</div><div class="detalle-value">{{ detalle.posta_nombre || '—' }}</div></v-col>
            <v-col cols="12" sm="6"><div class="detalle-label">Custodio</div><div class="detalle-value">{{ detalle.asp_nombre || '—' }}</div></v-col>
            <v-col cols="12" sm="6"><div class="detalle-label">Área</div><div class="detalle-value">{{ detalle.area || '—' }}</div></v-col>
            <v-col cols="12" sm="6"><div class="detalle-label">Registrada</div><div class="detalle-value">{{ formatFechaHora(detalle.creado_en) }}</div></v-col>
          </v-row>
          <div v-if="detalle.acciones_tomadas" class="mt-3">
            <div class="detalle-label">Acciones tomadas</div>
            <p class="text-body-2 mb-0 pre-wrap">{{ detalle.acciones_tomadas }}</p>
          </div>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" class="text-none text-body-1" @click="dialogDetalle = false">Cerrar</v-btn>
          <v-btn color="primary" class="text-none text-body-1" prepend-icon="mdi-pencil-outline" @click="editarDesdeDetalle">
            Editar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <IncidenciaDialog
      v-model="dialogIncidencia"
      :incidencia="incidenciaEditando"
      modo="admin"
      :opciones="opciones"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { incidenciaCuadroApi } from '../api/incidenciaCuadro'
import { cuadroApi } from '../api/cuadro'
import { postaApi } from '../api/posta'
import { aspApi } from '../api/asp'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { formatFechaHora } from '../utils/formatters'
import { SEVERIDADES, TIPOS_INCIDENCIA, severidadColor, severidadLabel, tipoLabel } from '../utils/incidencia'
import SkeletonList from '../components/SkeletonList.vue'
import IncidenciaDialog from '../components/IncidenciaDialog.vue'

const toast = useToast()
const { mobile, xs } = useDisplay()

const incidencias = ref([])
const cargando = ref(true)
const total = ref(0)
const pagina = ref(1)
const tamanoPagina = computed(() => (mobile.value ? 10 : 20))

const filtros = ref({
  desde: '',
  hasta: '',
  severidad: null,
  tipo: null,
  cuadro_id: null,
  requiere_seguimiento: null,
})

const severidadItems = SEVERIDADES
const tipoItems = TIPOS_INCIDENCIA
const cuadroItems = ref([])
const seguimientoItems = [
  { title: 'Sí', value: true },
  { title: 'No', value: false },
]

const dialogDetalle = ref(false)
const detalle = ref(null)
const dialogIncidencia = ref(false)
const incidenciaEditando = ref(null)
const opciones = ref({ postas: [], asp: [] })

const totalPaginas = computed(() => Math.max(1, Math.ceil(total.value / tamanoPagina.value)))

async function cargarIncidencias() {
  cargando.value = true
  try {
    const params = { page: pagina.value, size: tamanoPagina.value }
    if (filtros.value.desde) params.desde = filtros.value.desde
    if (filtros.value.hasta) params.hasta = filtros.value.hasta
    if (filtros.value.severidad) params.severidad = filtros.value.severidad
    if (filtros.value.tipo) params.tipo = filtros.value.tipo
    if (filtros.value.cuadro_id) params.cuadro_id = filtros.value.cuadro_id
    if (filtros.value.requiere_seguimiento !== null && filtros.value.requiere_seguimiento !== '') {
      params.requiere_seguimiento = filtros.value.requiere_seguimiento
    }
    const res = await incidenciaCuadroApi.listar(params)
    incidencias.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar las incidencias'))
  } finally {
    cargando.value = false
  }
}

async function cargarCuadros() {
  try {
    const items = []
    let page = 1
    let total = 0
    do {
      const res = await cuadroApi.listar({ page, size: 100 })
      items.push(...(res.data.items || []))
      total = res.data.total || 0
      page += 1
    } while (items.length < total && page <= 50)
    cuadroItems.value = items
      .map((c) => ({ title: `${c.nombre} ${c.apellidos}`.trim(), value: c.id }))
      .sort((a, b) => a.title.localeCompare(b.title, 'es'))
  } catch {
    cuadroItems.value = []
  }
}

async function cargarOpciones() {
  const [p, a] = await Promise.allSettled([
    postaApi.listar({ page: 1, size: 100, activa: true }),
    aspApi.listar({ page: 1, size: 100, estado: 'activo' }),
  ])
  opciones.value = {
    postas:
      p.status === 'fulfilled'
        ? (p.value.data.items || []).map((x) => ({ id: x.id, nombre: x.nombre }))
        : [],
    asp:
      a.status === 'fulfilled'
        ? (a.value.data.items || []).map((x) => ({
            id: x.id,
            nombre: `${x.nombre} ${x.apellidos || ''}`.trim(),
          }))
        : [],
  }
}

function limpiarFiltros() {
  filtros.value = {
    desde: '',
    hasta: '',
    severidad: null,
    tipo: null,
    cuadro_id: null,
    requiere_seguimiento: null,
  }
}

function cambiarPagina(delta) {
  const next = pagina.value + delta
  if (next < 1 || next > totalPaginas.value) return
  pagina.value = next
  cargarIncidencias().then(() => {
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function abrirDetalle(inc) {
  detalle.value = inc
  dialogDetalle.value = true
}

function abrirEditar(inc) {
  incidenciaEditando.value = inc
  dialogIncidencia.value = true
}

function editarDesdeDetalle() {
  incidenciaEditando.value = detalle.value
  dialogDetalle.value = false
  dialogIncidencia.value = true
}

async function onSaved() {
  await cargarIncidencias()
}

watch(
  filtros,
  () => {
    pagina.value = 1
    cargarIncidencias()
  },
  { deep: true },
)
watch(mobile, () => {
  pagina.value = 1
  cargarIncidencias()
})

onMounted(() => {
  cargarIncidencias()
  cargarCuadros()
  cargarOpciones()
})
</script>

<style scoped>
.incidencias-page {
  width: 100%;
}

.filtro {
  min-width: 180px;
  flex: 0 1 200px;
}

.filtro-auto {
  min-width: 240px;
  flex: 0 1 280px;
}

.desc-cell {
  max-width: 260px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pre-wrap {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.detalle-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.6;
}

.detalle-value {
  font-size: 14px;
  margin-bottom: 8px;
}

.incidencias-mobile-list {
  display: flex;
  flex-direction: column;
}

.incidencias-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@media (max-width: 599px) {
  .filtro {
    min-width: 0;
    flex: 1 1 140px;
  }

  .filtro-auto {
    min-width: 0;
    flex: 1 1 100%;
  }
}
</style>
