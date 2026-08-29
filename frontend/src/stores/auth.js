import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import { renovarSesion } from '../api/index'
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  clearTokens,
} from '../api/token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getAccessToken())
  const usuario = ref(null)

  const isAuthenticated = computed(() => !!getAccessToken() || !!getRefreshToken())

  async function login(username, password) {
    const response = await authApi.login({ username, password })
    const accessToken = response.data?.access_token
    const refreshToken = response.data?.refresh_token
    if (!accessToken || !refreshToken) throw new Error('Tokens no recibidos')
    token.value = accessToken
    setAccessToken(accessToken)
    setRefreshToken(refreshToken)
  }

  async function logout() {
    try {
      await authApi.logout(getRefreshToken())
    } catch {
      // logout falló pero limpiamos estado local, el refresh expira solo
    } finally {
      token.value = null
      usuario.value = null
      clearTokens()
    }
  }

  async function refrescarSesion() {
    const refresh = getRefreshToken()
    if (!refresh) return false
    try {
      const accessToken = await renovarSesion()
      token.value = accessToken
      return true
    } catch {
      token.value = null
      usuario.value = null
      clearTokens()
      return false
    }
  }

  return { token, usuario, isAuthenticated, login, logout, refrescarSesion }
})
