import api from './index'

export const cargoApi = {
  listar(soloActivos = true) {
    return api.get('/cargos', { params: { solo_activos: soloActivos } })
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