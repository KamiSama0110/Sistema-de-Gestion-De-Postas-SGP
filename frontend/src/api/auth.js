import api from './index'

export const authApi = {
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  logout(refreshToken) {
    return api.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : undefined)
  },
  cambiarContrasena(datos) {
    return api.patch('/auth/cambiar-contrasena', datos)
  },
  refresh(refreshToken) {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },
}
