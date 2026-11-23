<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminStatCard from '../../components/admin/AdminStatCard.vue'
import { reportService } from '../../services/reportService'
import { bookService } from '../../services/bookService'
import { authorService } from '../../services/authorService'
import { categoryService } from '../../services/categoryService'
import { loanService } from '../../services/loanService'
import { memberService } from '../../services/memberService'
import { userService } from '../../services/userService'
import { useAuth } from '../../composables/useAuth'
import {
  BookOpen,
  Feather,
  Tags,
  Users,
  Clock,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  Plus,
  ArrowRight,
  TrendingUp,
  Loader2,
  Calendar
} from 'lucide-vue-next'

const router = useRouter()
const { isAdmin } = useAuth()

const loading = ref(true)
const error = ref(null)

const stats = ref({
  totalLibros: 0,
  totalEjemplares: 0,
  prestamosActivos: 0,
  prestamosDevueltos: 0,
  prestamosVencidos: 0,
  totalSocios: 0,
  sociosActivos: 0,
  totalAutores: 0,
  totalCategorias: 0,
  totalUsuarios: 0,
  totalMultas: '0.00'
})

const topBooks = ref([])
const overdueLoans = ref([])
const recentLoans = ref([])

const loadDashboardData = async () => {
  loading.value = true
  error.value = null

  try {
    const [
      resumenRes,
      autoresRes,
      categoriasRes,
      sociosRes,
      prestamosActivosRes,
      prestamosDevueltosRes,
      topBooksRes,
      overdueLoansRes,
      recentLoansRes,
      usuariosRes
    ] = await Promise.allSettled([
      reportService.getSummary(),
      authorService.getAuthors({ limit: 1 }),
      categoryService.getCategories({ limit: 1 }),
      memberService.getMembers({ limit: 1 }),
      loanService.getLoans({ limit: 1, estado: 'activo' }),
      loanService.getLoans({ limit: 1, estado: 'devuelto' }),
      reportService.getMostBorrowedBooks(5),
      reportService.getOverdueLoans(),
      loanService.getLoans({ limit: 5 }),
      isAdmin.value ? userService.getUsers({ limit: 1 }) : Promise.resolve({ total: 0 })
    ])

    if (resumenRes.status === 'fulfilled') {
      const r = resumenRes.value
      stats.value.totalLibros = r.total_libros ?? 0
      stats.value.totalEjemplares = r.total_ejemplares ?? 0
      stats.value.sociosActivos = r.socios_activos ?? 0
      stats.value.prestamosVencidos = r.prestamos_vencidos ?? 0
      stats.value.totalMultas = r.total_multas ? Number(r.total_multas).toFixed(2) : '0.00'
    }

    if (autoresRes.status === 'fulfilled') {
      stats.value.totalAutores = autoresRes.value.total ?? 0
    }

    if (categoriasRes.status === 'fulfilled') {
      stats.value.totalCategorias = categoriasRes.value.total ?? 0
    }

    if (sociosRes.status === 'fulfilled') {
      stats.value.totalSocios = sociosRes.value.total ?? 0
    }

    if (prestamosActivosRes.status === 'fulfilled') {
      stats.value.prestamosActivos = prestamosActivosRes.value.total ?? 0
    }

    if (prestamosDevueltosRes.status === 'fulfilled') {
      stats.value.prestamosDevueltos = prestamosDevueltosRes.value.total ?? 0
    }

    if (usuariosRes.status === 'fulfilled') {
      stats.value.totalUsuarios = usuariosRes.value.total ?? 0
    }

    if (topBooksRes.status === 'fulfilled') {
      topBooks.value = topBooksRes.value || []
    }

    if (overdueLoansRes.status === 'fulfilled') {
      overdueLoans.value = overdueLoansRes.value || []
    }

    if (recentLoansRes.status === 'fulfilled') {
      recentLoans.value = recentLoansRes.value.items || []
    }
  } catch (err) {
    error.value = 'No fue posible cargar todas las métricas en tiempo real.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<template>
  <div class="admin-dashboard-view">
    <!-- Barra Superior de Acciones Rápidas -->
    <div class="dashboard-header-bar">
      <div>
        <h2 class="view-title">Cuadro de Mando General</h2>
        <p class="view-subtitle">Indicadores cuantitativos y estado operativo en tiempo real</p>
      </div>

      <div class="action-buttons-group">
        <button class="action-btn" @click="router.push('/admin/prestamos')">
          <Plus :size="16" />
          <span>Registrar Préstamo</span>
        </button>
        <button class="action-btn action-btn-secondary" @click="router.push('/admin/libros')">
          <BookOpen :size="16" />
          <span>Nuevo Libro</span>
        </button>
      </div>
    </div>

    <!-- Indicador de Carga General -->
    <div v-if="loading" class="dashboard-loader-state">
      <Loader2 :size="32" class="spin-icon" />
      <span>Consultando datos reales de PostgreSQL...</span>
    </div>

    <div v-else class="dashboard-content-grid">
      <!-- Malla de Tarjetas de Indicadores Clave -->
      <div class="stats-grid">
        <AdminStatCard
          title="Títulos de Libros"
          :value="stats.totalLibros"
          :subtitle="`${stats.totalEjemplares} ejemplares en inventario`"
          variant="forest"
        >
          <template #icon><BookOpen :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Préstamos Activos"
          :value="stats.prestamosActivos"
          subtitle="En manos de lectores"
          variant="gold"
        >
          <template #icon><Clock :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Préstamos Vencidos"
          :value="stats.prestamosVencidos"
          subtitle="Requieren seguimiento"
          variant="wine"
        >
          <template #icon><AlertTriangle :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Préstamos Devueltos"
          :value="stats.prestamosDevueltos"
          subtitle="Operaciones finalizadas"
          variant="emerald"
        >
          <template #icon><CheckCircle2 :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Socios Registrados"
          :value="stats.totalSocios"
          :subtitle="`${stats.sociosActivos} socios activos`"
          variant="forest"
        >
          <template #icon><Users :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Autores"
          :value="stats.totalAutores"
          subtitle="Creadores literarios"
          variant="amber"
        >
          <template #icon><Feather :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Categorías"
          :value="stats.totalCategorias"
          subtitle="Colecciones temáticas"
          variant="gold"
        >
          <template #icon><Tags :size="22" /></template>
        </AdminStatCard>

        <AdminStatCard
          title="Multas Pendientes"
          :value="`$${stats.totalMultas}`"
          subtitle="Acumuladas por retraso"
          variant="wine"
        >
          <template #icon><DollarSign :size="22" /></template>
        </AdminStatCard>
      </div>

      <!-- Sección de Análisis Operativo -->
      <div class="dashboard-widgets-row">
        <!-- Libros Más Solicitados -->
        <div class="dashboard-widget-card">
          <div class="widget-header">
            <div class="widget-title-group">
              <TrendingUp :size="18" class="widget-icon" />
              <h3 class="widget-title">Libros Más Prestados</h3>
            </div>
            <router-link to="/admin/reportes" class="widget-link">
              <span>Ver reporte completo</span>
              <ArrowRight :size="14" />
            </router-link>
          </div>

          <div class="widget-body">
            <div v-if="topBooks.length === 0" class="empty-widget-msg">
              Aún no se registran préstamos para calcular esta métrica.
            </div>
            <ul v-else class="top-books-list">
              <li v-for="(book, idx) in topBooks" :key="book.libro_id" class="top-book-item">
                <span class="ranking-badge">{{ idx + 1 }}</span>
                <div class="book-info-col">
                  <span class="book-title">{{ book.titulo }}</span>
                  <span class="book-author">{{ book.autor }}</span>
                </div>
                <div class="book-borrow-count">
                  <span class="count-number">{{ book.total_prestamos }}</span>
                  <span class="count-label">préstamos</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Alertas de Préstamos Vencidos -->
        <div class="dashboard-widget-card">
          <div class="widget-header">
            <div class="widget-title-group">
              <AlertTriangle :size="18" class="widget-icon warning" />
              <h3 class="widget-title">Préstamos Vencidos</h3>
            </div>
            <router-link to="/admin/prestamos" class="widget-link">
              <span>Gestionar</span>
              <ArrowRight :size="14" />
            </router-link>
          </div>

          <div class="widget-body">
            <div v-if="overdueLoans.length === 0" class="clean-state-box">
              <CheckCircle2 :size="24" class="clean-icon" />
              <span>No hay préstamos con retraso pendiente en este momento.</span>
            </div>
            <div v-else class="overdue-table-wrapper">
              <table class="mini-table">
                <thead>
                  <tr>
                    <th>Libro</th>
                    <th>Socio</th>
                    <th>Retraso</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="loan in overdueLoans.slice(0, 5)" :key="loan.prestamo_id">
                    <td class="font-medium">{{ loan.titulo }}</td>
                    <td>{{ loan.socio }}</td>
                    <td>
                      <span class="overdue-tag">{{ loan.dias_retraso }} días</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Actividad Reciente de Préstamos -->
      <div class="dashboard-widget-card full-width">
        <div class="widget-header">
          <div class="widget-title-group">
            <Calendar :size="18" class="widget-icon" />
            <h3 class="widget-title">Actividad Reciente en Préstamos</h3>
          </div>
          <router-link to="/admin/prestamos" class="widget-link">
            <span>Ver todos los préstamos</span>
            <ArrowRight :size="14" />
          </router-link>
        </div>

        <div class="widget-body">
          <div v-if="recentLoans.length === 0" class="empty-widget-msg">
            No se han registrado préstamos recientes.
          </div>
          <div v-else class="overdue-table-wrapper">
            <table class="mini-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Libro</th>
                  <th>Socio</th>
                  <th>Fecha Préstamo</th>
                  <th>Fecha Límite</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="loan in recentLoans" :key="loan.id">
                  <td>#{{ loan.id }}</td>
                  <td class="font-medium">{{ loan.libro?.titulo || `Libro #${loan.libro_id}` }}</td>
                  <td>{{ loan.socio?.nombre || `Socio #${loan.socio_id}` }}</td>
                  <td>{{ loan.fecha_prestamo }}</td>
                  <td>{{ loan.fecha_limite }}</td>
                  <td>
                    <span class="status-pill" :class="loan.estado">{{ loan.estado }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.dashboard-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.view-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.view-subtitle {
  font-size: 0.82rem;
  color: #7a7062;
  margin: 0.2rem 0 0 0;
}

.action-buttons-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.action-btn {
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

.action-btn:hover {
  background-color: #26352c;
  box-shadow: 0 4px 10px rgba(52, 72, 61, 0.15);
}

.action-btn-secondary {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  color: var(--color-forest, #34483D);
}

.action-btn-secondary:hover {
  background-color: var(--color-ivory, #F5F2E9);
  color: #a4763c;
  border-color: var(--color-gold, #C49A62);
}

.dashboard-loader-state {
  padding: 4rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: #7a7062;
  font-size: 0.9rem;
}

.spin-icon {
  animation: spin 1s linear infinite;
  color: var(--color-gold, #C49A62);
}

.dashboard-content-grid {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.dashboard-widgets-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

@media (max-width: 960px) {
  .dashboard-widgets-row {
    grid-template-columns: 1fr;
  }
}

.dashboard-widget-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1.35rem 1.5rem;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.03);
}

.dashboard-widget-card.full-width {
  width: 100%;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #ECE7DC;
}

.widget-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.widget-icon {
  color: var(--color-gold, #C49A62);
}

.widget-icon.warning {
  color: #dc2626;
}

.widget-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.widget-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-gold, #C49A62);
  text-decoration: none;
  transition: color 0.15s ease;
}

.widget-link:hover {
  color: #a4763c;
}

.empty-widget-msg {
  padding: 1.5rem 0;
  text-align: center;
  font-size: 0.85rem;
  color: #8c8273;
}

.clean-state-box {
  padding: 1.75rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
  color: #059669;
  font-size: 0.85rem;
}

.top-books-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.top-book-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  background-color: #FAF8F2;
  transition: background-color 0.15s ease;
}

.top-book-item:hover {
  background-color: #F4EFE6;
}

.ranking-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background-color: var(--color-forest, #34483D);
  color: var(--color-gold, #C49A62);
  font-weight: 700;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.book-info-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-author {
  font-size: 0.72rem;
  color: #7a7062;
}

.book-borrow-count {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.count-number {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--color-forest, #34483D);
}

.count-label {
  font-size: 0.68rem;
  color: #8c8273;
}

.overdue-table-wrapper {
  overflow-x: auto;
}

.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  text-align: left;
}

.mini-table th {
  padding: 0.5rem 0.65rem;
  color: #7a7062;
  font-weight: 600;
  border-bottom: 1px solid #ECE7DC;
}

.mini-table td {
  padding: 0.65rem;
  border-bottom: 1px solid #F5F2E9;
  color: var(--color-forest, #34483D);
}

.font-medium {
  font-weight: 600;
}

.overdue-tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #dc2626;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.72rem;
}

.status-pill {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-pill.activo {
  background-color: #ecfdf5;
  color: #059669;
}

.status-pill.vencido {
  background-color: #fef2f2;
  color: #dc2626;
}

.status-pill.devuelto {
  background-color: #f3f4f6;
  color: #4b5563;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
