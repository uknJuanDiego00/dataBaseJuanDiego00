<script setup>
import { 
  Feather, 
  BookOpen, 
  HeartHandshake, 
  CheckCircle2 
} from 'lucide-vue-next'
</script>

<template>
  <div class="about-page">
    <!-- Banner de Cabecera Simétrico -->
    <div class="about-hero-banner">
      <div class="container banner-inner">
        <span class="section-eyebrow">Nuestra Filosofía</span>
        <h1 class="page-title">Un Refugio Contra el Ruido del Mundo</h1>
        <p class="page-description">
          Nacimos de una convicción simple pero profunda: el conocimiento verdadero florece en la quietud, no en la prisa ni en el algoritmo de la distracción constante.
        </p>
      </div>
    </div>

    <!-- Sección de Manifiesto Principal -->
    <section class="container manifesto-section">
      <div class="manifesto-card">
        <span class="manifesto-label">Principio Rector</span>
        <blockquote class="manifesto-quote">
          “Menos ruido, más conocimiento.<br />
          Menos distracciones, más paz.”
        </blockquote>
        <p class="manifesto-subtext">
          En una época marcada por la sobrecarga informativa y la urgencia efímera, esta biblioteca propone volver a la lectura pausada, a las páginas que trascienden y al deleite de pensar sin interrupciones.
        </p>
      </div>
    </section>

    <!-- Los 3 Pilares del Refugio -->
    <section class="container pillars-section">
      <div class="section-header">
        <span class="section-eyebrow">Fundamentos</span>
        <h2 class="section-title">Nuestros Tres Pilares</h2>
        <p class="section-subtitle">
          Cada detalle de esta biblioteca, desde su paleta cromática hasta la disposición tipográfica, ha sido concebido para proteger tu atención.
        </p>
      </div>

      <div class="pillars-grid">
        <div class="pillar-card">
          <div class="pillar-icon-box">
            <Feather :size="24" />
          </div>
          <h3 class="pillar-title">1. Silencio Intencional</h3>
          <p class="pillar-desc">
            Diseñamos una interfaz sin notificaciones invasivas, sin publicidad y sin elementos parpadeantes. Tu atención y paz mental son sagradas.
          </p>
        </div>

        <div class="pillar-card">
          <div class="pillar-icon-box">
            <BookOpen :size="24" />
          </div>
          <h3 class="pillar-title">2. Curaduría Consciente</h3>
          <p class="pillar-desc">
            No buscamos la acumulación desmedida de títulos, sino una selección cuidada de obras atemporales en filosofía, literatura, ciencia, historia y espiritualidad.
          </p>
        </div>

        <div class="pillar-card">
          <div class="pillar-icon-box">
            <HeartHandshake :size="24" />
          </div>
          <h3 class="pillar-title">3. Calidez Humana</h3>
          <p class="pillar-desc">
            La tecnología debe ser un puente invisible que te acerque a la sabiduría de los autores, preservando la dignidad y la calma de las bibliotecas clásicas.
          </p>
        </div>
      </div>
    </section>

    <!-- El Espacio Físico & Digital Equilibrado -->
    <section class="space-section">
      <div class="container space-container">
        <div class="space-content">
          <span class="section-eyebrow">El Entorno</span>
          <h2 class="space-title">Donde la Madera Encuentra la Luz</h2>
          <p class="space-text">
            Nuestra sede física cuenta con mesas de roble, ventanales con vista a jardines de sombra y un compromiso irrenunciable con la serenidad sonora.
          </p>
          <ul class="space-features">
            <li>
              <CheckCircle2 :size="17" class="feature-check" />
              <span>Salas de lectura sin dispositivos móviles activos.</span>
            </li>
            <li>
              <CheckCircle2 :size="17" class="feature-check" />
              <span>Infusiones aromáticas naturales para acompañar las horas de estudio.</span>
            </li>
            <li>
              <CheckCircle2 :size="17" class="feature-check" />
              <span>Préstamos bibliotecarios flexibles sin presiones innecesarias.</span>
            </li>
          </ul>
        </div>

        <div class="space-visual">
          <img 
            src="https://images.unsplash.com/photo-1507842229451-9f7957388e0c?auto=format&fit=crop&w=800&q=80" 
            alt="Interior de biblioteca con estantes de madera y luz natural" 
            class="space-image"
            loading="lazy"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-page {
  padding-bottom: 5.5rem;
}

.about-hero-banner {
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
  padding: 4.5rem 0 3.5rem 0;
  text-align: center;
  margin-bottom: 3.5rem;
}

.banner-inner {
  max-width: 700px;
}

.page-title {
  font-size: clamp(2.3rem, 4vw, 3.2rem);
  color: var(--color-primary);
  margin-bottom: 1rem;
  line-height: 1.18;
}

.page-description {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  line-height: 1.68;
}

/* Manifiesto */
.manifesto-section {
  margin-bottom: 5rem;
}

.manifesto-card {
  background-color: var(--color-primary);
  color: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 4rem 3rem;
  text-align: center;
  box-shadow: var(--shadow-editorial);
  position: relative;
  overflow: hidden;
}

.manifesto-label {
  display: inline-block;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-accent);
  font-weight: 600;
  margin-bottom: 1.25rem;
}

.manifesto-quote {
  font-family: var(--font-editorial);
  font-style: italic;
  font-size: clamp(1.9rem, 3.5vw, 2.6rem);
  line-height: 1.35;
  color: #FAF8F3;
  margin-bottom: 1.5rem;
}

.manifesto-subtext {
  font-size: 1.02rem;
  color: rgba(245, 242, 233, 0.82);
  max-width: 580px;
  margin: 0 auto;
  line-height: 1.65;
}

/* Pilares */
.pillars-section {
  margin-bottom: 5.5rem;
}

.pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.pillar-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 2.2rem 1.85rem;
  text-align: left;
  transition: var(--transition-smooth);
  box-shadow: var(--shadow-subtle);
  display: flex;
  flex-direction: column;
}

.pillar-card:hover {
  background-color: #FFFFFF;
  border-color: var(--border-accent);
  transform: translateY(-3px);
  box-shadow: var(--shadow-card);
}

.pillar-icon-box {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background-color: var(--color-accent-subtle);
  color: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  border: 1px solid rgba(196, 154, 98, 0.2);
}

.pillar-title {
  font-size: 1.25rem;
  color: var(--color-primary);
  margin-bottom: 0.65rem;
}

.pillar-desc {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  line-height: 1.65;
}

/* Espacio */
.space-section {
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  padding: 4.5rem 0;
}

.space-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 3.5rem;
}

.space-title {
  font-size: clamp(1.8rem, 3vw, 2.3rem);
  color: var(--color-primary);
  margin-bottom: 1rem;
}

.space-text {
  font-size: 1rem;
  color: var(--color-text-muted);
  line-height: 1.68;
  margin-bottom: 1.75rem;
}

.space-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.space-features li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.94rem;
  color: var(--color-primary);
}

.feature-check {
  color: var(--color-accent);
  flex-shrink: 0;
}

.space-visual {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-editorial);
  border: 1px solid var(--border-subtle);
}

.space-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

@media (max-width: 992px) {
  .manifesto-card {
    padding: 3rem 1.75rem;
  }

  .pillars-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .space-container {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>
