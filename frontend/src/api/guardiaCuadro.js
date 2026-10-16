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
  iniciar(id, datos = {}) {
    return api.post(`/guardias-cuadro/${id}/iniciar`, datos)
  },
  finalizar(id, datos = {}) {
    return api.post(`/guardias-cuadro/${id}/finalizar`, datos)
  },
  incumplir(id, datos) {
    return api.post(`/guardias-cuadro/${id}/incumplir`, datos)
  },
  cancelar(id, datos) {
    return api.post(`/guardias-cuadro/${id}/cancelar`, datos)
  },
  crearIncidencia(id, datos) {
    return api.post(`/guardias-cuadro/${id}/incidencias`, datos)
  },
}
