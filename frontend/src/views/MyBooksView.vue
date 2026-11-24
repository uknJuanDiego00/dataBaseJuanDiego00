<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BookCard from '../components/BookCard.vue'
import { Bookmark, Trash2, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const favoriteBooks = ref([])

const loadFavorites = () => {
  try {
    favoriteBooks.value = JSON.parse(localStorage.getItem('biblioteca_favoritos') || '[]')
  } catch {
    favoriteBooks.value = []
  }
}

const toggleFavorite = (book) => {
  const index = favoriteBooks.value.findIndex(b => b.id === book.id)
  let action = 'removed'
  if (index > -1) {
    favoriteBooks.value.splice(index, 1)
  } else {
    favoriteBooks.value.push(book)
    action = 'added'
  }
  localStorage.setItem('biblioteca_favoritos', JSON.stringify(favoriteBooks.value))
  window.dispatchEvent(new CustomEvent('favorites-updated', {
    detail: { action, title: book.title }
  }))
}

const clearAllFavorites = () => {
  if (confirm('¿Deseas vaciar tu lista de libros guardados?')) {
    favoriteBooks.value = []
    localStorage.removeItem('biblioteca_favoritos')
    window.dispatchEvent(new CustomEvent('favorites-updated'))
  }
}

const goToCatalog = () => {
  router.push('/catalogo')
}

onMounted(() => {
  loadFavorites()
})
</script>

<template>
  <div class="my-books-page">
    <!-- Banner de Cabecera Simétrico -->
    <div class="my-books-banner">
      <div class="container banner-inner">
        <span class="section-eyebrow">Mi Rincón Personal</span>
        <h1 class="page-title">Libros Guardados para el Alma</h1>
        <p class="page-description">
          Tu selección íntima de obras para leer a tu ritmo, pausar el ruido cotidiano y volver a tus pasajes favoritos siempre que lo necesites.
        </p>
      </div>
    </div>

    <div class="container my-books-body">
      <!-- Barra superior de gestión simétrica -->
      <div v-if="favoriteBooks.length > 0" class="actions-header">
        <div class="saved-counter">
          <Bookmark :size="16" class="counter-icon" />
          <span>Tienes <strong>{{ favoriteBooks.length }}</strong> {{ favoriteBooks.length === 1 ? 'obra guardada' : 'obras guardadas' }}</span>
        </div>

        <button class="clear-all-btn" @click="clearAllFavorites">
          <Trash2 :size="14" />
          <span>Vaciar lista</span>
        </button>
      </div>

      <!-- Cuadrícula con alturas consistentes -->
      <div v-if="favoriteBooks.length > 0" class="books-grid">
        <BookCard 
          v-for="book in favoriteBooks"
          :key="book.id"
          :book="book"
          :is-favorite="true"
          @toggle-favorite="toggleFavorite"
        />
      </div>

      <!-- Estado Vacío Sereno y Equilibrado -->
      <div v-else class="empty-state-box">
        <div class="empty-icon-circle">
          <Bookmark :size="32" />
        </div>
        <h3 class="empty-title">Aún no has guardado ninguna obra</h3>
        <p class="empty-text">
          Explora nuestro catálogo sereno y presiona el icono de corazón en cualquier libro para conservarlo en tu colección personal.
        </p>
        <button class="btn btn-primary" @click="goToCatalog">
          <span>Explorar catálogo</span>
          <ArrowRight :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-books-page {
  padding-bottom: 5.5rem;
}

.my-books-banner {
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
  padding: 4rem 0 3.25rem 0;
  text-align: center;
  margin-bottom: 2.75rem;
}

.banner-inner {
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

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-subtle);
}

.saved-counter {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.92rem;
  color: var(--color-primary);
}

.counter-icon {
  color: var(--color-accent);
}

.clear-all-btn {
  background: none;
  border: 1px solid var(--border-subtle);
  color: var(--color-text-muted);
  font-size: 0.8rem;
  padding: 0.4rem 0.9rem;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  transition: var(--transition-fast);
}

.clear-all-btn:hover {
  background-color: rgba(192, 57, 43, 0.08);
  border-color: rgba(192, 57, 43, 0.25);
  color: #C0392B;
}

/* Cuadrícula idéntica al catálogo */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
  align-items: stretch;
}

/* Estado Vacío */
.empty-state-box {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 4.5rem 2rem;
  text-align: center;
  max-width: 540px;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: var(--shadow-subtle);
}

.empty-icon-circle {
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

.empty-text {
  font-size: 0.94rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 1.85rem;
}

@media (max-width: 640px) {
  .books-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
