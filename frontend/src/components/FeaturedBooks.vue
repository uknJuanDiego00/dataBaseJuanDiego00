<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { books } from '../data/books'
import BookCard from './BookCard.vue'
import { ArrowRight, Sparkles } from 'lucide-vue-next'

const router = useRouter()
const favorites = ref([])

const featuredBooks = books.filter(b => b.featured)

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

const goToCatalog = () => {
  router.push('/catalogo')
}

onMounted(() => {
  loadFavorites()
})
</script>

<template>
  <section class="section featured-section">
    <div class="container">
      <!-- Encabezado simétrico con botón alineado al pie del título -->
      <div class="featured-top">
        <div class="header-text">
          <span class="section-eyebrow">
            <Sparkles :size="13" />
            <span>Selección del Bibliotecario</span>
          </span>
          <h2 class="section-title">Obras Esenciales para el Sosiego</h2>
          <p class="section-subtitle">
            Lecturas escogidas minuciosamente por su capacidad de inspirar, acompañar en el silencio y despertar pensamientos perdurables.
          </p>
        </div>

        <button class="btn btn-secondary view-all-btn" @click="goToCatalog">
          <span>Ver catálogo completo</span>
          <ArrowRight :size="16" />
        </button>
      </div>

      <!-- Cuadrícula simétrica con tarjetas de alturas niveladas -->
      <div class="books-grid">
        <BookCard 
          v-for="book in featuredBooks"
          :key="book.id"
          :book="book"
          :is-favorite="isFavorite(book.id)"
          @toggle-favorite="toggleFavorite"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.featured-section {
  background-color: var(--bg-primary);
}

.featured-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 3rem;
  gap: 2rem;
  flex-wrap: wrap;
}

.header-text {
  max-width: 620px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
  align-items: stretch;
}

@media (max-width: 768px) {
  .featured-top {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 2rem;
  }

  .view-all-btn {
    width: 100%;
  }

  .books-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
