import api from './index'

export const cuadroApi = {
  listar(params = {}) {
    return api.get('/cuadros', { params })
  },
  obtener(id) {
    return api.get(`/cuadros/${id}`)
  },
  crear(datos) {
    return api.post('/cuadros', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/cuadros/${id}`, datos)
  },
  cambiarEstado(id, activo) {
    return api.patch(`/cuadros/${id}/estado`, { activo })
  },
  obtenerCuenta(id) {
    return api.get(`/cuadros/${id}/cuenta`)
  },
  crearCuenta(id, datos) {
    return api.post(`/cuadros/${id}/cuenta`, datos)
  },
  cambiarPassword(id, passwordNueva) {
    return api.patch(`/cuadros/${id}/cuenta/password`, { password_nueva: passwordNueva })
  },
}
