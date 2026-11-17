import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CatalogView from '../views/CatalogView.vue'
import CategoriesView from '../views/CategoriesView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import MyBooksView from '../views/MyBooksView.vue'
import AboutView from '../views/AboutView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { title: 'Inicio — Un Refugio de Conocimiento y Serenidad' }
  },
  {
    path: '/catalogo',
    name: 'catalog',
    component: CatalogView,
    meta: { title: 'Catálogo de Libros — Biblioteca' }
  },
  {
    path: '/categorias',
    name: 'categories',
    component: CategoriesView,
    meta: { title: 'Categorías — Biblioteca' }
  },
  {
    path: '/libro/:id',
    name: 'book-detail',
    component: BookDetailView,
    meta: { title: 'Detalle de Libro — Biblioteca' }
  },
  {
    path: '/mis-libros',
    name: 'my-books',
    component: MyBooksView,
    meta: { title: 'Mis Libros Favoritos — Biblioteca' }
  },
  {
    path: '/nosotros',
    name: 'about',
    component: AboutView,
    meta: { title: 'Nosotros — Un Refugio de Serenidad' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, behavior: 'smooth' }
  }
})

router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
