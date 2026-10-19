<template>
  <v-dialog
    :model-value="modelValue"
    :max-width="xs ? undefined : 640"
    :fullscreen="xs"
    scrollable
    @update:model-value="cerrar"
  >
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center justify-space-between ga-2 pa-5 pb-0">
        <span class="text-h6 font-weight-bold">Incidencias</span>
        <v-tooltip :disabled="permiteIncidencias" location="top">
          <template #activator="{ props: tipProps }">
            <span v-bind="tipProps">
              <v-btn
                color="primary"
                variant="tonal"
                size="small"
                prepend-icon="mdi-plus"
                class="text-none"
                :disabled="!permiteIncidencias"
                @click="abrirCrear"
              >
                Registrar
              </v-btn>
            </span>
          </template>
          <span>Solo se pueden registrar incidencias en guardias activas o finalizadas</span>
        </v-tooltip>
      </v-card-title>
      <v-card-text class="pa-5">
        <div v-if="cargando" class="d-flex justify-center py-8">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else-if="incidencias.length === 0" class="text-center py-8">
          <v-icon icon="mdi-clipboard-text-outline" size="40" color="grey-lighten-1" class="mb-2" />
          <p class="text-body-2 text-medium-emphasis mb-0">No hay incidencias registradas</p>
        </div>

        <div v-else class="d-flex flex-column ga-3">
          <v-card
            v-for="inc in incidencias"
            :key="inc.id"
            variant="outlined"
            rounded="lg"
            class="pa-3"
          >
            <div class="d-flex align-center justify-space-between ga-2 mb-1">
              <div class="d-flex align-center ga-2 flex-wrap">
                <v-chip :color="severidadColor(inc.severidad)" variant="tonal" size="x-small" label class="font-weight-bold">
                  {{ severidadLabel(inc.severidad) }}
                </v-chip>
                <span class="text-body-2 font-weight-medium">{{ tipoLabel(inc.tipo) }}</span>
                <v-chip v-if="inc.requiere_seguimiento" color="warning" variant="tonal" size="x-small" label>
                  Seguimiento
                </v-chip>
              </div>
              <v-btn icon size="small" variant="text" color="primary" aria-label="Editar incidencia" @click="abrirEditar(inc)">
                <v-icon icon="mdi-pencil-outline" size="18" />
              </v-btn>
            </div>
            <p><strong>Descripción:</strong> {{ inc.descripcion }}</p>
            <div class="d-flex flex-wrap ga-x-3 ga-y-1 text-caption text-medium-emphasis">
              <span class="d-flex align-center ga-1">
                <v-icon icon="mdi-clock-outline" size="14" />{{ formatFechaHora(inc.fecha_hora) }}
              </span>
              <span v-if="inc.posta_nombre" class="d-flex align-center ga-1">
                <v-icon icon="mdi-office-building-outline" size="14" />{{ inc.posta_nombre }}
              </span>
              <span v-if="inc.asp_nombre" class="d-flex align-center ga-1">
                <v-icon icon="mdi-account-outline" size="14" />{{ inc.asp_nombre }}
              </span>
              <span v-if="inc.area" class="d-flex align-center ga-1">
                <v-icon icon="mdi-map-marker-outline" size="14" />{{ inc.area }}
              </span>
            </div>
            <p v-if="inc.acciones_tomadas" class="text-body-2 text-medium-emphasis mt-2 mb-0 pre-wrap">
              <strong>Acciones:</strong> {{ inc.acciones_tomadas }}
            </p>
          </v-card>
        </div>
      </v-card-text>
      <v-card-actions class="pa-5 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-none text-body-1" @click="cerrar">Cerrar</v-btn>
      </v-card-actions>
    </v-card>

    <IncidenciaDialog
      v-model="dialogIncidencia"
      :guardia-id="guardia?.id"
      :incidencia="incidenciaEditando"
      :modo="modo"
      :opciones="opciones"
      @saved="onSaved"
    />
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import IncidenciaDialog from './IncidenciaDialog.vue'
import { miGuardiaApi } from '../api/miGuardia'
import { incidenciaCuadroApi } from '../api/incidenciaCuadro'
import { normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { formatFechaHora } from '../utils/formatters'
import { severidadColor, severidadLabel, tipoLabel } from '../utils/incidencia'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  guardia: { type: Object, default: null },
  modo: { type: String, default: 'cuadro' },
  opciones: { type: Object, default: () => ({ postas: [], asp: [] }) },
})
const emit = defineEmits(['update:modelValue', 'changed'])

const toast = useToast()
const { xs } = useDisplay()

const incidencias = ref([])
const cargando = ref(false)
const dialogIncidencia = ref(false)
const incidenciaEditando = ref(null)

const permiteIncidencias = computed(
  () => !!props.guardia && ['activa', 'finalizada'].includes(props.guardia.estado),
)

async function cargar() {
  if (!props.guardia) return
  cargando.value = true
  try {
    const res =
      props.modo === 'cuadro'
        ? await miGuardiaApi.incidencias(props.guardia.id, { size: 100 })
        : await incidenciaCuadroApi.listar({ guardia_id: props.guardia.id, size: 100 })
    incidencias.value = res.data.items || []
  } catch (e) {
    toast.error(normalizeApiError(e, 'Error al cargar las incidencias'))
    incidencias.value = []
  } finally {
    cargando.value = false
  }
}

watch(
  () => props.modelValue,
  (abierto) => {
    if (abierto) cargar()
  },
)

function cerrar() {
  emit('update:modelValue', false)
}

function abrirCrear() {
  incidenciaEditando.value = null
  dialogIncidencia.value = true
}

function abrirEditar(inc) {
  incidenciaEditando.value = inc
  dialogIncidencia.value = true
}

async function onSaved() {
  await cargar()
  emit('changed')
}
</script>

<style scoped>
.pre-wrap {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}
</style>
