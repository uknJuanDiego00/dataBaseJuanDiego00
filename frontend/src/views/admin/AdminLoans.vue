<script setup>
import { ref, onMounted } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import { loanService } from '../../services/loanService'
import { bookService } from '../../services/bookService'
import { memberService } from '../../services/memberService'
import {
  Plus,
  Filter,
  CheckCircle,
  DollarSign,
  Clock,
  Calendar,
  AlertTriangle,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const loans = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

// Filtros
const filterStatus = ref('')
const filterMemberId = ref('')
const filterBookId = ref('')

// Listas maestras para formulario de préstamo
const booksList = ref([])
const membersList = ref([])

const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isCreateModalOpen = ref(false)
const isReturnModalOpen = ref(false)
const isFineModalOpen = ref(false)
const submitting = ref(false)

const targetLoan = ref(null)

// Formulario de nuevo préstamo
const form = ref({
  libro_id: '',
  socio_id: '',
  fecha_prestamo: new Date().toISOString().split('T')[0],
  dias: 14
})

// Fecha de devolución
const returnDate = ref(new Date().toISOString().split('T')[0])

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4500)
}

const loadMasters = async () => {
  try {
    const [booksRes, membersRes] = await Promise.all([
      bookService.getBooks({ limit: 100 }),
      memberService.getMembers({ limit: 100, activo: true })
    ])
    booksList.value = Array.isArray(booksRes) ? booksRes : (booksRes.items || [])
    membersList.value = membersRes.items || []
  } catch (err) {
    console.error('Error cargando maestros para préstamos:', err)
  }
}

const loadLoans = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }
    if (filterStatus.value) params.estado = filterStatus.value
    if (filterMemberId.value) params.socio_id = Number(filterMemberId.value)
    if (filterBookId.value) params.libro_id = Number(filterBookId.value)

    const res = await loanService.getLoans(params)
    loans.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar préstamos.', 'error')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  skip.value = 0
  loadLoans()
}

const handleClearFilter = () => {
  filterStatus.value = ''
  filterMemberId.value = ''
  filterBookId.value = ''
  skip.value = 0
  loadLoans()
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadLoans()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadLoans()
  }
}

const openCreateModal = () => {
  form.value = {
    libro_id: booksList.value.length ? booksList.value[0].id : '',
    socio_id: membersList.value.length ? membersList.value[0].id : '',
    fecha_prestamo: new Date().toISOString().split('T')[0],
    dias: 14
  }
  isCreateModalOpen.value = true
}

const submitCreateLoan = async () => {
  if (!form.value.libro_id || !form.value.socio_id) {
    showAlert('Selecciona el libro y el socio solicitante.', 'error')
    return
  }

  submitting.value = true
  try {
    await loanService.createLoan(form.value)
    showAlert('Préstamo registrado exitosamente.')
    isCreateModalOpen.value = false
    loadLoans()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No fue posible registrar el préstamo. Revisa si el socio tiene multas pendientes o cupo excedido.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Registrar Devolución
const openReturnModal = (loan) => {
  targetLoan.value = loan
  returnDate.value = new Date().toISOString().split('T')[0]
  isReturnModalOpen.value = true
}

const submitReturnLoan = async () => {
  submitting.value = true
  try {
    const res = await loanService.returnLoan(targetLoan.value.id, returnDate.value)
    if (res.multa && Number(res.multa) > 0) {
      showAlert(`Devolución registrada con multa de $${res.multa} por retraso.`, 'error')
    } else {
      showAlert('Devolución registrada a tiempo sin sanciones.')
    }
    isReturnModalOpen.value = false
    loadLoans()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al procesar la devolución.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Pagar Multa
const openFineModal = (loan) => {
  targetLoan.value = loan
  isFineModalOpen.value = true
}

const submitPayFine = async () => {
  submitting.value = true
  try {
    await loanService.payFine(targetLoan.value.id)
    showAlert('Multa saldada exitosamente.')
    isFineModalOpen.value = false
    loadLoans()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al registrar el pago de la multa.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMasters()
  loadLoans()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Préstamos y Devoluciones</h2>
        <p class="module-subtitle">Control de entregas, plazos de devolución, inventario en circulación y multas</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <Plus :size="16" />
        <span>Registrar Nuevo Préstamo</span>
      </button>
    </div>

    <!-- Alerta Flotante -->
    <div v-if="alertMsg.text" class="module-alert" :class="alertMsg.type">
      <CheckCircle2 v-if="alertMsg.type === 'success'" :size="18" />
      <AlertCircle v-else :size="18" />
      <span>{{ alertMsg.text }}</span>
    </div>

    <!-- Filtros -->
    <div class="filter-card">
      <div class="filter-inputs-grid">
        <div class="filter-field">
          <label class="filter-label">Estado del Préstamo</label>
          <select v-model="filterStatus" class="filter-select" @change="handleFilter">
            <option value="">Todos los estados</option>
            <option value="activo">Activos</option>
            <option value="vencido">Vencidos (Con retraso)</option>
            <option value="devuelto">Devueltos (Finalizados)</option>
          </select>
        </div>

        <div class="filter-actions">
          <button class="filter-btn" @click="handleFilter">
            <Filter :size="15" />
            <span>Filtrar</span>
          </button>
          <button class="clear-filter-btn" @click="handleClearFilter" title="Limpiar filtros">
            <X :size="15" />
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla de Préstamos -->
    <AdminTable
      :loading="loading"
      :items-count="loans.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay préstamos encontrados"
      empty-subtitle="Utiliza «Registrar Nuevo Préstamo» para iniciar una asignación de libro."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Libro Prestado</th>
          <th>Socio Lector</th>
          <th>Fecha Préstamo</th>
          <th>Límite Devolución</th>
          <th>Estado</th>
          <th>Multa</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="loan in loans" :key="loan.id">
          <td>#{{ loan.id }}</td>
          <td>
            <div class="loan-book-cell">
              <span class="loan-book-title">{{ loan.libro?.titulo || `Libro #${loan.libro_id}` }}</span>
              <span class="loan-book-isbn">ISBN: {{ loan.libro?.isbn || '—' }}</span>
            </div>
          </td>
          <td>
            <div class="loan-member-cell">
              <span class="loan-member-name">{{ loan.socio?.nombre || `Socio #${loan.socio_id}` }}</span>
              <span class="loan-member-email">{{ loan.socio?.email || '' }}</span>
            </div>
          </td>
          <td>
            <span class="loan-date">{{ loan.fecha_prestamo }}</span>
          </td>
          <td>
            <div class="due-date-cell">
              <span class="loan-due-date">{{ loan.fecha_limite }}</span>
              <span v-if="loan.fecha_devolucion" class="return-date-sub">
                Devuelto: {{ loan.fecha_devolucion }}
              </span>
            </div>
          </td>
          <td>
            <span class="status-pill" :class="loan.estado">
              {{ loan.estado }}
            </span>
          </td>
          <td>
            <div v-if="Number(loan.multa) > 0" class="fine-badge-box">
              <span class="fine-amount">${{ Number(loan.multa).toFixed(2) }}</span>
              <span
                class="fine-status"
                :class="{ 'paid': loan.multa_pagada, 'unpaid': !loan.multa_pagada }"
              >
                {{ loan.multa_pagada ? 'Pagada' : 'Pendiente' }}
              </span>
            </div>
            <span v-else class="no-fine">Sin multa</span>
          </td>
          <td>
            <div class="actions-cell">
              <!-- Botón registrar devolución si aún no está devuelto -->
              <button
                v-if="loan.estado !== 'devuelto'"
                class="icon-action-btn return-btn"
                title="Registrar devolución"
                @click="openReturnModal(loan)"
              >
                <CheckCircle :size="16" />
              </button>

              <!-- Botón pagar multa si tiene multa impaga -->
              <button
                v-if="Number(loan.multa) > 0 && !loan.multa_pagada"
                class="icon-action-btn pay-btn"
                title="Cobrar / Saladar multa"
                @click="openFineModal(loan)"
              >
                <DollarSign :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Nuevo Préstamo -->
    <AdminModal
      :is-open="isCreateModalOpen"
      title="Registrar Préstamo"
      subtitle="Asigna un ejemplar del catálogo a un socio activo"
      max-width="540px"
      @close="isCreateModalOpen = false"
    >
      <form class="admin-modal-form" @submit.prevent="submitCreateLoan">
        <div class="form-group">
          <label class="form-label required">Libro a Prestar</label>
          <select v-model="form.libro_id" class="form-select" required>
            <option value="" disabled>Selecciona un libro disponible</option>
            <option v-for="b in booksList" :key="b.id" :value="b.id">
              {{ b.titulo }} ({{ b.disponibles ?? b.ejemplares }} disponibles)
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label required">Socio Solicitante</label>
          <select v-model="form.socio_id" class="form-select" required>
            <option value="" disabled>Selecciona un socio activo</option>
            <option v-for="m in membersList" :key="m.id" :value="m.id">
              {{ m.nombre }} ({{ m.email }})
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label required">Fecha de Inicio</label>
            <input
              v-model="form.fecha_prestamo"
              type="date"
              class="form-input"
              :max="new Date().toISOString().split('T')[0]"
              required
            />
          </div>

          <div class="form-group flex-1">
            <label class="form-label required">Plazo en Días (1 a 30)</label>
            <input
              v-model.number="form.dias"
              type="number"
              class="form-input"
              min="1"
              max="30"
              required
            />
          </div>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isCreateModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting"
          @click="submitCreateLoan"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Confirmar Préstamo</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Registrar Devolución -->
    <AdminModal
      :is-open="isReturnModalOpen"
      title="Registrar Devolución de Libro"
      :subtitle="`Devolución de «${targetLoan?.libro?.titulo || 'Libro'}»`"
      max-width="480px"
      @close="isReturnModalOpen = false"
    >
      <div class="return-modal-content">
        <p class="return-modal-prompt">
          Ingresa la fecha efectiva en la que el lector devolvió el ejemplar a la biblioteca.
          El backend calculará automáticamente si existen multas por retraso respecto a la fecha límite (<strong>{{ targetLoan?.fecha_limite }}</strong>).
        </p>

        <div class="form-group">
          <label class="form-label required">Fecha Efectiva de Devolución</label>
          <input
            v-model="returnDate"
            type="date"
            class="form-input"
            required
          />
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isReturnModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting"
          @click="submitReturnLoan"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Confirmar Devolución</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Pagar Multa -->
    <AdminModal
      :is-open="isFineModalOpen"
      title="Registrar Pago de Multa"
      :subtitle="`Saldar penalización de Préstamo #${targetLoan?.id}`"
      max-width="440px"
      @close="isFineModalOpen = false"
    >
      <div class="fine-payment-box">
        <div class="fine-amount-display">
          ${{ Number(targetLoan?.multa || 0).toFixed(2) }}
        </div>
        <p class="fine-payment-desc">
          El socio <strong>{{ targetLoan?.socio?.nombre }}</strong> abonará el valor de la sanción generada por entrega fuera de plazo.
        </p>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isFineModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting"
          @click="submitPayFine"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Confirmar Pago Recibido</span>
        </button>
      </template>
    </AdminModal>
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

.primary-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.primary-action-btn:hover {
  background-color: #26352c;
  box-shadow: 0 4px 10px rgba(52, 72, 61, 0.15);
}

.module-alert {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
}

.module-alert.success {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

.module-alert.error {
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #b91c1c;
}

.filter-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.filter-inputs-grid {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 200px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7a7062;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-select {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.9rem;
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border: none;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.clear-filter-btn {
  padding: 0.55rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  color: #7a7062;
  cursor: pointer;
}

.loan-book-cell,
.loan-member-cell {
  display: flex;
  flex-direction: column;
}

.loan-book-title,
.loan-member-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
  font-size: 0.88rem;
}

.loan-book-isbn,
.loan-member-email {
  font-size: 0.72rem;
  color: #7a7062;
}

.loan-date,
.loan-due-date {
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.due-date-cell {
  display: flex;
  flex-direction: column;
}

.return-date-sub {
  font-size: 0.7rem;
  color: #059669;
  font-weight: 500;
}

.status-pill {
  display: inline-block;
  padding: 0.2rem 0.6rem;
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

.fine-badge-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.fine-amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 0.85rem;
}

.fine-status {
  font-size: 0.68rem;
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
  font-weight: 600;
}

.fine-status.paid {
  background-color: #ecfdf5;
  color: #059669;
}

.fine-status.unpaid {
  background-color: #fef2f2;
  color: #dc2626;
}

.no-fine {
  font-size: 0.8rem;
  color: #8c8273;
}

.actions-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.4rem;
}

.icon-action-btn {
  background: none;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  display: flex;
  transition: all 0.15s ease;
}

.icon-action-btn.return-btn {
  color: #059669;
}

.icon-action-btn.return-btn:hover {
  background-color: #ecfdf5;
  border-color: #a7f3d0;
}

.icon-action-btn.pay-btn {
  color: #b45309;
}

.icon-action-btn.pay-btn:hover {
  background-color: #fffbeb;
  border-color: #fde68a;
}

/* Modales */
.admin-modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.flex-1 { flex: 1; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.form-label.required::after {
  content: " *";
  color: #dc2626;
}

.form-input,
.form-select {
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.88rem;
  color: var(--color-forest, #34483D);
}

.admin-btn-secondary {
  padding: 0.55rem 1.15rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  color: #5d5345;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
}

.admin-btn-primary {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1.25rem;
  background-color: var(--color-forest, #34483D);
  border: none;
  border-radius: 8px;
  color: var(--color-ivory, #F5F2E9);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.return-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.return-modal-prompt {
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

.fine-payment-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0;
  gap: 0.85rem;
}

.fine-amount-display {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 2.5rem;
  font-weight: 700;
  color: #dc2626;
}

.fine-payment-desc {
  font-size: 0.88rem;
  color: #4b5563;
  margin: 0;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
