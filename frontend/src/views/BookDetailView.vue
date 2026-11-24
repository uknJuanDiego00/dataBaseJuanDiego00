<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { books } from '../data/books'
import BookCard from '../components/BookCard.vue'
import { 
  ArrowLeft, 
  Heart, 
  BookOpen, 
  CheckCircle, 
  Share2, 
  Calendar,
  Layers,
  Barcode,
  Quote,
  Check
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const bookId = computed(() => Number(route.params.id))
const currentBook = computed(() => books.find(b => b.id === bookId.value))

const favorites = ref([])
const showLoanModal = ref(false)
const loanSuccess = ref(false)
const copiedLink = ref(false)

const loadFavorites = () => {
  try {
    favorites.value = JSON.parse(localStorage.getItem('biblioteca_favoritos') || '[]')
  } catch {
    favorites.value = []
  }
}

const isFavorite = computed(() => {
  return currentBook.value && favorites.value.some(b => b.id === currentBook.value.id)
})

const toggleFavorite = () => {
  if (!currentBook.value) return
  const index = favorites.value.findIndex(b => b.id === currentBook.value.id)
  let action = 'added'
  if (index > -1) {
    favorites.value.splice(index, 1)
    action = 'removed'
  } else {
    favorites.value.push(currentBook.value)
  }
  localStorage.setItem('biblioteca_favoritos', JSON.stringify(favorites.value))
  window.dispatchEvent(new CustomEvent('favorites-updated', {
    detail: { action, title: currentBook.value.title }
  }))
}

const relatedBooks = computed(() => {
  if (!currentBook.value) return []
  return books
    .filter(b => b.categorySlug === currentBook.value.categorySlug && b.id !== currentBook.value.id)
    .slice(0, 3)
})

const handleLoanRequest = () => {
  loanSuccess.value = true
  setTimeout(() => {
    showLoanModal.value = false
    loanSuccess.value = false
  }, 2200)
}

const shareBook = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copiedLink.value = true
    setTimeout(() => {
      copiedLink.value = false
    }, 2000)
  } catch {
    // Fallback silencioso
  }
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/catalogo')
  }
}

onMounted(() => {
  loadFavorites()
})

watch(() => route.params.id, () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<template>
  <div v-if="currentBook" class="book-detail-page">
    <div class="container">
      <!-- Navegación superior simétrica -->
      <nav class="detail-nav" aria-label="Ruta de navegación">
        <button class="back-link-btn" @click="goBack">
          <ArrowLeft :size="17" />
          <span>Regresar al catálogo</span>
        </button>

        <div class="nav-breadcrumbs">
          <router-link to="/catalogo">Catálogo</router-link>
          <span class="crumb-separator">/</span>
          <router-link :to="`/catalogo?categoria=${currentBook.categorySlug}`">{{ currentBook.category }}</router-link>
          <span class="crumb-separator">/</span>
          <span class="active-crumb">{{ currentBook.title }}</span>
        </div>
      </nav>

      <!-- Layout Editorial Simétrico en 2 Columnas -->
      <div class="detail-grid">
        <!-- Columna Izquierda: Portada Proporcionada -->
        <div class="detail-visual-col">
          <div class="cover-frame">
            <img 
              :src="currentBook.cover" 
              :alt="`Portada de ${currentBook.title}`"
              class="detail-cover-img"
            />
          </div>

          <!-- Acciones de cabecera de portada -->
          <div class="cover-actions-row">
            <button 
              class="action-pill-btn fav-pill" 
              :class="{ active: isFavorite }"
              @click="toggleFavorite"
              :aria-label="isFavorite ? 'Quitar de mis libros' : 'Guardar en mis libros'"
            >
              <Heart :size="17" :fill="isFavorite ? 'currentColor' : 'none'" />
              <span>{{ isFavorite ? 'En mis libros' : 'Guardar en mis libros' }}</span>
            </button>

            <button 
              class="action-pill-btn share-pill" 
              @click="shareBook"
              title="Copiar enlace permanente"
              aria-label="Compartir enlace de esta obra"
            >
              <Check v-if="copiedLink" :size="16" class="check-icon" />
              <Share2 v-else :size="16" />
              <span>{{ copiedLink ? 'Copiado' : 'Compartir' }}</span>
            </button>
          </div>
        </div>

        <!-- Columna Derecha: Contenido y Lectura -->
        <div class="detail-content-col">
          <div class="header-tags">
            <span class="badge badge-gold">{{ currentBook.category }}</span>
            <div class="badge" :class="currentBook.available ? 'badge-available' : 'badge-borrowed'">
              <span class="status-dot"></span>
              <span>{{ currentBook.available ? `${currentBook.copiesAvailable} copias disponibles` : 'Actualmente en préstamo' }}</span>
            </div>
          </div>

          <h1 class="book-main-title">{{ currentBook.title }}</h1>
          <p class="book-main-author">
            de <strong class="author-name">{{ currentBook.author }}</strong>
          </p>

          <!-- Metadatos bibliográficos en cuadrícula de 3 columnas -->
          <div class="meta-strip">
            <div class="meta-card">
              <Calendar :size="16" class="meta-icon" />
              <div class="meta-text">
                <span class="meta-k">Publicación</span>
                <span class="meta-v">{{ currentBook.year }}</span>
              </div>
            </div>

            <div class="meta-card">
              <Layers :size="16" class="meta-icon" />
              <div class="meta-text">
                <span class="meta-k">Extensión</span>
                <span class="meta-v">{{ currentBook.pages }} páginas</span>
              </div>
            </div>

            <div class="meta-card">
              <Barcode :size="16" class="meta-icon" />
              <div class="meta-text">
                <span class="meta-k">ISBN</span>
                <span class="meta-v">{{ currentBook.isbn }}</span>
              </div>
            </div>
          </div>

          <!-- Cita Destacada de la Obra -->
          <div class="book-quote-box">
            <Quote :size="20" class="quote-box-icon" />
            <blockquote class="book-quote-text">
              “{{ currentBook.quote }}”
            </blockquote>
          </div>

          <!-- Sinopsis y Contemplación -->
          <div class="synopsis-section">
            <h3 class="synopsis-title">Sinopsis de la Obra</h3>
            <p class="synopsis-text">
              {{ currentBook.fullDescription }}
            </p>
          </div>

          <!-- Caja de Solicitud de Préstamo -->
          <div class="loan-action-box">
            <div class="loan-info">
              <h4>¿Deseas consultar o solicitar este ejemplar?</h4>
              <p>Puedes reservar la obra para lectura serena en sala o préstamo domiciliario por 14 días.</p>
            </div>

            <button 
              class="btn btn-primary loan-btn" 
              :disabled="!currentBook.available"
              @click="showLoanModal = true"
            >
              <BookOpen :size="17" />
              <span>{{ currentBook.available ? 'Solicitar en préstamo' : 'Notificar devolución' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Obras Relacionadas de la Misma Rama -->
      <section v-if="relatedBooks.length > 0" class="related-section">
        <div class="related-header">
          <span class="section-eyebrow">Afinidades Temáticas</span>
          <h2 class="section-title">Obras en {{ currentBook.category }}</h2>
        </div>

        <div class="related-grid">
          <BookCard 
            v-for="b in relatedBooks"
            :key="b.id"
            :book="b"
            :is-favorite="favorites.some(fav => fav.id === b.id)"
            @toggle-favorite="toggleFavorite"
          />
        </div>
      </section>
    </div>

    <!-- Modal Sereno de Préstamo -->
    <transition name="modal-fade">
      <div v-if="showLoanModal" class="modal-backdrop" @click.self="showLoanModal = false">
        <div class="modal-card">
          <div v-if="!loanSuccess" class="modal-body-confirm">
            <div class="modal-icon-badge">
              <BookOpen :size="26" />
            </div>
            <h3 class="modal-title">Confirmar Préstamo Sereno</h3>
            <p class="modal-desc">
              Estás reservando <strong>«{{ currentBook.title }}»</strong> de {{ currentBook.author }}. Tu ejemplar estará disponible en la sala de lectura.
            </p>
            <div class="modal-dates">
              <div class="date-row">
                <span>Fecha de préstamo:</span>
                <strong>Hoy</strong>
              </div>
              <div class="date-row">
                <span>Fecha límite de devolución:</span>
                <strong>14 días hábiles</strong>
              </div>
            </div>

            <div class="modal-actions">
              <button class="btn btn-subtle" @click="showLoanModal = false">Cancelar</button>
              <button class="btn btn-primary" @click="handleLoanRequest">Confirmar reserva</button>
            </div>
          </div>

          <!-- Confirmación Pacífica -->
          <div v-else class="modal-body-success">
            <div class="success-icon-badge">
              <CheckCircle :size="32" />
            </div>
            <h3 class="modal-title">Reserva Confirmada</h3>
            <p class="modal-desc">
              Te deseamos una lectura tranquila y enriquecedora. Podrás consultar los detalles en tu rincón de libros guardados.
            </p>
          </div>
        </div>
      </div>
    </transition>
  </div>

  <!-- Estado no encontrado -->
  <div v-else class="container not-found-view">
    <h2>Obra no encontrada</h2>
    <p>El libro solicitado no figura en el catálogo actual.</p>
    <router-link to="/catalogo" class="btn btn-primary">Volver al catálogo</router-link>
  </div>
</template>

<style scoped>
.book-detail-page {
  padding: 2.5rem 0 5.5rem 0;
}

/* Navegación */
.detail-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
  gap: 1rem;
}

.back-link-btn {
  background: none;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-primary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.back-link-btn:hover {
  color: var(--color-accent);
  transform: translateX(-3px);
}

.nav-breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.84rem;
  color: var(--color-text-light);
}

.crumb-separator {
  color: #C5BFB2;
}

.nav-breadcrumbs a {
  color: var(--color-text-muted);
}

.nav-breadcrumbs a:hover {
  color: var(--color-primary);
}

.active-crumb {
  color: var(--color-primary);
  font-weight: 600;
}

/* Layout en 2 Columnas */
.detail-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 4rem;
  align-items: start;
  margin-bottom: 5rem;
}

/* Columna Visual Izquierda */
.detail-visual-col {
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 95px;
}

.cover-frame {
  width: 100%;
  aspect-ratio: 2 / 2.85;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-editorial);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  margin-bottom: 1.25rem;
}

.detail-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-actions-row {
  display: flex;
  gap: 0.75rem;
}

.action-pill-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.75rem 1rem;
  min-height: 44px;
  border-radius: var(--radius-full);
  font-family: var(--font-sans);
  font-size: 0.84rem;
  font-weight: 500;
  cursor: pointer;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--color-primary);
  transition: var(--transition-fast);
}

.action-pill-btn:hover {
  background-color: #FFFFFF;
  border-color: var(--color-accent);
}

.action-pill-btn.fav-pill.active {
  background-color: #FFFFFF;
  color: #C0392B;
  border-color: rgba(192, 57, 43, 0.25);
}

.action-pill-btn .check-icon {
  color: #1F693F;
}

/* Columna de Contenido Editorial */
.detail-content-col {
  display: flex;
  flex-direction: column;
}

.header-tags {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.book-main-title {
  font-size: clamp(2.2rem, 3.8vw, 3rem);
  line-height: 1.15;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
  letter-spacing: -0.015em;
}

.book-main-author {
  font-size: 1.15rem;
  color: var(--color-text-muted);
  margin-bottom: 1.85rem;
}

.author-name {
  color: var(--color-primary);
  font-weight: 600;
}

/* Franja de Metadatos */
.meta-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1.15rem 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 2rem;
}

.meta-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.meta-icon {
  color: var(--color-accent);
}

.meta-text {
  display: flex;
  flex-direction: column;
}

.meta-k {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--color-text-light);
  letter-spacing: 0.05em;
}

.meta-v {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-primary);
}

/* Caja de Cita */
.book-quote-box {
  background-color: var(--bg-surface);
  border-left: 3px solid var(--color-accent);
  padding: 1.35rem 1.65rem;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  margin-bottom: 2.25rem;
  box-shadow: var(--shadow-subtle);
}

.quote-box-icon {
  color: var(--color-accent);
  opacity: 0.45;
  margin-bottom: 0.35rem;
}

.book-quote-text {
  font-family: var(--font-editorial);
  font-style: italic;
  font-size: 1.25rem;
  color: var(--color-primary);
  line-height: 1.45;
}

/* Sinopsis */
.synopsis-section {
  margin-bottom: 2.5rem;
}

.synopsis-title {
  font-size: 1.25rem;
  color: var(--color-primary);
  margin-bottom: 0.75rem;
}

.synopsis-text {
  font-size: 1rem;
  color: var(--color-text-muted);
  line-height: 1.72;
}

/* Caja de Préstamo */
.loan-action-box {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 1.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  box-shadow: var(--shadow-subtle);
}

.loan-info h4 {
  font-size: 1.15rem;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.loan-info p {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.loan-btn {
  flex-shrink: 0;
  padding: 0.85rem 1.85rem;
}

/* Obras Relacionadas */
.related-section {
  border-top: 1px solid var(--border-subtle);
  padding-top: 4rem;
}

.related-header {
  margin-bottom: 2.25rem;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.75rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(30, 45, 37, 0.55);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1.25rem;
}

.modal-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  max-width: 480px;
  width: 100%;
  padding: 2.5rem 2rem;
  box-shadow: var(--shadow-editorial);
  text-align: center;
}

.modal-icon-badge,
.success-icon-badge {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem auto;
}

.modal-icon-badge {
  background-color: var(--color-accent-subtle);
  color: var(--color-accent);
}

.success-icon-badge {
  background-color: #EAF4EE;
  color: #1F693F;
}

.modal-title {
  font-size: 1.45rem;
  color: var(--color-primary);
  margin-bottom: 0.65rem;
}

.modal-desc {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.modal-dates {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 0.9rem 1.15rem;
  margin-bottom: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.85rem;
  text-align: left;
}

.date-row {
  display: flex;
  justify-content: space-between;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 0.85rem;
}

.not-found-view {
  text-align: center;
  padding: 5.5rem 0;
}

@media (max-width: 992px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .detail-visual-col {
    position: static;
    max-width: 320px;
    margin: 0 auto;
  }

  .loan-action-box {
    flex-direction: column;
    align-items: flex-start;
  }

  .loan-btn {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .meta-strip {
    grid-template-columns: 1fr;
    gap: 0.85rem;
  }
}
</style>
