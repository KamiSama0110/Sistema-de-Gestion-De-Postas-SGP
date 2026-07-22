<template>
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
    <div v-if="isRail" class="d-flex flex-column align-center ga-1 py-2">
      <v-tooltip v-for="item in navItems" :key="item.to" :text="item.label" location="end">
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

    <!-- Expanded mode: standard list -->
    <v-list v-else nav density="comfortable" class="px-2" active-class="sgp-nav-active" aria-label="Navegación principal">
      <v-list-item
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.label"
        rounded="lg"
        :active="isActive(item.to)"
      />
    </v-list>

    <template #append>
      <v-divider class="mx-3 mt-2 mb-2" />

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
      <template v-else>
        <v-list nav density="comfortable" class="px-2">
          <v-list-item
            prepend-icon="mdi-chevron-left"
            title="Contraer menú"
            rounded="lg"
            @click="toggleRail"
          />
        </v-list>
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
    </v-app-bar>

    <v-container fluid id="main-content" tabindex="-1" class="pa-4 pa-sm-6">
      <RouterView />
    </v-container>
  </v-main>
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

const navItems = [
  { to: '/', icon: 'mdi-view-dashboard-outline', label: 'Dashboard' },
  { to: '/asp', icon: 'mdi-account-group-outline', label: 'ASP' },
  { to: '/cargos', icon: 'mdi-card-account-details-outline', label: 'Cargos' },
  { to: '/turnos', icon: 'mdi-clock-outline', label: 'Turnos' },
  { to: '/postas', icon: 'mdi-office-building-outline', label: 'Postas' },
  { to: '/guardias', icon: 'mdi-shield-check-outline', label: 'Guardias' },
  { to: '/reportes', icon: 'mdi-chart-box-outline', label: 'Reportes' },
]

const sectionLabel = computed(() => {
  const item = navItems.find((n) => n.to === route.path)
  return item?.label || 'Panel'
})

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
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

async function handleLogout() {
  try {
    await auth.logout()
  } catch {
    // logout falló pero limpiamos estado local
  } finally {
    router.push({ name: 'login' })
  }
}
</script>

<style>
.sgp-sidebar {
  border-right: 1px solid rgb(var(--v-border-color)) !important;
}

.sgp-nav-active {
  background-color: rgba(21, 101, 192, 0.08) !important;
  color: rgb(var(--v-theme-primary)) !important;
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
