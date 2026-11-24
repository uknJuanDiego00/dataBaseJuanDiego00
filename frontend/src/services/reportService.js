import api from './api'

export const reportService = {
  /**
   * Resumen cuantitativo global de la biblioteca.
   */
  async getSummary() {
    const response = await api.get('/api/v1/reportes/resumen')
    return response.data
  },

  /**
   * Libros con mayor número de préstamos.
   */
  async getMostBorrowedBooks(limit = 5) {
    const response = await api.get('/api/v1/reportes/libros-mas-prestados', {
      params: { limite: limit }
    })
    return response.data
  },

  /**
   * Total de libros agrupados por categoría.
   */
  async getCategoriesReport() {
    const response = await api.get('/api/v1/reportes/categorias')
    return response.data
  },

  /**
   * Lista detallada de préstamos vencidos no devueltos.
   */
  async getOverdueLoans() {
    const response = await api.get('/api/v1/reportes/prestamos-vencidos')
    return response.data
  },

  /**
   * Lista de socios con multas acumuladas.
   */
  async getMembersWithFines() {
    const response = await api.get('/api/v1/reportes/socios-con-multas')
    return response.data
  },

  /**
   * Estadísticas de producción y préstamos por autor.
   */
  async getAuthorsReport() {
    const response = await api.get('/api/v1/reportes/autores')
    return response.data
  }
}
