<template>
  <div class="sgp-app-layout">
    <a href="#main-content" class="sgp-skip-link">Saltar al contenido</a>

  <v-navigation-drawer
    v-model="drawer"
    :rail="isRail"
    :permanent="!mobile"
    :temporary="mobile"
    :width="240"
    :rail-width="64"
    elevation="0"
    class="sgp-sidebar"
  >
    <div class="d-flex align-center pa-3 ga-3 sidebar-logo">
      <v-avatar color="primary" size="36" rounded="lg">
        <v-icon color="white" size="18">mdi-shield-half</v-icon>
      </v-avatar>
      <div v-if="!isRail" class="overflow-hidden">
        <div class="text-subtitle-2 font-weight-bold text-truncate">SGP</div>
        <div class="text-caption text-medium-emphasis text-truncate">Gestion operativa</div>
      </div>
    </div>

    <v-divider v-if="!isRail" class="mx-3 mb-2" />

    <!-- Rail mode: icon buttons -->
    <div v-if="isRail" class="d-flex flex-column align-center py-2">
      <template v-for="(group, gi) in navGroupsVisibles" :key="group.label">
        <v-divider v-if="gi > 0 && group.mostrarCabecera" class="my-2" style="width: 32px" />
        <div class="d-flex flex-column align-center ga-1">
          <v-tooltip v-for="item in group.items" :key="item.to" :text="item.label" location="end">
            <template #activator="{ props: tipProps }">
              <v-btn
                v-bind="tipProps"
                :to="item.to"
                icon
                size="small"
                variant="text"
                :color="isActive(item.to) ? 'primary' : undefined"
                :class="{ 'sgp-nav-active-rail': isActive(item.to) }"
                :aria-label="item.label"
              >
                <v-icon :icon="item.icon" size="20" />
              </v-btn>
            </template>
          </v-tooltip>
        </div>
      </template>
    </div>

    <!-- Expanded mode: standard list -->
    <v-list v-else nav density="comfortable" class="px-2" active-class="sgp-nav-active" aria-label="Navegación principal">
      <template v-for="(group, gi) in navGroupsVisibles" :key="group.label">
        <v-divider v-if="gi > 0 && group.mostrarCabecera" class="mx-3 mb-1" />
        <v-list-subheader v-if="group.mostrarCabecera" class="sgp-nav-header">
          {{ group.label }}
        </v-list-subheader>
        <v-list-item
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.label"
          rounded="lg"
          :active="isActive(item.to)"
        />
      </template>
    </v-list>

    <template #append>
      <!-- Rail: toggle + logout as icon buttons -->
      <div v-if="isRail" class="d-flex flex-column align-center ga-1 py-2">
        <v-tooltip text="Expandir menú" location="end">
          <template #activator="{ props: tipProps }">
            <v-btn v-bind="tipProps" icon size="small" variant="text" aria-label="Expandir menú" @click="toggleRail">
              <v-icon icon="mdi-chevron-right" size="20" />
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip text="Salir" location="end">
          <template #activator="{ props: tipProps }">
            <v-btn v-bind="tipProps" icon size="small" variant="text" color="error" aria-label="Salir" @click="handleLogout">
              <v-icon icon="mdi-logout" size="20" />
            </v-btn>
          </template>
        </v-tooltip>
      </div>

      <!-- Expanded: list items -->
      <template v-if="!isRail">
        <template v-if="!mobile">
          <v-divider class="mx-3 my-2" />
          <v-list nav density="comfortable" class="px-2">
            <v-list-item
              prepend-icon="mdi-chevron-left"
              title="Contraer menú"
              rounded="lg"
              @click="toggleRail"
            />
          </v-list>
        </template>
        <v-divider class="mx-3 my-2" />
        <v-list nav density="comfortable" class="px-2">
          <v-list-item
            prepend-icon="mdi-logout"
            title="Salir"
            rounded="lg"
            class="text-error"
            @click="handleLogout"
          />
        </v-list>
      </template>
    </template>
  </v-navigation-drawer>

  <v-main>
    <v-app-bar flat height="64" class="sgp-topbar border-b">
      <v-app-bar-nav-icon
        v-if="mobile"
        aria-label="Abrir menu"
        @click="drawer = !drawer"
      />
      <v-toolbar-title class="text-subtitle-1 font-weight-bold">
        {{ sectionLabel }}
      </v-toolbar-title>
      <div class="d-none d-sm-flex align-center ga-2 mr-4 text-body-2 text-medium-emphasis">
        <v-icon size="16" icon="mdi-calendar-clock-outline" />
        <span>{{ now }}</span>
      </div>
      <div class="d-flex align-center ga-2 mr-2">
        <span class="text-body-2 font-weight-medium d-none d-sm-inline text-truncate">{{
          auth.nombreMostrado
        }}</span>
        <v-chip
          size="small"
          variant="tonal"
          :color="auth.esAdmin ? 'primary' : 'secondary'"
          :prepend-icon="auth.esAdmin ? 'mdi-shield-account-outline' : 'mdi-account-outline'"
        >
          {{ auth.esAdmin ? 'Administrador' : 'Cuadro' }}
        </v-chip>
      </div>
    </v-app-bar>

    <v-container fluid id="main-content" tabindex="-1" class="pa-4 pa-sm-6">
      <RouterView v-slot="{ Component }">
        <Transition name="page-slide" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </v-container>
    </v-main>

    <v-dialog v-model="logoutDialog" max-width="400">
      <v-card class="pa-sm-5 pa-3">
        <v-card-title class="d-flex align-center ga-2 text-subtitle-1 font-weight-bold">
          <v-icon color="error">mdi-logout</v-icon>
          Cerrar sesión
        </v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          ¿Seguro que deseas cerrar la sesión? Deberás iniciar sesión nuevamente.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="logoutDialog = false">Cancelar</v-btn>
          <v-btn color="error" :loading="logoutLoading" @click="confirmLogout">Sí, salir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useDisplay } from 'vuetify'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { mobile } = useDisplay()

const drawer = ref(true)
const rail = ref(false)
const now = ref(formatNow())

let clockInterval = null

function formatNow() {
  const d = new Date()
  const dia = d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  const hora = d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  return `${dia} · ${hora}`
}

onMounted(() => {
  clockInterval = setInterval(() => { now.value = formatNow() }, 30000)
})

onUnmounted(() => {
  clearInterval(clockInterval)
})

const isRail = computed(() => !mobile.value && rail.value)

const navGroups = [
  {
    label: 'General',
    items: [{ to: '/', icon: 'mdi-view-dashboard-outline', label: 'Dashboard', roles: ['admin'] }],
  },
  {
    label: 'Operación ASP',
    items: [
      { to: '/cargos', icon: 'mdi-card-account-details-outline', label: 'Cargos', roles: ['admin'] },
      { to: '/postas', icon: 'mdi-office-building-outline', label: 'Postas', roles: ['admin'] },
      { to: '/turnos', icon: 'mdi-clock-outline', label: 'Turnos', roles: ['admin'] },
      { to: '/asp', icon: 'mdi-account-group-outline', label: 'ASP', roles: ['admin'] },
      { to: '/guardias', icon: 'mdi-shield-check-outline', label: 'Guardias', roles: ['admin'] },
      { to: '/reportes', icon: 'mdi-chart-box-outline', label: 'Reportes', roles: ['admin'] },
    ],
  },
  {
    label: 'Cuadros',
    items: [
      { to: '/cuadros', icon: 'mdi-account-tie-outline', label: 'Cuadros', roles: ['admin'] },
      { to: '/configuracion-guardias', icon: 'mdi-tune-variant', label: 'Config. de guardias', roles: ['admin'] },
      { to: '/planes-cuadro', icon: 'mdi-calendar-month-outline', label: 'Planificación de cuadros', roles: ['admin'] },
      { to: '/operativo-cuadro', icon: 'mdi-clipboard-clock-outline', label: 'Guardias de cuadro', roles: ['admin'] },
      { to: '/incidencias-cuadro', icon: 'mdi-clipboard-alert-outline', label: 'Incidencias de cuadros', roles: ['admin'] },
      { to: '/reportes-cuadros', icon: 'mdi-file-chart-outline', label: 'Reportes de cuadros', roles: ['admin'] },
    ],
  },
  {
    label: 'Mis guardias',
    items: [{ to: '/mis-guardias', icon: 'mdi-shield-account-outline', label: 'Mis guardias', roles: ['cuadro'] }],
  },
]

const navGroupsVisibles = computed(() =>
  navGroups
    .map((g) => {
      const items = g.items.filter((i) => i.roles.includes(auth.rol))
      return { label: g.label, items, mostrarCabecera: items.length > 1 }
    })
    .filter((g) => g.items.length > 0),
)

const navFiltrados = computed(() => navGroupsVisibles.value.flatMap((g) => g.items))

const sectionLabel = computed(() => {
  const item = navFiltrados.value.find((n) => isActive(n.to))
  return item?.label || 'Panel'
})

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path === to || route.path.startsWith(`${to}/`)
}

function toggleRail() {
  rail.value = !rail.value
}

watch(() => mobile.value, (isMobile) => {
  if (isMobile) {
    rail.value = false
    drawer.value = false
  } else {
    drawer.value = true
  }
}, { immediate: true })

watch(() => route.fullPath, () => {
  if (mobile.value) drawer.value = false
})

const logoutDialog = ref(false)
const logoutLoading = ref(false)

function handleLogout() {
  logoutDialog.value = true
}

async function confirmLogout() {
  logoutLoading.value = true
  try {
    await auth.logout()
  } catch {
    // logout falló pero limpiamos estado local
  } finally {
    logoutLoading.value = false
    logoutDialog.value = false
    router.push({ name: 'login' })
  }
}
</script>

<style>
.sgp-app-layout {
  display: flex;
  flex: 1 1 auto;
  min-width: 0;
}

.sgp-sidebar {
  border-right: 1px solid rgb(var(--v-border-color)) !important;
}

.sgp-nav-active {
  background-color: rgba(21, 101, 192, 0.08) !important;
  color: rgb(var(--v-theme-primary)) !important;
}

.sgp-nav-header {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(0, 0, 0, 0.45);
  height: 32px;
  min-height: 32px;
}

.sgp-nav-active-rail {
  background-color: rgba(21, 101, 192, 0.08) !important;
}

.sgp-topbar {
  border-bottom: 1px solid rgb(var(--v-border-color));
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(8px);
}

#main-content:focus {
  outline: none;
}
</style>
