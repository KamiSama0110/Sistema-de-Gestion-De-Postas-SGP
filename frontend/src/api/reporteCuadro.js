import api from './index'

export const reporteCuadroApi = {
  cumplimiento(params) {
    return api.get('/reportes-cuadros/cumplimiento', { params })
  },
  guardiasPorCuadro(params) {
    return api.get('/reportes-cuadros/guardias-por-cuadro', { params })
  },
  incidencias(params) {
    return api.get('/reportes-cuadros/incidencias', { params })
  },
  diasSinCubrir(params) {
    return api.get('/reportes-cuadros/dias-sin-cubrir', { params })
  },
  incumplimientos(params) {
    return api.get('/reportes-cuadros/incumplimientos', { params })
  },
}
