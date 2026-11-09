import api from './index'

export const franjaApi = {
  listar() {
    return api.get('/franjas-cuadro')
  },
  actualizar(id, datos) {
    return api.patch(`/franjas-cuadro/${id}`, datos)
  },
}
