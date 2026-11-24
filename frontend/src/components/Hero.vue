<script setup>
import { useRouter } from 'vue-router'
import { ArrowRight, Compass, Sparkles } from 'lucide-vue-next'

const router = useRouter()

const navigateToCatalog = () => {
  router.push('/catalogo')
}

const navigateToCategories = () => {
  router.push('/categorias')
}
</script>

<template>
  <section class="hero-section">
    <div class="container hero-container">
      <!-- Columna de Texto Editorial Equilibrada -->
      <div class="hero-content">
        <div class="hero-tag">
          <Sparkles :size="13" class="tag-icon" />
          <span>Refugio de Sabiduría & Silencio</span>
        </div>

        <h1 class="hero-title">
          Un lugar para detener el tiempo y dejar que las ideas florezcan
        </h1>

        <p class="hero-subtitle">
          Descubre historias, conocimientos y pensamientos que alimentan el alma. Una colección curada para leer con calma, pensar con hondura y reencontrar la serenidad.
        </p>

        <div class="hero-actions">
          <button class="btn btn-primary hero-btn" @click="navigateToCatalog">
            <span>Explorar biblioteca</span>
            <ArrowRight :size="17" />
          </button>
          <button class="btn btn-secondary hero-btn" @click="navigateToCategories">
            <Compass :size="17" />
            <span>Descubrir libros</span>
          </button>
        </div>

        <!-- Indicadores de confianza simétricos -->
        <div class="hero-meta">
          <div class="meta-item">
            <span class="meta-number">+2,400</span>
            <span class="meta-label">Obras selectas</span>
          </div>
          <div class="meta-divider"></div>
          <div class="meta-item">
            <span class="meta-number">7</span>
            <span class="meta-label">Ramas del saber</span>
          </div>
          <div class="meta-divider"></div>
          <div class="meta-item">
            <span class="meta-number">100%</span>
            <span class="meta-label">Libre de ruido</span>
          </div>
        </div>
      </div>

      <!-- Columna de Imagen Proporcionada -->
      <div class="hero-visual">
        <div class="visual-wrapper">
          <img 
            src="https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=900&q=80" 
            alt="Biblioteca serena con luz natural y estantes de libros" 
            class="hero-image"
            loading="eager"
          />
          
          <!-- Cita flotante equilibrada -->
          <div class="floating-quote">
            <p class="quote-text">“El silencio es el espacio donde las palabras cobran su verdadero peso.”</p>
            <span class="quote-author">— Filosofía del Refugio</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  padding: 4.5rem 0 5rem 0;
  background: radial-gradient(circle at 15% 20%, rgba(196, 154, 98, 0.07) 0%, transparent 45%),
              radial-gradient(circle at 85% 75%, rgba(52, 72, 61, 0.05) 0%, transparent 50%);
}

.hero-container {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
  gap: 3.5rem;
}

/* Columna de Texto */
.hero-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 580px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.32rem 0.85rem;
  border-radius: var(--radius-full);
  background-color: var(--color-accent-subtle);
  color: #8A642F;
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  margin-bottom: 1.35rem;
  border: 1px solid rgba(196, 154, 98, 0.25);
}

.tag-icon {
  color: var(--color-accent);
}

.hero-title {
  font-size: clamp(2.3rem, 4vw, 3.25rem);
  font-weight: 700;
  line-height: 1.18;
  color: var(--color-primary);
  margin-bottom: 1.25rem;
  letter-spacing: -0.018em;
}

.hero-subtitle {
  font-size: 1.08rem;
  line-height: 1.68;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.hero-btn {
  font-size: 0.94rem;
  padding: 0.85rem 1.85rem;
}

/* Indicadores */
.hero-meta {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
  width: 100%;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-number {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.1;
}

.meta-label {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-divider {
  width: 1px;
  height: 32px;
  background-color: var(--border-subtle);
}

/* Columna de Imagen */
.hero-visual {
  display: flex;
  justify-content: center;
  position: relative;
}

.visual-wrapper {
  position: relative;
  width: 100%;
  max-width: 440px;
}

.hero-image {
  width: 100%;
  aspect-ratio: 4 / 4.9;
  max-height: 500px;
  object-fit: cover;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-editorial);
  border: 1px solid var(--border-subtle);
  display: block;
}

/* Cita flotante */
.floating-quote {
  position: absolute;
  bottom: -1.25rem;
  left: -1.5rem;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-accent);
  padding: 1.15rem 1.45rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  max-width: 300px;
}

.quote-text {
  font-family: var(--font-editorial);
  font-style: italic;
  font-size: 1.05rem;
  color: var(--color-primary);
  line-height: 1.4;
  margin-bottom: 0.35rem;
}

.quote-author {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-accent);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Responsive */
@media (max-width: 992px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 3.5rem;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-visual {
    order: -1;
  }

  .visual-wrapper {
    max-width: 480px;
  }

  .floating-quote {
    left: 1rem;
    bottom: -1rem;
  }
}

@media (max-width: 640px) {
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-btn {
    width: 100%;
  }

  .floating-quote {
    display: none;
  }
}
</style>
