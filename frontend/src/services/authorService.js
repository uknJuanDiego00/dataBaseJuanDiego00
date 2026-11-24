import api from './api'

export const authorService = {
  /**
   * Obtiene la lista paginada de autores con filtro opcional por nacionalidad.
   */
  async getAuthors(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.nacionalidad) cleanParams.nacionalidad = params.nacionalidad.trim()

    const response = await api.get('/api/v1/autores', { params: cleanParams })
    return response.data
  },

  /**
   * Obtiene el detalle de un autor por su ID.
   */
  async getAuthor(id) {
    const response = await api.get(`/api/v1/autores/${id}`)
    return response.data
  },

  /**
   * Obtiene los libros vinculados a un autor específico.
   */
  async getAuthorBooks(id, params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit

    const response = await api.get(`/api/v1/autores/${id}/libros`, { params: cleanParams })
    return response.data
  },

  /**
   * Registra un nuevo autor.
   */
  async createAuthor(data) {
    const payload = {
      nombre: data.nombre.trim(),
      nacionalidad: data.nacionalidad ? data.nacionalidad.trim() : null,
      anio_nacimiento: data.anio_nacimiento ? Number(data.anio_nacimiento) : null
    }
    const response = await api.post('/api/v1/autores', payload)
    return response.data
  },

  /**
   * Actualiza los datos de un autor existente.
   */
  async updateAuthor(id, data) {
    const payload = {}
    if (data.nombre !== undefined) payload.nombre = data.nombre.trim()
    if (data.nacionalidad !== undefined) payload.nacionalidad = data.nacionalidad ? data.nacionalidad.trim() : null
    if (data.anio_nacimiento !== undefined) payload.anio_nacimiento = data.anio_nacimiento ? Number(data.anio_nacimiento) : null

    const response = await api.patch(`/api/v1/autores/${id}`, payload)
    return response.data
  },

  /**
   * Elimina un autor si no tiene libros asociados.
   */
  async deleteAuthor(id) {
    await api.delete(`/api/v1/autores/${id}`)
    return true
  }
}
