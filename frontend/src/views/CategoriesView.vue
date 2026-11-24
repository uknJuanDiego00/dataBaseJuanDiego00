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
  ArrowRight,
  Bookmark
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

const goToCategoryCatalog = (categoryId) => {
  router.push({
    path: '/catalogo',
    query: { categoria: categoryId }
  })
}
</script>

<template>
  <div class="categories-page">
    <div class="categories-banner">
      <div class="container banner-inner">
        <span class="section-eyebrow">Ramas del Saber</span>
        <h1 class="page-title">Siete Senderos Hacia el Conocimiento</h1>
        <p class="page-description">
          Cada disciplina representa una ventana distinta al asombro, al sosiego y a la comprensión de lo humano. Elige la rama que resuene hoy con tu búsqueda.
        </p>
      </div>
    </div>

    <div class="container categories-body">
      <div class="categories-list">
        <article 
          v-for="cat in categories" 
          :key="cat.id" 
          class="category-detail-card"
          @click="goToCategoryCatalog(cat.id)"
          role="button"
          tabindex="0"
          :aria-label="`Explorar colección de ${cat.name}`"
          @keydown.enter="goToCategoryCatalog(cat.id)"
        >
          <div class="card-left">
            <div class="category-icon-box">
              <component :is="iconMap[cat.icon]" :size="26" />
            </div>
            <div class="category-meta-info">
              <span class="books-count-badge">
                <Bookmark :size="12" />
                <span>{{ cat.count }} títulos disponibles</span>
              </span>
              <h2 class="category-title">{{ cat.name }}</h2>
              <p class="category-long-desc">{{ cat.description }}</p>
            </div>
          </div>

          <div class="card-right">
            <button class="btn btn-primary explore-cat-btn" @click.stop="goToCategoryCatalog(cat.id)">
              <span>Ver obras</span>
              <ArrowRight :size="15" />
            </button>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped>
.categories-page {
  padding-bottom: 5.5rem;
}

.categories-banner {
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
  padding: 4rem 0 3.25rem 0;
  text-align: center;
  margin-bottom: 3rem;
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

/* Lista de Categorías Detalladas */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.category-detail-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 1.85rem 2.2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  cursor: pointer;
  transition: var(--transition-smooth);
  box-shadow: var(--shadow-subtle);
}

.category-detail-card:hover {
  background-color: #FFFFFF;
  border-color: var(--border-accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.card-left {
  display: flex;
  align-items: flex-start;
  gap: 1.75rem;
  flex: 1;
}

.category-icon-box {
  width: 58px;
  height: 58px;
  border-radius: var(--radius-md);
  background-color: rgba(52, 72, 61, 0.05);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: var(--transition-smooth);
  border: 1px solid rgba(52, 72, 61, 0.06);
}

.category-detail-card:hover .category-icon-box {
  background-color: var(--color-accent);
  color: #FFFFFF;
  border-color: var(--color-accent);
}

.category-meta-info {
  display: flex;
  flex-direction: column;
}

.books-count-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}

.category-title {
  font-size: 1.5rem;
  color: var(--color-primary);
  margin-bottom: 0.45rem;
}

.category-long-desc {
  font-size: 0.94rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  max-width: 620px;
}

.card-right {
  flex-shrink: 0;
}

.explore-cat-btn {
  padding: 0.75rem 1.45rem;
}

@media (max-width: 768px) {
  .category-detail-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.5rem;
  }

  .card-left {
    flex-direction: column;
    gap: 1rem;
  }

  .card-right {
    width: 100%;
  }

  .explore-cat-btn {
    width: 100%;
  }
}
</style>
