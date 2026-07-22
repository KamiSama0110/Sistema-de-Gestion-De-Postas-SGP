<template>
  <v-app>
    <RouterView />

    <v-snackbar
      v-for="toast in toasts"
      :key="toast.id"
      v-model="toast.visible"
      :color="snackbarColor(toast.type)"
      location="bottom right"
      timeout="-1"
      rounded="lg"
      elevation="8"
      class="sgp-toast"
    >
      <div class="d-flex align-center ga-2">
        <v-icon v-if="toastIcon(toast.type)" size="small">
          {{ toastIcon(toast.type) }}
        </v-icon>
        <div>
          <div v-if="toast.title" class="font-weight-bold text-body-2">{{ toast.title }}</div>
          <div class="text-body-2">{{ toast.message }}</div>
        </div>
      </div>
      <template #actions>
        <v-btn icon size="small" variant="text" @click="remove(toast.id)">
          <v-icon size="small">mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { useToast } from './composables/useToast'

const { toasts, remove } = useToast()

function snackbarColor(type) {
  const map = { success: 'success', error: 'error', warning: 'warning', info: 'primary' }
  return map[type] || 'primary'
}

function toastIcon(type) {
  const map = {
    success: 'mdi-check-circle',
    error: 'mdi-alert-circle',
    warning: 'mdi-alert',
    info: 'mdi-information',
  }
  return map[type] || ''
}
</script>

<style>
.sgp-toast {
  z-index: 9999 !important;
}
</style>
