<template>
  <div>
    <div v-if="!items.length" class="text-body-2 text-medium-emphasis">
      Sin datos para graficar
    </div>
    <div v-else>
      <div v-for="item in items" :key="item.label" class="d-flex align-center ga-3 mb-2">
        <span class="grafico-barras-label text-body-2 text-medium-emphasis">{{ item.label }}</span>
        <v-progress-linear
          :model-value="animado ? porcentaje(item) : 0"
          :color="item.color || 'primary'"
          height="12"
          rounded
          bg-color="grey-lighten-1"
          :aria-label="`${item.label}: ${item.value} (${Math.round(porcentaje(item))}%)`"
        />
        <span class="grafico-barras-valor text-body-2 font-weight-medium">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  animar: { type: Boolean, default: true },
})

const animado = ref(false)

const total = computed(() =>
  props.items.reduce((suma, item) => suma + (Number(item.value) || 0), 0),
)

function porcentaje(item) {
  if (item.porcentaje != null) return Math.min(100, Math.max(0, Number(item.porcentaje) || 0))
  if (!total.value) return 0
  return Math.min(100, ((Number(item.value) || 0) / total.value) * 100)
}

function lanzarAnimacion() {
  if (!props.animar) {
    animado.value = true
    return
  }
  animado.value = false
  nextTick(() => {
    requestAnimationFrame(() => {
      animado.value = true
    })
  })
}

onMounted(lanzarAnimacion)
watch(() => props.items, lanzarAnimacion, { deep: true })
</script>

<style scoped>
.grafico-barras-label {
  flex: 0 0 128px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.grafico-barras-valor {
  flex: 0 0 56px;
  text-align: right;
}

:deep(.v-progress-linear__determinate) {
  transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

@media (max-width: 599px) {
  .grafico-barras-label {
    flex-basis: 96px;
  }
}

@media (prefers-reduced-motion: reduce) {
  :deep(.v-progress-linear__determinate) {
    transition: none;
  }
}
</style>
