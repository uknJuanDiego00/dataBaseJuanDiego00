<script setup>
import { useRouter } from 'vue-router'
import { Heart, ArrowUpRight, BookOpen } from 'lucide-vue-next'

const props = defineProps({
  book: {
    type: Object,
    required: true
  },
  isFavorite: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-favorite'])

const router = useRouter()

const viewDetail = () => {
  router.push(`/libro/${props.book.id}`)
}

const onFavoriteClick = (e) => {
  e.stopPropagation()
  emit('toggle-favorite', props.book)
}
</script>

<template>
  <article class="book-card" @click="viewDetail">
    <!-- Portada con relación de aspecto consistente 2:2.8 -->
    <div class="book-cover-container">
      <img 
        :src="book.portada_url || book.cover || book.url_imagen" 
        :alt="`Portada del libro ${book.titulo || book.title || ''}`"
        class="book-cover-img"
        loading="lazy"
      />
      
      <!-- Overlay de interacción al hover -->
      <div class="cover-overlay">
        <span class="preview-btn">
          <span>Ver detalle</span>
          <ArrowUpRight :size="14" />
        </span>
      </div>

      <!-- Botón de Favorito Flotante -->
      <button 
        class="favorite-btn" 
        :class="{ active: isFavorite }"
        :title="isFavorite ? 'Quitar de mis favoritos' : 'Guardar en mis libros'"
        @click="onFavoriteClick"
        :aria-label="isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'"
      >
        <Heart :size="18" :fill="isFavorite ? 'currentColor' : 'none'" />
      </button>

      <!-- Insignia de Disponibilidad -->
      <div class="availability-pill" :class="book.available ? 'is-available' : 'is-borrowed'">
        <span class="status-dot"></span>
        <span>{{ book.available ? 'Disponible' : 'En préstamo' }}</span>
      </div>
    </div>

    <!-- Contenido editorial con alineación simétrica -->
    <div class="book-info">
      <div class="book-meta-top">
        <span class="book-category">{{ book.category }}</span>
        <span class="book-year">{{ book.year }}</span>
      </div>

      <h3 class="book-title" :title="book.title">
        {{ book.title }}
      </h3>

      <p class="book-author">
        de <span class="author-highlight">{{ book.author }}</span>
      </p>

      <p class="book-description">
        {{ book.description }}
      </p>

      <!-- Pie de tarjeta anclado al fondo de forma uniforme -->
      <div class="book-footer">
        <button class="consult-btn" @click.stop="viewDetail">
          <BookOpen :size="15" />
          <span>Consultar</span>
        </button>

        <span class="copies-info" v-if="book.available">
          {{ book.copiesAvailable }} de {{ book.totalCopies }} copias
        </span>
        <span class="copies-info borrowed" v-else>
          Próxima devolución
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.book-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: var(--transition-smooth);
  cursor: pointer;
  position: relative;
  box-shadow: var(--shadow-subtle);
}

.book-card:hover {
  background-color: #FFFFFF;
  border-color: var(--border-accent);
  transform: translateY(-4px);
  box-shadow: var(--shadow-card);
}

/* Contenedor de Portada con proporción fija */
.book-cover-container {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 2.75;
  overflow: hidden;
  background-color: var(--bg-secondary);
}

.book-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
  display: block;
}

.book-card:hover .book-cover-img {
  transform: scale(1.03);
}

/* Overlay al hover */
.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(30, 45, 37, 0.55) 0%, rgba(30, 45, 37, 0.08) 60%, transparent 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.22s ease;
}

.book-card:hover .cover-overlay {
  opacity: 1;
}

.preview-btn {
  background-color: rgba(255, 254, 250, 0.96);
  color: var(--color-primary);
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.55rem 1.1rem;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  gap: 0.35rem;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
  transform: translateY(6px);
  transition: transform 0.22s ease;
}

.book-card:hover .preview-btn {
  transform: translateY(0);
}

/* Botón de Favorito */
.favorite-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background-color: rgba(255, 254, 250, 0.92);
  backdrop-filter: blur(6px);
  border: 1px solid var(--border-subtle);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
  z-index: 2;
}

.favorite-btn:hover {
  background-color: #FFFFFF;
  color: #C0392B;
  transform: scale(1.08);
}

.favorite-btn.active {
  background-color: #FFFFFF;
  color: #C0392B;
  border-color: rgba(192, 57, 43, 0.25);
}

/* Pastilla de Disponibilidad */
.availability-pill {
  position: absolute;
  bottom: 0.75rem;
  left: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  backdrop-filter: blur(6px);
  z-index: 2;
}

.availability-pill.is-available {
  background-color: rgba(234, 244, 238, 0.94);
  color: #1F693F;
  border: 1px solid rgba(31, 105, 63, 0.2);
}

.availability-pill.is-borrowed {
  background-color: rgba(248, 239, 228, 0.94);
  color: #92581A;
  border: 1px solid rgba(146, 88, 26, 0.2);
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: currentColor;
}

/* Cuerpo de Información */
.book-info {
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.book-meta-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.45rem;
}

.book-category {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
}

.book-year {
  font-size: 0.76rem;
  color: var(--color-text-light);
}

.book-title {
  font-size: 1.18rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6em; /* Altura equilibrada para 2 líneas */
}

.book-author {
  font-size: 0.86rem;
  color: var(--color-text-muted);
  margin-bottom: 0.75rem;
}

.author-highlight {
  font-weight: 500;
  color: var(--color-primary);
}

.book-description {
  font-size: 0.84rem;
  color: var(--color-text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 1.25rem;
}

/* Pie de tarjeta anclado simétricamente */
.book-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.95rem;
  border-top: 1px solid rgba(52, 72, 61, 0.07);
  gap: 0.5rem;
}

.consult-btn {
  background-color: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: var(--transition-fast);
}

.consult-btn:hover {
  background-color: var(--color-primary);
  color: var(--bg-primary);
  border-color: var(--color-primary);
}

.copies-info {
  font-size: 0.74rem;
  color: var(--color-text-light);
}

.copies-info.borrowed {
  color: #92581A;
}
</style>
