import api from './index'

export const feriadoApi = {
  listar(params = {}) {
    return api.get('/feriados', { params })
  },
  crear(datos) {
    return api.post('/feriados', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/feriados/${id}`, datos)
  },
  eliminar(id) {
    return api.delete(`/feriados/${id}`)
  },
  sugeridos(anio) {
    return api.get('/feriados/sugeridos', { params: { anio } })
  },
  cargarSugeridos(anio) {
    return api.post('/feriados/sugeridos', null, { params: { anio } })
  },
}
