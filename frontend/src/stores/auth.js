import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('token') || null)
  const usuario = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const response = await authApi.login({ username, password })
    const tokenValue = response.data?.access_token
    if (!tokenValue) throw new Error('Token no recibido')
    token.value = tokenValue
    sessionStorage.setItem('token', tokenValue)
  }

  async function logout() {
    token.value = null
    usuario.value = null
    sessionStorage.removeItem('token')
    await authApi.logout().catch(() => {})
  }

  return { token, usuario, isAuthenticated, login, logout }
})
