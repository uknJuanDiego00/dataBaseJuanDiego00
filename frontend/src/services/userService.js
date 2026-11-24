import api from './api'

export const userService = {
  /**
   * Obtiene la lista paginada de usuarios (Requiere rol Admin).
   */
  async getUsers(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.rol) cleanParams.rol = params.rol
    if (params.activo !== undefined && params.activo !== null && params.activo !== '') {
      cleanParams.activo = params.activo
    }

    const response = await api.get('/api/v1/usuarios', { params: cleanParams })
    return response.data
  },

  /**
   * Crea un nuevo usuario en el sistema con un rol específico.
   */
  async createUser(data) {
    const payload = {
      email: data.email.trim().toLowerCase(),
      nombre: data.nombre.trim(),
      password: data.password,
      password_confirmacion: data.password_confirmacion,
      rol: data.rol || 'socio'
    }
    const response = await api.post('/api/v1/usuarios', payload)
    return response.data
  },

  /**
   * Actualiza el rol de un usuario.
   */
  async updateRole(id, rol) {
    const response = await api.patch(`/api/v1/usuarios/${id}/rol`, { rol })
    return response.data
  },

  /**
   * Activa o desactiva la cuenta de un usuario.
   */
  async updateActive(id, activo) {
    const response = await api.patch(`/api/v1/usuarios/${id}/activo`, { activo: Boolean(activo) })
    return response.data
  }
}
