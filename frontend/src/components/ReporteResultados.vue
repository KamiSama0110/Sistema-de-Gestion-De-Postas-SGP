<template>
  <div v-if="!filas.length" class="text-center py-8">
    <v-icon icon="mdi-text-box-search-outline" size="40" color="grey-lighten-1" class="mb-2" />
    <p class="text-body-2 text-medium-emphasis">Sin registros para el período seleccionado</p>
  </div>

  <v-table v-else-if="!mobile" density="comfortable">
    <thead>
      <tr>
        <th
          v-for="col in columnas"
          :key="col.key"
          class="text-caption font-weight-bold text-medium-emphasis"
          :class="col.align === 'right' ? 'text-right' : ''"
        >
          {{ col.label }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, idx) in filas" :key="idx">
        <td
          v-for="col in columnas"
          :key="col.key"
          :class="[
            col.align === 'right' ? 'text-right text-no-wrap' : '',
            col.primary ? 'font-weight-medium' : '',
          ]"
        >
          <v-chip
            v-if="col.colorFn && col.colorFn(row[col.key])"
            :color="col.colorFn(row[col.key])"
            size="x-small"
            variant="tonal"
            label
          >
            {{ valor(row, col) }}
          </v-chip>
          <template v-else>{{ valor(row, col) }}</template>
        </td>
      </tr>
    </tbody>
  </v-table>

  <div v-else class="reporte-mobile-list">
    <div v-for="(row, idx) in filas" :key="idx" class="reporte-mobile-card pa-3 mb-2">
      <div class="d-flex align-start justify-space-between ga-2">
        <div class="text-body-2 font-weight-medium reporte-mobile-titulo">
          {{ valor(row, columnas[0]) }}
        </div>
        <v-chip
          v-if="chipPrincipal(row)"
          :color="chipPrincipal(row).color"
          size="x-small"
          variant="tonal"
          label
          class="flex-shrink-0"
        >
          {{ chipPrincipal(row).texto }}
        </v-chip>
      </div>
      <div class="reporte-mobile-grid mt-2">
        <div
          v-for="col in columnas.slice(1)"
          :key="col.key"
          :class="col.wrap ? 'reporte-mobile-full' : ''"
        >
          <div class="text-caption text-medium-emphasis">{{ col.label }}</div>
          <div class="text-body-2">{{ valor(row, col) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDisplay } from 'vuetify'

const props = defineProps({
  columnas: { type: Array, required: true },
  filas: { type: Array, required: true },
})

const { mobile } = useDisplay()

function valor(row, col) {
  const v = col.fn ? col.fn(row[col.key]) : row[col.key]
  return v == null || v === '' ? '—' : v
}

function chipPrincipal(row) {
  const col = props.columnas[0]
  if (!col?.colorFn) return null
  const color = col.colorFn(row[col.key])
  if (!color) return null
  return { color, texto: valor(row, col) }
}
</script>

<style scoped>
.reporte-mobile-list {
  display: flex;
  flex-direction: column;
}

.reporte-mobile-card {
  border: 1px solid rgb(var(--v-border-color));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.reporte-mobile-titulo {
  overflow-wrap: anywhere;
}

.reporte-mobile-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 14px;
}

.reporte-mobile-full {
  grid-column: 1 / -1;
}
</style>
