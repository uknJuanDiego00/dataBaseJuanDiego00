<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import {
  LayoutDashboard,
  BookOpen,
  Feather,
  Tags,
  Clock,
  Users,
  ShieldCheck,
  BarChart3,
  FileCode,
  ArrowLeft,
  LogOut,
  Sparkles,
  X
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const route = useRoute()
const router = useRouter()
const { user, isAdmin, isBibliotecario, logout } = useAuth()

const navItems = computed(() => {
  const items = [
    { name: 'Dashboard', path: '/admin', icon: LayoutDashboard },
    { name: 'Libros', path: '/admin/libros', icon: BookOpen },
    { name: 'Autores', path: '/admin/autores', icon: Feather },
    { name: 'Categorías', path: '/admin/categorias', icon: Tags },
    { name: 'Préstamos', path: '/admin/prestamos', icon: Clock },
    { name: 'Socios', path: '/admin/socios', icon: Users },
    { name: 'Reportes', path: '/admin/reportes', icon: BarChart3 }
  ]

  if (isAdmin.value) {
    items.push({ name: 'Usuarios', path: '/admin/usuarios', icon: ShieldCheck })
  }

  items.push({ name: 'Arquitectura Pág.', path: '/admin/paginas', icon: FileCode })

  return items
})

const handleLogout = async () => {
  await logout()
  router.push('/admin/login')
}
</script>

<template>
  <div>
    <!-- Backdrop móvil -->
    <div
      v-if="isOpen"
      class="admin-sidebar-backdrop md-hidden"
      @click="emit('close')"
    ></div>

    <aside class="admin-sidebar" :class="{ 'is-open': isOpen }">
      <!-- Header del Sidebar -->
      <div class="sidebar-header">
        <router-link to="/admin" class="sidebar-brand">
          <div class="brand-emblem">
            <Sparkles :size="16" class="emblem-star" />
          </div>
          <div class="brand-info">
            <span class="brand-title">SERENIDAD</span>
            <span class="brand-sub">Panel de Gestión</span>
          </div>
        </router-link>
        <button class="sidebar-close-btn md-hidden" @click="emit('close')" aria-label="Cerrar menú">
          <X :size="20" />
        </button>
      </div>

      <!-- Navegación -->
      <nav class="sidebar-nav">
        <span class="nav-section-title">ADMINISTRACIÓN</span>
        <ul class="nav-list">
          <li v-for="item in navItems" :key="item.path" class="nav-item">
            <router-link
              :to="item.path"
              class="nav-link"
              :class="{ 'is-active': route.path === item.path }"
              @click="emit('close')"
            >
              <component :is="item.icon" :size="18" class="nav-icon" />
              <span class="nav-label">{{ item.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- Pie del Sidebar -->
      <div class="sidebar-footer">
        <router-link to="/" class="public-site-link" title="Ir a la biblioteca pública">
          <ArrowLeft :size="16" />
          <span>Ver Biblioteca Pública</span>
        </router-link>

        <div class="sidebar-user-card">
          <div class="user-avatar">
            {{ user?.nombre ? user.nombre.charAt(0).toUpperCase() : 'A' }}
          </div>
          <div class="user-details">
            <div class="user-name" :title="user?.nombre">{{ user?.nombre || 'Administrador' }}</div>
            <div class="user-badge" :class="user?.rol">{{ user?.rol || 'admin' }}</div>
          </div>
          <button class="logout-btn" @click="handleLogout" title="Cerrar sesión">
            <LogOut :size="16" />
          </button>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.admin-sidebar-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(52, 72, 61, 0.4);
  backdrop-filter: blur(2px);
  z-index: 990;
}

.admin-sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  width: 260px;
  background-color: var(--color-surface, #FFFEFA);
  border-right: 1px solid var(--color-border, #E5E0D4);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transition: transform var(--transition-normal, 0.25s ease);
}

@media (max-width: 900px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  .admin-sidebar.is-open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
  }
}

.sidebar-header {
  padding: 1.5rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border, #E5E0D4);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.brand-emblem {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--color-forest, #34483D) 0%, #1e2c24 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gold, #C49A62);
  box-shadow: 0 2px 6px rgba(52, 72, 61, 0.15);
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  letter-spacing: 0.08em;
  line-height: 1.1;
}

.brand-sub {
  font-size: 0.7rem;
  color: var(--color-gold, #C49A62);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 600;
}

.sidebar-close-btn {
  background: transparent;
  border: none;
  color: var(--color-forest, #34483D);
  cursor: pointer;
  padding: 4px;
  display: flex;
}

.sidebar-nav {
  flex: 1;
  padding: 1.25rem 0.85rem;
  overflow-y: auto;
}

.nav-section-title {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #8c8273;
  margin-bottom: 0.65rem;
  padding-left: 0.75rem;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.7rem 0.85rem;
  border-radius: 8px;
  color: var(--color-forest, #34483D);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--transition-fast, 0.15s ease);
}

.nav-icon {
  color: #7a7062;
  transition: color 0.15s ease;
}

.nav-link:hover {
  background-color: var(--color-ivory, #F5F2E9);
  color: var(--color-forest, #34483D);
}

.nav-link:hover .nav-icon {
  color: var(--color-gold, #C49A62);
}

.nav-link.is-active {
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  font-weight: 600;
}

.nav-link.is-active .nav-icon {
  color: var(--color-gold, #C49A62);
}

.sidebar-footer {
  padding: 1rem 0.85rem;
  border-top: 1px solid var(--color-border, #E5E0D4);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background-color: #FAF8F2;
}

.public-site-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  background-color: transparent;
  border: 1px dashed var(--color-border, #E5E0D4);
  color: var(--color-forest, #34483D);
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.public-site-link:hover {
  background-color: var(--color-surface, #FFFEFA);
  border-color: var(--color-gold, #C49A62);
  color: var(--color-gold, #C49A62);
}

.sidebar-user-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.65rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--color-gold, #C49A62);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-badge {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: #7a7062;
}

.user-badge.admin {
  color: #b45309;
}

.user-badge.bibliotecario {
  color: #1e3a8a;
}

.logout-btn {
  background: transparent;
  border: none;
  color: #a89f91;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.logout-btn:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

@media (min-width: 901px) {
  .md-hidden {
    display: none !important;
  }
}
</style>
