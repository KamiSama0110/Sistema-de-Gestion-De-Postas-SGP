<template>
  <div class="notfound-page">
    <div class="notfound-card">
      <div class="notfound-brand">
        <v-avatar color="primary" size="56" rounded="xl">
          <v-icon color="white" size="28">mdi-map-marker-question</v-icon>
        </v-avatar>
        <div class="notfound-brand-text">
          <h1 class="text-h5 font-weight-bold">SGP</h1>
          <p class="text-body-2 text-medium-emphasis">Sistema de Gestión de Postas</p>
        </div>
      </div>

      <v-divider class="mb-6" />

      <div class="text-primary font-weight-black notfound-code mb-2">404</div>
      <h2 class="text-h6 font-weight-bold mb-2 text-center">Página no encontrada</h2>
      <p class="text-body-2 text-medium-emphasis text-center mb-6">
        La ruta que buscas no existe o fue movida.
      </p>

      <div class="d-flex flex-column ga-3">
        <v-btn
          color="primary"
          prepend-icon="mdi-home"
          block
          :elevation="0"
          :to="auth.isAuthenticated ? { name: 'dashboard' } : { name: 'login' }"
        >
          {{ auth.isAuthenticated ? 'Ir al dashboard' : 'Ir al login' }}
        </v-btn>
        <v-btn
          variant="outlined"
          prepend-icon="mdi-arrow-left"
          block
          @click="volver"
        >
          Volver
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function destino() {
  return auth.isAuthenticated ? { name: 'dashboard' } : { name: 'login' }
}

function volver() {
  router.replace(destino())
}

onMounted(() => {
  if (window.history.length <= 1) {
    router.replace(destino())
  }
})
</script>

<style scoped>
.notfound-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #e8eef6 0%, #dce4ef 50%, #e2e8f0 100%);
}

.notfound-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.04),
    0 8px 24px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.notfound-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.notfound-brand-text {
  text-align: center;
}

.notfound-code {
  font-size: 64px;
  line-height: 1;
  text-align: center;
}
</style>
