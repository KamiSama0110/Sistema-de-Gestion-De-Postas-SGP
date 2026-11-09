export function normalizeApiError(error, fallback = 'Ocurrio un error') {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map(item => {
        if (typeof item?.msg !== 'string') return ''
        return item.msg.replace(/^Value error,\s*/i, '')
      })
      .filter(Boolean)
    if (messages.length) {
      return messages.join(', ')
    }
  }

  if (detail && typeof detail === 'object') {
    const message = detail.message || detail.error || detail.detail
    if (typeof message === 'string' && message.trim()) {
      return message
    }
  }

  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }

  return fallback
}

function inferFieldFromMessage(msg) {
  const lower = msg.toLowerCase()
  if (/\bci\b/.test(lower) || lower.includes('cédula') || lower.includes('cedula') || lower.includes('dígito') || lower.includes('digito')) {
    return 'ci'
  }
  if (lower.includes('contraseña') || lower.includes('contrasena') || lower.includes('password')) return 'password'
  if (lower.includes('usuario') || lower.includes('username')) return 'username'
  if (lower.includes('apellido')) return 'apellidos'
  if (lower.includes('nombre')) return 'nombre'
  if (lower.includes('cargo')) return 'cargo'
  if (lower.includes('área') || /\barea\b/.test(lower)) return 'area'
  if (lower.includes('teléfono') || lower.includes('telefono')) return 'telefono'
  if (lower.includes('sexo')) return 'sexo'
  if (lower.includes('observacion') || lower.includes('observación')) return 'observaciones'
  if (lower.includes('fecha')) return 'fecha'
  if (lower.includes('descripcion') || lower.includes('descripción')) return 'descripcion'
  return null
}

export function extractFieldErrors(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') {
    const msg = detail.replace(/^Value error,\s*/i, '')
    const field = inferFieldFromMessage(msg)
    return field ? { [field]: msg } : { _global: msg }
  }
  if (Array.isArray(detail)) {
    const fields = {}
    for (const item of detail) {
      if (!item?.loc) continue
      const field = item.loc[item.loc.length - 1]
      const msg = (item.msg || '').replace(/^Value error,\s*/i, '')
      if (msg) fields[field] = msg
    }
    return Object.keys(fields).length ? fields : { _global: detail.map(d => d.msg).join(', ') }
  }
  return {}
}
