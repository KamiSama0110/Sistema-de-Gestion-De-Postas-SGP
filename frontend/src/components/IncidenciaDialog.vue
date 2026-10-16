<template>
  <v-dialog
    :model-value="modelValue"
    :max-width="xs ? undefined : 620"
    :fullscreen="xs"
    persistent
    scrollable
    @update:model-value="cerrar"
  >
    <v-card rounded="lg">
      <v-card-title class="text-h6 font-weight-bold pa-5 pb-0">
        {{ esEdicion ? 'Editar incidencia' : 'Registrar incidencia' }}
      </v-card-title>
      <v-card-text class="pa-5">
        <v-alert
          v-if="errores._global"
          role="alert"
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
              <v-select
                v-model="form.tipo"
                label="Tipo *"
                :items="TIPOS_INCIDENCIA"
                variant="outlined"
                density="comfortable"
                :error-messages="errores.tipo"
                class="mb-1"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.severidad"
                label="Severidad *"
                :items="SEVERIDADES"
                variant="outlined"
                density="comfortable"
                :error-messages="errores.severidad"
                class="mb-1"
              />
            </v-col>
          </v-row>

          <v-textarea
            v-model="form.descripcion"
            label="Descripción *"
            variant="outlined"
            density="comfortable"
            rows="3"
            auto-grow
            maxlength="1000"
            counter
            :error-messages="errores.descripcion"
            class="mb-1"
          />

          <p class="text-caption text-medium-emphasis mb-2">
            Posta, custodio y área pueden quedar vacíos.
          </p>

          <v-row dense>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.posta_id"
                label="Posta (opcional)"
                :items="postaItems"
                variant="outlined"
                density="comfortable"
                clearable
                :disabled="esEdicion"
                :error-messages="errores.posta_id"
                class="mb-1"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.asp_id"
                label="Custodio (opcional)"
                :items="aspItems"
                variant="outlined"
                density="comfortable"
                clearable
                :disabled="esEdicion"
                :error-messages="errores.asp_id"
                class="mb-1"
              />
            </v-col>
          </v-row>

          <v-text-field
            v-model="form.area"
            label="Área (opcional)"
            variant="outlined"
            density="comfortable"
            maxlength="120"
            :disabled="esEdicion"
            :error-messages="errores.area"
            class="mb-1"
          />

          <v-textarea
            v-model="form.acciones_tomadas"
            label="Acciones tomadas (opcional)"
            variant="outlined"
            density="comfortable"
            rows="2"
            auto-grow
            :error-messages="errores.acciones_tomadas"
            class="mb-1"
          />

          <v-switch
            v-model="form.requiere_seguimiento"
            color="primary"
            label="Requiere seguimiento"
            density="comfortable"
            hide-details
            class="mb-1"
          />
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-5 pt-0">
        <v-spacer />
        <v-btn variant="text" class="text-none text-body-1" @click="cerrar">Cancelar</v-btn>
        <v-btn color="primary" :loading="guardando" class="text-none text-body-1" @click="guardar">
          {{ esEdicion ? 'Guardar' : 'Registrar' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { miGuardiaApi } from '../api/miGuardia'
import { guardiaCuadroApi } from '../api/guardiaCuadro'
import { incidenciaCuadroApi } from '../api/incidenciaCuadro'
import { extractFieldErrors, normalizeApiError } from '../utils/error'
import { useToast } from '../composables/useToast'
import { SEVERIDADES, TIPOS_INCIDENCIA } from '../utils/incidencia'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  guardiaId: { type: Number, default: null },
  incidencia: { type: Object, default: null },
  modo: { type: String, default: 'cuadro' },
  opciones: { type: Object, default: () => ({ postas: [], asp: [] }) },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const toast = useToast()
const { xs } = useDisplay()

const guardando = ref(false)
const errores = ref({})
const form = ref(emptyForm())

const esEdicion = computed(() => !!props.incidencia)

const postaItems = computed(() =>
  (props.opciones.postas || []).map((p) => ({ title: p.nombre, value: p.id })),
)
const aspItems = computed(() =>
  (props.opciones.asp || []).map((a) => ({
    title: a.apellidos ? `${a.nombre} ${a.apellidos}` : a.nombre,
    value: a.id,
  })),
)

function emptyForm() {
  return {
    tipo: 'incidente',
    severidad: 'baja',
    descripcion: '',
    posta_id: null,
    asp_id: null,
    area: '',
    acciones_tomadas: '',
    requiere_seguimiento: false,
  }
}

function cargarDesde(incidencia) {
  if (!incidencia) {
    form.value = emptyForm()
    return
  }
  form.value = {
    tipo: incidencia.tipo,
    severidad: incidencia.severidad,
    descripcion: incidencia.descripcion || '',
    posta_id: incidencia.posta_id ?? null,
    asp_id: incidencia.asp_id ?? null,
    area: incidencia.area || '',
    acciones_tomadas: incidencia.acciones_tomadas || '',
    requiere_seguimiento: !!incidencia.requiere_seguimiento,
  }
}

watch(
  () => props.modelValue,
  (abierto) => {
    if (abierto) {
      errores.value = {}
      cargarDesde(props.incidencia)
    }
  },
  { immediate: true },
)

function cerrar() {
  emit('update:modelValue', false)
}

function construirPayload() {
  const f = form.value
  const payload = {
    tipo: f.tipo,
    severidad: f.severidad,
    descripcion: f.descripcion.trim(),
    acciones_tomadas: f.acciones_tomadas.trim() || null,
    requiere_seguimiento: f.requiere_seguimiento,
  }
  if (f.area.trim()) payload.area = f.area.trim()
  if (!esEdicion.value) {
    if (f.posta_id) payload.posta_id = f.posta_id
    if (f.asp_id) payload.asp_id = f.asp_id
  }
  return payload
}

function validar() {
  const e = {}
  if (!form.value.descripcion.trim()) e.descripcion = 'La descripción es requerida'
  errores.value = e
  return Object.keys(e).length === 0
}

async function guardar() {
  if (!validar()) return
  guardando.value = true
  errores.value = {}
  try {
    const payload = construirPayload()
    if (esEdicion.value) {
      if (props.modo === 'cuadro') {
        await miGuardiaApi.editarIncidencia(props.incidencia.id, payload)
      } else {
        await incidenciaCuadroApi.editar(props.incidencia.id, payload)
      }
      toast.success('Incidencia actualizada correctamente')
    } else if (props.modo === 'cuadro') {
      await miGuardiaApi.crearIncidencia(props.guardiaId, payload)
      toast.success('Incidencia registrada correctamente')
    } else {
      await guardiaCuadroApi.crearIncidencia(props.guardiaId, payload)
      toast.success('Incidencia registrada correctamente')
    }
    emit('saved')
    cerrar()
  } catch (e) {
    const fieldErrors = extractFieldErrors(e)
    const hasFields = Object.keys(fieldErrors).some((k) => k !== '_global')
    if (hasFields) {
      errores.value = { ...fieldErrors }
    } else {
      errores.value = { _global: normalizeApiError(e, 'No se pudo guardar la incidencia') }
    }
  } finally {
    guardando.value = false
  }
}
</script>
