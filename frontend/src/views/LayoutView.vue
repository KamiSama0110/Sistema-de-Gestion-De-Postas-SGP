<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span>SGP</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/" class="nav-item" :class="{ active: route.name === 'dashboard' }">
          <i class="pi pi-home nav-icon"></i>
          <span class="nav-label">Dashboard</span>
        </RouterLink>
        <RouterLink to="/asp" class="nav-item" :class="{ active: route.name === 'asp' }">
          <i class="pi pi-users nav-icon"></i>
          <span class="nav-label">ASP</span>
        </RouterLink>
        <RouterLink to="/cargos" class="nav-item" :class="{ active: route.name === 'cargos' }">
          <i class="pi pi-id-card nav-icon"></i>
          <span class="nav-label">Cargos</span>
        </RouterLink>
        <RouterLink to="/postas" class="nav-item" :class="{ active: route.name === 'postas' }">
          <i class="pi pi-map-marker nav-icon"></i>
          <span class="nav-label">Postas</span>
        </RouterLink>
        <RouterLink to="/guardias" class="nav-item" :class="{ active: route.name === 'guardias' }">
          <i class="pi pi-shield nav-icon"></i>
          <span class="nav-label">Guardias</span>
        </RouterLink>
        <RouterLink to="/reportes" class="nav-item" :class="{ active: route.name === 'reportes' }">
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

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
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
</style>