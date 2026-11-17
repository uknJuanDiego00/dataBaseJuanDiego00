<script setup>
import { ref } from 'vue'
import { Quote, Sparkles, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const quotes = [
  {
    text: "Leer es darle un momento de silencio al mundo para escuchar lo que nuestra mente tiene por decir.",
    author: "Filosofía del Refugio",
    context: "Manifiesto de la Biblioteca Sereno"
  },
  {
    text: "Siempre imaginé que el Paraíso sería algún tipo de biblioteca.",
    author: "Jorge Luis Borges",
    context: "Poema de los Dones"
  },
  {
    text: "La tranquilidad perfecta consiste en el buen orden de la mente, el reino que verdaderamente te pertenece.",
    author: "Marco Aurelio",
    context: "Meditaciones, Libro IV"
  },
  {
    text: "El silencio no es la ausencia de sonido, sino la presencia de un sosiego fértil donde nacen las grandes ideas.",
    author: "Erling Kagge",
    context: "El Silencio en la Era del Ruido"
  }
]

const currentIndex = ref(0)

const prevQuote = () => {
  currentIndex.value = (currentIndex.value - 1 + quotes.length) % quotes.length
}

const nextQuote = () => {
  currentIndex.value = (currentIndex.value + 1) % quotes.length
}

const setQuote = (index) => {
  currentIndex.value = index
}
</script>

<template>
  <section class="inspiration-section">
    <div class="container inspiration-container">
      <!-- Insignia dorada superior -->
      <div class="inspiration-badge">
        <Sparkles :size="13" />
        <span>Rincón de Contemplación</span>
      </div>

      <!-- Icono de comillas simétricas -->
      <div class="quote-icon-wrapper">
        <Quote :size="36" stroke-width="1.3" class="quote-svg" />
      </div>

      <!-- Cita inspiradora con animación suave -->
      <transition name="quote-fade" mode="out-in">
        <div :key="currentIndex" class="quote-content">
          <blockquote class="inspiration-quote">
            “{{ quotes[currentIndex].text }}”
          </blockquote>

          <div class="quote-attribution">
            <cite class="quote-author">{{ quotes[currentIndex].author }}</cite>
            <span class="quote-context">{{ quotes[currentIndex].context }}</span>
          </div>
        </div>
      </transition>

      <!-- Controles de navegación simétricos -->
      <div class="quote-controls">
        <button class="quote-nav-btn" @click="prevQuote" aria-label="Cita anterior">
          <ChevronLeft :size="18" />
        </button>

        <div class="quote-dots">
          <button 
            v-for="(q, idx) in quotes" 
            :key="idx"
            class="quote-dot" 
            :class="{ active: idx === currentIndex }"
            @click="setQuote(idx)"
            :aria-label="`Ir a la cita ${idx + 1}`"
          ></button>
        </div>

        <button class="quote-nav-btn" @click="nextQuote" aria-label="Siguiente cita">
          <ChevronRight :size="18" />
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* 30% Verde Bosque estricto */
.inspiration-section {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  padding: 5.5rem 0;
  position: relative;
  overflow: hidden;
}

.inspiration-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
}

.inspiration-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 800px;
}

/* Insignia dorada */
.inspiration-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.95rem;
  border-radius: var(--radius-full);
  background-color: rgba(196, 154, 98, 0.15);
  color: var(--color-accent);
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  border: 1px solid rgba(196, 154, 98, 0.3);
  margin-bottom: 1.75rem;
}

/* Comillas */
.quote-icon-wrapper {
  color: var(--color-accent);
  margin-bottom: 1.25rem;
  opacity: 0.85;
}

/* Contenido de la Cita */
.quote-content {
  margin-bottom: 2.5rem;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.inspiration-quote {
  font-family: var(--font-editorial);
  font-style: italic;
  font-size: clamp(1.6rem, 2.8vw, 2.15rem);
  font-weight: 400;
  line-height: 1.45;
  color: #FAF8F3;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
}

.quote-attribution {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.quote-author {
  font-family: var(--font-sans);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-accent);
  font-style: normal;
  letter-spacing: 0.02em;
}

.quote-context {
  font-size: 0.8rem;
  color: rgba(245, 242, 233, 0.65);
}

/* Controles */
.quote-controls {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.quote-nav-btn {
  background: none;
  border: 1px solid rgba(245, 242, 233, 0.2);
  color: var(--bg-primary);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
}

.quote-nav-btn:hover {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
  color: #FFFFFF;
}

.quote-dots {
  display: flex;
  gap: 0.55rem;
}

.quote-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: rgba(245, 242, 233, 0.25);
  border: none;
  cursor: pointer;
  transition: var(--transition-fast);
}

.quote-dot.active {
  background-color: var(--color-accent);
  width: 20px;
  border-radius: var(--radius-full);
}

/* Transición */
.quote-fade-enter-active,
.quote-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.quote-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.quote-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
