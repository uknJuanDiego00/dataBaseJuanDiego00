<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { books } from '../data/books'
import BookCard from '../components/BookCard.vue'
import SearchBar from '../components/SearchBar.vue'
import { BookOpen, RotateCcw } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const selectedCategory = ref('')
const selectedAvailability = ref('all')
const sortBy = ref('title')
const favorites = ref([])

const loadFavorites = () => {
  try {
    favorites.value = JSON.parse(localStorage.getItem('biblioteca_favoritos') || '[]')
  } catch {
    favorites.value = []
  }
}

const isFavorite = (id) => {
  return favorites.value.some(b => b.id === id)
}

const toggleFavorite = (book) => {
  const index = favorites.value.findIndex(b => b.id === book.id)
  let action = 'added'
  if (index > -1) {
    favorites.value.splice(index, 1)
    action = 'removed'
  } else {
    favorites.value.push(book)
  }
  localStorage.setItem('biblioteca_favoritos', JSON.stringify(favorites.value))
  window.dispatchEvent(new CustomEvent('favorites-updated', {
    detail: { action, title: book.title }
  }))
}

const initFromQuery = () => {
  if (route.query.categoria) {
    selectedCategory.value = String(route.query.categoria)
  }
  if (route.query.q) {
    searchQuery.value = String(route.query.q)
  }
}

watch(() => route.query, () => {
  initFromQuery()
})

const filteredBooks = computed(() => {
  return books.filter(book => {
    const query = searchQuery.value.toLowerCase().trim()
    const matchesSearch = !query || 
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query) ||
      book.description.toLowerCase().includes(query)

    const matchesCategory = !selectedCategory.value || 
      book.categorySlug === selectedCategory.value

    let matchesAvailability = true
    if (selectedAvailability.value === 'available') {
      matchesAvailability = book.available === true
    } else if (selectedAvailability.value === 'borrowed') {
      matchesAvailability = book.available === false
    }

    return matchesSearch && matchesCategory && matchesAvailability
  }).sort((a, b) => {
    if (sortBy.value === 'title') {
      return a.title.localeCompare(b.title)
    }
    if (sortBy.value === 'author') {
      return a.author.localeCompare(b.author)
    }
    if (sortBy.value === 'year-desc') {
      return b.year - a.year
    }
    if (sortBy.value === 'year-asc') {
      return a.year - b.year
    }
    return 0
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedAvailability.value = 'all'
  sortBy.value = 'title'
  router.replace({ query: {} })
}

onMounted(() => {
  initFromQuery()
  loadFavorites()
})
</script>

<template>
  <div class="catalog-page">
    <div class="catalog-header-banner">
      <div class="container banner-container">
        <span class="section-eyebrow">Catálogo General</span>
        <h1 class="page-title">Un Archivo para la Mente Serena</h1>
        <p class="page-description">
          Explora nuestra colección íntegra de obras pensadas para enriquecer el alma. Filtra por temática, autor o disponibilidad según tu momento de lectura.
        </p>
      </div>
    </div>

    <div class="container catalog-body">
      <!-- Barra y panel de filtros simétricos -->
      <SearchBar 
        v-model:searchQuery="searchQuery"
        v-model:selectedCategory="selectedCategory"
        v-model:selectedAvailability="selectedAvailability"
        v-model:sortBy="sortBy"
        :totalResults="filteredBooks.length"
        @reset-filters="resetFilters"
      />

      <!-- Cuadrícula con alturas perfectamente alineadas -->
      <div v-if="filteredBooks.length > 0" class="books-grid">
        <BookCard 
          v-for="book in filteredBooks"
          :key="book.id"
          :book="book"
          :is-favorite="isFavorite(book.id)"
          @toggle-favorite="toggleFavorite"
        />
      </div>

      <!-- Estado Vacío Sereno y Centrado -->
      <div v-else class="empty-state">
        <div class="empty-icon-wrapper">
          <BookOpen :size="32" />
        </div>
        <h3 class="empty-title">Ninguna obra coincide con los criterios</h3>
        <p class="empty-subtitle">
          Intenta ajustar los filtros seleccionados o buscar con términos más amplios. La serenidad también está en explorar otros senderos.
        </p>
        <button class="btn btn-primary empty-btn" @click="resetFilters">
          <RotateCcw :size="15" />
          <span>Restablecer filtros</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-page {
  padding-bottom: 5.5rem;
}

.catalog-header-banner {
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
  padding: 4rem 0 3.25rem 0;
  margin-bottom: 2.75rem;
  text-align: center;
}

.banner-container {
  max-width: 680px;
}

.page-title {
  font-size: clamp(2.2rem, 3.8vw, 3rem);
  color: var(--color-primary);
  margin-bottom: 0.85rem;
}

.page-description {
  font-size: 1.05rem;
  color: var(--color-text-muted);
  line-height: 1.65;
}

/* Cuadrícula simétrica */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
  align-items: stretch;
}

/* Estado Vacío Equilibrado */
.empty-state {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 4rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 540px;
  margin: 2.5rem auto;
  box-shadow: var(--shadow-subtle);
}

.empty-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: var(--color-accent-subtle);
  color: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.35rem;
}

.empty-title {
  font-size: 1.4rem;
  color: var(--color-primary);
  margin-bottom: 0.65rem;
}

.empty-subtitle {
  font-size: 0.94rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 1.75rem;
}

.empty-btn {
  padding: 0.75rem 1.6rem;
}

@media (max-width: 640px) {
  .books-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
