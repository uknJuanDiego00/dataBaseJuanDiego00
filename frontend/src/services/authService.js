import api from './api'

export const authService = {
  /**
   * Inicia sesión utilizando el flujo estándar OAuth2 Password Flow.
   * Envía x-www-form-urlencoded con `username` y `password`.
   */
  async login(email, password) {
    const params = new URLSearchParams()
    params.append('username', email.trim().toLowerCase())
    params.append('password', password)

    const response = await api.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  /**
   * Obtiene la información del usuario autenticado actual.
   */
  async getMe() {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },

  /**
   * Renueva el access_token utilizando el refresh_token.
   */
  async refresh(refreshToken) {
    const response = await api.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  /**
   * Cierra sesión revocando el refresh token en backend.
   */
  async logout(refreshToken) {
    if (!refreshToken) return
    try {
      await api.post('/api/v1/auth/logout', {
        refresh_token: refreshToken
      })
    } catch {
      // Ignorar errores de red en logout
    }
  },

  /**
   * Cambia la contraseña del usuario en sesión.
   */
  async cambiarPassword(passwordActual, passwordNueva, passwordConfirmacion) {
    const response = await api.patch('/api/v1/auth/me/password', {
      password_actual: passwordActual,
      password_nueva: passwordNueva,
      password_nueva_confirmacion: passwordConfirmacion
    })
    return response.data
  }
}
