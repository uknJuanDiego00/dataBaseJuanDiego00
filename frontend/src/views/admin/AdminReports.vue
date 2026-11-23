<script setup>
import { ref, onMounted } from 'vue'
import { reportService } from '../../services/reportService'
import {
  BarChart3,
  BookOpen,
  AlertTriangle,
  DollarSign,
  Tags,
  Feather,
  Download,
  Loader2,
  RefreshCw,
  CheckCircle2
} from 'lucide-vue-next'

const activeTab = ref('libros') // 'libros', 'vencidos', 'multas', 'categorias', 'autores'
const loading = ref(false)
const booksLimit = ref(10)

// Datos de reportes
const mostBorrowed = ref([])
const overdueLoans = ref([])
const membersWithFines = ref([])
const categoryDistribution = ref([])
const authorStats = ref([])

const loadReportData = async () => {
  loading.value = true
  try {
    const [borrowedRes, overdueRes, finesRes, catRes, authRes] = await Promise.allSettled([
      reportService.getMostBorrowedBooks(booksLimit.value),
      reportService.getOverdueLoans(),
      reportService.getMembersWithFines(),
      reportService.getCategoriesReport(),
      reportService.getAuthorsReport()
    ])

    if (borrowedRes.status === 'fulfilled') mostBorrowed.value = borrowedRes.value || []
    if (overdueRes.status === 'fulfilled') overdueLoans.value = overdueRes.value || []
    if (finesRes.status === 'fulfilled') membersWithFines.value = finesRes.value || []
    if (catRes.status === 'fulfilled') categoryDistribution.value = catRes.value || []
    if (authRes.status === 'fulfilled') authorStats.value = authRes.value || []
  } catch (err) {
    console.error('Error al consultar reportes:', err)
  } finally {
    loading.value = false
  }
}

// Función de exportación a CSV
const exportToCsv = (filename, rows) => {
  if (!rows || !rows.length) return
  const separator = ','
  const keys = Object.keys(rows[0])
  const csvContent =
    keys.join(separator) +
    '\n' +
    rows.map(row => {
      return keys.map(k => {
        let cell = row[k] === null || row[k] === undefined ? '' : row[k]
        cell = cell instanceof Date ? cell.toLocaleString() : cell.toString().replace(/"/g, '""')
        if (cell.search(/("|,|\n)/g) >= 0) cell = `"${cell}"`
        return cell
      }).join(separator)
    }).join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleExportCurrentTab = () => {
  switch (activeTab.value) {
    case 'libros':
      exportToCsv('libros_mas_prestados', mostBorrowed.value)
      break
    case 'vencidos':
      exportToCsv('prestamos_vencidos', overdueLoans.value)
      break
    case 'multas':
      exportToCsv('socios_con_multas', membersWithFines.value)
      break
    case 'categorias':
      exportToCsv('distribucion_categorias', categoryDistribution.value)
      break
    case 'autores':
      exportToCsv('estadisticas_autores', authorStats.value)
      break
  }
}

onMounted(() => {
  loadReportData()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Centro de Analítica e Inteligencia Bibliotecaria</h2>
        <p class="module-subtitle">Consulta estadísticas de circulación, cobranza de multas, inventario temático y desempeño</p>
      </div>

      <div class="header-action-cluster">
        <button class="secondary-action-btn" :disabled="loading" @click="loadReportData">
          <RefreshCw :size="15" :class="{ 'spin-icon': loading }" />
          <span>Actualizar</span>
        </button>
        <button class="primary-action-btn" :disabled="loading" @click="handleExportCurrentTab">
          <Download :size="16" />
          <span>Exportar a CSV</span>
        </button>
      </div>
    </div>

    <!-- Navegación por pestañas de reportes -->
    <div class="report-tabs-bar">
      <button
        class="tab-btn"
        :class="{ 'is-active': activeTab === 'libros' }"
        @click="activeTab = 'libros'"
      >
        <BookOpen :size="16" />
        <span>Más Prestados ({{ mostBorrowed.length }})</span>
      </button>

      <button
        class="tab-btn"
        :class="{ 'is-active': activeTab === 'vencidos' }"
        @click="activeTab = 'vencidos'"
      >
        <AlertTriangle :size="16" />
        <span>Préstamos Vencidos ({{ overdueLoans.length }})</span>
      </button>

      <button
        class="tab-btn"
        :class="{ 'is-active': activeTab === 'multas' }"
        @click="activeTab = 'multas'"
      >
        <DollarSign :size="16" />
        <span>Socios con Multas ({{ membersWithFines.length }})</span>
      </button>

      <button
        class="tab-btn"
        :class="{ 'is-active': activeTab === 'categorias' }"
        @click="activeTab = 'categorias'"
      >
        <Tags :size="16" />
        <span>Por Categorías ({{ categoryDistribution.length }})</span>
      </button>

      <button
        class="tab-btn"
        :class="{ 'is-active': activeTab === 'autores' }"
        @click="activeTab = 'autores'"
      >
        <Feather :size="16" />
        <span>Por Autores ({{ authorStats.length }})</span>
      </button>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="reports-loading-box">
      <Loader2 :size="32" class="spin-icon" />
      <span>Consultando agregaciones analíticas de la base de datos...</span>
    </div>

    <!-- Contenido de las Pestañas -->
    <div v-else class="report-tab-body">
      <!-- 1. LIBROS MÁS PRESTADOS -->
      <div v-if="activeTab === 'libros'" class="report-card">
        <div class="report-card-header">
          <h3 class="card-title">Ranking de Libros con Mayor Demanda</h3>
          <div class="limit-selector-box">
            <label class="limit-label">Mostrar top:</label>
            <select v-model="booksLimit" class="limit-select" @change="loadReportData">
              <option :value="5">5 libros</option>
              <option :value="10">10 libros</option>
              <option :value="20">20 libros</option>
            </select>
          </div>
        </div>

        <div v-if="mostBorrowed.length === 0" class="no-data-notice">
          No hay registros de préstamos disponibles para tabular esta estadística.
        </div>
        <div v-else class="table-wrapper">
          <table class="report-table">
            <thead>
              <tr>
                <th style="width: 70px;">Puesto</th>
                <th>Título del Libro</th>
                <th>Autor</th>
                <th style="text-align: right;">Total Préstamos</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in mostBorrowed" :key="item.libro_id">
                <td>
                  <span class="rank-circle">{{ index + 1 }}</span>
                </td>
                <td class="font-bold">{{ item.titulo }}</td>
                <td>{{ item.autor }}</td>
                <td style="text-align: right;">
                  <span class="metric-pill">{{ item.total_prestamos }} solicitudes</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 2. PRÉSTAMOS VENCIDOS -->
      <div v-else-if="activeTab === 'vencidos'" class="report-card">
        <div class="report-card-header">
          <h3 class="card-title">Detalle de Préstamos Vencidos No Devueltos</h3>
          <span class="card-counter-tag">{{ overdueLoans.length }} préstamos con mora</span>
        </div>

        <div v-if="overdueLoans.length === 0" class="clean-box">
          <CheckCircle2 :size="28" class="clean-icon" />
          <p>¡Excelente! Todos los préstamos se encuentran dentro del plazo o devueltos.</p>
        </div>
        <div v-else class="table-wrapper">
          <table class="report-table">
            <thead>
              <tr>
                <th>Préstamo</th>
                <th>Libro Solicitado</th>
                <th>Socio Titular</th>
                <th>Correo</th>
                <th>Fecha Límite</th>
                <th style="text-align: right;">Días de Retraso</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in overdueLoans" :key="item.prestamo_id">
                <td>#{{ item.prestamo_id }}</td>
                <td class="font-bold">{{ item.titulo }}</td>
                <td>{{ item.socio }}</td>
                <td class="text-muted">{{ item.email }}</td>
                <td>{{ item.fecha_limite }}</td>
                <td style="text-align: right;">
                  <span class="danger-tag">{{ item.dias_retraso }} días</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 3. SOCIOS CON MULTAS -->
      <div v-else-if="activeTab === 'multas'" class="report-card">
        <div class="report-card-header">
          <h3 class="card-title">Consolidado de Socios con Sanciones Económicas</h3>
          <span class="card-counter-tag">{{ membersWithFines.length }} socios registrados</span>
        </div>

        <div v-if="membersWithFines.length === 0" class="clean-box">
          <CheckCircle2 :size="28" class="clean-icon" />
          <p>No hay socios con multas acumuladas en el sistema.</p>
        </div>
        <div v-else class="table-wrapper">
          <table class="report-table">
            <thead>
              <tr>
                <th>ID Socio</th>
                <th>Nombre del Lector</th>
                <th>Correo Electrónico</th>
                <th>Préstamos Sancionados</th>
                <th style="text-align: right;">Multa Total Acumulada</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in membersWithFines" :key="item.socio_id">
                <td>#{{ item.socio_id }}</td>
                <td class="font-bold">{{ item.socio }}</td>
                <td class="text-muted">{{ item.email }}</td>
                <td>{{ item.prestamos_con_multa }} préstamo(s)</td>
                <td style="text-align: right;">
                  <span class="fine-total-badge">${{ Number(item.total_multas).toFixed(2) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. DISTRIBUCIÓN POR CATEGORÍAS -->
      <div v-else-if="activeTab === 'categorias'" class="report-card">
        <div class="report-card-header">
          <h3 class="card-title">Distribución del Fondo Editorial por Categoría</h3>
        </div>

        <div v-if="categoryDistribution.length === 0" class="no-data-notice">
          No hay datos de categorías disponibles.
        </div>
        <div v-else class="table-wrapper">
          <table class="report-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Categoría Temática</th>
                <th style="text-align: right;">Total de Libros</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in categoryDistribution" :key="item.categoria_id">
                <td>#{{ item.categoria_id }}</td>
                <td class="font-bold">{{ item.categoria }}</td>
                <td style="text-align: right;">
                  <span class="metric-pill">{{ item.total_libros }} libros</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 5. ESTADÍSTICAS POR AUTORES -->
      <div v-else-if="activeTab === 'autores'" class="report-card">
        <div class="report-card-header">
          <h3 class="card-title">Producción y Circulación por Autor</h3>
        </div>

        <div v-if="authorStats.length === 0" class="no-data-notice">
          No hay estadísticas registradas para autores.
        </div>
        <div v-else class="table-wrapper">
          <table class="report-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre del Autor</th>
                <th>Títulos en Catálogo</th>
                <th>Ejemplares Físicos</th>
                <th style="text-align: right;">Préstamos Históricos</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in authorStats" :key="item.autor_id">
                <td>#{{ item.autor_id }}</td>
                <td class="font-bold">{{ item.autor }}</td>
                <td>{{ item.total_libros }} obras</td>
                <td>{{ item.total_ejemplares }} ejemplares</td>
                <td style="text-align: right;">
                  <span class="metric-pill">{{ item.total_prestamos }} préstamos</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-module-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.module-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.module-subtitle {
  font-size: 0.8rem;
  color: #7a7062;
  margin: 0.2rem 0 0 0;
}

.header-action-cluster {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.primary-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1rem;
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.secondary-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 0.9rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  color: var(--color-forest, #34483D);
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.secondary-action-btn:hover {
  background-color: var(--color-ivory, #F5F2E9);
}

.report-tabs-bar {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 10px;
  padding: 0.35rem;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.9rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #7a7062;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background-color: var(--color-ivory, #F5F2E9);
  color: var(--color-forest, #34483D);
}

.tab-btn.is-active {
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
}

.reports-loading-box {
  padding: 4rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #7a7062;
  font-size: 0.9rem;
}

.report-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.03);
}

.report-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #ECE7DC;
}

.card-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.limit-selector-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.limit-label {
  font-size: 0.78rem;
  color: #7a7062;
}

.limit-select {
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.8rem;
  color: var(--color-forest, #34483D);
}

.card-counter-tag {
  font-size: 0.78rem;
  color: #b45309;
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 600;
}

.table-wrapper {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}

.report-table th {
  padding: 0.8rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #7a7062;
  background-color: #FAF8F2;
  border-bottom: 1px solid var(--color-border, #E5E0D4);
}

.report-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #F5F2E9;
  color: var(--color-forest, #34483D);
}

.font-bold {
  font-weight: 600;
}

.text-muted {
  color: #7a7062;
  font-size: 0.82rem;
}

.rank-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background-color: var(--color-forest, #34483D);
  color: var(--color-gold, #C49A62);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
}

.metric-pill {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.danger-tag {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 4px;
  color: #dc2626;
  font-size: 0.75rem;
  font-weight: 700;
}

.fine-total-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 14px;
  color: #dc2626;
  font-weight: 700;
  font-size: 0.85rem;
}

.clean-box {
  padding: 3rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
  color: #059669;
  font-size: 0.88rem;
}

.no-data-notice {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #8c8273;
  font-size: 0.88rem;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
