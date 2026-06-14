import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'
import './assets/main.css'

function scrollFirstFormErrorIntoView() {
  const formMessages = Array.from(document.querySelectorAll('.form-message'))
    .filter((element) => element instanceof HTMLElement && element.offsetParent !== null)

  const target = formMessages[0]
  if (!target) return

  target.scrollIntoView({ block: 'start', behavior: 'smooth' })
}

let scrollScheduled = false

function scheduleFormErrorScroll() {
  if (scrollScheduled) return
  scrollScheduled = true

  requestAnimationFrame(() => {
    scrollScheduled = false
    scrollFirstFormErrorIntoView()
  })
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: 'none',
      cssLayer: false,
    },
  },
})
app.use(ToastService)

app.mount('#app')

const observer = new MutationObserver(scheduleFormErrorScroll)
observer.observe(document.body, {
  subtree: true,
  childList: true,
  attributes: true,
  attributeFilter: ['class', 'style'],
})

window.addEventListener('load', scheduleFormErrorScroll, { once: true })
