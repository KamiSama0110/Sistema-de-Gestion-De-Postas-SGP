<template>
  <RouterView />
  <Toast :position="toastPosition" class="app-toast" />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'

const isMobile = ref(false)

function updateViewportState() {
  isMobile.value = window.matchMedia('(max-width: 640px)').matches
}

const toastPosition = computed(() => (isMobile.value ? 'bottom-center' : 'top-right'))

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportState)
})
</script>
