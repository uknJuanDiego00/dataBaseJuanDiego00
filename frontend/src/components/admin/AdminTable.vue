<script setup>
import { Loader2, ChevronLeft, ChevronRight, Inbox } from 'lucide-vue-next'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  itemsCount: {
    type: Number,
    default: 0
  },
  total: {
    type: Number,
    default: 0
  },
  skip: {
    type: Number,
    default: 0
  },
  limit: {
    type: Number,
    default: 10
  },
  emptyTitle: {
    type: String,
    default: 'No se encontraron registros'
  },
  emptySubtitle: {
    type: String,
    default: 'Aún no hay elementos registrados o no coinciden con los filtros.'
  }
})

const emit = defineEmits(['prev-page', 'next-page'])
</script>

<template>
  <div class="admin-table-container">
    <div class="table-scroll-wrapper">
      <table class="admin-data-table">
        <thead>
          <slot name="header"></slot>
        </thead>
        <tbody v-if="!loading && itemsCount > 0">
          <slot name="body"></slot>
        </tbody>
      </table>
    </div>

    <!-- Indicador de Carga -->
    <div v-if="loading" class="table-state-box">
      <Loader2 :size="26" class="table-spinner" />
      <span class="state-text">Consultando información de la biblioteca...</span>
    </div>

    <!-- Estado Vacío -->
    <div v-else-if="itemsCount === 0" class="table-state-box">
      <div class="empty-icon-box">
        <Inbox :size="30" />
      </div>
      <h4 class="empty-title">{{ emptyTitle }}</h4>
      <p class="empty-desc">{{ emptySubtitle }}</p>
    </div>

    <!-- Paginación -->
    <div v-if="!loading && total > 0" class="table-pagination">
      <div class="pagination-info">
        Mostrando <span class="highlight">{{ skip + 1 }}</span> a
        <span class="highlight">{{ Math.min(skip + limit, total) }}</span> de
        <span class="highlight">{{ total }}</span> registros
      </div>

      <div class="pagination-controls">
        <button
          class="page-btn"
          :disabled="skip <= 0"
          @click="emit('prev-page')"
          title="Página anterior"
        >
          <ChevronLeft :size="16" />
          <span>Anterior</span>
        </button>

        <span class="page-number-display">
          Pág. {{ Math.floor(skip / limit) + 1 }} de {{ Math.ceil(total / limit) || 1 }}
        </span>

        <button
          class="page-btn"
          :disabled="skip + limit >= total"
          @click="emit('next-page')"
          title="Página siguiente"
        >
          <span>Siguiente</span>
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-table-container {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.03);
}

.table-scroll-wrapper {
  overflow-x: auto;
  width: 100%;
}

.admin-data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}

:deep(thead tr) {
  background-color: #FAF8F2;
  border-bottom: 1px solid var(--color-border, #E5E0D4);
}

:deep(th) {
  padding: 0.95rem 1.15rem;
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7a7062;
  white-space: nowrap;
}

:deep(tbody tr) {
  border-bottom: 1px solid #ECE7DC;
  transition: background-color 0.15s ease;
}

:deep(tbody tr:last-child) {
  border-bottom: none;
}

:deep(tbody tr:hover) {
  background-color: #F8F5EE;
}

:deep(td) {
  padding: 0.95rem 1.15rem;
  color: var(--color-forest, #34483D);
  vertical-align: middle;
}

.table-state-box {
  padding: 3.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.table-spinner {
  animation: spin 1s linear infinite;
  color: var(--color-gold, #C49A62);
  margin-bottom: 0.85rem;
}

.state-text {
  font-size: 0.88rem;
  color: #7a7062;
}

.empty-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: var(--color-ivory, #F5F2E9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8c8273;
  margin-bottom: 0.85rem;
}

.empty-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.15rem;
  color: var(--color-forest, #34483D);
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.82rem;
  color: #8c8273;
  margin: 0;
  max-width: 320px;
}

.table-pagination {
  padding: 0.85rem 1.25rem;
  border-top: 1px solid var(--color-border, #E5E0D4);
  background-color: #FAF8F2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.82rem;
  color: #7a7062;
}

.pagination-info .highlight {
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-forest, #34483D);
  cursor: pointer;
  transition: all 0.15s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: var(--color-ivory, #F5F2E9);
  border-color: var(--color-gold, #C49A62);
  color: #a4763c;
}

.page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-number-display {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
  padding: 0 0.35rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
