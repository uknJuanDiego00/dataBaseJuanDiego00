<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import { Sparkles, Lock, Mail, Loader2, ArrowLeft, AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const { login, loading } = useAuth()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  if (!email.value || !password.value) {
    errorMessage.value = 'Por favor ingresa tu correo y contraseña.'
    return
  }

  try {
    const user = await login(email.value, password.value)
    if (user.rol !== 'admin' && user.rol !== 'bibliotecario') {
      errorMessage.value = 'Tu cuenta no tiene privilegios de gestión (se requiere rol Bibliotecario o Administrador).'
      return
    }
    const redirect = route.query.redirect || '/admin'
    router.push(redirect)
  } catch (err) {
    errorMessage.value = err.message || 'Credenciales inválidas o cuenta inaccesible.'
  }
}
</script>

<template>
  <div class="admin-login-page">
    <div class="login-card">
      <router-link to="/" class="back-link">
        <ArrowLeft :size="16" />
        <span>Volver a la Biblioteca</span>
      </router-link>

      <div class="login-brand">
        <div class="brand-emblem">
          <Sparkles :size="20" />
        </div>
        <h1 class="brand-title">SERENIDAD</h1>
        <p class="brand-subtitle">Gestión y Administración Bibliotecaria</p>
      </div>

      <div v-if="errorMessage" class="login-error-alert">
        <AlertCircle :size="18" class="error-icon" />
        <span>{{ errorMessage }}</span>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email" class="form-label">Correo Electrónico</label>
          <div class="input-wrapper">
            <Mail :size="17" class="input-icon" />
            <input
              id="email"
              v-model="email"
              type="email"
              class="form-input"
              placeholder="admin@biblioteca.com"
              required
              autocomplete="email"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Contraseña</label>
          <div class="input-wrapper">
            <Lock :size="17" class="input-icon" />
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-input"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
          </div>
        </div>

        <button type="submit" class="login-submit-btn" :disabled="loading">
          <Loader2 v-if="loading" :size="18" class="spin-icon" />
          <span>{{ loading ? 'Ingresando al sistema...' : 'Acceder al Panel' }}</span>
        </button>
      </form>

      <div class="login-footer">
        <p class="footer-hint">
          Espacio reservado para personal autorizado.<br>
          Las credenciales son validadas con cifrado Argon2 y tokens JWT.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-ivory, #F5F2E9);
  padding: 1.5rem;
  background-image: radial-gradient(circle at 10% 20%, rgba(196, 154, 98, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(52, 72, 61, 0.05) 0%, transparent 40%);
}

.login-card {
  width: 100%;
  max-width: 440px;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 16px;
  padding: 2.25rem;
  box-shadow: 0 16px 36px rgba(52, 72, 61, 0.08);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.8rem;
  color: #7a7062;
  text-decoration: none;
  margin-bottom: 1.5rem;
  transition: color 0.15s ease;
}

.back-link:hover {
  color: var(--color-forest, #34483D);
}

.login-brand {
  text-align: center;
  margin-bottom: 2rem;
}

.brand-emblem {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-forest, #34483D) 0%, #1e2c24 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gold, #C49A62);
  margin: 0 auto 0.85rem auto;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.15);
}

.brand-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  letter-spacing: 0.08em;
  margin: 0;
  line-height: 1.1;
}

.brand-subtitle {
  font-size: 0.82rem;
  color: #7a7062;
  margin: 0.35rem 0 0 0;
}

.login-error-alert {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.82rem;
  margin-bottom: 1.25rem;
}

.error-icon {
  flex-shrink: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.9rem;
  color: #8c8273;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 0.7rem 0.9rem 0.7rem 2.4rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--color-forest, #34483D);
  transition: all 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-gold, #C49A62);
  background-color: var(--color-surface, #FFFEFA);
  box-shadow: 0 0 0 3px rgba(196, 154, 98, 0.18);
}

.login-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: all 0.2s ease;
}

.login-submit-btn:hover:not(:disabled) {
  background-color: #26352c;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.2);
}

.login-submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
}

.footer-hint {
  font-size: 0.72rem;
  color: #a89f91;
  line-height: 1.4;
  margin: 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
