import { ref, computed } from 'vue'
import { authService } from '../services/authService'

const user = ref(JSON.parse(localStorage.getItem('serenidad_user') || 'null'))
const token = ref(localStorage.getItem('serenidad_access_token') || null)
const loading = ref(false)
const error = ref(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.rol === 'admin')
  const isBibliotecario = computed(() => user.value?.rol === 'bibliotecario' || user.value?.rol === 'admin')
  const userRole = computed(() => user.value?.rol || 'visitante')
  const userName = computed(() => user.value?.nombre || 'Usuario')
  const userEmail = computed(() => user.value?.email || '')

  const login = async (email, password) => {
    loading.value = true
    error.value = null
    try {
      const tokenData = await authService.login(email, password)
      token.value = tokenData.access_token
      localStorage.setItem('serenidad_access_token', tokenData.access_token)
      if (tokenData.refresh_token) {
        localStorage.setItem('serenidad_refresh_token', tokenData.refresh_token)
      }

      // Obtener datos del perfil con el token recién guardado
      const userData = await authService.getMe()
      user.value = userData
      localStorage.setItem('serenidad_user', JSON.stringify(userData))

      return userData
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.'
      error.value = detail
      throw new Error(detail)
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    const refreshToken = localStorage.getItem('serenidad_refresh_token')
    try {
      if (refreshToken) {
        await authService.logout(refreshToken)
      }
    } catch {
      // Ignorar errores en logout
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('serenidad_access_token')
      localStorage.removeItem('serenidad_refresh_token')
      localStorage.removeItem('serenidad_user')
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return null
    try {
      const userData = await authService.getMe()
      user.value = userData
      localStorage.setItem('serenidad_user', JSON.stringify(userData))
      return userData
    } catch {
      logout()
      return null
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isBibliotecario,
    userRole,
    userName,
    userEmail,
    login,
    logout,
    fetchCurrentUser
  }
}
