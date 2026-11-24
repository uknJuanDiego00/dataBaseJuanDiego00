import api from './api'

export const memberService = {
  /**
   * Obtiene la lista paginada de socios con filtro opcional por estado activo.
   */
  async getMembers(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.activo !== undefined && params.activo !== null && params.activo !== '') {
      cleanParams.activo = params.activo
    }

    const response = await api.get('/api/v1/socios', { params: cleanParams })
    return response.data
  },

  /**
   * Obtiene la información detallada de un socio por ID.
   */
  async getMember(id) {
    const response = await api.get(`/api/v1/socios/${id}`)
    return response.data
  },

  /**
   * Registra un nuevo socio.
   */
  async createMember(data) {
    const payload = {
      nombre: data.nombre.trim(),
      email: data.email.trim().toLowerCase(),
      telefono: data.telefono ? data.telefono.trim() : null,
      activo: data.activo !== undefined ? Boolean(data.activo) : true
    }
    const response = await api.post('/api/v1/socios', payload)
    return response.data
  },

  /**
   * Actualiza los datos de un socio existente.
   */
  async updateMember(id, data) {
    const payload = {}
    if (data.nombre !== undefined) payload.nombre = data.nombre.trim()
    if (data.email !== undefined) payload.email = data.email.trim().toLowerCase()
    if (data.telefono !== undefined) payload.telefono = data.telefono ? data.telefono.trim() : null
    if (data.activo !== undefined) payload.activo = Boolean(data.activo)

    const response = await api.patch(`/api/v1/socios/${id}`, payload)
    return response.data
  },

  /**
   * Elimina o desactiva un socio.
   */
  async deleteMember(id) {
    await api.delete(`/api/v1/socios/${id}`)
    return true
  },

  /**
   * Consulta el historial de préstamos de un socio.
   */
  async getMemberLoans(id, params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.estado) cleanParams.estado = params.estado

    const response = await api.get(`/api/v1/socios/${id}/prestamos`, { params: cleanParams })
    return response.data
  }
}
