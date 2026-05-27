export function normalizeApiError(error, fallback = 'Ocurrio un error') {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map(item => (typeof item?.msg === 'string' ? item.msg : ''))
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
