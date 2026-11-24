<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminConfirmModal from '../../components/admin/AdminConfirmModal.vue'
import { bookService } from '../../services/bookService'
import { authorService } from '../../services/authorService'
import { categoryService } from '../../services/categoryService'
import {
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Upload,
  BookOpen,
  Image as ImageIcon,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const books = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

// Filtros
const searchTitle = ref('')
const selectedCategoryId = ref('')
const searchAuthor = ref('')

// Listas maestras para formularios
const authorsList = ref([])
const categoriesList = ref([])

// Notificaciones
const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isFormModalOpen = ref(false)
const isCoverModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const submitting = ref(false)

const isEditing = ref(false)
const currentBookId = ref(null)

// Formulario de Libro
const form = ref({
  titulo: '',
  isbn: '',
  anio_publicacion: new Date().getFullYear(),
  ejemplares: 1,
  autor_id: '',
  categoria_ids: [],
  portada_url: ''
})

// Subida de Portada
const coverFile = ref(null)
const coverPreview = ref('')
const targetBookForCover = ref(null)

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4000)
}

const loadMasters = async () => {
  try {
    const [authRes, catRes] = await Promise.all([
      authorService.getAuthors({ limit: 100 }),
      categoryService.getCategories({ limit: 100 })
    ])
    authorsList.value = authRes.items || []
    categoriesList.value = catRes.items || []
  } catch (err) {
    console.error('Error cargando maestros:', err)
  }
}

const loadBooks = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: limit.value
    }
    if (searchTitle.value) params.buscar = searchTitle.value
    if (searchAuthor.value) params.autor = searchAuthor.value
    if (selectedCategoryId.value) params.categoria_id = Number(selectedCategoryId.value)

    const res = await bookService.getBooks(params)
    // El backend retorna un array directo de libros en /libros o un array
    if (Array.isArray(res)) {
      books.value = res
      total.value = res.length
    } else if (res && res.items) {
      books.value = res.items
      total.value = res.total || 0
    }
  } catch (err) {
    showAlert('Error al consultar el catálogo de libros.', 'error')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  skip.value = 0
  loadBooks()
}

const handleClearFilters = () => {
  searchTitle.value = ''
  selectedCategoryId.value = ''
  searchAuthor.value = ''
  skip.value = 0
  loadBooks()
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadBooks()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadBooks()
  }
}

// Abrir modal de creación
const openCreateModal = () => {
  isEditing.value = false
  currentBookId.value = null
  form.value = {
    titulo: '',
    isbn: '',
    anio_publicacion: new Date().getFullYear(),
    ejemplares: 3,
    autor_id: authorsList.value.length ? authorsList.value[0].id : '',
    categoria_ids: [],
    portada_url: ''
  }
  isFormModalOpen.value = true
}

// Abrir modal de edición
const openEditModal = (book) => {
  isEditing.value = true
  currentBookId.value = book.id
  form.value = {
    titulo: book.titulo,
    isbn: book.isbn,
    anio_publicacion: book.anio_publicacion,
    ejemplares: book.ejemplares,
    autor_id: book.autor_id || (book.autor ? book.autor.id : ''),
    categoria_ids: book.categorias ? book.categorias.map(c => c.id) : [],
    portada_url: book.portada_url || ''
  }
  isFormModalOpen.value = true
}

// Guardar libro (crear o editar)
const submitBookForm = async () => {
  if (!form.value.titulo || !form.value.isbn || !form.value.autor_id) {
    showAlert('Completa los campos obligatorios.', 'error')
    return
  }

  if (form.value.categoria_ids.length === 0) {
    showAlert('Selecciona al menos una categoría.', 'error')
    return
  }

  if (form.value.isbn.length !== 13 || !/^\d{13}$/.test(form.value.isbn)) {
    showAlert('El código ISBN debe tener exactamente 13 dígitos numéricos.', 'error')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value) {
      await bookService.updateBook(currentBookId.value, form.value)
      showAlert(`Libro «${form.value.titulo}» actualizado exitosamente.`)
    } else {
      await bookService.createBook(form.value)
      showAlert(`Libro «${form.value.titulo}» registrado exitosamente.`)
    }
    isFormModalOpen.value = false
    loadBooks()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al procesar el libro.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal eliminar
const openDeleteModal = (book) => {
  currentBookId.value = book.id
  targetBookForCover.value = book
  isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  submitting.value = true
  try {
    await bookService.deleteBook(currentBookId.value)
    showAlert('Libro retirado del catálogo.')
    isDeleteModalOpen.value = false
    loadBooks()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se pudo eliminar el libro (puede tener préstamos activos).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Modal subir portada
const openCoverModal = (book) => {
  targetBookForCover.value = book
  coverFile.value = null
  coverPreview.value = book.portada_url || ''
  isCoverModalOpen.value = true
}

const onFileSelected = (e) => {
  const file = e.target.files[0]
  if (file) {
    coverFile.value = file
    coverPreview.value = URL.createObjectURL(file)
  }
}

const submitCoverUpload = async () => {
  if (!coverFile.value) {
    showAlert('Selecciona un archivo de imagen.', 'error')
    return
  }

  submitting.value = true
  try {
    await bookService.uploadCover(targetBookForCover.value.id, coverFile.value)
    showAlert(`Portada actualizada para «${targetBookForCover.value.titulo}» vía Cloudinary.`)
    isCoverModalOpen.value = false
    loadBooks()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al subir la imagen a Cloudinary.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Toggle selección de categoría
const toggleCategory = (catId) => {
  const idx = form.value.categoria_ids.indexOf(catId)
  if (idx > -1) {
    form.value.categoria_ids.splice(idx, 1)
  } else {
    if (form.value.categoria_ids.length >= 5) {
      showAlert('Máximo 5 categorías permitidas.', 'error')
      return
    }
    form.value.categoria_ids.push(catId)
  }
}

onMounted(() => {
  loadMasters()
  loadBooks()
})
</script>

<template>
  <div class="admin-module-page">
    <!-- Header del Módulo -->
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Catálogo de Libros</h2>
        <p class="module-subtitle">Administra los títulos, ejemplares disponibles, portadas en Cloudinary y autores</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <Plus :size="16" />
        <span>Registrar Nuevo Libro</span>
      </button>
    </div>

    <!-- Alerta Flotante -->
    <div v-if="alertMsg.text" class="module-alert" :class="alertMsg.type">
      <CheckCircle2 v-if="alertMsg.type === 'success'" :size="18" />
      <AlertCircle v-else :size="18" />
      <span>{{ alertMsg.text }}</span>
    </div>

    <!-- Barra de Filtros y Búsqueda -->
    <div class="filter-card">
      <div class="filter-inputs-grid">
        <div class="filter-field">
          <label class="filter-label">Buscar por Título</label>
          <div class="search-input-box">
            <Search :size="16" class="search-icon" />
            <input
              v-model="searchTitle"
              type="text"
              placeholder="Ej. Cien Años de Soledad..."
              class="filter-input"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>

        <div class="filter-field">
          <label class="filter-label">Buscar por Autor</label>
          <input
            v-model="searchAuthor"
            type="text"
            placeholder="Ej. García Márquez..."
            class="filter-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="filter-field">
          <label class="filter-label">Categoría</label>
          <select v-model="selectedCategoryId" class="filter-select" @change="handleSearch">
            <option value="">Todas las categorías</option>
            <option v-for="cat in categoriesList" :key="cat.id" :value="cat.id">
              {{ cat.nombre }}
            </option>
          </select>
        </div>

        <div class="filter-actions">
          <button class="filter-btn" @click="handleSearch">
            <Filter :size="15" />
            <span>Filtrar</span>
          </button>
          <button class="clear-filter-btn" @click="handleClearFilters" title="Limpiar filtros">
            <X :size="15" />
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla de Libros -->
    <AdminTable
      :loading="loading"
      :items-count="books.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay libros registrados"
      empty-subtitle="Utiliza el botón «Registrar Nuevo Libro» para agregar el primer ejemplar."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Portada</th>
          <th>Título & ISBN</th>
          <th>Autor</th>
          <th>Categorías</th>
          <th>Inventario</th>
          <th>Disponibles</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="book in books" :key="book.id">
          <td>#{{ book.id }}</td>
          <td>
            <div class="book-cover-cell">
              <img
                v-if="book.portada_url"
                :src="book.portada_url"
                :alt="book.titulo"
                class="cover-thumbnail"
              />
              <div v-else class="no-cover-placeholder" title="Sin portada">
                <BookOpen :size="16" />
              </div>
            </div>
          </td>
          <td>
            <div class="book-title-meta">
              <span class="book-name">{{ book.titulo }}</span>
              <span class="book-isbn">ISBN: {{ book.isbn }} · Año {{ book.anio_publicacion }}</span>
            </div>
          </td>
          <td>
            <span class="author-name">{{ book.autor?.nombre || 'Autor desconocido' }}</span>
          </td>
          <td>
            <div class="tags-cluster">
              <span v-for="cat in book.categorias" :key="cat.id" class="category-tag">
                {{ cat.nombre }}
              </span>
              <span v-if="!book.categorias || book.categorias.length === 0" class="no-tags">-</span>
            </div>
          </td>
          <td>
            <span class="inventory-badge">{{ book.ejemplares }} copias</span>
          </td>
          <td>
            <span
              class="availability-pill"
              :class="{
                'available': (book.disponibles ?? book.ejemplares) > 0,
                'exhausted': (book.disponibles ?? book.ejemplares) === 0
              }"
            >
              {{ book.disponibles ?? book.ejemplares }} disponibles
            </span>
          </td>
          <td>
            <div class="actions-cell">
              <button
                class="icon-action-btn"
                title="Subir/Cambiar portada Cloudinary"
                @click="openCoverModal(book)"
              >
                <Upload :size="16" />
              </button>
              <button
                class="icon-action-btn"
                title="Editar libro"
                @click="openEditModal(book)"
              >
                <Edit :size="16" />
              </button>
              <button
                class="icon-action-btn delete-btn"
                title="Eliminar libro"
                @click="openDeleteModal(book)"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Formulario Libro (Crear / Editar) -->
    <AdminModal
      :is-open="isFormModalOpen"
      :title="isEditing ? 'Editar Libro' : 'Registrar Nuevo Libro'"
      :subtitle="isEditing ? `Modificando ID #${currentBookId}` : 'Completa los metadatos requeridos por el catálogo'"
      max-width="620px"
      @close="isFormModalOpen = false"
    >
      <form class="admin-modal-form" @submit.prevent="submitBookForm">
        <div class="form-row">
          <div class="form-group flex-2">
            <label class="form-label required">Título del Libro</label>
            <input
              v-model="form.titulo"
              type="text"
              class="form-input"
              placeholder="Ej. El Aleph"
              required
            />
          </div>

          <div class="form-group flex-1">
            <label class="form-label required">Código ISBN (13 dígitos)</label>
            <input
              v-model="form.isbn"
              type="text"
              class="form-input"
              placeholder="9780142437230"
              maxlength="13"
              required
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group flex-1">
            <label class="form-label required">Autor</label>
            <select v-model="form.autor_id" class="form-select" required>
              <option value="" disabled>Selecciona un autor</option>
              <option v-for="a in authorsList" :key="a.id" :value="a.id">
                {{ a.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group flex-1">
            <label class="form-label required">Año de Publicación</label>
            <input
              v-model.number="form.anio_publicacion"
              type="number"
              class="form-input"
              min="1450"
              :max="new Date().getFullYear()"
              required
            />
          </div>

          <div class="form-group flex-1">
            <label class="form-label required">Ejemplares (1 a 50)</label>
            <input
              v-model.number="form.ejemplares"
              type="number"
              class="form-input"
              min="1"
              max="50"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label required">Categorías Asociadas (Entre 1 y 5)</label>
          <div class="category-chips-selector">
            <button
              v-for="cat in categoriesList"
              :key="cat.id"
              type="button"
              class="chip-toggle"
              :class="{ 'is-selected': form.categoria_ids.includes(cat.id) }"
              @click="toggleCategory(cat.id)"
            >
              {{ cat.nombre }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">URL de Portada Externa (Opcional)</label>
          <input
            v-model="form.portada_url"
            type="url"
            class="form-input"
            placeholder="https://..."
          />
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
          @click="submitBookForm"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>{{ isEditing ? 'Guardar Cambios' : 'Registrar Libro' }}</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Subida de Portada a Cloudinary -->
    <AdminModal
      :is-open="isCoverModalOpen"
      title="Actualizar Portada en Cloudinary"
      :subtitle="`Asociar imagen oficial para «${targetBookForCover?.titulo}»`"
      max-width="480px"
      @close="isCoverModalOpen = false"
    >
      <div class="cover-upload-area">
        <div class="cover-preview-box">
          <img
            v-if="coverPreview"
            :src="coverPreview"
            alt="Vista previa de portada"
            class="cover-preview-img"
          />
          <div v-else class="cover-placeholder-box">
            <ImageIcon :size="40" class="placeholder-icon" />
            <span>Selecciona un archivo JPG, PNG o WEBP</span>
          </div>
        </div>

        <div class="file-picker-row">
          <input
            id="cover-file-input"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="hidden-file-input"
            @change="onFileSelected"
          />
          <label for="cover-file-input" class="file-picker-label">
            <Upload :size="16" />
            <span>Examinar Imagen...</span>
          </label>
          <span v-if="coverFile" class="file-chosen-name">{{ coverFile.name }}</span>
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          class="admin-btn-secondary"
          :disabled="submitting"
          @click="isCoverModalOpen = false"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="admin-btn-primary"
          :disabled="submitting || !coverFile"
          @click="submitCoverUpload"
        >
          <Loader2 v-if="submitting" :size="16" class="spin-icon" />
          <span>Subir a Cloudinary</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Confirmar Eliminación -->
    <AdminConfirmModal
      :is-open="isDeleteModalOpen"
      title="Eliminar Libro"
      :message="`¿Deseas retirar «${targetBookForCover?.titulo}» del catálogo? No podrá eliminarse si tiene préstamos activos asociados.`"
      confirm-text="Retirar Libro"
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
  min-width: 180px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7a7062;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.search-input-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #8c8273;
}

.filter-input {
  width: 100%;
  padding: 0.55rem 0.75rem 0.55rem 2.2rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.filter-field > .filter-input {
  padding-left: 0.75rem;
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

.book-cover-cell {
  width: 44px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover-placeholder {
  color: #8c8273;
}

.book-title-meta {
  display: flex;
  flex-direction: column;
}

.book-name {
  font-weight: 600;
  color: var(--color-forest, #34483D);
  font-size: 0.9rem;
}

.book-isbn {
  font-size: 0.74rem;
  color: #7a7062;
}

.author-name {
  font-size: 0.85rem;
  color: var(--color-forest, #34483D);
}

.tags-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.category-tag {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background-color: var(--color-ivory, #F5F2E9);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  font-size: 0.72rem;
  color: #6b6051;
}

.inventory-badge {
  font-size: 0.82rem;
  color: #5d5345;
  font-weight: 500;
}

.availability-pill {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 600;
}

.availability-pill.available {
  background-color: #ecfdf5;
  color: #065f46;
}

.availability-pill.exhausted {
  background-color: #fef2f2;
  color: #991b1b;
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
  align-items: center;
  justify-content: center;
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

/* Formularios modales */
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
.flex-2 { flex: 2; }

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

.category-chips-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  max-height: 120px;
  overflow-y: auto;
  padding: 0.4rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
}

.chip-toggle {
  background: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.78rem;
  color: #7a7062;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip-toggle.is-selected {
  background-color: var(--color-forest, #34483D);
  color: var(--color-ivory, #F5F2E9);
  border-color: var(--color-forest, #34483D);
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

.admin-btn-primary:hover:not(:disabled) {
  background-color: #26352c;
}

.cover-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.cover-preview-box {
  width: 140px;
  height: 200px;
  border-radius: 8px;
  border: 1px dashed var(--color-border, #E5E0D4);
  background-color: #FAF8F2;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.cover-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-box {
  padding: 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #8c8273;
  font-size: 0.75rem;
}

.hidden-file-input {
  display: none;
}

.file-picker-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
  cursor: pointer;
}

.file-chosen-name {
  font-size: 0.78rem;
  color: #7a7062;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
