import api from './index'

export const guardiaCuadroApi = {
  listar(params = {}) {
    return api.get('/guardias-cuadro', { params })
  },
  crear(planId, datos) {
    return api.post(`/planes-guardia-cuadro/${planId}/guardias`, datos)
  },
  actualizar(id, datos) {
    return api.patch(`/guardias-cuadro/${id}`, datos)
  },
  eliminar(id) {
    return api.delete(`/guardias-cuadro/${id}`)
  },
}
