<template>
  <div class="layout">
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">
          <i class="pi pi-shield"></i>
        </div>
        <div class="sidebar-logo-copy">
          <span class="sidebar-logo-title">SGP</span>
          <span class="sidebar-logo-subtitle">Gestion operativa</span>
        </div>
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
        <button class="nav-item nav-item-logout" @click="handleLogout">
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
        <div class="topbar-badge">
          <i class="pi pi-compass"></i>
          <span>Operativo</span>
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
  try {
    await auth.logout()
  } catch {
    // logout del backend falló, pero limpiamos el estado local de todas formas
  } finally {
    closeMenu()
    router.push({ name: 'login' })
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.08), transparent 28%),
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.05), transparent 24%),
    linear-gradient(180deg, #f7faff 0%, var(--bg) 100%);
}
.sidebar {
  width: 220px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(241, 247, 252, 0.98) 100%);
  border-right: 1px solid rgba(226, 232, 240, 0.85);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 40;
  box-shadow: 10px 0 30px rgba(15, 23, 42, 0.04);
}
.sidebar-logo {
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}
.sidebar-logo-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--brand-500), var(--brand-700));
  color: white;
  font-size: 18px;
  box-shadow: 0 10px 24px rgba(2, 132, 199, 0.22);
  flex-shrink: 0;
}
.sidebar-logo-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.sidebar-logo-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: var(--text);
}
.sidebar-logo-subtitle {
  font-size: 12px;
  color: var(--text-muted);
}
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: 12px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  transition: background 0.15s, color 0.15s, transform 0.15s, box-shadow 0.15s;
  text-decoration: none;
}
.nav-item:hover {
  background: rgba(224, 242, 254, 0.8);
  color: var(--text);
  transform: translateX(1px);
}
.nav-item.active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(2, 132, 199, 0.08));
  color: var(--brand-700);
  box-shadow: inset 0 0 0 1px rgba(14, 165, 233, 0.16);
}
.nav-icon { font-size: 16px; }
.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--border);
}
.nav-item-logout {
  background: rgba(239, 68, 68, 0.05);
  color: #b91c1c;
}
.nav-item-logout:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #991b1b;
}
.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 24px;
  min-height: 100vh;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  margin-bottom: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.06);
}

.menu-button {
  display: none;
}
.topbar-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}
.topbar-kicker {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.topbar-title {
  font-size: 16px;
  line-height: 1.2;
  color: var(--text);
}
.topbar-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.1);
  color: var(--brand-700);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
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
    padding: 12px 14px;
    margin: -14px -14px 16px;
    position: sticky;
    top: 0;
    z-index: 10;
    border-radius: 0;
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

  .topbar-badge {
    display: none;
  }
}

@media (min-width: 901px) {
  .sidebar {
    transform: none !important;
  }
}
</style>
