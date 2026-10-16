import api from './index'

export const miGuardiaApi = {
  misGuardias(params = {}) {
    return api.get('/mis-guardias', { params })
  },
  obtener(id) {
    return api.get(`/mis-guardias/${id}`)
  },
  incidencias(id, params = {}) {
    return api.get(`/mis-guardias/${id}/incidencias`, { params })
  },
  crearIncidencia(id, datos) {
    return api.post(`/mis-guardias/${id}/incidencias`, datos)
  },
  editarIncidencia(incidenciaId, datos) {
    return api.patch(`/mis-incidencias/${incidenciaId}`, datos)
  },
  planificacion(params = {}) {
    return api.get('/mi-planificacion', { params })
  },
  opcionesIncidencia() {
    return api.get('/mis-guardias/opciones-incidencia')
  },
}
