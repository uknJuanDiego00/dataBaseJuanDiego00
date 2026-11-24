<script setup>
import { ref, onMounted } from 'vue'
import AdminTable from '../../components/admin/AdminTable.vue'
import AdminModal from '../../components/admin/AdminModal.vue'
import AdminConfirmModal from '../../components/admin/AdminConfirmModal.vue'
import { categoryService } from '../../services/categoryService'
import { bookService } from '../../services/bookService'
import {
  Plus,
  Edit,
  Trash2,
  BookOpen,
  Tags,
  Loader2,
  CheckCircle2,
  AlertCircle
} from 'lucide-vue-next'

const categories = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)

const alertMsg = ref({ text: '', type: 'success' })

// Modales
const isFormModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isBooksModalOpen = ref(false)
const submitting = ref(false)

const isEditing = ref(false)
const currentCategoryId = ref(null)
const targetCategory = ref(null)

const categoryBooks = ref([])
const loadingBooks = ref(false)

const form = ref({
  nombre: '',
  descripcion: ''
})

const showAlert = (text, type = 'success') => {
  alertMsg.value = { text, type }
  setTimeout(() => {
    alertMsg.value.text = ''
  }, 4000)
}

const loadCategories = async () => {
  loading.value = true
  try {
    const res = await categoryService.getCategories({
      skip: skip.value,
      limit: limit.value
    })
    categories.value = res.items || []
    total.value = res.total || 0
  } catch (err) {
    showAlert('Error al consultar categorías.', 'error')
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (skip.value >= limit.value) {
    skip.value -= limit.value
    loadCategories()
  }
}

const nextPage = () => {
  if (skip.value + limit.value < total.value) {
    skip.value += limit.value
    loadCategories()
  }
}

const openCreateModal = () => {
  isEditing.value = false
  currentCategoryId.value = null
  form.value = {
    nombre: '',
    descripcion: ''
  }
  isFormModalOpen.value = true
}

const openEditModal = (cat) => {
  isEditing.value = true
  currentCategoryId.value = cat.id
  form.value = {
    nombre: cat.nombre,
    descripcion: cat.descripcion || ''
  }
  isFormModalOpen.value = true
}

const submitForm = async () => {
  if (!form.value.nombre.trim() || form.value.nombre.trim().length < 3) {
    showAlert('El nombre de la categoría debe tener al menos 3 caracteres.', 'error')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value) {
      await categoryService.updateCategory(currentCategoryId.value, form.value)
      showAlert(`Categoría «${form.value.nombre}» actualizada.`)
    } else {
      await categoryService.createCategory(form.value)
      showAlert(`Categoría «${form.value.nombre}» creada.`)
    }
    isFormModalOpen.value = false
    loadCategories()
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al guardar la categoría.'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

const openDeleteModal = (cat) => {
  currentCategoryId.value = cat.id
  targetCategory.value = cat
  isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  submitting.value = true
  try {
    await categoryService.deleteCategory(currentCategoryId.value)
    showAlert('Categoría eliminada del catálogo.')
    isDeleteModalOpen.value = false
    loadCategories()
  } catch (err) {
    const msg = err.response?.data?.detail || 'No se puede eliminar la categoría (tiene libros asociados).'
    showAlert(msg, 'error')
  } finally {
    submitting.value = false
  }
}

// Consultar libros asociados
const openCategoryBooksModal = async (cat) => {
  targetCategory.value = cat
  isBooksModalOpen.value = true
  loadingBooks.value = true
  categoryBooks.value = []
  try {
    const res = await bookService.getBooks({ categoria_id: cat.id, limit: 50 })
    categoryBooks.value = Array.isArray(res) ? res : (res.items || [])
  } catch (err) {
    console.error('Error cargando libros de categoría:', err)
  } finally {
    loadingBooks.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Gestión de Categorías</h2>
        <p class="module-subtitle">Clasifica y organiza el acervo bibliográfico por áreas del conocimiento</p>
      </div>

      <button class="primary-action-btn" @click="openCreateModal">
        <Plus :size="16" />
        <span>Crear Nueva Categoría</span>
      </button>
    </div>

    <!-- Alerta Flotante -->
    <div v-if="alertMsg.text" class="module-alert" :class="alertMsg.type">
      <CheckCircle2 v-if="alertMsg.type === 'success'" :size="18" />
      <AlertCircle v-else :size="18" />
      <span>{{ alertMsg.text }}</span>
    </div>

    <!-- Tabla -->
    <AdminTable
      :loading="loading"
      :items-count="categories.length"
      :total="total"
      :skip="skip"
      :limit="limit"
      empty-title="No hay categorías registradas"
      empty-subtitle="Utiliza «Crear Nueva Categoría» para agregar áreas temáticas."
      @prev-page="prevPage"
      @next-page="nextPage"
    >
      <template #header>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Descripción</th>
          <th style="text-align: right;">Acciones</th>
        </tr>
      </template>

      <template #body>
        <tr v-for="cat in categories" :key="cat.id">
          <td>#{{ cat.id }}</td>
          <td>
            <span class="category-name-badge">{{ cat.nombre }}</span>
          </td>
          <td>
            <span class="category-desc-text">{{ cat.descripcion || 'Sin descripción detallada' }}</span>
          </td>
          <td>
            <div class="actions-cell">
              <button
                class="icon-action-btn"
                title="Consultar libros asociados"
                @click="openCategoryBooksModal(cat)"
              >
                <BookOpen :size="16" />
              </button>
              <button
                class="icon-action-btn"
                title="Editar categoría"
                @click="openEditModal(cat)"
              >
                <Edit :size="16" />
              </button>
              <button
                class="icon-action-btn delete-btn"
                title="Eliminar categoría"
                @click="openDeleteModal(cat)"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </td>
        </tr>
      </template>
    </AdminTable>

    <!-- Modal Formulario Categoría -->
    <AdminModal
      :is-open="isFormModalOpen"
      :title="isEditing ? 'Editar Categoría' : 'Nueva Categoría'"
      :subtitle="isEditing ? `Modificando ID #${currentCategoryId}` : 'Define el nombre y alcance de la categoría'"
      max-width="480px"
      @close="isFormModalOpen = false"
    >
      <form class="admin-modal-form" @submit.prevent="submitForm">
        <div class="form-group">
          <label class="form-label required">Nombre de la Categoría</label>
          <input
            v-model="form.nombre"
            type="text"
            class="form-input"
            placeholder="Ej. filosofía, ciencia ficción..."
            minlength="3"
            maxlength="50"
            required
          />
          <span class="form-hint">El sistema lo almacenará en minúsculas normalizadas.</span>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción Opcional (Hasta 200 caracteres)</label>
          <textarea
            v-model="form.descripcion"
            class="form-textarea"
            rows="3"
            maxlength="200"
            placeholder="Breve reseña sobre los libros que abarca esta categoría..."
          ></textarea>
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
          <span>{{ isEditing ? 'Guardar Cambios' : 'Crear Categoría' }}</span>
        </button>
      </template>
    </AdminModal>

    <!-- Modal Libros de la Categoría -->
    <AdminModal
      :is-open="isBooksModalOpen"
      :title="`Libros en «${targetCategory?.nombre}»`"
      subtitle="Obras asociadas actualmente a esta categoría temática"
      max-width="560px"
      @close="isBooksModalOpen = false"
    >
      <div v-if="loadingBooks" class="books-loader-box">
        <Loader2 :size="24" class="spin-icon" />
        <span>Consultando libros asociados...</span>
      </div>
      <div v-else-if="categoryBooks.length === 0" class="no-books-box">
        <Tags :size="32" class="empty-icon" />
        <p>No hay libros asociados a esta categoría en este momento.</p>
      </div>
      <ul v-else class="cat-books-sublist">
        <li v-for="b in categoryBooks" :key="b.id" class="cat-book-row">
          <div class="book-mini-meta">
            <span class="sublist-book-title">{{ b.titulo }}</span>
            <span class="sublist-book-meta">{{ b.autor?.nombre }} · Año {{ b.anio_publicacion }}</span>
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

    <!-- Modal Confirmar Eliminación -->
    <AdminConfirmModal
      :is-open="isDeleteModalOpen"
      title="Eliminar Categoría"
      :message="`¿Deseas eliminar la categoría «${targetCategory?.nombre}»? Fallará si contiene libros clasificados.`"
      confirm-text="Eliminar Categoría"
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

.category-name-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 14px;
  font-weight: 600;
  color: var(--color-forest, #34483D);
}

.category-desc-text {
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
.form-textarea {
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 6px;
  background-color: #FAF8F2;
  font-size: 0.88rem;
  color: var(--color-forest, #34483D);
  font-family: inherit;
}

.form-hint {
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

.cat-books-sublist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: 280px;
  overflow-y: auto;
}

.cat-book-row {
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

.sublist-book-meta {
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
