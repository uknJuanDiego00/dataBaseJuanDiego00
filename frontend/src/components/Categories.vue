<script setup>
import { useRouter } from 'vue-router'
import { categories } from '../data/categories'
import { 
  BookOpen, 
  Compass, 
  Landmark, 
  Sparkles, 
  Palette, 
  Sun, 
  Feather,
  ArrowRight
} from 'lucide-vue-next'

const router = useRouter()

const iconMap = {
  BookOpen,
  Compass,
  Landmark,
  Sparkles,
  Palette,
  Sun,
  Feather
}

const selectCategory = (categoryId) => {
  router.push({
    path: '/catalogo',
    query: { categoria: categoryId }
  })
}
</script>

<template>
  <section class="section categories-section">
    <div class="container">
      <!-- Encabezado de la sección -->
      <div class="section-header">
        <span class="section-eyebrow">Exploración Temática</span>
        <h2 class="section-title">Ramas del Conocimiento</h2>
        <p class="section-subtitle">
          Recorre nuestros senderos temáticos diseñados para alimentar la curiosidad, enriquecer el pensamiento y cultivar la serenidad interior.
        </p>
      </div>

      <!-- Cuadrícula Simétrica de Categorías -->
      <div class="categories-grid">
        <div 
          v-for="cat in categories" 
          :key="cat.id"
          class="category-card"
          @click="selectCategory(cat.id)"
          role="button"
          tabindex="0"
          :aria-label="`Explorar categoría ${cat.name}`"
          @keydown.enter="selectCategory(cat.id)"
        >
          <div class="card-icon-wrapper">
            <component :is="iconMap[cat.icon]" :size="22" class="card-icon" />
          </div>

          <div class="card-content">
            <div class="card-title-row">
              <h3 class="category-name">{{ cat.name }}</h3>
              <span class="category-count">{{ cat.count }} libros</span>
            </div>
            <p class="category-desc">{{ cat.description }}</p>
          </div>

          <div class="card-footer">
            <span class="explore-text">Explorar colección</span>
            <ArrowRight :size="14" class="arrow-icon" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.categories-section {
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

/* Tarjeta individual con altura equilibrada */
.category-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1.85rem 1.65rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: var(--transition-smooth);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-subtle);
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: transparent;
  transition: var(--transition-fast);
}

.category-card:hover {
  background-color: #FFFFFF;
  border-color: var(--border-accent);
  transform: translateY(-3px);
  box-shadow: var(--shadow-card);
}

.category-card:hover::before {
  background-color: var(--color-accent);
}

/* Icono simétrico */
.card-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background-color: rgba(52, 72, 61, 0.05);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.35rem;
  transition: var(--transition-smooth);
  border: 1px solid rgba(52, 72, 61, 0.06);
}

.category-card:hover .card-icon-wrapper {
  background-color: var(--color-accent);
  color: #FFFFFF;
  border-color: var(--color-accent);
  transform: scale(1.04);
}

/* Título y descripción */
.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.category-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
}

.category-count {
  font-size: 0.74rem;
  font-weight: 500;
  color: var(--color-accent);
  white-space: nowrap;
}

.category-desc {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  line-height: 1.58;
  margin-bottom: 1.5rem;
  min-height: 4.5em; /* Nivelación simétrica de párrafos */
}

/* Pie de la tarjeta */
.card-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-primary);
  transition: var(--transition-fast);
  padding-top: 0.75rem;
  border-top: 1px solid rgba(52, 72, 61, 0.05);
}

.arrow-icon {
  transition: transform 0.2s ease;
}

.category-card:hover .card-footer {
  color: var(--color-accent-hover);
}

.category-card:hover .arrow-icon {
  transform: translateX(3px);
}

@media (max-width: 992px) {
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }

  .category-desc {
    min-height: auto;
  }
}
</style>
