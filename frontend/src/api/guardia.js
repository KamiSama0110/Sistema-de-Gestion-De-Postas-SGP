import api from './index'

export const guardiaApi = {
  listar(params = {}) {
    return api.get('/guardias', { params })
  },
  obtener(id) {
    return api.get(`/guardias/${id}`)
  },
  crear(datos) {
    return api.post('/guardias', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/guardias/${id}`, datos)
  },
  confirmarLlegada(id, hora_llegada) {
    return api.patch(`/guardias/${id}/confirmar-llegada`, { hora_llegada })
  },
  finalizar(id, datos) {
    return api.patch(`/guardias/${id}/finalizar`, datos)
  },
  registrarNovedad(id, datos) {
    return api.post(`/guardias/${id}/novedades`, datos)
  },
  listarNovedades(id) {
    return api.get(`/guardias/${id}/novedades`)
  },
}