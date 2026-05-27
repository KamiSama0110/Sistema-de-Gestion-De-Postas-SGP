import api from './index'

export const aspApi = {
  listar(params = {}) {
    return api.get('/asp', { params })
  },
  obtener(id) {
    return api.get(`/asp/${id}`)
  },
  crear(datos) {
    return api.post('/asp', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/asp/${id}`, datos)
  },
  cambiarEstado(id, datos) {
    return api.patch(`/asp/${id}/estado`, datos)
  },
}