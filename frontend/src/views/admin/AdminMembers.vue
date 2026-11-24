<script setup>
import { ref, onMounted } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminConfirmModal from '../../components/admin/AdminConfirmModal.vue'
import { memberService } from '../../services/memberService'
import {
  Plus,
  Filter,
  Edit,
  Trash2,
  Clock,
  UserCheck,
  UserX,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const members = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

const filterActive = ref('')

const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isFormModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isLoansModalOpen = ref(false)
const submitting = ref(false)

const isEditing = ref(false)
const currentMemberId = ref(null)
const targetMember = ref(null)

const memberLoans = ref([])
const loadingLoans = ref(false)

const form = ref({
  nombre: '',
  email: '',
  telefono: '',
  activo: true
})

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4500)
}

const loadMembers = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }
    if (filterActive.value !== '') {
      params.activo = filterActive.value === 'true'
    }

    const res = await memberService.getMembers(params)
    members.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar socios de la biblioteca.', 'error')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  skip.value = 0
  loadMembers()
}

const handleClearFilter = () => {
  filterActive.value = ''
  skip.value = 0
  loadMembers()
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadMembers()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadMembers()
  }
}

const openCreateModal = () => {
  isEditing.value = false
  currentMemberId.value = null
  form.value = {
    nombre: '',
    email: '',
    telefono: '',
    activo: true
  }
  isFormModalOpen.value = true
}

const openEditModal = (member) => {
  isEditing.value = true
  currentMemberId.value = member.id
  form.value = {
    nombre: member.nombre,
    email: member.email,
    telefono: member.telefono || '',
    activo: member.activo
  }
  isFormModalOpen.value = true
}

const submitForm = async () => {
  if (!form.value.nombre.trim() || !form.value.email.trim()) {
    showAlert('Nombre y correo electrónico son requeridos.', 'error')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value) {
      await memberService.updateMember(currentMemberId.value, form.value)
      showAlert(`Ficha del socio «${form.value.nombre}» actualizada.`)
    } else {
      await memberService.createMember(form.value)
      showAlert(`Socio «${form.value.nombre}» incorporado exitosamente.`)
    }
    isFormModalOpen.value = false
    loadMembers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al procesar el socio (verifica si el correo ya existe).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

const openDeleteModal = (member) => {
  currentMemberId.value = member.id
  targetMember.value = member
  isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  submitting.value = true
  try {
    await memberService.deleteMember(currentMemberId.value)
    showAlert('Socio eliminado o desactivado del sistema.')
    isDeleteModalOpen.value = false
    loadMembers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se puede eliminar el socio (tiene préstamos activos pendientes de devolución).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Consultar préstamos del socio
const openMemberLoansModal = async (member) => {
  targetMember.value = member
  isLoansModalOpen.value = true
  loadingLoans.value = true
  memberLoans.value = []
  try {
    const res = await memberService.getMemberLoans(member.id, { limit: 50 })
    memberLoans.value = res.items || []
  } catch (err) {
    console.error('Error cargando préstamos del socio:', err)
  } finally {
    loadingLoans.value = false
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Socios Lectores</h2>
        <p class="module-subtitle">Administra los carnets de socios, sus datos de contacto y su historial de préstamos</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <Plus :size="16" />
        <span>Registrar Nuevo Socio</span>
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
          <label class="filter-label">Estado de la Ficha</label>
          <select v-model="filterActive" class="filter-select" @change="handleFilter">
            <option value="">Todos los socios</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos / Suspendidos</option>
          </select>
        </div>

        <div class="filter-actions">
          <button class="filter-btn" @click="handleFilter">
            <Filter :size="15" />
            <span>Filtrar</span>
          </button>
          <button class="clear-filter-btn" @click="handleClearFilter" title="Limpiar filtro">
            <X :size="15" />
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla -->
    <AdminTable
      :loading="loading"
      :items-count="members.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay socios registrados"
      empty-subtitle="Utiliza «Registrar Nuevo Socio» para enrolar al primer lector."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Nombre Completo</th>
          <th>Correo Electrónico</th>
          <th>Teléfono</th>
          <th>Estado</th>
          <th>Fecha Registro</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="member in members" :key="member.id">
          <td>#{{ member.id }}</td>
          <td>
            <span class="member-name">{{ member.nombre }}</span>
          </td>
          <td>
            <span class="member-email">{{ member.email }}</span>
          </td>
          <td>
            <span class="member-phone">{{ member.telefono || '—' }}</span>
          </td>
          <td>
            <span class="active-badge" :class="{ 'active': member.activo, 'inactive': !member.activo }">
              <UserCheck v-if="member.activo" :size="13" />
              <UserX v-else :size="13" />
              <span>{{ member.activo ? 'Activo' : 'Inactivo' }}</span>
            </span>
          </td>
          <td>
            <span class="registration-date">
              {{ new Date(member.fecha_alta).toLocaleDateString() }}
            </span>
          </td>
          <td>
            <div class="actions-cell">
              <button
                class="icon-action-btn"
                title="Ver historial de préstamos"
                @click="openMemberLoansModal(member)"
              >
                <Clock :size="16" />
              </button>
              <button
                class="icon-action-btn"
                title="Editar socio"
                @click="openEditModal(member)"
              >
                <Edit :size="16" />
              </button>
              <button
                class="icon-action-btn delete-btn"
                title="Eliminar o desactivar socio"
                @click="openDeleteModal(member)"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Formulario Socio -->
    <AdminModal
      :is-open="isFormModalOpen"
      :title="isEditing ? 'Editar Socio' : 'Registrar Nuevo Socio'"
      :subtitle="isEditing ? `Modificando ID #${currentMemberId}` : 'Completa la información del lector'"
      max-width="500px"
      @close="isFormModalOpen = false"
    >
      <form class="admin-modal-form" @submit.prevent="submitForm">
        <div class="form-group">
          <label class="form-label required">Nombre Completo</label>
          <input
            v-model="form.nombre"
            type="text"
            class="form-input"
            placeholder="Ej. Gabriel García"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label required">Correo Electrónico Único</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="socio@correo.com"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">Teléfono (Opcional, 7 a 15 dígitos)</label>
          <input
            v-model="form.telefono"
            type="text"
            class="form-input"
            placeholder="+57 300 1234567"
          />
        </div>

        <div class="form-checkbox-group">
          <label class="checkbox-label">
            <input v-model="form.activo" type="checkbox" class="checkbox-input" />
            <span>Socio con membresía activa para solicitar préstamos</span>
          </label>
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isFormModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting"
          @click="submitForm"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>{{ isEditing ? 'Guardar Cambios' : 'Registrar Socio' }}</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Historial de Préstamos del Socio -->
    <AdminModal
      :is-open="isLoansModalOpen"
      :title="`Historial de ${targetMember?.nombre}`"
      subtitle="Todos los préstamos vinculados a este socio"
      max-width="640px"
      @close="isLoansModalOpen = false"
    >
      <div v-if="loadingLoans" class="loader-box">
        <Loader2 :size="24" class="spin-icon" />
        <span>Cargando préstamos del socio...</span>
      </div>
      <div v-else-if="memberLoans.length === 0" class="no-data-box">
        <Clock :size="32" class="empty-icon" />
        <p>Este socio aún no registra préstamos en la biblioteca.</p>
      </div>
      <div v-else class="member-loans-table-wrapper">
        <table class="sub-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Libro</th>
              <th>Fecha Préstamo</th>
              <th>Fecha Límite</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in memberLoans" :key="l.id">
              <td>#{{ l.id }}</td>
              <td class="font-medium">{{ l.libro?.titulo || `Libro #${l.libro_id}` }}</td>
              <td>{{ l.fecha_prestamo }}</td>
              <td>{{ l.fecha_limite }}</td>
              <td>
                <span class="status-pill" :class="l.estado">{{ l.estado }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <template #footer>
        <button type="button" class="admin-btn-secondary" @click="isLoansModalOpen = false">
          Cerrar
        </button>
      </template>
    </AdminModal>

    <!-- Modal Confirmar Eliminación -->
    <AdminConfirmModal
      :is-open="isDeleteModalOpen"
      title="Eliminar o Desactivar Socio"
      :message="`¿Deseas retirar a «${targetMember?.nombre}»? Si tiene préstamos activos la operación será rechazada por seguridad.`"
      confirm-text="Confirmar Retiro"
      :loading="submitting"
      @close="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />
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

.member-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.member-email {
  font-size: 0.85rem;
  color: #5d5345;
}

.member-phone {
  font-size: 0.82rem;
  color: #7a7062;
}

.active-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 600;
}

.active-badge.active {
  background-color: #ecfdf5;
  color: #059669;
}

.active-badge.inactive {
  background-color: #fef2f2;
  color: #dc2626;
}

.registration-date {
  font-size: 0.82rem;
  color: #7a7062;
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
  color: var(--color-forest, #34483D);
  cursor: pointer;
  display: flex;
  transition: all 0.15s ease;
}

.icon-action-btn:hover {
  background-color: var(--color-ivory, #F5F2E9);
  color: var(--color-gold, #C49A62);
  border-color: var(--color-gold, #C49A62);
}

.icon-action-btn.delete-btn:hover {
  background-color: #fef2f2;
  color: #dc2626;
  border-color: #fca5a5;
}

/* Modales */
.admin-modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

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

.form-input {
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.88rem;
  color: var(--color-forest, #34483D);
}

.form-checkbox-group {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.82rem;
  color: var(--color-forest, #34483D);
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-forest, #34483D);
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

.loader-box,
.no-data-box {
  padding: 2.5rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #7a7062;
  font-size: 0.85rem;
  text-align: center;
}

.empty-icon {
  color: var(--color-gold, #C49A62);
}

.member-loans-table-wrapper {
  overflow-x: auto;
}

.sub-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  text-align: left;
}

.sub-table th {
  padding: 0.5rem 0.65rem;
  color: #7a7062;
  font-weight: 600;
  border-bottom: 1px solid #ECE7DC;
}

.sub-table td {
  padding: 0.65rem;
  border-bottom: 1px solid #F5F2E9;
  color: var(--color-forest, #34483D);
}

.font-medium {
  font-weight: 600;
}

.status-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
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

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
