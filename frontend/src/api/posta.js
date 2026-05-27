import api from './index'

export const postaApi = {
  listar(params = {}) {
    return api.get('/postas', { params })
  },
  obtener(id) {
    return api.get(`/postas/${id}`)
  },
  crear(datos) {
    return api.post('/postas', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/postas/${id}`, datos)
  },
  cambiarEstado(id, activa) {
    return api.patch(`/postas/${id}/estado`, null, { params: { activa } })
  },
  agregarTurno(postaId, datos) {
    return api.post(`/postas/${postaId}/turnos`, datos)
  },
  actualizarTurno(turnoId, datos) {
    return api.patch(`/postas/turnos/${turnoId}`, datos)
  },
  cambiarEstadoTurno(turnoId, activo) {
    return api.patch(`/postas/turnos/${turnoId}/estado`, null, { params: { activo } })
  },
}
