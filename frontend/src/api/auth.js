import api from './index'

export const authApi = {
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  logout() {
    return api.post('/auth/logout')
  },
  cambiarContrasena(datos) {
    return api.patch('/auth/cambiar-contrasena', datos)
  },
}