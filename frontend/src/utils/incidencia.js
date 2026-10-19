export const TIPOS_INCIDENCIA = [
  { title: 'Incidente', value: 'incidente' },
  { title: 'Comunicado', value: 'comunicado' },
  { title: 'Entrega/recepción', value: 'entrega_recepcion' },
  { title: 'Solicitud', value: 'solicitud' },
  { title: 'Otro', value: 'otro' },
]

export const SEVERIDADES = [
  { title: 'Baja', value: 'baja', color: 'grey' },
  { title: 'Media', value: 'media', color: 'info' },
  { title: 'Alta', value: 'alta', color: 'warning' },
  { title: 'Crítica', value: 'critica', color: 'error' },
]

export function tipoLabel(value) {
  return TIPOS_INCIDENCIA.find((t) => t.value === value)?.title || value
}

export function severidadLabel(value) {
  return SEVERIDADES.find((s) => s.value === value)?.title || value
}

export function severidadColor(value) {
  return SEVERIDADES.find((s) => s.value === value)?.color || 'grey'
}

export const AVISO_FUERA_FECHA =
  'Fuera de la fecha de la guardia. Debe comunicarse con el administrador.'

// Margen de registro: 24 h antes o después de la fecha de la guardia.
export function ventanaRegistro(fecha) {
  if (!fecha) return { dentro: false, despues: false }
  const [y, m, d] = fecha.split('-').map(Number)
  const ahora = new Date()
  const inicio = new Date(y, m - 1, d - 1)
  const fin = new Date(y, m - 1, d + 2) 
  const despues = ahora >= new Date(y, m - 1, d + 1)
  return { dentro: ahora >= inicio && ahora < fin, despues }
}

export function puedeRegistrarIncidencia(guardia) {
  if (!guardia) return false
  if (['activa', 'finalizada'].includes(guardia.estado)) return true
  return ventanaRegistro(guardia.fecha).dentro
}

export function requiereAvisoAdministrador(guardia) {
  if (!guardia || !puedeRegistrarIncidencia(guardia)) return false
  return ventanaRegistro(guardia.fecha).despues
}
