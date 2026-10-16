import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'
import { getAccessToken } from '../api/token'

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
          meta: { roles: ['admin'] },
        },
        {
          path: 'cargos',
          name: 'cargos',
          component: () => import('../views/CargosView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'turnos',
          name: 'turnos',
          component: () => import('../views/TurnosView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'asp',
          name: 'asp',
          component: () => import('../views/AspView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'postas',
          name: 'postas',
          component: () => import('../views/PostasView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'guardias',
          name: 'guardias',
          component: () => import('../views/GuardiasView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'cuadros',
          name: 'cuadros',
          component: () => import('../views/CuadrosView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'configuracion-guardias',
          name: 'configuracion-guardias',
          component: () => import('../views/ConfiguracionGuardiasView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'planes-cuadro',
          name: 'planes-cuadro',
          component: () => import('../views/PlanesCuadroView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'planes-cuadro/:id',
          name: 'plan-cuadro-detalle',
          component: () => import('../views/PlanCuadroDetalleView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'operativo-cuadro',
          name: 'operativo-cuadro',
          component: () => import('../views/GuardiasCuadroView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'incidencias-cuadro',
          name: 'incidencias-cuadro',
          component: () => import('../views/IncidenciasCuadroView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'reportes-cuadros',
          name: 'reportes-cuadros',
          component: () => import('../views/ReportesCuadrosView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('../views/ReportesView.vue'),
          meta: { roles: ['admin'] },
        },
        {
          path: 'mis-guardias',
          name: 'mis-guardias',
          component: () => import('../views/MisGuardiasView.vue'),
          meta: { roles: ['cuadro'] },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

// Guard de navegación
// Tras un F5 el access token (memoria) se pierde; si existe refresh token
// en sessionStorage se restaura la sesión y se recarga el usuario antes de
// decidir. El rol del usuario decide a qué pantallas puede entrar.
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth !== false) {
    if (!auth.isAuthenticated()) {
      return { name: 'login' }
    }
    if (!getAccessToken()) {
      const restaurada = await auth.refrescarSesion()
      if (!restaurada) {
        useToast().warning('Su sesión expiró. Inicie sesión nuevamente.')
        return { name: 'login' }
      }
    }
    if (!auth.usuario) {
      const cargado = await auth.cargarUsuario()
      if (!cargado) {
        return { name: 'login' }
      }
    }
    const roles = to.meta.roles
    if (Array.isArray(roles) && roles.length && !roles.includes(auth.rol)) {
      useToast().warning('No tiene permisos para esta acción')
      return { name: auth.esCuadro ? 'mis-guardias' : 'dashboard' }
    }
    return true
  }
  if (to.name === 'login' && auth.isAuthenticated()) {
    if (!getAccessToken()) {
      const restaurada = await auth.refrescarSesion()
      if (!restaurada) return true
    }
    if (!auth.usuario) {
      const cargado = await auth.cargarUsuario()
      if (!cargado) return true
    }
    return { name: auth.esCuadro ? 'mis-guardias' : 'dashboard' }
  }
})

export default router
