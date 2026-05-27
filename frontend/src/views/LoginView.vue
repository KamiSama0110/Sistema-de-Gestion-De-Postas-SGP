<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <i class="pi pi-shield" style="font-size: 2.5rem; color: #2563eb"></i>
        <h1>Sistema de Gestión de Postas</h1>
        <p>Acceso restringido al personal autorizado</p>
      </div>

      <Message v-if="error" severity="error" :closable="false" style="margin-bottom: 16px">
        {{ error }}
      </Message>

      <div class="p-fluid">
        <div class="field">
          <label>Usuario</label>
          <InputText v-model="form.username" placeholder="Introduce tu usuario" autofocus />
        </div>
        <div class="field" style="margin-top: 14px">
          <label>Contraseña</label>
          <Password v-model="form.password" :feedback="false" toggleMask placeholder="Introduce tu contraseña" />
        </div>
        <Button
          label="Iniciar sesión"
          icon="pi pi-sign-in"
          style="margin-top: 20px; width: 100%"
          :loading="loading"
          @click="handleLogin"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { normalizeApiError } from '../utils/error'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    error.value = 'Introduce tu usuario y contraseña'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = normalizeApiError(e, 'Usuario o contraseña incorrectos')
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
  background: #f5f3ee;
  padding: 20px;
}
.login-card {
  background: #ffffff;
  border: 1px solid #e5e3dc;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.login-header {
  text-align: center;
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.login-header h1 {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a18;
}
.login-header p {
  font-size: 13px;
  color: #6b7280;
}
.field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 6px;
}
</style>

<style>
.login-card .p-inputtext {
  width: 100%;
}
.login-card .p-password {
  width: 100%;
  display: flex;
  position: relative;
}
.login-card .p-password input {
  width: 100%;
  flex: 1;
  min-width: 0;
}
.login-card .p-password-toggle-mask-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  margin: 0;
}
</style>

