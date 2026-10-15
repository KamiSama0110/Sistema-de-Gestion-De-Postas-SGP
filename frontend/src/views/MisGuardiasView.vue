<template>
  <div class="mis-guardias mx-auto">
    <div class="d-flex align-center justify-space-between flex-wrap ga-3 mb-4">
      <div>
        <h1 class="text-h5 font-weight-bold">Mis guardias</h1>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Planificación y registro de sus guardias
        </p>
      </div>
      <v-chip v-if="auth.nombreMostrado" size="small" variant="tonal" color="primary">
        {{ auth.nombreMostrado }}
      </v-chip>
    </div>

    <v-card rounded="lg" class="pa-sm-5 pa-3">
      <div class="text-center py-10">
        <v-avatar color="primary" size="64" rounded="xl" class="mb-4">
          <v-icon color="white" size="32">mdi-shield-account-outline</v-icon>
        </v-avatar>
        <h2 class="text-subtitle-1 font-weight-bold mb-2">Próximamente</h2>
        <p class="text-body-2 text-medium-emphasis">
          Esta sección estará disponible en una próxima actualización.
        </p>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<style scoped>
.mis-guardias {
  max-width: 1100px;
}
</style>
