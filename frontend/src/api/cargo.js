import api from './index'

export const cargoApi = {
  listar(soloActivos = true, page = 1, size = 10, buscar = null) {
    const params = { solo_activos: soloActivos, page, size }
    if (buscar) params.buscar = buscar
    return api.get('/cargos', { params })
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