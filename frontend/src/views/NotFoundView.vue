<template>
  <section class="state-page">
    <div class="state-card">
      <div class="state-badge">404</div>
      <span class="state-kicker">Pagina no encontrada</span>
      <h1 class="state-title">La ruta que buscabas no existe.</h1>
      <p class="state-copy">
        Puede que la pagina haya sido movida, eliminada o que la URL se haya escrito con un error.
      </p>

      <div class="state-actions">
        <button class="state-button primary" type="button" @click="goHome">
          <i class="pi pi-home"></i>
          <span>{{ auth.isAuthenticated ? 'Ir al dashboard' : 'Ir al login' }}</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function goHome() {
  router.push({ name: auth.isAuthenticated ? 'dashboard' : 'login' })
}
</script>

<style scoped>
.state-page {
  min-height: calc(100vh - 48px);
  display: grid;
  place-items: center;
  padding: 24px 0 8px;
}

.state-card {
  width: min(680px, 100%);
  position: relative;
  overflow: hidden;
  padding: 40px;
  border-radius: 28px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  background:
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.14), transparent 30%),
    radial-gradient(circle at bottom left, rgba(2, 132, 199, 0.08), transparent 26%),
    rgba(255, 255, 255, 0.88);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
  text-align: center;
}

.state-card::before,
.state-card::after {
  content: '';
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
}

.state-card::before {
  width: 180px;
  height: 180px;
  background: rgba(14, 165, 233, 0.08);
  top: -70px;
  right: -40px;
}

.state-card::after {
  width: 120px;
  height: 120px;
  background: rgba(37, 99, 235, 0.06);
  bottom: -50px;
  left: -30px;
}

.state-badge {
  width: 88px;
  height: 88px;
  margin: 0 auto 18px;
  border-radius: 24px;
  display: grid;
  place-items: center;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: var(--brand-700);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(2, 132, 199, 0.08));
  box-shadow: inset 0 0 0 1px rgba(14, 165, 233, 0.14);
}

.state-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--brand-700);
}

.state-title {
  margin-top: 14px;
  font-size: clamp(28px, 4vw, 44px);
  line-height: 1.05;
  color: var(--text);
}

.state-copy {
  max-width: 520px;
  margin: 14px auto 0;
  font-size: 15px;
  line-height: 1.65;
  color: var(--text-muted);
}

.state-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.state-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, border-color 0.15s ease;
}

.state-button:hover {
  transform: translateY(-1px);
}

.state-button.primary {
  color: white;
  background: linear-gradient(135deg, var(--brand-600), var(--brand-700));
  box-shadow: 0 14px 26px rgba(2, 132, 199, 0.2);
}

.state-button.secondary {
  color: var(--text);
  background: rgba(255, 255, 255, 0.72);
  border-color: rgba(203, 213, 225, 0.9);
}

@media (max-width: 640px) {
  .state-page {
    min-height: calc(100vh - 24px);
    padding-top: 12px;
  }

  .state-card {
    padding: 28px 20px;
    border-radius: 22px;
  }

  .state-actions {
    flex-direction: column;
  }

  .state-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
