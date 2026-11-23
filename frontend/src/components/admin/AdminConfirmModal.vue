<script setup>
import { AlertTriangle, Loader2 } from 'lucide-vue-next'
import AdminModal from './AdminModal.vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmar eliminación'
  },
  message: {
    type: String,
    default: '¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.'
  },
  confirmText: {
    type: String,
    default: 'Eliminar'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <AdminModal :is-open="isOpen" :title="title" max-width="440px" @close="emit('close')">
    <div class="confirm-content">
      <div class="confirm-icon-box">
        <AlertTriangle :size="28" class="warning-icon" />
      </div>
      <p class="confirm-message">{{ message }}</p>
    </div>

    <template #footer>
      <button
        type="button"
        class="admin-btn-secondary"
        :disabled="loading"
        @click="emit('close')"
      >
        Cancelar
      </button>
      <button
        type="button"
        class="admin-btn-danger"
        :disabled="loading"
        @click="emit('confirm')"
      >
        <Loader2 v-if="loading" :size="16" class="spin-icon" />
        <span>{{ confirmText }}</span>
      </button>
    </template>
  </AdminModal>
</template>

<style scoped>
.confirm-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem 0;
  gap: 1rem;
}

.confirm-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
}

.confirm-message {
  font-size: 0.92rem;
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

.admin-btn-secondary {
  padding: 0.55rem 1.15rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  color: #5d5345;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-secondary:hover:not(:disabled) {
  background-color: var(--color-ivory, #F5F2E9);
  color: var(--color-forest, #34483D);
}

.admin-btn-danger {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1.25rem;
  background-color: #dc2626;
  border: 1px solid #b91c1c;
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
