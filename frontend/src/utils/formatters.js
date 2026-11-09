function toLocalDate(value) {
  if (value instanceof Date) return value
  const s = String(value)
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    const [year, month, day] = s.split('-').map(Number)
    return new Date(year, month - 1, day)
  }
  return new Date(s)
}

export function formatFecha(value) {
  if (!value) return ''
  const d = toLocalDate(value)
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
  const d = toLocalDate(value)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

export function soloDigitos(value, maxLength = 11) {
  return String(value ?? '').replace(/\D/g, '').slice(0, maxLength)
}

export function parseDateOnly(value) {
  if (!value) return null
  if (value instanceof Date) return value
  if (typeof value !== 'string') return null
  const [year, month, day] = value.split('T')[0].split('-').map(Number)
  if (!year || !month || !day) return null
  return new Date(year, month - 1, day, 12, 0, 0)
}
