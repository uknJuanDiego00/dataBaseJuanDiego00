<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  BookOpen, 
  Search, 
  Menu, 
  X, 
  User
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const isScrolled = ref(false)
const mobileMenuOpen = ref(false)
const quickSearchQuery = ref('')
const favoritesCount = ref(0)

const updateFavoritesCount = () => {
  try {
    const favs = JSON.parse(localStorage.getItem('biblioteca_favoritos') || '[]')
    favoritesCount.value = favs.length
  } catch {
    favoritesCount.value = 0
  }
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 15
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleQuickSearch = () => {
  if (quickSearchQuery.value.trim()) {
    router.push({
      path: '/catalogo',
      query: { q: quickSearchQuery.value.trim() }
    })
    quickSearchQuery.value = ''
    closeMobileMenu()
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('favorites-updated', updateFavoritesCount)
  window.addEventListener('storage', updateFavoritesCount)
  updateFavoritesCount()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('favorites-updated', updateFavoritesCount)
  window.removeEventListener('storage', updateFavoritesCount)
})
</script>

<template>
  <header class="site-header" :class="{ 'is-scrolled': isScrolled }">
    <div class="container header-container">
      <!-- Logotipo & Nombre -->
      <router-link to="/" class="logo" @click="closeMobileMenu" aria-label="Ir a Inicio de Biblioteca">
        <div class="logo-icon">
          <BookOpen :size="20" stroke-width="1.8" />
        </div>
        <div class="logo-text">
          <span class="logo-title">BIBLIOTECA</span>
          <span class="logo-tagline">Refugio de Serenidad</span>
        </div>
      </router-link>

      <!-- Navegación de Escritorio -->
      <nav class="desktop-nav" aria-label="Navegación principal">
        <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">
          Inicio
        </router-link>
        <router-link to="/catalogo" class="nav-link" :class="{ active: route.path.startsWith('/catalogo') }">
          Catálogo
        </router-link>
        <router-link to="/categorias" class="nav-link" :class="{ active: route.path === '/categorias' }">
          Categorías
        </router-link>
        <router-link to="/mis-libros" class="nav-link" :class="{ active: route.path === '/mis-libros' }">
          <span>Mis libros</span>
          <span v-if="favoritesCount > 0" class="nav-counter">{{ favoritesCount }}</span>
        </router-link>
        <router-link to="/nosotros" class="nav-link" :class="{ active: route.path === '/nosotros' }">
          Nosotros
        </router-link>
      </nav>

      <!-- Acciones de cabecera -->
      <div class="header-actions">
        <!-- Buscador integrado -->
        <form class="quick-search-form" @submit.prevent="handleQuickSearch" role="search">
          <Search class="search-icon" :size="16" />
          <input 
            v-model="quickSearchQuery"
            type="text" 
            placeholder="Buscar libro o autor..." 
            class="quick-search-input"
            aria-label="Buscar libros o autores"
          />
        </form>

        <!-- Perfil del usuario / Lector -->
        <div class="user-pill" title="Lector en modo sereno">
          <div class="user-avatar">
            <User :size="14" />
          </div>
          <span class="user-name">Lector</span>
        </div>

        <!-- Botón Menú Móvil -->
        <button 
          class="mobile-toggle" 
          @click="toggleMobileMenu" 
          aria-label="Abrir menú de navegación"
          :aria-expanded="mobileMenuOpen"
        >
          <Menu v-if="!mobileMenuOpen" :size="22" />
          <X v-else :size="22" />
        </button>
      </div>
    </div>

    <!-- Menú Móvil Desplegable -->
    <transition name="drawer">
      <div v-if="mobileMenuOpen" class="mobile-drawer">
        <form class="mobile-search-form" @submit.prevent="handleQuickSearch">
          <Search class="search-icon" :size="17" />
          <input 
            v-model="quickSearchQuery"
            type="text" 
            placeholder="Buscar libro, autor o tema..." 
            class="mobile-search-input"
          />
        </form>

        <nav class="mobile-nav">
          <router-link to="/" class="mobile-link" @click="closeMobileMenu">
            Inicio
          </router-link>
          <router-link to="/catalogo" class="mobile-link" @click="closeMobileMenu">
            Catálogo
          </router-link>
          <router-link to="/categorias" class="mobile-link" @click="closeMobileMenu">
            Categorías
          </router-link>
          <router-link to="/mis-libros" class="mobile-link" @click="closeMobileMenu">
            <span>Mis libros guardados</span>
            <span v-if="favoritesCount > 0" class="badge badge-gold">{{ favoritesCount }}</span>
          </router-link>
          <router-link to="/nosotros" class="mobile-link" @click="closeMobileMenu">
            Nosotros & Filosofía
          </router-link>
        </nav>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: rgba(245, 242, 233, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-subtle);
  transition: var(--transition-fast);
}

.site-header.is-scrolled {
  background-color: rgba(245, 242, 233, 0.98);
  box-shadow: 0 4px 18px rgba(52, 72, 61, 0.04);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 74px;
  gap: 1.5rem;
}

/* Logotipo */
.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-smooth);
}

.logo:hover .logo-icon {
  background-color: var(--color-accent);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-family: var(--font-serif);
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--color-primary);
  line-height: 1.1;
}

.logo-tagline {
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  color: var(--color-accent);
  text-transform: uppercase;
  font-weight: 500;
}

/* Navegación Desktop */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 1.75rem;
}

.nav-link {
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--color-text-main);
  padding: 0.4rem 0.1rem;
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: var(--transition-fast);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-accent);
  transition: var(--transition-smooth);
  border-radius: var(--radius-full);
}

.nav-link:hover {
  color: var(--color-primary);
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.nav-link.active {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-counter {
  font-size: 0.7rem;
  font-weight: 600;
  background-color: var(--color-accent);
  color: #FFFFFF;
  border-radius: var(--radius-full);
  padding: 0.1rem 0.45rem;
  line-height: 1.2;
}

/* Acciones de la cabecera */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.quick-search-form {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.95rem;
  color: var(--color-text-light);
  pointer-events: none;
}

.quick-search-input {
  width: 210px;
  height: 38px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding-left: 2.35rem;
  padding-right: 0.85rem;
  font-family: var(--font-sans);
  font-size: 0.86rem;
  color: var(--color-text-main);
  outline: none;
  transition: var(--transition-smooth);
}

.quick-search-input:focus {
  width: 260px;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(196, 154, 98, 0.14);
}

/* Pastilla de usuario */
.user-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.7rem 0.28rem 0.28rem;
  background-color: rgba(52, 72, 61, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-primary);
}

/* Botón de menú móvil */
.mobile-toggle {
  display: none;
  background: none;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--color-primary);
  cursor: pointer;
  padding: 0.45rem;
  display: none;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  min-height: 40px;
}

/* Drawer móvil */
.mobile-drawer {
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  padding: 1.5rem 1.25rem 2rem 1.25rem;
  box-shadow: 0 10px 25px rgba(52, 72, 61, 0.08);
}

.mobile-search-form {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1.25rem;
}

.mobile-search-input {
  width: 100%;
  height: 44px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding-left: 2.6rem;
  padding-right: 1rem;
  font-size: 0.94rem;
  color: var(--color-text-main);
  outline: none;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
}

.mobile-link {
  font-family: var(--font-serif);
  font-size: 1.25rem;
  color: var(--color-primary);
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(52, 72, 61, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Animación Drawer */
.drawer-enter-active,
.drawer-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  transform: translateY(-8px);
  opacity: 0;
}

@media (max-width: 992px) {
  .desktop-nav,
  .quick-search-form,
  .user-pill {
    display: none;
  }

  .mobile-toggle {
    display: flex;
  }
}
</style>
