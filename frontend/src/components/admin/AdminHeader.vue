<script setup>
import { Menu, ShieldCheck, Activity } from 'lucide-vue-next'
import { useAuth } from '../../composables/useAuth'

defineProps({
  title: {
    type: String,
    default: 'Panel de Administración'
  },
  subtitle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['toggle-sidebar'])
const { user } = useAuth()
</script>

<template>
  <header class="admin-header">
    <div class="header-left">
      <button class="menu-toggle-btn md-hidden" @click="emit('toggle-sidebar')" aria-label="Abrir menú">
        <Menu :size="22" />
      </button>
      <div class="header-title-box">
        <h1 class="header-title">{{ title }}</h1>
        <p v-if="subtitle" class="header-subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="header-right">
      <div class="system-status-indicator" title="Servicio backend activo">
        <span class="status-dot"></span>
        <span class="status-label">Sistema Conectado</span>
      </div>

      <div class="admin-profile-pill">
        <ShieldCheck :size="16" class="pill-icon" />
        <span class="pill-name">{{ user?.nombre || 'Administrador' }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.admin-header {
  height: 70px;
  background-color: var(--color-surface, #FFFEFA);
  border-bottom: 1px solid var(--color-border, #E5E0D4);
  padding: 0 1.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(52, 72, 61, 0.03);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle-btn {
  background: none;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  padding: 6px;
  color: var(--color-forest, #34483D);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title-box {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.78rem;
  color: #7a7062;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.system-status-indicator {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.75rem;
  color: #4b5563;
  padding: 0.35rem 0.65rem;
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 20px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #16a34a;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.admin-profile-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.4rem 0.85rem;
  background-color: var(--color-ivory, #F5F2E9);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.pill-icon {
  color: var(--color-gold, #C49A62);
}

@media (max-width: 768px) {
  .admin-header {
    padding: 0 1rem;
    height: 62px;
  }
  .header-title {
    font-size: 1.15rem;
  }
  .header-subtitle,
  .system-status-indicator {
    display: none;
  }
}

@media (min-width: 901px) {
  .md-hidden {
    display: none !important;
  }
}
</style>
