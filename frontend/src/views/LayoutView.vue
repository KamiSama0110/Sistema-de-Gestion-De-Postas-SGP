<template>
  <div class="layout">
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="sidebar-logo">
        <span>SGP</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/" class="nav-item" :class="{ active: route.name === 'dashboard' }" @click="closeMenu">
          <i class="pi pi-home nav-icon"></i>
          <span class="nav-label">Dashboard</span>
        </RouterLink>
        <RouterLink to="/asp" class="nav-item" :class="{ active: route.name === 'asp' }" @click="closeMenu">
          <i class="pi pi-users nav-icon"></i>
          <span class="nav-label">ASP</span>
        </RouterLink>
        <RouterLink to="/cargos" class="nav-item" :class="{ active: route.name === 'cargos' }" @click="closeMenu">
          <i class="pi pi-id-card nav-icon"></i>
          <span class="nav-label">Cargos</span>
        </RouterLink>
        <RouterLink to="/turnos" class="nav-item" :class="{ active: route.name === 'turnos' }" @click="closeMenu">
          <i class="pi pi-clock nav-icon"></i>
          <span class="nav-label">Turnos</span>
        </RouterLink>
        <RouterLink to="/postas" class="nav-item" :class="{ active: route.name === 'postas' }" @click="closeMenu">
          <i class="pi pi-map-marker nav-icon"></i>
          <span class="nav-label">Postas</span>
        </RouterLink>
        <RouterLink to="/guardias" class="nav-item" :class="{ active: route.name === 'guardias' }" @click="closeMenu">
          <i class="pi pi-shield nav-icon"></i>
          <span class="nav-label">Guardias</span>
        </RouterLink>
        <RouterLink to="/reportes" class="nav-item" :class="{ active: route.name === 'reportes' }" @click="closeMenu">
          <i class="pi pi-chart-line nav-icon"></i>
          <span class="nav-label">Reportes</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button class="nav-item" @click="handleLogout">
          <i class="pi pi-sign-out nav-icon"></i>
          <span class="nav-label">Salir</span>
        </button>
      </div>
    </aside>

    <button v-if="menuOpen" class="sidebar-backdrop" type="button" aria-label="Cerrar menu" @click="closeMenu"></button>

    <main class="main-content">
      <header class="topbar">
        <button class="menu-button" type="button" aria-label="Abrir menu" @click="toggleMenu">
          <i class="pi pi-bars"></i>
        </button>
        <div class="topbar-copy">
          <span class="topbar-kicker">Sistema de gestion</span>
          <strong class="topbar-title">{{ sectionLabel }}</strong>
        </div>
      </header>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const menuOpen = ref(false)

const sectionLabel = computed(() => {
  const labels = {
    dashboard: 'Dashboard',
    asp: 'ASP',
    cargos: 'Cargos',
    turnos: 'Turnos',
    postas: 'Postas',
    guardias: 'Guardias',
    reportes: 'Reportes',
    login: 'Acceso',
  }
  return labels[route.name] || 'Panel'
})

watch(() => route.fullPath, () => {
  menuOpen.value = false
})

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}

async function handleLogout() {
  await auth.logout()
  closeMenu()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(180deg, #f7faff 0%, var(--bg) 100%);
}
.sidebar {
  width: 200px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 40;
}
.sidebar-logo {
  padding: 20px 16px;
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-600);
  border-bottom: 1px solid var(--border);
}
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  transition: background 0.15s, color 0.15s;
  text-decoration: none;
}
.nav-item:hover {
  background: var(--surface-2);
  color: var(--text);
}
.nav-item.active {
  background: var(--brand-50);
  color: var(--brand-700);
}
.nav-icon { font-size: 16px; }
.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--border);
}
.main-content {
  flex: 1;
  margin-left: 200px;
  padding: 24px;
  min-height: 100vh;
}
.topbar {
  display: none;
}

.sidebar-backdrop {
  display: none;
}

@media (max-width: 900px) {
  .layout {
    display: block;
  }

  .sidebar {
    width: min(86vw, 280px);
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    border: none;
    background: rgba(15, 23, 42, 0.45);
    z-index: 30;
  }

  .main-content {
    margin-left: 0;
    padding: 14px 14px 24px;
    min-height: 100vh;
  }

  .topbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    margin: -14px -14px 16px;
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(14px);
    background: rgba(247, 250, 255, 0.88);
    border-bottom: 1px solid rgba(226, 232, 240, 0.85);
  }

  .menu-button {
    width: 42px;
    height: 42px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--surface);
    color: var(--text);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }

  .topbar-copy {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .topbar-kicker {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .topbar-title {
    font-size: 15px;
    line-height: 1.2;
  }
}

@media (min-width: 901px) {
  .sidebar {
    transform: none !important;
  }
}
</style>
