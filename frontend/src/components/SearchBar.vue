<script setup>
import { ref, watch } from 'vue'
import { categories } from '../data/categories'
import { 
  Search, 
  X, 
  SlidersHorizontal, 
  ChevronDown,
  RotateCcw
} from 'lucide-vue-next'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  selectedCategory: {
    type: String,
    default: ''
  },
  selectedAvailability: {
    type: String,
    default: 'all'
  },
  sortBy: {
    type: String,
    default: 'title'
  },
  totalResults: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'update:searchQuery',
  'update:selectedCategory',
  'update:selectedAvailability',
  'update:sortBy',
  'reset-filters'
])

const showFilters = ref(true)

const localSearch = ref(props.searchQuery)
const localCategory = ref(props.selectedCategory)
const localAvailability = ref(props.selectedAvailability)
const localSort = ref(props.sortBy)

watch(() => props.searchQuery, (newVal) => localSearch.value = newVal)
watch(() => props.selectedCategory, (newVal) => localCategory.value = newVal)
watch(() => props.selectedAvailability, (newVal) => localAvailability.value = newVal)
watch(() => props.sortBy, (newVal) => localSort.value = newVal)

const onSearchInput = () => {
  emit('update:searchQuery', localSearch.value)
}

const onCategoryChange = () => {
  emit('update:selectedCategory', localCategory.value)
}

const onAvailabilityChange = () => {
  emit('update:selectedAvailability', localAvailability.value)
}

const onSortChange = () => {
  emit('update:sortBy', localSort.value)
}

const clearSearch = () => {
  localSearch.value = ''
  emit('update:searchQuery', '')
}

const resetAll = () => {
  localSearch.value = ''
  localCategory.value = ''
  localAvailability.value = 'all'
  localSort.value = 'title'
  emit('reset-filters')
}

const hasActiveFilters = () => {
  return localSearch.value.trim() !== '' || 
         localCategory.value !== '' || 
         localAvailability.value !== 'all' || 
         localSort.value !== 'title'
}
</script>

<template>
  <div class="search-bar-container">
    <!-- Fila Principal Simétrica -->
    <div class="search-main-row">
      <div class="search-input-wrapper">
        <Search class="search-icon" :size="18" />
        <input 
          v-model="localSearch"
          type="text"
          placeholder="Buscar por título, autor, palabras clave o tema..."
          class="main-search-input"
          @input="onSearchInput"
          aria-label="Buscar libros en el catálogo"
        />
        <button 
          v-if="localSearch" 
          class="clear-btn" 
          @click="clearSearch"
          title="Borrar texto"
          aria-label="Borrar texto de búsqueda"
        >
          <X :size="15" />
        </button>
      </div>

      <button 
        class="toggle-filters-btn" 
        :class="{ active: showFilters }"
        @click="showFilters = !showFilters"
        :aria-expanded="showFilters"
      >
        <SlidersHorizontal :size="16" />
        <span>Filtros</span>
      </button>
    </div>

    <!-- Panel de Filtros Equilibrado -->
    <transition name="filters-slide">
      <div v-if="showFilters" class="filters-panel">
        <div class="filters-grid">
          <!-- Categoría -->
          <div class="filter-group">
            <label class="filter-label">Categoría temática</label>
            <div class="select-wrapper">
              <select v-model="localCategory" class="filter-select" @change="onCategoryChange">
                <option value="">Todas las ramas</option>
                <option 
                  v-for="cat in categories" 
                  :key="cat.id" 
                  :value="cat.id"
                >
                  {{ cat.name }} ({{ cat.count }})
                </option>
              </select>
              <ChevronDown :size="14" class="select-chevron" />
            </div>
          </div>

          <!-- Disponibilidad -->
          <div class="filter-group">
            <label class="filter-label">Estado de ejemplares</label>
            <div class="select-wrapper">
              <select v-model="localAvailability" class="filter-select" @change="onAvailabilityChange">
                <option value="all">Todos los estados</option>
                <option value="available">Disponibles ahora</option>
                <option value="borrowed">En préstamo</option>
              </select>
              <ChevronDown :size="14" class="select-chevron" />
            </div>
          </div>

          <!-- Ordenación -->
          <div class="filter-group">
            <label class="filter-label">Criterio de orden</label>
            <div class="select-wrapper">
              <select v-model="localSort" class="filter-select" @change="onSortChange">
                <option value="title">Título (A — Z)</option>
                <option value="author">Autor</option>
                <option value="year-desc">Año (Más reciente)</option>
                <option value="year-asc">Año (Clásicos)</option>
              </select>
              <ChevronDown :size="14" class="select-chevron" />
            </div>
          </div>
        </div>

        <!-- Barra de Estado Inferior -->
        <div class="filters-status-bar">
          <span class="results-badge">
            Mostrando <strong>{{ totalResults }}</strong> {{ totalResults === 1 ? 'obra' : 'obras' }}
          </span>

          <button 
            v-if="hasActiveFilters()" 
            class="reset-filters-btn" 
            @click="resetAll"
          >
            <RotateCcw :size="12" />
            <span>Restablecer criterios</span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.search-bar-container {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 1.35rem 1.6rem;
  box-shadow: var(--shadow-subtle);
  margin-bottom: 2.5rem;
}

/* Fila Principal */
.search-main-row {
  display: flex;
  gap: 0.85rem;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 1.15rem;
  color: var(--color-text-light);
  pointer-events: none;
}

.main-search-input {
  width: 100%;
  height: 48px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding-left: 2.9rem;
  padding-right: 2.75rem;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  color: var(--color-text-main);
  outline: none;
  transition: var(--transition-fast);
}

.main-search-input:focus {
  border-color: var(--color-accent);
  background-color: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(196, 154, 98, 0.14);
}

.clear-btn {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: var(--color-text-light);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.clear-btn:hover {
  color: var(--color-primary);
  background-color: rgba(52, 72, 61, 0.06);
}

.toggle-filters-btn {
  height: 48px;
  padding: 0 1.35rem;
  border-radius: var(--radius-full);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  color: var(--color-primary);
  font-size: 0.88rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  cursor: pointer;
  transition: var(--transition-fast);
  white-space: nowrap;
}

.toggle-filters-btn:hover,
.toggle-filters-btn.active {
  background-color: var(--color-primary);
  color: var(--bg-primary);
  border-color: var(--color-primary);
}

/* Panel de Filtros */
.filters-panel {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select {
  width: 100%;
  height: 40px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0 2rem 0 0.85rem;
  font-family: var(--font-sans);
  font-size: 0.86rem;
  color: var(--color-text-main);
  outline: none;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  transition: var(--transition-fast);
}

.filter-select:focus {
  border-color: var(--color-accent);
  background-color: #FFFFFF;
}

.select-chevron {
  position: absolute;
  right: 0.75rem;
  color: var(--color-text-light);
  pointer-events: none;
}

/* Barra de Estado */
.filters-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.results-badge strong {
  color: var(--color-primary);
}

.reset-filters-btn {
  background: none;
  border: none;
  color: var(--color-accent);
  font-size: 0.78rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: var(--transition-fast);
}

.reset-filters-btn:hover {
  background-color: var(--color-accent-subtle);
  color: var(--color-accent-hover);
}

@media (max-width: 840px) {
  .search-main-row {
    flex-direction: column;
  }

  .toggle-filters-btn {
    width: 100%;
    justify-content: center;
  }

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .filters-status-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.6rem;
  }
}
</style>
