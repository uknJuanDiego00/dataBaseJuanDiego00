import api from './api'

export const bookService = {
  /**
   * Obtiene la lista de libros con filtros y paginación.
   */
  async getBooks(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.buscar) cleanParams.buscar = params.buscar.trim()
    if (params.autor) cleanParams.autor = params.autor.trim()
    if (params.categoria_id) cleanParams.categoria_id = params.categoria_id
    if (params.desde) cleanParams.desde = params.desde
    if (params.hasta) cleanParams.hasta = params.hasta
    if (params.orden) cleanParams.orden = params.orden

    const response = await api.get('/api/v1/libros', { params: cleanParams })
    return response.data
  },

  /**
   * Consulta un libro por su ID.
   */
  async getBook(id) {
    const response = await api.get(`/api/v1/libros/${id}`)
    return response.data
  },

  /**
   * Crea un nuevo libro en el catálogo.
   */
  async createBook(data) {
    const payload = {
      titulo: data.titulo.trim(),
      isbn: data.isbn.trim(),
      anio_publicacion: Number(data.anio_publicacion),
      ejemplares: Number(data.ejemplares),
      autor_id: Number(data.autor_id),
      categoria_ids: data.categoria_ids.map(Number),
      portada_url: data.portada_url || null
    }
    const response = await api.post('/api/v1/libros', payload)
    return response.data
  },

  /**
   * Actualiza los datos de un libro existente.
   */
  async updateBook(id, data) {
    const payload = {}
    if (data.titulo !== undefined) payload.titulo = data.titulo.trim()
    if (data.isbn !== undefined) payload.isbn = data.isbn.trim()
    if (data.anio_publicacion !== undefined) payload.anio_publicacion = Number(data.anio_publicacion)
    if (data.ejemplares !== undefined) payload.ejemplares = Number(data.ejemplares)
    if (data.autor_id !== undefined) payload.autor_id = Number(data.autor_id)
    if (data.categoria_ids !== undefined) payload.categoria_ids = data.categoria_ids.map(Number)
    if (data.portada_url !== undefined) payload.portada_url = data.portada_url || null

    const response = await api.patch(`/api/v1/libros/${id}`, payload)
    return response.data
  },

  /**
   * Elimina un libro del catálogo si no tiene préstamos activos.
   */
  async deleteBook(id) {
    await api.delete(`/api/v1/libros/${id}`)
    return true
  },

  /**
   * Sube una imagen de portada directamente a Cloudinary a través del backend.
   */
  async uploadCover(id, file) {
    const formData = new FormData()
    formData.append('archivo', file)

    const response = await api.post(`/api/v1/libros/${id}/portada`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}
