import axios from 'axios'
import {
  getAccessToken,
  setAccessToken,
  getRefreshToken,
  setRefreshToken,
  clearTokens,
} from './token'

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir el access token (solo en memoria) a cada request
api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

// Renueva la sesión usando el refresh token y actualiza ambos tokens.
// Exportada para ser reutilizada por el store (restauración en F5).
export async function renovarSesion() {
  const refresh = getRefreshToken()
  if (!refresh) throw new Error('No hay refresh token')
  const { data } = await api.post('/auth/refresh', { refresh_token: refresh })
  if (!data?.access_token || !data?.refresh_token) {
    throw new Error('Respuesta de refresh inválida')
  }
  setAccessToken(data.access_token)
  setRefreshToken(data.refresh_token)
  return data.access_token
}

// Single-flight: si varios requests fallan con 401 a la vez, todos se cuelgan
// del mismo refresh en curso en vez de disparar N rotaciones paralelas.
function refrescoEnCurso() {
  if (!refreshPromise) {
    refreshPromise = renovarSesion().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const requestUrl = String(original?.url || '')

    if (
      error.response?.status === 401 &&
      !requestUrl.includes('/auth/login') &&
      !requestUrl.includes('/auth/refresh') &&
      original &&
      !original._retry
    ) {
      original._retry = true
      try {
        await refrescoEnCurso()
        original.headers.Authorization = `Bearer ${getAccessToken()}`
        return api(original)
      } catch (refreshError) {
        clearTokens()
        // window.location.href fuerza un reload completo que limpia el estado
        // de Vue y mitiga XSS.
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  },
)

export default api
