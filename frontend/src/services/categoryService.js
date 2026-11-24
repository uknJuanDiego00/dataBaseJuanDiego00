import api from './api'

export const categoryService = {
  /**
   * Obtiene la lista paginada de categorías.
   */
  async getCategories(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit

    const response = await api.get('/api/v1/categorias', { params: cleanParams })
    return response.data
  },

  /**
   * Obtiene el detalle de una categoría por su ID.
   */
  async getCategory(id) {
    const response = await api.get(`/api/v1/categorias/${id}`)
    return response.data
  },

  /**
   * Crea una nueva categoría.
   */
  async createCategory(data) {
    const payload = {
      nombre: data.nombre.trim().toLowerCase(),
      descripcion: data.descripcion ? data.descripcion.trim() : null
    }
    const response = await api.post('/api/v1/categorias', payload)
    return response.data
  },

  /**
   * Actualiza los datos de una categoría existente.
   */
  async updateCategory(id, data) {
    const payload = {}
    if (data.nombre !== undefined) payload.nombre = data.nombre.trim().toLowerCase()
    if (data.descripcion !== undefined) payload.descripcion = data.descripcion ? data.descripcion.trim() : null

    const response = await api.patch(`/api/v1/categorias/${id}`, payload)
    return response.data
  },

  /**
   * Elimina una categoría si no tiene libros asociados.
   */
  async deleteCategory(id) {
    await api.delete(`/api/v1/categorias/${id}`)
    return true
  }
}
