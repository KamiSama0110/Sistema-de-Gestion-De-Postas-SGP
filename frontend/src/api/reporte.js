import api from './index'

export const reporteApi = {
  cobertura(params) {
    return api.get('/reportes/cobertura', { params })
  },
  ausentismo(params) {
    return api.get('/reportes/ausentismo', { params })
  },
  horasAsp(params) {
    return api.get('/reportes/horas-asp', { params })
  },
  incidencias(params) {
    return api.get('/reportes/incidencias', { params })
  },
  tardanzas(params) {
    return api.get('/reportes/tardanzas', { params })
  },
}