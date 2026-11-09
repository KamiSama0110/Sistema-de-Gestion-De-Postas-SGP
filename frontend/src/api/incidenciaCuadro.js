import api from './index'

const BASE = '/incidencias-cuadro'

export const incidenciaCuadroApi = {
  listar(params = {}) {
    return api.get(BASE, { params })
  },
  obtener(id) {
    return api.get(`${BASE}/${id}`)
  },
  editar(id, datos) {
    return api.patch(`${BASE}/${id}`, datos)
  },
}
