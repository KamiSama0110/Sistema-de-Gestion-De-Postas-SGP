<template>
  <a href="#main-content" class="sgp-skip-link">Saltar al contenido</a>

  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    :permanent="!mobile"
    :temporary="mobile"
    :width="220"
    :rail-width="72"
    elevation="0"
    class="sgp-sidebar"
    @click="handleRailClick"
  >
    <div class="d-flex align-center pa-3 ga-3 sidebar-logo">
      <v-avatar color="primary" size="40" rounded="lg">
        <v-icon color="white" size="20">mdi-shield-half</v-icon>
      </v-avatar>
      <div v-if="!rail" class="overflow-hidden">
        <div class="text-subtitle-2 font-weight-bold text-truncate">SGP</div>
        <div class="text-caption text-medium-emphasis text-truncate">Gestion operativa</div>
      </div>
    </div>

    <v-divider v-if="!rail" class="mx-3 mb-2" />

    <v-list nav density="comfortable" class="px-2" active-class="sgp-nav-active" aria-label="Navegación principal">
      <v-list-item
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="rail ? undefined : item.label"
        rounded="lg"
        :active="isActive(item.to)"
        :class="{ 'justify-center': rail }"
      />
    </v-list>

    <template #append>
      <v-divider class="mx-3 mt-2 mb-2" />
      <v-list nav density="comfortable" class="px-2">
        <v-list-item
          prepend-icon="mdi-logout"
          :title="rail ? undefined : 'Salir'"
          rounded="lg"
          :class="{ 'justify-center': rail, 'text-error': true }"
          @click="handleLogout"
        />
      </v-list>
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
      <v-chip
        color="primary"
        variant="tonal"
        size="small"
        prepend-icon="mdi-circle"
        class="mr-4 d-none d-sm-flex"
      >
        Operativo
      </v-chip>
    </v-app-bar>

    <v-container fluid id="main-content" tabindex="-1" class="pa-4 pa-sm-6">
      <RouterView />
    </v-container>
  </v-main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useDisplay } from 'vuetify'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { mobile } = useDisplay()

const drawer = ref(true)
const rail = ref(false)

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

function handleRailClick(e) {
  if (rail.value) {
    const clickedItem = e.target.closest('.v-list-item')
    if (clickedItem) return
    rail.value = false
  }
}

watch(() => route.fullPath, () => {
  if (mobile.value) drawer.value = false
  if (!mobile.value) rail.value = true
}, { immediate: true })

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

.sgp-topbar {
  border-bottom: 1px solid rgb(var(--v-border-color));
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(8px);
}

#main-content:focus {
  outline: none;
}
</style>
