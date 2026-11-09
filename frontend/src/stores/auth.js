import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
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

  const rol = computed(() => usuario.value?.rol || null)
  const esAdmin = computed(() => rol.value === 'admin')
  const esCuadro = computed(() => rol.value === 'cuadro')
  const nombreMostrado = computed(() => {
    const u = usuario.value
    if (!u) return ''
    if (u.cuadro) return `${u.cuadro.nombre} ${u.cuadro.apellidos}`.trim()
    return u.username || ''
  })

  function isAuthenticated() {
    return !!getAccessToken() || !!getRefreshToken()
  }

  async function cargarUsuario() {
    try {
      const { data } = await authApi.me()
      usuario.value = data
      return true
    } catch (err) {
      usuario.value = null
      if (err?.response?.status === 401) {
        token.value = null
        clearTokens()
      }
      return false
    }
  }

  async function login(username, password) {
    const response = await authApi.login({ username, password })
    const accessToken = response.data?.access_token
    const refreshToken = response.data?.refresh_token
    if (!accessToken || !refreshToken) throw new Error('Tokens no recibidos')
    token.value = accessToken
    setAccessToken(accessToken)
    setRefreshToken(refreshToken)
    const cargado = await cargarUsuario()
    if (!cargado) {
      token.value = null
      usuario.value = null
      clearTokens()
      throw new Error('No se pudo obtener el perfil del usuario')
    }
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

  return {
    token,
    usuario,
    rol,
    esAdmin,
    esCuadro,
    nombreMostrado,
    isAuthenticated,
    cargarUsuario,
    login,
    logout,
    refrescarSesion,
  }
})
