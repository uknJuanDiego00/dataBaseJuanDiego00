<script setup>
import { X } from 'lucide-vue-next'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  maxWidth: {
    type: String,
    default: '540px'
  }
})

const emit = defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-card" :style="{ maxWidth: maxWidth }">
          <!-- Encabezado Modal -->
          <div class="modal-header">
            <div>
              <h3 class="modal-title">{{ title }}</h3>
              <p v-if="subtitle" class="modal-subtitle">{{ subtitle }}</p>
            </div>
            <button class="modal-close-btn" @click="emit('close')" aria-label="Cerrar ventana">
              <X :size="18" />
            </button>
          </div>

          <!-- Contenido Modal -->
          <div class="modal-body">
            <slot></slot>
          </div>

          <!-- Pie Modal (Opcional) -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(30, 44, 36, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  z-index: 2000;
}

.modal-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 14px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #E5E0D4);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.78rem;
  color: #7a7062;
  margin: 0.2rem 0 0 0;
}

.modal-close-btn {
  background: none;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  padding: 6px;
  color: #7a7062;
  cursor: pointer;
  display: flex;
  transition: all 0.15s ease;
}

.modal-close-btn:hover {
  background-color: var(--color-ivory, #F5F2E9);
  color: var(--color-forest, #34483D);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border, #E5E0D4);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  background-color: #FAF8F2;
}

/* Transiciones */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.22s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-card {
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-fade-enter-from .modal-card {
  transform: scale(0.96) translateY(8px);
}
</style>
