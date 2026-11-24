<script setup>
import { BookOpen, MapPin, Mail, Phone } from 'lucide-vue-next'
</script>

<template>
  <footer class="site-footer">
    <div class="container footer-container">
      <div class="footer-grid">
        <!-- Columna 1: Identidad y Misión -->
        <div class="footer-brand">
          <div class="footer-logo">
            <div class="footer-logo-icon">
              <BookOpen :size="18" />
            </div>
            <div class="footer-logo-text">
              <span class="brand-title">BIBLIOTECA</span>
              <span class="brand-subtitle">Refugio de Serenidad</span>
            </div>
          </div>
          <p class="brand-desc">
            Un espacio concebido para pausar la prisa moderna, reencontrarse con el silencio y explorar obras que iluminan la mente con sosiego y hondura.
          </p>
          <div class="peace-pill">
            <span class="peace-dot"></span>
            <span>Espacio libre de ruido digital</span>
          </div>
        </div>

        <!-- Columna 2: Navegación Serana -->
        <div class="footer-nav-col">
          <h4 class="footer-col-title">Exploración</h4>
          <ul class="footer-links">
            <li><router-link to="/">Inicio</router-link></li>
            <li><router-link to="/catalogo">Catálogo completo</router-link></li>
            <li><router-link to="/categorias">Ramas del saber</router-link></li>
            <li><router-link to="/mis-libros">Mis libros guardados</router-link></li>
            <li><router-link to="/nosotros">Filosofía & Nosotros</router-link></li>
          </ul>
        </div>

        <!-- Columna 3: Horarios de Serenidad -->
        <div class="footer-nav-col">
          <h4 class="footer-col-title">Horas de Silencio</h4>
          <ul class="footer-schedule">
            <li>
              <span class="day-label">Lunes a Viernes</span>
              <span class="hour-label">08:00 — 19:30</span>
            </li>
            <li>
              <span class="day-label">Sábados de Calma</span>
              <span class="hour-label">09:00 — 16:00</span>
            </li>
            <li>
              <span class="day-label">Domingos</span>
              <span class="hour-label">Lectura contemplativa</span>
            </li>
          </ul>
        </div>

        <!-- Columna 4: Encuentro y Contacto -->
        <div class="footer-nav-col">
          <h4 class="footer-col-title">El Refugio</h4>
          <ul class="footer-contact">
            <li>
              <MapPin :size="15" class="contact-icon" />
              <span>Claustro del Saber, Calle de la Calma #12</span>
            </li>
            <li>
              <Mail :size="15" class="contact-icon" />
              <span>contacto@bibliotecaserena.org</span>
            </li>
            <li>
              <Phone :size="15" class="contact-icon" />
              <span>+57 (601) 320 8800</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Divisor sutil -->
      <div class="footer-divider"></div>

      <!-- Pie inferior con frase y derechos -->
      <div class="footer-bottom">
        <p class="final-motto">
          “Que cada página sea un nuevo comienzo.”
        </p>

        <p class="copyright-text">
          &copy; {{ new Date().getFullYear() }} BIBLIOTECA. Menos ruido, más conocimiento. Menos distracciones, más paz.
        </p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background-color: var(--color-primary-dark);
  color: #ECE6D9;
  padding: 4.5rem 0 2.25rem 0;
  margin-top: auto;
  border-top: 1px solid rgba(196, 154, 98, 0.2);
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.35fr 0.85fr 0.95fr 1.05fr;
  gap: 3rem;
  margin-bottom: 3.5rem;
}

/* Columna de Marca */
.footer-brand {
  display: flex;
  flex-direction: column;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.15rem;
}

.footer-logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--color-accent);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-logo-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-serif);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #FAF8F3;
}

.brand-subtitle {
  font-size: 0.68rem;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.brand-desc {
  font-size: 0.86rem;
  color: rgba(236, 230, 217, 0.75);
  line-height: 1.62;
  margin-bottom: 1.35rem;
}

.peace-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.72rem;
  color: var(--color-accent);
  background-color: rgba(196, 154, 98, 0.12);
  padding: 0.3rem 0.8rem;
  border-radius: var(--radius-full);
  border: 1px solid rgba(196, 154, 98, 0.25);
  align-self: flex-start;
}

.peace-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--color-accent);
}

/* Títulos de Columnas */
.footer-col-title {
  font-family: var(--font-serif);
  font-size: 1.05rem;
  color: #FAF8F3;
  margin-bottom: 1.25rem;
  letter-spacing: 0.02em;
}

/* Enlaces */
.footer-links,
.footer-schedule,
.footer-contact {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.footer-links a {
  font-size: 0.86rem;
  color: rgba(236, 230, 217, 0.75);
  transition: var(--transition-fast);
}

.footer-links a:hover {
  color: var(--color-accent);
  transform: translateX(3px);
  display: inline-block;
}

/* Horarios */
.footer-schedule li {
  display: flex;
  flex-direction: column;
  font-size: 0.84rem;
  border-bottom: 1px solid rgba(236, 230, 217, 0.08);
  padding-bottom: 0.45rem;
}

.day-label {
  color: rgba(236, 230, 217, 0.9);
  font-weight: 500;
}

.hour-label {
  color: var(--color-accent);
  font-size: 0.78rem;
}

/* Contacto */
.footer-contact li {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.84rem;
  color: rgba(236, 230, 217, 0.75);
}

.contact-icon {
  color: var(--color-accent);
  margin-top: 0.15rem;
  flex-shrink: 0;
}

/* Divisor */
.footer-divider {
  height: 1px;
  background-color: rgba(236, 230, 217, 0.1);
  margin-bottom: 2rem;
}

/* Pie Inferior */
.footer-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.65rem;
}

.final-motto {
  font-family: var(--font-editorial);
  font-style: italic;
  font-size: 1.28rem;
  color: var(--color-accent);
  letter-spacing: 0.02em;
}

.copyright-text {
  font-size: 0.76rem;
  color: rgba(236, 230, 217, 0.5);
}

@media (max-width: 992px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 2.25rem;
  }
}

@media (max-width: 640px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}
</style>
