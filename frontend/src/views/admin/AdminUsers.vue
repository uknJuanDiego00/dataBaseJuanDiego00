<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import { userService } from '../../services/userService'
import { useAuth } from '../../composables/useAuth'
import {
  UserPlus,
  Filter,
  ShieldCheck,
  User,
  UserCheck,
  UserCog,
  Users,
  Power,
  Edit2,
  Eye,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle,
  Search,
  Calendar,
  Mail,
  Shield,
  IdCard,
  Check,
  HelpCircle
} from 'lucide-vue-next'

const { user: currentUser } = useAuth()

// Estado principal de usuarios
const users = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

// Conteos por categoría para los badges de las pestañas y tarjetas KPI
const counts = ref({
  all: 0,
  admin: 0,
  socio: 0,
  bibliotecario: 0
})
const loadingCounts = ref(false)

// Pestaña activa: 'all' | 'admin' | 'socio' | 'bibliotecario'
const activeTab = ref('all')

// Búsqueda y filtros adicionales
const searchQuery = ref('')
const filterActive = ref('')

// Notificaciones flotantes
const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isCreateModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const isRoleModalOpen = ref(false)
const isToggleActiveModalOpen = ref(false)
const submitting = ref(false)

// Usuario seleccionado para ver detalle o editar
const targetUser = ref(null)
const newRole = ref('socio')

// Formulario de creación
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

/**
 * Obtiene los conteos globales por rol para los badges y tarjetas informativas.
 */
const loadRoleCounts = async () => {
  loadingCounts.value = true
  try {
    const [allRes, adminRes, socioRes, biblioRes] = await Promise.all([
      userService.getUsers({ limit: 1 }),
      userService.getUsers({ rol: 'admin', limit: 1 }),
      userService.getUsers({ rol: 'socio', limit: 1 }),
      userService.getUsers({ rol: 'bibliotecario', limit: 1 })
    ])
    counts.value = {
      all: allRes.total || 0,
      admin: adminRes.total || 0,
      socio: socioRes.total || 0,
      bibliotecario: biblioRes.total || 0
    }
  } catch (err) {
    console.error('Error cargando conteos de roles:', err)
  } finally {
    loadingCounts.value = false
  }
}

/**
 * Consulta la lista de usuarios al backend respetando la pestaña y filtros seleccionados.
 */
const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }

    // Filtrar por rol según la pestaña seleccionada
    if (activeTab.value !== 'all') {
      params.rol = activeTab.value
    }

    // Filtro por estado activo/inactivo
    if (filterActive.value !== '') {
      params.activo = filterActive.value === 'true'
    }

    const res = await userService.getUsers(params)
    users.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar usuarios del sistema (se requiere rol Admin).', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Filtro reactivo en cliente para búsqueda instantánea por nombre o correo
 * sobre la página o elementos cargados.
 */
const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const q = searchQuery.value.trim().toLowerCase()
  return users.value.filter(u =>
    (u.nombre && u.nombre.toLowerCase().includes(q)) ||
    (u.email && u.email.toLowerCase().includes(q)) ||
    String(u.id).includes(q)
  )
})

// Cambio de pestaña
const selectTab = (tab) => {
  if (activeTab.value === tab) return
  activeTab.value = tab
  skip.value = 0
  loadUsers()
}

// Búsqueda y reseteo
const handleFilterChange = () => {
  skip.value = 0
  loadUsers()
}

const handleClearFilter = () => {
  searchQuery.value = ''
  filterActive.value = ''
  skip.value = 0
  loadUsers()
}

// Paginación
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

// Modal Ver Detalle
const openDetailModal = (user) => {
  targetUser.value = user
  isDetailModalOpen.value = true
}

// Modal Crear Usuario
const openCreateModal = (defaultRole = null) => {
  form.value = {
    nombre: '',
    email: '',
    password: '',
    password_confirmacion: '',
    rol: defaultRole && defaultRole !== 'all' ? defaultRole : 'socio'
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
    loadRoleCounts()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al crear usuario. Verifica los requisitos de la contraseña.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Cambio de Rol
const openRoleModal = (user) => {
  if (user.id === currentUser.value?.id) {
    showAlert('Por seguridad, no puedes modificar tu propio rol de administrador.', 'error')
    return
  }
  targetUser.value = user
  newRole.value = user.rol
  isRoleModalOpen.value = true
}

const submitChangeRole = async () => {
  submitting.value = true
  try {
    await userService.updateRole(targetUser.value.id, newRole.value)
    showAlert(`Rol de «${targetUser.value.email}» actualizado a ${getRoleLabel(newRole.value)}.`)
    isRoleModalOpen.value = false
    if (isDetailModalOpen.value && targetUser.value) {
      targetUser.value.rol = newRole.value
    }
    loadUsers()
    loadRoleCounts()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se pudo modificar el rol (protección de último admin activo).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal Activar/Desactivar
const openToggleActiveModal = (user) => {
  if (user.id === currentUser.value?.id) {
    showAlert('Por seguridad, no puedes desactivar tu propia cuenta activa.', 'error')
    return
  }
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
    if (isDetailModalOpen.value && targetUser.value) {
      targetUser.value.activo = nextState
    }
    loadUsers()
    loadRoleCounts()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se pudo cambiar el estado de la cuenta.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Helpers visuales para roles
const getRoleLabel = (role) => {
  switch (role) {
    case 'admin': return 'Administrador'
    case 'bibliotecario': return 'Bibliotecario / Personal'
    case 'socio': return 'Socio Lector'
    default: return role || 'Usuario'
  }
}

const getRoleDescription = (role) => {
  switch (role) {
    case 'admin':
      return 'Control total del sistema: gestión de cuentas, configuración, préstamos y catálogo.'
    case 'bibliotecario':
      return 'Gestión operativa: registro y edición de libros, autores, categorías y préstamos.'
    case 'socio':
      return 'Lector registrado con credencial: consulta de catálogo y solicitud de préstamos.'
    default:
      return 'Acceso básico al sistema.'
  }
}

const getInitials = (name) => {
  if (!name) return 'U'
  const parts = name.trim().split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

onMounted(() => {
  loadRoleCounts()
  loadUsers()
})
</script>

<template>
  <div class="admin-users-module">
    <!-- Encabezado de la página -->
    <div class="module-header">
      <div class="header-titles">
        <h2 class="module-title">Gestión de Usuarios y Roles</h2>
        <p class="module-subtitle">
          Supervisa y administra el acceso a Serenidad organizado por roles de seguridad y categorías de cuentas
        </p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal(activeTab)">
        <UserPlus :size="16" />
        <span>Crear Nuevo Usuario</span>
      </button>
    </div>

    <!-- Alerta Flotante -->
    <transition name="fade">
      <div v-if="alertMsg.text" class="module-alert" :class="alertMsg.type">
        <CheckCircle2 v-if="alertMsg.type === 'success'" :size="18" />
        <AlertCircle v-else :size="18" />
        <span>{{ alertMsg.text }}</span>
      </div>
    </transition>

    <!-- Tarjetas Resumen de Roles (KPI Cards) -->
    <div class="role-kpi-grid">
      <!-- Total Cuentas -->
      <div
        class="role-kpi-card"
        :class="{ 'active-card': activeTab === 'all' }"
        @click="selectTab('all')"
      >
        <div class="kpi-icon-wrap all-users">
          <Users :size="20" />
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Todos los Usuarios</span>
          <span class="kpi-value">{{ counts.all }}</span>
          <span class="kpi-hint">Cuentas registradas en total</span>
        </div>
      </div>

      <!-- Administradores -->
      <div
        class="role-kpi-card"
        :class="{ 'active-card': activeTab === 'admin' }"
        @click="selectTab('admin')"
      >
        <div class="kpi-icon-wrap admin-role">
          <ShieldCheck :size="20" />
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Administradores</span>
          <span class="kpi-value">{{ counts.admin }}</span>
          <span class="kpi-hint">Acceso total al sistema</span>
        </div>
      </div>

      <!-- Socios -->
      <div
        class="role-kpi-card"
        :class="{ 'active-card': activeTab === 'socio' }"
        @click="selectTab('socio')"
      >
        <div class="kpi-icon-wrap socio-role">
          <UserCheck :size="20" />
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Socios Lectores</span>
          <span class="kpi-value">{{ counts.socio }}</span>
          <span class="kpi-hint">Lectores con préstamos</span>
        </div>
      </div>

      <!-- Bibliotecarios / Personal -->
      <div
        class="role-kpi-card"
        :class="{ 'active-card': activeTab === 'bibliotecario' }"
        @click="selectTab('bibliotecario')"
      >
        <div class="kpi-icon-wrap biblio-role">
          <UserCog :size="20" />
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Personal / Sistema</span>
          <span class="kpi-value">{{ counts.bibliotecario }}</span>
          <span class="kpi-hint">Bibliotecarios y operadores</span>
        </div>
      </div>
    </div>

    <!-- Navegación de Pestañas por Rol (Tabs) -->
    <div class="role-tabs-bar">
      <button
        class="role-tab-btn"
        :class="{ active: activeTab === 'all' }"
        @click="selectTab('all')"
      >
        <Users :size="15" />
        <span>Todos los Usuarios</span>
        <span class="tab-badge">{{ counts.all }}</span>
      </button>

      <button
        class="role-tab-btn"
        :class="{ active: activeTab === 'admin' }"
        @click="selectTab('admin')"
      >
        <ShieldCheck :size="15" />
        <span>Administradores</span>
        <span class="tab-badge badge-admin">{{ counts.admin }}</span>
      </button>

      <button
        class="role-tab-btn"
        :class="{ active: activeTab === 'socio' }"
        @click="selectTab('socio')"
      >
        <UserCheck :size="15" />
        <span>Socios</span>
        <span class="tab-badge badge-socio">{{ counts.socio }}</span>
      </button>

      <button
        class="role-tab-btn"
        :class="{ active: activeTab === 'bibliotecario' }"
        @click="selectTab('bibliotecario')"
      >
        <UserCog :size="15" />
        <span>Personal / Bibliotecarios</span>
        <span class="tab-badge badge-biblio">{{ counts.bibliotecario }}</span>
      </button>
    </div>

    <!-- Barra de Filtros y Búsqueda -->
    <div class="filter-card">
      <div class="filter-inputs-grid">
        <!-- Búsqueda en tiempo real -->
        <div class="filter-field search-field">
          <label class="filter-label">Buscar Usuario</label>
          <div class="search-input-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              class="filter-input search-input"
              placeholder="Buscar por nombre, correo electrónico o ID..."
            />
            <button
              v-if="searchQuery"
              class="clear-input-btn"
              title="Borrar búsqueda"
              @click="searchQuery = ''"
            >
              <X :size="13" />
            </button>
          </div>
        </div>

        <!-- Filtro por Estado Activo/Inactivo -->
        <div class="filter-field status-field">
          <label class="filter-label">Estado de la Cuenta</label>
          <select
            v-model="filterActive"
            class="filter-select"
            @change="handleFilterChange"
          >
            <option value="">Todos los estados</option>
            <option value="true">Activas únicamente</option>
            <option value="false">Desactivadas únicamente</option>
          </select>
        </div>

        <!-- Acciones de Filtro -->
        <div class="filter-actions">
          <button
            class="clear-filter-btn"
            title="Limpiar filtros"
            @click="handleClearFilter"
          >
            <X :size="15" />
            <span>Limpiar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla Principal de Usuarios -->
    <AdminTable
      :loading="loading"
      :items-count="filteredUsers.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      :empty-title="searchQuery ? 'No hay resultados para la búsqueda' : 'No hay usuarios en esta categoría'"
      :empty-subtitle="searchQuery ? `No encontramos usuarios con «${searchQuery}». Prueba con otro término.` : 'Haz clic en «Crear Nuevo Usuario» para registrar una nueva cuenta con este rol.'"
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th style="width: 70px;">ID</th>
          <th>Usuario</th>
          <th>Correo Electrónico</th>
          <th>Rol Asignado</th>
          <th>Estado</th>
          <th>Ficha de Socio</th>
          <th>Fecha Registro</th>
          <th style="text-align: right; width: 140px;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr
          v-for="u in filteredUsers"
          :key="u.id"
          :class="{ 'current-user-row': u.id === currentUser?.id }"
        >
          <!-- ID -->
          <td class="id-cell">#{{ u.id }}</td>

          <!-- Nombre y Avatar -->
          <td>
            <div class="user-profile-cell">
              <div class="user-avatar" :class="u.rol">
                {{ getInitials(u.nombre) }}
              </div>
              <div class="user-info-text">
                <div class="user-name-line">
                  <span class="user-full-name">{{ u.nombre }}</span>
                  <span v-if="u.id === currentUser?.id" class="self-tag">(Tú)</span>
                </div>
                <span class="user-sub-id">Cuenta #{{ u.id }}</span>
              </div>
            </div>
          </td>

          <!-- Correo -->
          <td>
            <span class="user-email-text">{{ u.email }}</span>
          </td>

          <!-- Rol Asignado con Badge Distintivo -->
          <td>
            <span class="role-badge" :class="u.rol">
              <ShieldCheck v-if="u.rol === 'admin'" :size="13" />
              <UserCog v-else-if="u.rol === 'bibliotecario'" :size="13" />
              <UserCheck v-else :size="13" />
              <span>{{ getRoleLabel(u.rol) }}</span>
            </span>
          </td>

          <!-- Estado de la Cuenta -->
          <td>
            <span
              class="active-status-pill"
              :class="{ 'is-active': u.activo, 'is-inactive': !u.activo }"
            >
              <span class="status-dot"></span>
              <span>{{ u.activo ? 'Activa' : 'Desactivada' }}</span>
            </span>
          </td>

          <!-- Ficha de Socio Asociada -->
          <td>
            <span v-if="u.socio_id" class="socio-link-badge">
              <IdCard :size="12" />
              <span>Socio #{{ u.socio_id }}</span>
            </span>
            <span v-else class="no-socio-badge">Sin ficha</span>
          </td>

          <!-- Fecha de Creación -->
          <td>
            <span class="creation-date">
              {{ u.creado_en ? new Date(u.creado_en).toLocaleDateString() : '—' }}
            </span>
          </td>

          <!-- Acciones Disponibles -->
          <td>
            <div class="actions-cell">
              <!-- Ver Detalle -->
              <button
                class="icon-action-btn detail-btn"
                title="Consultar información completa"
                @click="openDetailModal(u)"
              >
                <Eye :size="15" />
              </button>

              <!-- Cambiar Rol -->
              <button
                class="icon-action-btn role-btn"
                :title="u.id === currentUser?.id ? 'No puedes cambiar tu propio rol' : 'Modificar rol'"
                :disabled="u.id === currentUser?.id"
                @click="openRoleModal(u)"
              >
                <Edit2 :size="15" />
              </button>

              <!-- Activar / Desactivar -->
              <button
                class="icon-action-btn toggle-btn"
                :class="{ 'deactivate': u.activo, 'activate': !u.activo }"
                :title="u.id === currentUser?.id ? 'No puedes desactivar tu propia cuenta' : (u.activo ? 'Desactivar cuenta' : 'Activar cuenta')"
                :disabled="u.id === currentUser?.id"
                @click="openToggleActiveModal(u)"
              >
                <Power :size="15" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- MODAL 1: Consultar Detalle de Usuario -->
    <AdminModal
      :is-open="isDetailModalOpen"
      title="Ficha Detallada del Usuario"
      subtitle="Consulta los privilegios, accesos y estado en el sistema Serenidad"
      max-width="520px"
      @close="isDetailModalOpen = false"
    >
      <div v-if="targetUser" class="user-detail-modal">
        <!-- Tarjeta de Perfil -->
        <div class="detail-header-card">
          <div class="detail-avatar" :class="targetUser.rol">
            {{ getInitials(targetUser.nombre) }}
          </div>
          <div class="detail-user-main">
            <h3 class="detail-user-name">
              {{ targetUser.nombre }}
              <span v-if="targetUser.id === currentUser?.id" class="self-tag">(Tú)</span>
            </h3>
            <span class="detail-user-email">{{ targetUser.email }}</span>
          </div>
        </div>

        <!-- Atributos del Usuario -->
        <div class="detail-attributes-grid">
          <!-- Rol -->
          <div class="attribute-box">
            <span class="attr-title">Rol Asignado</span>
            <div class="attr-body">
              <span class="role-badge" :class="targetUser.rol">
                <ShieldCheck v-if="targetUser.rol === 'admin'" :size="14" />
                <UserCog v-else-if="targetUser.rol === 'bibliotecario'" :size="14" />
                <UserCheck v-else :size="14" />
                <span>{{ getRoleLabel(targetUser.rol) }}</span>
              </span>
            </div>
            <p class="attr-desc">{{ getRoleDescription(targetUser.rol) }}</p>
          </div>

          <!-- Estado de Cuenta -->
          <div class="attribute-box">
            <span class="attr-title">Estado de Acceso</span>
            <div class="attr-body">
              <span
                class="active-status-pill"
                :class="{ 'is-active': targetUser.activo, 'is-inactive': !targetUser.activo }"
              >
                <span class="status-dot"></span>
                <span>{{ targetUser.activo ? 'Cuenta Activa' : 'Cuenta Suspendida / Desactivada' }}</span>
              </span>
            </div>
            <p class="attr-desc">
              {{ targetUser.activo ? 'El usuario puede iniciar sesión normalmente.' : 'El usuario tiene bloqueado el inicio de sesión.' }}
            </p>
          </div>

          <!-- Ficha de Socio -->
          <div class="attribute-box">
            <span class="attr-title">Vínculo con Socio Lector</span>
            <div class="attr-body">
              <span v-if="targetUser.socio_id" class="socio-link-badge">
                <IdCard :size="13" />
                <span>Asociado al Carnet #{{ targetUser.socio_id }}</span>
              </span>
              <span v-else class="no-socio-badge">No tiene ficha de socio asignada</span>
            </div>
          </div>

          <!-- Fecha de Alta -->
          <div class="attribute-box">
            <span class="attr-title">Fecha de Registro</span>
            <div class="attr-body flex-row">
              <Calendar :size="14" class="icon-muted" />
              <span class="attr-val">
                {{ targetUser.creado_en ? new Date(targetUser.creado_en).toLocaleString() : 'No registrada' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          @click="isDetailModalOpen = false"
        >
          Cerrar
        </button>
        <button
          v-if="targetUser && targetUser.id !== currentUser?.id"
          type="button"
          class="admin-btn-primary"
          @click="isDetailModalOpen = false; openRoleModal(targetUser)"
        >
          <Edit2 :size="14" />
          <span>Cambiar Rol</span>
        </button>
      </template>
    </AdminModal>

    <!-- MODAL 2: Crear Nuevo Usuario -->
    <AdminModal
      :is-open="isCreateModalOpen"
      title="Registrar Nuevo Usuario"
      subtitle="Genera una cuenta con credenciales seguras y rol predefinido"
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
            placeholder="Ej. Gabriela Mistral"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label required">Correo Electrónico (Usuario de acceso)</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="usuario@serenidad.biblioteca.com"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label required">Rol en el Sistema</label>
          <select v-model="form.rol" class="form-select" required>
            <option value="socio">Socio Lector (Acceso estándar al catálogo y préstamos)</option>
            <option value="bibliotecario">Bibliotecario / Personal (Gestión de préstamos y catálogo)</option>
            <option value="admin">Administrador (Acceso y control total del sistema)</option>
          </select>
          <span class="form-hint">
            {{ getRoleDescription(form.rol) }}
          </span>
        </div>

        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label required">Contraseña (Mín. 8 caracteres)</label>
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
          <span>Registrar Usuario</span>
        </button>
      </template>
    </AdminModal>

    <!-- MODAL 3: Modificar Rol de Usuario -->
    <AdminModal
      :is-open="isRoleModalOpen"
      title="Modificar Rol de Usuario"
      :subtitle="`Actualizar privilegios de seguridad para «${targetUser?.email}»`"
      max-width="460px"
      @close="isRoleModalOpen = false"
    >
      <div class="role-modal-content">
        <div class="form-group">
          <label class="form-label required">Selecciona el Nuevo Rol</label>
          <select v-model="newRole" class="form-select">
            <option value="admin">👑 Administrador (Acceso total)</option>
            <option value="bibliotecario">👤 Bibliotecario / Personal (Gestión operativa)</option>
            <option value="socio">📖 Socio Lector (Catálogo y préstamos)</option>
          </select>
        </div>

        <div class="role-preview-box">
          <span class="preview-title">Nivel de privilegios seleccionado:</span>
          <p class="preview-desc">{{ getRoleDescription(newRole) }}</p>
        </div>

        <p class="role-warning">
          <AlertCircle :size="16" />
          <span>Al confirmar el cambio de rol, las sesiones activas del usuario se revocarán inmediatamente para que inicie sesión con sus nuevos permisos.</span>
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
          <span>Confirmar Cambio de Rol</span>
        </button>
      </template>
    </AdminModal>

    <!-- MODAL 4: Activar / Desactivar Cuenta -->
    <AdminModal
      :is-open="isToggleActiveModalOpen"
      :title="targetUser?.activo ? 'Suspender / Desactivar Cuenta' : 'Reactivar Cuenta de Usuario'"
      :subtitle="targetUser?.email"
      max-width="460px"
      @close="isToggleActiveModalOpen = false"
    >
      <div class="toggle-modal-content">
        <div v-if="targetUser?.activo" class="toggle-alert warning">
          <AlertCircle :size="24" class="warning-icon" />
          <div>
            <h4 class="toggle-alert-title">¿Deseas suspender esta cuenta?</h4>
            <p class="toggle-alert-desc">
              El usuario «{{ targetUser?.nombre }}» no podrá iniciar sesión en Serenidad y todas sus sesiones activas quedarán revocadas de inmediato.
            </p>
          </div>
        </div>

        <div v-else class="toggle-alert info">
          <CheckCircle2 :size="24" class="info-icon" />
          <div>
            <h4 class="toggle-alert-title">¿Deseas reactivar esta cuenta?</h4>
            <p class="toggle-alert-desc">
              El usuario «{{ targetUser?.nombre }}» recuperará el acceso a la plataforma con su contraseña y rol habitual.
            </p>
          </div>
        </div>
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
          <span>{{ targetUser?.activo ? 'Suspender Cuenta' : 'Reactivar Cuenta' }}</span>
        </button>
      </template>
    </AdminModal>
  </div>
</template>

<style scoped>
.admin-users-module {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Encabezado */
.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.module-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
}

.module-subtitle {
  font-size: 0.85rem;
  color: #7a7062;
  margin: 0.25rem 0 0 0;
}

.primary-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-action-btn:hover {
  background-color: #26352c;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.18);
  transform: translateY(-1px);
}

/* Alertas */
.module-alert {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.8rem 1rem;
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

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Tarjetas KPI de Roles */
.role-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 1rem;
}

.role-kpi-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1.15rem 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.role-kpi-card:hover {
  border-color: var(--color-gold, #C49A62);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.role-kpi-card.active-card {
  border-color: var(--color-forest, #34483D);
  background-color: #F8F6EF;
  box-shadow: 0 4px 12px rgba(52, 72, 61, 0.08);
}

.kpi-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-wrap.all-users {
  background-color: #F0EDE4;
  color: var(--color-forest, #34483D);
}

.kpi-icon-wrap.admin-role {
  background-color: #FEF3C7;
  color: #B45309;
}

.kpi-icon-wrap.socio-role {
  background-color: #ECFDF5;
  color: #065F46;
}

.kpi-icon-wrap.biblio-role {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #7A7062;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-value {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  line-height: 1.2;
}

.kpi-hint {
  font-size: 0.72rem;
  color: #9C9181;
}

/* Barra de Pestañas (Role Tabs) */
.role-tabs-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 2px solid var(--color-border, #E5E0D4);
  padding-bottom: 2px;
  overflow-x: auto;
}

.role-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -4px;
  color: #6B6051;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.role-tab-btn:hover {
  color: var(--color-forest, #34483D);
}

.role-tab-btn.active {
  color: var(--color-forest, #34483D);
  border-bottom-color: var(--color-forest, #34483D);
}

.tab-badge {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  background-color: #EFECE3;
  color: #5D5345;
  font-weight: 700;
}

.tab-badge.badge-admin {
  background-color: #FEF3C7;
  color: #B45309;
}

.tab-badge.badge-socio {
  background-color: #ECFDF5;
  color: #065F46;
}

.tab-badge.badge-biblio {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

/* Filtros y Búsqueda */
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
}

.filter-field.search-field {
  flex: 2;
  min-width: 260px;
}

.filter-field.status-field {
  flex: 1;
  min-width: 180px;
}

.filter-label {
  font-size: 0.74rem;
  font-weight: 600;
  color: #7A7062;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #8C8273;
  pointer-events: none;
}

.search-input {
  padding-left: 2.2rem !important;
  padding-right: 2rem !important;
  width: 100%;
}

.clear-input-btn {
  position: absolute;
  right: 0.65rem;
  background: none;
  border: none;
  color: #8C8273;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
}

.filter-input,
.filter-select {
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  background-color: #FAF8F2;
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
  transition: border-color 0.15s ease;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: var(--color-gold, #C49A62);
  background-color: #FFFFFF;
}

.filter-actions {
  display: flex;
  align-items: center;
}

.clear-filter-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.6rem 0.9rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  color: #7A7062;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.clear-filter-btn:hover {
  background-color: #F5F2E9;
  color: var(--color-forest, #34483D);
}

/* Celdas de la Tabla */
.id-cell {
  font-family: monospace;
  font-size: 0.82rem;
  color: #8C8273;
  font-weight: 600;
}

.current-user-row {
  background-color: #FAF8F0 !important;
}

.user-profile-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
  flex-shrink: 0;
}

.user-avatar.admin {
  background-color: #FEF3C7;
  color: #B45309;
  border: 1px solid #FDE68A;
}

.user-avatar.socio {
  background-color: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.user-avatar.bibliotecario {
  background-color: #EFF6FF;
  color: #1D4ED8;
  border: 1px solid #BFDBFE;
}

.user-info-text {
  display: flex;
  flex-direction: column;
}

.user-name-line {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.user-full-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
  font-size: 0.88rem;
}

.self-tag {
  font-size: 0.68rem;
  background-color: var(--color-gold, #C49A62);
  color: #FFFFFF;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  font-weight: 700;
}

.user-sub-id {
  font-size: 0.72rem;
  color: #9C9181;
}

.user-email-text {
  font-size: 0.85rem;
  color: #5D5345;
}

/* Badges de Rol */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.role-badge.admin {
  background-color: #FEF3C7;
  color: #B45309;
  border: 1px solid #FDE68A;
}

.role-badge.bibliotecario {
  background-color: #EFF6FF;
  color: #1D4ED8;
  border: 1px solid #BFDBFE;
}

.role-badge.socio {
  background-color: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

/* Status Pill */
.active-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.22rem 0.6rem;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 600;
}

.active-status-pill.is-active {
  background-color: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.active-status-pill.is-inactive {
  background-color: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

/* Socio ID Badge */
.socio-link-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  color: #6B6051;
  font-weight: 500;
}

.no-socio-badge {
  color: #A39B8F;
  font-size: 0.78rem;
  font-style: italic;
}

.creation-date {
  font-size: 0.82rem;
  color: #7A7062;
}

/* Acciones */
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.icon-action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icon-action-btn.detail-btn {
  color: var(--color-forest, #34483D);
}

.icon-action-btn.detail-btn:hover:not(:disabled) {
  background-color: #F5F2E9;
  border-color: var(--color-forest, #34483D);
}

.icon-action-btn.role-btn {
  color: #B45309;
}

.icon-action-btn.role-btn:hover:not(:disabled) {
  background-color: #FFFBEB;
  border-color: #FDE68A;
}

.icon-action-btn.toggle-btn.deactivate {
  color: #DC2626;
}

.icon-action-btn.toggle-btn.deactivate:hover:not(:disabled) {
  background-color: #FEF2F2;
  border-color: #FCA5A5;
}

.icon-action-btn.toggle-btn.activate {
  color: #059669;
}

.icon-action-btn.toggle-btn.activate:hover:not(:disabled) {
  background-color: #ECFDF5;
  border-color: #A7F3D0;
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
  color: #DC2626;
}

.form-input,
.form-select {
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  background-color: #FAF8F2;
  font-size: 0.88rem;
  color: var(--color-forest, #34483D);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-gold, #C49A62);
  background-color: #FFFFFF;
}

.form-hint {
  font-size: 0.74rem;
  color: #7A7062;
  margin-top: 0.2rem;
}

.password-rule-hint {
  font-size: 0.72rem;
  color: #8C8273;
}

.admin-btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.15rem;
  background-color: transparent;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  color: #5D5345;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-secondary:hover {
  background-color: #F5F2E9;
  color: var(--color-forest, #34483D);
}

.admin-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1.25rem;
  background-color: var(--color-forest, #34483D);
  border: none;
  border-radius: 8px;
  color: var(--color-ivory, #F5F2E9);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-primary:hover:not(:disabled) {
  background-color: #26352c;
  box-shadow: 0 4px 10px rgba(52, 72, 61, 0.2);
}

.admin-btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1.25rem;
  background-color: #DC2626;
  border: 1px solid #B91C1C;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.admin-btn-danger:hover:not(:disabled) {
  background-color: #B91C1C;
  box-shadow: 0 4px 10px rgba(220, 38, 38, 0.2);
}

/* Modal Detalle */
.user-detail-modal {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detail-header-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 10px;
}

.detail-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 700;
}

.detail-avatar.admin {
  background-color: #FEF3C7;
  color: #B45309;
}

.detail-avatar.socio {
  background-color: #ECFDF5;
  color: #065F46;
}

.detail-avatar.bibliotecario {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

.detail-user-main {
  display: flex;
  flex-direction: column;
}

.detail-user-name {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-user-email {
  font-size: 0.85rem;
  color: #6B6051;
}

.detail-attributes-grid {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.attribute-box {
  padding: 0.75rem 0.9rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.attr-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: #7A7062;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.attr-body {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.attr-body.flex-row {
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.attr-desc {
  font-size: 0.78rem;
  color: #8C8273;
  margin: 0;
}

.icon-muted {
  color: #8C8273;
}

/* Modal Cambio de Rol */
.role-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.role-preview-box {
  padding: 0.85rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #7A7062;
  text-transform: uppercase;
}

.preview-desc {
  font-size: 0.82rem;
  color: var(--color-forest, #34483D);
  margin: 0.25rem 0 0 0;
}

.role-warning {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.8rem;
  color: #B45309;
  background-color: #FFFBEB;
  border: 1px solid #FEF3C7;
  padding: 0.75rem 0.9rem;
  border-radius: 8px;
  margin: 0;
  line-height: 1.45;
}

/* Modal Toggle Activo */
.toggle-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toggle-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 1rem;
  border-radius: 10px;
}

.toggle-alert.warning {
  background-color: #FEF2F2;
  border: 1px solid #FECACA;
  color: #991B1B;
}

.toggle-alert.info {
  background-color: #EFF6FF;
  border: 1px solid #BFDBFE;
  color: #1E40AF;
}

.warning-icon {
  color: #DC2626;
  flex-shrink: 0;
}

.info-icon {
  color: #2563EB;
  flex-shrink: 0;
}

.toggle-alert-title {
  font-size: 0.92rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.toggle-alert-desc {
  font-size: 0.82rem;
  line-height: 1.45;
  margin: 0;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsividad */
@media (max-width: 768px) {
  .role-kpi-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-inputs-grid {
    flex-direction: column;
    align-items: stretch;
  }

  .form-row {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .role-kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
