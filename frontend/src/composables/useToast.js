import { reactive } from 'vue'

const toasts = reactive([])
let toastId = 0

export function useToast() {
  function add({ type = 'info', title = '', message = '', timeout = 3000 } = {}) {
    const id = ++toastId
    toasts.push({ id, type, title, message, visible: true })
    if (timeout > 0) {
      setTimeout(() => remove(id), timeout)
    }
    return id
  }

  function remove(id) {
    const idx = toasts.findIndex((t) => t.id === id)
    if (idx !== -1) toasts.splice(idx, 1)
  }

  function success(message, title = '') {
    return add({ type: 'success', title, message })
  }

  function error(message, title = '') {
    return add({ type: 'error', title, message })
  }

  function warning(message, title = '') {
    return add({ type: 'warning', title, message })
  }

  function info(message, title = '') {
    return add({ type: 'info', title, message })
  }

  return { toasts, add, remove, success, error, warning, info }
}
