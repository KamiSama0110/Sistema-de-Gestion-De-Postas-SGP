import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('../views/LayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'cargos',
          name: 'cargos',
          component: () => import('../views/CargosView.vue'),
        },
        {
          path: 'turnos',
          name: 'turnos',
          component: () => import('../views/TurnosView.vue'),
        },
        {
          path: 'asp',
          name: 'asp',
          component: () => import('../views/AspView.vue'),
        },
        {
          path: 'postas',
          name: 'postas',
          component: () => import('../views/PostasView.vue'),
        },
        {
          path: 'guardias',
          name: 'guardias',
          component: () => import('../views/GuardiasView.vue'),
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('../views/ReportesView.vue'),
        },
      ],
    },
  ],
})

// Guard de navegación
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth !== false && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
