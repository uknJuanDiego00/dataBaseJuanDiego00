<script setup>
import { ref, onMounted } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminConfirmModal from '../../components/admin/AdminConfirmModal.vue'
import { authorService } from '../../services/authorService'
import {
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  BookOpen,
  Feather,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const authors = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

const filterNationality = ref('')

const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isFormModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isBooksModalOpen = ref(false)
const submitting = ref(false)

const isEditing = ref(false)
const currentAuthorId = ref(null)
const targetAuthor = ref(null)
const authorBooksList = ref([])
const loadingBooks = ref(false)

const form = ref({
  nombre: '',
  nacionalidad: '',
  anio_nacimiento: ''
})

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4000)
}

const loadAuthors = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }
    if (filterNationality.value) params.nacionalidad = filterNationality.value

    const res = await authorService.getAuthors(params)
    authors.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar autores.', 'error')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  skip.value = 0
  loadAuthors()
}

const handleClearFilter = () => {
  filterNationality.value = ''
  skip.value = 0
  loadAuthors()
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadAuthors()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadAuthors()
  }
}

const openCreateModal = () => {
  isEditing.value = false
  currentAuthorId.value = null
  form.value = {
    nombre: '',
    nacionalidad: '',
    anio_nacimiento: ''
  }
  isFormModalOpen.value = true
}

const openEditModal = (author) => {
  isEditing.value = true
  currentAuthorId.value = author.id
  form.value = {
    nombre: author.nombre,
    nacionalidad: author.nacionalidad || '',
    anio_nacimiento: author.anio_nacimiento || ''
  }
  isFormModalOpen.value = true
}

const submitForm = async () => {
  if (!form.value.nombre.trim()) {
    showAlert('El nombre del autor es obligatorio.', 'error')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value) {
      await authorService.updateAuthor(currentAuthorId.value, form.value)
      showAlert(`Autor «${form.value.nombre}» actualizado.`)
    } else {
      await authorService.createAuthor(form.value)
      showAlert(`Autor «${form.value.nombre}» registrado.`)
    }
    isFormModalOpen.value = false
    loadAuthors()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al guardar el autor.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

const openDeleteModal = (author) => {
  currentAuthorId.value = author.id
  targetAuthor.value = author
  isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  submitting.value = true
  try {
    await authorService.deleteAuthor(currentAuthorId.value)
    showAlert('Autor eliminado exitosamente.')
    isDeleteModalOpen.value = false
    loadAuthors()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se puede eliminar el autor (tiene libros asociados).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Ver libros del autor
const openAuthorBooksModal = async (author) => {
  targetAuthor.value = author
  isBooksModalOpen.value = true
  loadingBooks.value = true
  authorBooksList.value = []
  try {
    const res = await authorService.getAuthorBooks(author.id)
    authorBooksList.value = res.items || res || []
  } catch (err) {
    console.error('Error cargando libros del autor:', err)
  } finally {
    loadingBooks.value = false
  }
}

onMounted(() => {
  loadAuthors()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Autores Literarios</h2>
        <p class="module-subtitle">Crea, edita y consulta el repertorio de autores y sus obras publicadas</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <Plus :size="16" />
        <span>Registrar Nuevo Autor</span>
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
          <label class="filter-label">Filtrar por Nacionalidad</label>
          <input
            v-model="filterNationality"
            type="text"
            placeholder="Ej. Colombiana, Argentina, Española..."
            class="filter-input"
            @keyup.enter="handleFilter"
          />
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
      :items-count="authors.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay autores registrados"
      empty-subtitle="Utiliza «Registrar Nuevo Autor» para ingresar el primer autor."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Nombre del Autor</th>
          <th>Nacionalidad</th>
          <th>Año Nacimiento</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="author in authors" :key="author.id">
          <td>#{{ author.id }}</td>
          <td>
            <div class="author-name-cell">
              <span class="author-full-name">{{ author.nombre }}</span>
            </div>
          </td>
          <td>
            <span class="author-nationality">{{ author.nacionalidad || 'No especificada' }}</span>
          </td>
          <td>
            <span class="birth-year">{{ author.anio_nacimiento || '—' }}</span>
          </td>
          <td>
            <div class="actions-cell">
              <button
                class="icon-action-btn"
                title="Consultar libros del autor"
                @click="openAuthorBooksModal(author)"
              >
                <BookOpen :size="16" />
              </button>
              <button
                class="icon-action-btn"
                title="Editar autor"
                @click="openEditModal(author)"
              >
                <Edit :size="16" />
              </button>
              <button
                class="icon-action-btn delete-btn"
                title="Eliminar autor"
                @click="openDeleteModal(author)"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Formulario Autor -->
    <AdminModal
      :is-open="isFormModalOpen"
      :title="isEditing ? 'Editar Autor' : 'Registrar Nuevo Autor'"
      :subtitle="isEditing ? `Modificando ID #${currentAuthorId}` : 'Completa los datos del autor'"
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
            placeholder="Ej. Jorge Luis Borges"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label">Nacionalidad</label>
            <input
              v-model="form.nacionalidad"
              type="text"
              class="form-input"
              placeholder="Ej. Argentina"
            />
          </div>

          <div class="form-group flex-1">
            <label class="form-label">Año de Nacimiento</label>
            <input
              v-model.number="form.anio_nacimiento"
              type="number"
              class="form-input"
              placeholder="1899"
              min="1000"
              :max="new Date().getFullYear()"
            />
          </div>
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
          <span>{{ isEditing ? 'Guardar Cambios' : 'Registrar Autor' }}</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Libros del Autor -->
    <AdminModal
      :is-open="isBooksModalOpen"
      :title="`Obras de ${targetAuthor?.nombre}`"
      subtitle="Libros registrados en el catálogo bajo este autor"
      max-width="560px"
      @close="isBooksModalOpen = false"
    >
      <div v-if="loadingBooks" class="books-loader-box">
        <Loader2 :size="24" class="spin-icon" />
        <span>Consultando obras...</span>
      </div>
      <div v-else-if="authorBooksList.length === 0" class="no-books-box">
        <Feather :size="32" class="empty-icon" />
        <p>Este autor no tiene libros registrados en el catálogo actualmente.</p>
      </div>
      <ul v-else class="author-books-sublist">
        <li v-for="b in authorBooksList" :key="b.id" class="author-book-row">
          <div class="book-mini-meta">
            <span class="sublist-book-title">{{ b.titulo }}</span>
            <span class="sublist-book-isbn">ISBN: {{ b.isbn }} · Año {{ b.anio_publicacion }}</span>
          </div>
          <span class="sublist-copies-badge">{{ b.ejemplares }} ejemplares</span>
        </li>
      </ul>

      <template #footer>
        <button type="button" class="admin-btn-secondary" @click="isBooksModalOpen = false">
          Cerrar
        </button>
      </template>
    </AdminModal>

    <!-- Modal Eliminar -->
    <AdminConfirmModal
      :is-open="isDeleteModalOpen"
      title="Eliminar Autor"
      :message="`¿Deseas eliminar a «${targetAuthor?.nombre}»? Esta acción fallará si el autor tiene libros asociados en el catálogo.`"
      confirm-text="Eliminar Autor"
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

.filter-input {
  width: 100%;
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

.author-full-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.author-nationality {
  font-size: 0.85rem;
  color: #6b6051;
}

.birth-year {
  font-size: 0.85rem;
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
  transition: all 0.15s ease;
  display: flex;
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

.form-input {
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

.books-loader-box {
  padding: 2.5rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #7a7062;
  font-size: 0.85rem;
}

.no-books-box {
  padding: 2.5rem 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #8c8273;
  font-size: 0.85rem;
}

.empty-icon {
  color: var(--color-gold, #C49A62);
}

.author-books-sublist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: 280px;
  overflow-y: auto;
}

.author-book-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  background-color: #FAF8F2;
  border-radius: 6px;
  border: 1px solid #ECE7DC;
}

.book-mini-meta {
  display: flex;
  flex-direction: column;
}

.sublist-book-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.sublist-book-isbn {
  font-size: 0.72rem;
  color: #7a7062;
}

.sublist-copies-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #a4763c;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
