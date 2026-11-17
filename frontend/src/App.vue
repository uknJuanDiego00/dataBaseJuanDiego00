<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import { CheckCircle2, Bookmark } from 'lucide-vue-next'

const toast = ref({
  visible: false,
  message: '',
  type: 'info'
})

let toastTimeout = null

const showToast = (message, type = 'info') => {
  if (toastTimeout) clearTimeout(toastTimeout)
  toast.value = {
    visible: true,
    message,
    type
  }
  toastTimeout = setTimeout(() => {
    toast.value.visible = false
  }, 2600)
}

const onFavoritesUpdated = (e) => {
  const detail = e.detail
  if (detail && detail.action) {
    if (detail.action === 'added') {
      showToast(`«${detail.title}» se ha guardado en tus libros`, 'success')
    } else if (detail.action === 'removed') {
      showToast(`«${detail.title}» se ha retirado de tus libros`, 'info')
    }
  }
}

onMounted(() => {
  window.addEventListener('favorites-updated', onFavoritesUpdated)
})

onUnmounted(() => {
  window.removeEventListener('favorites-updated', onFavoritesUpdated)
})
</script>

<template>
  <div class="app-layout">
    <!-- Cabecera Sticky -->
    <Header />

    <!-- Contenido Principal con Transición Suave -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Pie de Página -->
    <Footer />

    <!-- Notificación Toast Serena -->
    <transition name="toast-slide">
      <div v-if="toast.visible" class="serene-toast" :class="toast.type">
        <CheckCircle2 v-if="toast.type === 'success'" :size="17" class="toast-icon" />
        <Bookmark v-else :size="17" class="toast-icon" />
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

/* Toast Sereno */
.serene-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: var(--color-primary);
  color: var(--bg-primary);
  border: 1px solid var(--border-accent);
  padding: 0.85rem 1.45rem;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  gap: 0.65rem;
  box-shadow: 0 10px 28px rgba(30, 45, 37, 0.22);
  z-index: 300;
  font-size: 0.88rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
}

.toast-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}

.toast-text {
  letter-spacing: 0.01em;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

@media (max-width: 640px) {
  .serene-toast {
    left: 1rem;
    right: 1rem;
    bottom: 1rem;
    justify-content: center;
  }
}
</style>
