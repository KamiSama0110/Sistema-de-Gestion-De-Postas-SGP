export function formatFecha(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.split('T')[0]
  const d = value instanceof Date ? value : new Date(value)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function formatHora(value) {
  if (!value) return ''
  const parts = String(value).split(':')
  if (parts.length < 2) return value
  return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`
}

export function formatFechaHora(value) {
  if (!value) return ''
  if (typeof value === 'string') return value.replace('T', ' ').slice(0, 16)
  const d = new Date(value)
  return d.toISOString().replace('T', ' ').slice(0, 16)
}

export function parseDateOnly(value) {
  if (!value) return null
  if (value instanceof Date) return value
  if (typeof value !== 'string') return null
  const [year, month, day] = value.split('T')[0].split('-').map(Number)
  if (!year || !month || !day) return null
  return new Date(year, month - 1, day, 12, 0, 0)
}
