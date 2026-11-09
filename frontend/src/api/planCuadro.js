import api from './index'

const BASE = '/planes-guardia-cuadro'

export const planCuadroApi = {
  listar(params = {}) {
    return api.get(BASE, { params })
  },
  obtener(id) {
    return api.get(`${BASE}/${id}`)
  },
  crear(datos) {
    return api.post(BASE, datos)
  },
  actualizar(id, datos) {
    return api.patch(`${BASE}/${id}`, datos)
  },
  eliminar(id) {
    return api.delete(`${BASE}/${id}`)
  },
  enviar(id) {
    return api.post(`${BASE}/${id}/enviar`)
  },
  aprobar(id) {
    return api.post(`${BASE}/${id}/aprobar`)
  },
  rechazar(id, datos = {}) {
    return api.post(`${BASE}/${id}/rechazar`, datos)
  },
  reabrir(id) {
    return api.post(`${BASE}/${id}/reabrir`)
  },
  generar(id, datos) {
    return api.post(`${BASE}/${id}/generar`, datos)
  },
  calendario(id) {
    return api.get(`${BASE}/${id}/calendario`)
  },
  candidatos(id, params) {
    return api.get(`${BASE}/${id}/candidatos`, { params })
  },
}
