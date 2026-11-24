import api from './api'

export const loanService = {
  /**
   * Obtiene la lista paginada de préstamos con filtros opcionales.
   */
  async getLoans(params = {}) {
    const cleanParams = {}
    if (params.skip !== undefined) cleanParams.skip = params.skip
    if (params.limit !== undefined) cleanParams.limit = params.limit
    if (params.estado) cleanParams.estado = params.estado
    if (params.socio_id) cleanParams.socio_id = params.socio_id
    if (params.libro_id) cleanParams.libro_id = params.libro_id

    const response = await api.get('/api/v1/prestamos', { params: cleanParams })
    return response.data
  },

  /**
   * Obtiene el detalle de un préstamo por su ID.
   */
  async getLoan(id) {
    const response = await api.get(`/api/v1/prestamos/${id}`)
    return response.data
  },

  /**
   * Registra un nuevo préstamo.
   */
  async createLoan(data) {
    const payload = {
      libro_id: Number(data.libro_id),
      socio_id: Number(data.socio_id),
      dias: data.dias ? Number(data.dias) : 14
    }
    if (data.fecha_prestamo) {
      payload.fecha_prestamo = data.fecha_prestamo
    }
    const response = await api.post('/api/v1/prestamos', payload)
    return response.data
  },

  /**
   * Registra la devolución de un préstamo.
   */
  async returnLoan(id, fechaDevolucion = null) {
    const payload = {}
    if (fechaDevolucion) {
      payload.fecha_devolucion = fechaDevolucion
    }
    const response = await api.post(`/api/v1/prestamos/${id}/devolucion`, payload)
    return response.data
  },

  /**
   * Registra el pago de una multa pendiente.
   */
  async payFine(id) {
    const response = await api.post(`/api/v1/prestamos/${id}/pago-multa`)
    return response.data
  }
}
