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
