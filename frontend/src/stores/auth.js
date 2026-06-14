import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('token') || null)
  const usuario = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const response = await authApi.login({ username, password })
    token.value = response.data.access_token
    sessionStorage.setItem('token', token.value)
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      token.value = null
      usuario.value = null
      sessionStorage.removeItem('token')
    }
  }

  return { token, usuario, isAuthenticated, login, logout }
})
