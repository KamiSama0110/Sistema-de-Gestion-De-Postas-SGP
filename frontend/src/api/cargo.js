import api from './index'

export const cargoApi = {
  listar(soloActivos = true, page = 1, size = 10) {
    return api.get('/cargos', { params: { solo_activos: soloActivos, page, size } })
  },
  obtener(id) {
    return api.get(`/cargos/${id}`)
  },
  crear(datos) {
    return api.post('/cargos', datos)
  },
  actualizar(id, datos) {
    return api.patch(`/cargos/${id}`, datos)
  },
  cambiarEstado(id, activo) {
    return api.patch(`/cargos/${id}/estado`, { activo })
  },
}