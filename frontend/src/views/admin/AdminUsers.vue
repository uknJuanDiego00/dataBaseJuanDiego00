<script setup>
import { ref, onMounted } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import { userService } from '../../services/userService'
import { useAuth } from '../../composables/useAuth'
import {
  UserPlus,
  Filter,
  ShieldCheck,
  ShieldAlert,
  User,
  Power,
  Edit2,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const { user: currentUser } = useAuth()

const users = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

// Filtros
const filterRole = ref('')
const filterActive = ref('')

const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isCreateModalOpen = ref(false)
const isRoleModalOpen = ref(false)
const isToggleActiveModalOpen = ref(false)
const submitting = ref(false)

const targetUser = ref(null)
const newRole = ref('socio')

// Formulario de creación de usuario
const form = ref({
  nombre: '',
  email: '',
  password: '',
  password_confirmacion: '',
  rol: 'socio'
})

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4500)
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }
    if (filterRole.value) params.rol = filterRole.value
    if (filterActive.value !== '') params.activo = filterActive.value === 'true'

    const res = await userService.getUsers(params)
    users.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar usuarios del sistema (se requiere rol Admin).', 'error')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  skip.value = 0
  loadUsers()
}

const handleClearFilter = () => {
  filterRole.value = ''
  filterActive.value = ''
  skip.value = 0
  loadUsers()
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadUsers()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadUsers()
  }
}

const openCreateModal = () => {
  form.value = {
    nombre: '',
    email: '',
    password: '',
    password_confirmacion: '',
    rol: 'socio'
  }
  isCreateModalOpen.value = true
}

const submitCreateUser = async () => {
  if (!form.value.nombre.trim() || !form.value.email.trim() || !form.value.password) {
    showAlert('Todos los campos son obligatorios.', 'error')
    return
  }

  if (form.value.password !== form.value.password_confirmacion) {
    showAlert('Las contraseñas no coinciden.', 'error')
    return
  }

  submitting.value = true
  try {
    await userService.createUser(form.value)
    showAlert(`Usuario «${form.value.email}» registrado exitosamente.`)
    isCreateModalOpen.value = false
    loadUsers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al crear usuario. Verifica requisitos de contraseña.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Cambio de Rol
const openRoleModal = (user) => {
  targetUser.value = user
  newRole.value = user.rol
  isRoleModalOpen.value = true
}

const submitChangeRole = async () => {
  submitting.value = true
  try {
    await userService.updateRole(targetUser.value.id, newRole.value)
    showAlert(`Rol de «${targetUser.value.email}» actualizado a ${newRole.value}.`)
    isRoleModalOpen.value = false
    loadUsers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se pudo modificar el rol (protección de último admin activo).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Toggle Activo
const openToggleActiveModal = (user) => {
  targetUser.value = user
  isToggleActiveModalOpen.value = true
}

const submitToggleActive = async () => {
  submitting.value = true
  const nextState = !targetUser.value.activo
  try {
    await userService.updateActive(targetUser.value.id, nextState)
    showAlert(`Cuenta de «${targetUser.value.email}» ${nextState ? 'activada' : 'desactivada'}.`)
    isToggleActiveModalOpen.value = false
    loadUsers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se pudo cambiar el estado de la cuenta.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Cuentas y Accesos</h2>
        <p class="module-subtitle">Administra los roles del sistema (Administrador, Bibliotecario, Socio) y estados de acceso</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <UserPlus :size="16" />
        <span>Crear Nueva Cuenta</span>
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
          <label class="filter-label">Filtrar por Rol</label>
          <select v-model="filterRole" class="filter-select" @change="handleFilter">
            <option value="">Todos los roles</option>
            <option value="admin">Administrador</option>
            <option value="bibliotecario">Bibliotecario</option>
            <option value="socio">Socio Lector</option>
          </select>
        </div>

        <div class="filter-field">
          <label class="filter-label">Estado de Cuenta</label>
          <select v-model="filterActive" class="filter-select" @change="handleFilter">
            <option value="">Todos los estados</option>
            <option value="true">Activas</option>
            <option value="false">Desactivadas</option>
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

    <!-- Tabla -->
    <AdminTable
      :loading="loading"
      :items-count="users.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay usuarios encontrados"
      empty-subtitle="Utiliza «Crear Nueva Cuenta» para incorporar administradores o bibliotecarios."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Nombre Completo</th>
          <th>Correo Electrónico</th>
          <th>Rol en Sistema</th>
          <th>Estado</th>
          <th>Ficha de Socio</th>
          <th>Fecha Creación</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="u in users" :key="u.id">
          <td>#{{ u.id }}</td>
          <td>
            <div class="user-name-cell">
              <span class="user-full-name">{{ u.nombre }}</span>
              <span v-if="u.id === currentUser?.id" class="self-tag">(Tú)</span>
            </div>
          </td>
          <td>
            <span class="user-email-text">{{ u.email }}</span>
          </td>
          <td>
            <span class="role-badge" :class="u.rol">
              <ShieldCheck v-if="u.rol === 'admin'" :size="13" />
              <ShieldAlert v-else-if="u.rol === 'bibliotecario'" :size="13" />
              <User v-else :size="13" />
              <span>{{ u.rol }}</span>
            </span>
          </td>
          <td>
            <span class="active-badge" :class="{ 'active': u.activo, 'inactive': !u.activo }">
              {{ u.activo ? 'Activa' : 'Desactivada' }}
            </span>
          </td>
          <td>
            <span v-if="u.socio_id" class="socio-link-badge">Socio #{{ u.socio_id }}</span>
            <span v-else class="no-socio-badge">—</span>
          </td>
          <td>
            <span class="creation-date">
              {{ new Date(u.creado_en).toLocaleDateString() }}
            </span>
          </td>
          <td>
            <div class="actions-cell">
              <button
                class="icon-action-btn role-btn"
                title="Cambiar rol"
                @click="openRoleModal(u)"
              >
                <Edit2 :size="16" />
              </button>
              <button
                class="icon-action-btn toggle-btn"
                :class="{ 'deactivate': u.activo, 'activate': !u.activo }"
                :title="u.activo ? 'Desactivar cuenta' : 'Activar cuenta'"
                @click="openToggleActiveModal(u)"
              >
                <Power :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Crear Cuenta -->
    <AdminModal
      :is-open="isCreateModalOpen"
      title="Crear Nueva Cuenta"
      subtitle="Genera credenciales de acceso seguras con cifrado Argon2"
      max-width="540px"
      @close="isCreateModalOpen = false"
    >
      <form class="admin-modal-form" @submit.prevent="submitCreateUser">
        <div class="form-group">
          <label class="form-label required">Nombre Completo</label>
          <input
            v-model="form.nombre"
            type="text"
            class="form-input"
            placeholder="Ej. Ana Pérez"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label required">Correo Electrónico (Username)</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="usuario@biblioteca.com"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label required">Rol del Usuario</label>
          <select v-model="form.rol" class="form-select" required>
            <option value="socio">Socio Lector (Acceso estándar)</option>
            <option value="bibliotecario">Bibliotecario (Gestión de préstamos y catálogo)</option>
            <option value="admin">Administrador (Acceso total al sistema)</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label required">Contraseña (Mín. 8 chars)</label>
            <input
              v-model="form.password"
              type="password"
              class="form-input"
              placeholder="••••••••"
              required
            />
            <span class="password-rule-hint">Debe incluir mayúscula, minúscula y número.</span>
          </div>

          <div class="form-group flex-1">
            <label class="form-label required">Confirmar Contraseña</label>
            <input
              v-model="form.password_confirmacion"
              type="password"
              class="form-input"
              placeholder="••••••••"
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
          @click="submitCreateUser"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Crear Usuario</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Modificar Rol -->
    <AdminModal
      :is-open="isRoleModalOpen"
      title="Modificar Rol de Usuario"
      :subtitle="`Actualizar privilegios para «${targetUser?.email}»`"
      max-width="440px"
      @close="isRoleModalOpen = false"
    >
      <div class="role-modal-content">
        <div class="form-group">
          <label class="form-label required">Nuevo Rol</label>
          <select v-model="newRole" class="form-select">
            <option value="admin">Administrador</option>
            <option value="bibliotecario">Bibliotecario</option>
            <option value="socio">Socio Lector</option>
          </select>
        </div>
        <p class="role-warning">
          El cambio revoca los tokens de sesión activos del usuario para forzar una reautenticación con sus nuevos permisos.
        </p>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isRoleModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting"
          @click="submitChangeRole"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Actualizar Rol</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Cambiar Activo -->
    <AdminModal
      :is-open="isToggleActiveModalOpen"
      :title="targetUser?.activo ? 'Desactivar Cuenta' : 'Reactivar Cuenta'"
      :subtitle="targetUser?.email"
      max-width="440px"
      @close="isToggleActiveModalOpen = false"
    >
      <div class="toggle-modal-content">
        <p v-if="targetUser?.activo" class="toggle-desc warning">
          ¿Seguro que deseas desactivar esta cuenta? El usuario no podrá iniciar sesión en la plataforma y sus tokens actuales serán revocados inmediatamente.
        </p>
        <p v-else class="toggle-desc">
          ¿Deseas reactivar esta cuenta para restaurar el acceso del usuario?
        </p>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isToggleActiveModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          :class="targetUser?.activo ? 'admin-btn-danger' : 'admin-btn-primary'"
          :disabled="submitting"
          @click="submitToggleActive"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>{{ targetUser?.activo ? 'Desactivar Cuenta' : 'Activar Cuenta' }}</span>
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

.user-name-cell {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.user-full-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.self-tag {
  font-size: 0.7rem;
  background-color: var(--color-gold, #C49A62);
  color: #fff;
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
  font-weight: 600;
}

.user-email-text {
  font-size: 0.85rem;
  color: #5d5345;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.admin {
  background-color: #fef3c7;
  color: #b45309;
}

.role-badge.bibliotecario {
  background-color: #dbeafe;
  color: #1e40af;
}

.role-badge.socio {
  background-color: #f3f4f6;
  color: #4b5563;
}

.active-badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  font-size: 0.72rem;
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

.socio-link-badge {
  font-size: 0.75rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  color: #6b6051;
}

.no-socio-badge {
  color: #9ca3af;
}

.creation-date {
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
  cursor: pointer;
  display: flex;
  transition: all 0.15s ease;
}

.icon-action-btn.role-btn {
  color: #b45309;
}

.icon-action-btn.role-btn:hover {
  background-color: #fffbeb;
  border-color: #fde68a;
}

.icon-action-btn.toggle-btn.deactivate {
  color: #dc2626;
}

.icon-action-btn.toggle-btn.deactivate:hover {
  background-color: #fef2f2;
  border-color: #fca5a5;
}

.icon-action-btn.toggle-btn.activate {
  color: #059669;
}

.icon-action-btn.toggle-btn.activate:hover {
  background-color: #ecfdf5;
  border-color: #a7f3d0;
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

.password-rule-hint {
  font-size: 0.72rem;
  color: #8c8273;
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

.admin-btn-danger {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1.25rem;
  background-color: #dc2626;
  border: 1px solid #b91c1c;
  border-radius: 8px;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.role-modal-content,
.toggle-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-warning {
  font-size: 0.8rem;
  color: #b45309;
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
  padding: 0.65rem 0.85rem;
  border-radius: 6px;
  margin: 0;
}

.toggle-desc {
  font-size: 0.88rem;
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

.toggle-desc.warning {
  color: #dc2626;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
