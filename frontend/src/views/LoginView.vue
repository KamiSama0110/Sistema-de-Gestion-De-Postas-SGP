<template>
  <div class="login-page">
    <div class="login-orb login-orb-left"></div>
    <div class="login-orb login-orb-right"></div>

    <div class="login-shell">
      <div class="login-brand">
        <div class="login-brand-mark">
          <i class="pi pi-shield"></i>
        </div>
        <div class="login-brand-copy">
          <h1>Sistema de Seguridad</h1>
          <p>Gestion de Postas y Personal</p>
        </div>
      </div>

      <div class="login-card">
        <div class="login-card-head">
          <h2>Iniciar Sesion</h2>
          <p>Ingrese sus credenciales para acceder al sistema</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <Message v-if="error" severity="error" :closable="false" class="login-error">
            <template #icon>
              <i class="pi pi-exclamation-circle"></i>
            </template>
            {{ error }}
          </Message>

          <div class="login-field">
            <label for="username">Usuario</label>
            <InputText
              id="username"
              v-model="form.username"
              type="text"
              placeholder="Ingrese su usuario"
              :disabled="loading"
              autocomplete="username"
              autofocus
              class="login-input"
            />
          </div>

          <div class="login-field">
            <label for="password">Contrasena</label>
            <div class="password-wrap">
              <InputText
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Ingrese su contrasena"
                :disabled="loading"
                autocomplete="current-password"
                class="login-input password-input"
              />
              <button
                type="button"
                class="password-toggle"
                :disabled="loading"
                :aria-label="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'pi pi-eye-slash' : 'pi pi-eye'" class="toggle-icon"></i>
              </button>
            </div>
          </div>

          <Button type="submit" class="login-submit" :disabled="loading">
            <template v-if="loading">
              <span class="login-spinner"></span>
              <span>Ingresando...</span>
            </template>
            <template v-else>
              <span>Ingresar</span>
            </template>
          </Button>
        </form>
      </div>

      <p class="login-footnote">Sistema de Gestion de Seguridad v1.0</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { normalizeApiError } from '../utils/error'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  username: '',
  password: '',
})
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
    error.value = normalizeApiError(err, 'Error al iniciar sesión. Verifique sus credenciales.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.05), transparent 34%),
    radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.05), transparent 36%),
    var(--bg);
}

.login-orb {
  position: absolute;
  width: 18rem;
  height: 18rem;
  border-radius: 9999px;
  filter: blur(70px);
  opacity: 0.8;
}

.login-orb-left {
  left: -4rem;
  top: 22%;
  background: rgba(14, 165, 233, 0.05);
}

.login-orb-right {
  right: -4rem;
  bottom: 18%;
  background: rgba(59, 130, 246, 0.05);
}

.login-shell {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 26.5rem;
}

.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.login-brand-mark {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: var(--brand-600);
  font-size: 1.85rem;
}

.login-brand-copy {
  text-align: center;
}

.login-brand-copy h1 {
  margin: 0;
  font-size: 1.5rem;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text);
}

.login-brand-copy p {
  margin: 0.35rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.login-card {
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
  background: color-mix(in srgb, var(--surface) 50%, transparent);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(12px);
}

.login-card-head {
  margin-bottom: 1rem;
}

.login-card-head h2 {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.3;
  font-weight: 600;
  color: var(--text);
}

.login-card-head p {
  margin: 0.4rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-field label {
  display: inline-block;
  margin-bottom: 0.4rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
}

.login-error {
  margin-bottom: 0.25rem;
}

.password-wrap {
  position: relative;
}

.password-input {
  width: 100%;
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 2.35rem;
  height: 2.35rem;
  padding: 0;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: var(--text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.password-toggle:hover:not(:disabled) {
  background: transparent;
  color: var(--text);
}

.password-toggle:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.toggle-icon {
  font-size: 1rem;
  line-height: 1;
}

.login-submit {
  width: 100%;
  justify-content: center;
  margin-top: 0.15rem;
}

.login-spinner {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
  border-radius: 9999px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: spin 0.85s linear infinite;
}

.login-footnote {
  margin: 1.4rem 0 0;
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.login-input {
  width: 100%;
  background: color-mix(in srgb, var(--surface) 50%, transparent);
}

.login-input:enabled:focus,
.login-input:enabled:hover {
  border-color: color-mix(in srgb, var(--brand-500) 55%, var(--border));
}

.login-submit {
  background: var(--brand-500);
  border-color: var(--brand-500);
}

.login-submit:hover:not(:disabled) {
  background: var(--brand-600);
  border-color: var(--brand-600);
}

.login-submit:disabled {
  opacity: 0.7;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 16px;
  }

  .login-shell {
    max-width: 100%;
  }

  .login-brand-copy h1 {
    font-size: 1.35rem;
  }

  .login-card {
    padding: 1.25rem;
  }
}
</style>

