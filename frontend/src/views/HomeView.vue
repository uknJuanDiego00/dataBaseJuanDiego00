<script setup>
import Hero from '../components/Hero.vue'
import Categories from '../components/Categories.vue'
import FeaturedBooks from '../components/FeaturedBooks.vue'
import Inspiration from '../components/Inspiration.vue'
import { Feather, HeartHandshake, BookOpen } from 'lucide-vue-next'
</script>

<template>
  <div class="home-view">
    <!-- Hero Principal Equilibrado -->
    <Hero />

    <!-- Franja de Filosofía Simétrica -->
    <section class="philosophy-strip">
      <div class="container strip-container">
        <div class="strip-item">
          <div class="strip-icon"><Feather :size="18" /></div>
          <div class="strip-text">
            <h4>Silencio Intencional</h4>
            <p>Un espacio donde cada rincón invita a la concentración y la paz mental.</p>
          </div>
        </div>

        <div class="strip-divider"></div>

        <div class="strip-item">
          <div class="strip-icon"><BookOpen :size="18" /></div>
          <div class="strip-text">
            <h4>Curaduría Consciente</h4>
            <p>Obras seleccionadas con rigor editorial para nutrir el espíritu y el intelecto.</p>
          </div>
        </div>

        <div class="strip-divider"></div>

        <div class="strip-item">
          <div class="strip-icon"><HeartHandshake :size="18" /></div>
          <div class="strip-text">
            <h4>Comunidad Reflexiva</h4>
            <p>Encuentro para lectores que aprecian el valor de las ideas bien decantadas.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Exploración de Categorías -->
    <Categories />

    <!-- Libros Destacados -->
    <FeaturedBooks />

    <!-- Sección de Inspiración y Citas -->
    <Inspiration />
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
}

/* Franja de Filosofía Equilibrada */
.philosophy-strip {
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  padding: 2.75rem 0;
}

.strip-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.strip-item {
  display: flex;
  align-items: flex-start;
  gap: 1.15rem;
  flex: 1;
}

.strip-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background-color: var(--color-accent-subtle);
  color: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(196, 154, 98, 0.2);
}

.strip-text h4 {
  font-family: var(--font-serif);
  font-size: 1.12rem;
  margin-bottom: 0.3rem;
  color: var(--color-primary);
}

.strip-text p {
  font-size: 0.86rem;
  color: var(--color-text-muted);
  line-height: 1.55;
}

.strip-divider {
  width: 1px;
  height: 52px;
  background-color: var(--border-subtle);
}

@media (max-width: 992px) {
  .strip-container {
    flex-direction: column;
    align-items: stretch;
    gap: 1.75rem;
  }

  .strip-divider {
    display: none;
  }
}
</style>
