<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <v-avatar color="primary" size="56" rounded="xl">
          <v-icon color="white" size="28">mdi-shield-half</v-icon>
        </v-avatar>
        <div class="login-brand-text">
          <h1 class="text-h5 font-weight-bold">SGP</h1>
          <p class="text-body-2 text-medium-emphasis">Sistema de Gestión de Postas</p>
        </div>
      </div>

      <v-divider class="mb-6" />

      <h2 class="text-subtitle-1 font-weight-medium text-center mb-1">Iniciar Sesión</h2>
      <p class="text-body-2 text-medium-emphasis text-center mb-6">
       Ingrese sus credenciales para acceder
      </p>

      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4"
        closable
        @click:close="error = ''"
      >
        {{ error }}
      </v-alert>

      <v-form @submit.prevent="handleLogin">
        <v-text-field
          id="username"
          v-model="form.username"
          label="Usuario"
          placeholder="Ingrese su usuario"
          prepend-inner-icon="mdi-account-outline"
          autocomplete="username"
          autofocus
          :disabled="loading"
          class="mb-1"
        />
        <v-text-field
          id="password"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          label="Contraseña"
          placeholder="Ingrese su contraseña"
          prepend-inner-icon="mdi-lock-outline"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          autocomplete="current-password"
          :disabled="loading"
          class="mb-6"
          @click:append-inner="showPassword = !showPassword"
        />
        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          :elevation="0"
          :loading="loading"
        >
          Ingresar
        </v-btn>
      </v-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { normalizeApiError } from '../utils/error'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

async function handleLogin() {
  if (!form.username || !form.password) {
    error.value = 'Ingrese usuario y contraseña'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push({ name: 'dashboard' })
  } catch (err) {
    if (err?.response?.status === 401) {
      error.value = 'Usuario o contraseña incorrectos'
      return
    }
    if (err?.response?.status === 429) {
      error.value = 'Demasiados intentos. Espere un momento e intente de nuevo.'
      return
    }
    error.value = normalizeApiError(err, 'Error al iniciar sesión. Intente nuevamente.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #e8eef6 0%, #dce4ef 50%, #e2e8f0 100%);
}

.login-card {
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

.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.login-brand-text {
  text-align: center;
}
</style>
