import { createRouter, createWebHistory } from 'vue-router'

// Vistas Públicas de Lectura
import HomeView from '../views/HomeView.vue'
import CatalogView from '../views/CatalogView.vue'
import CategoriesView from '../views/CategoriesView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import MyBooksView from '../views/MyBooksView.vue'
import AboutView from '../views/AboutView.vue'

// Vistas y Layout del Panel de Administración
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminLogin from '../views/admin/AdminLogin.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminBooks from '../views/admin/AdminBooks.vue'
import AdminAuthors from '../views/admin/AdminAuthors.vue'
import AdminCategories from '../views/admin/AdminCategories.vue'
import AdminLoans from '../views/admin/AdminLoans.vue'
import AdminMembers from '../views/admin/AdminMembers.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminReports from '../views/admin/AdminReports.vue'
import AdminPages from '../views/admin/AdminPages.vue'

const routes = [
  // -------------------------------------------------------------
  // EXPERIENCIA PÚBLICA DE LECTURA (SERENIDAD)
  // -------------------------------------------------------------
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

  // -------------------------------------------------------------
  // ACCESO Y AUTENTICACIÓN ADMINISTRATIVA
  // -------------------------------------------------------------
  {
    path: '/admin/login',
    name: 'admin-login',
    component: AdminLogin,
    meta: {
      title: 'Acceso Administrativo — Serenidad',
      guestOnly: true
    }
  },

  // -------------------------------------------------------------
  // PANEL ADMINISTRATIVO PROTEGIDO (/admin)
  // -------------------------------------------------------------
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      roles: ['admin', 'bibliotecario']
    },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: AdminDashboard,
        meta: {
          title: 'Cuadro de Mando General',
          subtitle: 'Métricas cuantitativas e indicadores en tiempo real'
        }
      },
      {
        path: 'libros',
        name: 'admin-books',
        component: AdminBooks,
        meta: {
          title: 'Gestión de Libros',
          subtitle: 'Catálogo, inventario y portadas en Cloudinary'
        }
      },
      {
        path: 'autores',
        name: 'admin-authors',
        component: AdminAuthors,
        meta: {
          title: 'Gestión de Autores',
          subtitle: 'Repertorio literario y obras asociadas'
        }
      },
      {
        path: 'categorias',
        name: 'admin-categories',
        component: AdminCategories,
        meta: {
          title: 'Gestión de Categorías',
          subtitle: 'Clasificación temática del acervo'
        }
      },
      {
        path: 'prestamos',
        name: 'admin-loans',
        component: AdminLoans,
        meta: {
          title: 'Gestión de Préstamos',
          subtitle: 'Control de entregas, plazos, devoluciones y multas'
        }
      },
      {
        path: 'socios',
        name: 'admin-members',
        component: AdminMembers,
        meta: {
          title: 'Gestión de Socios',
          subtitle: 'Fichas de lectores e historial de préstamos'
        }
      },
      {
        path: 'usuarios',
        name: 'admin-users',
        component: AdminUsers,
        meta: {
          title: 'Gestión de Usuarios',
          subtitle: 'Cuentas del sistema y control de roles (Solo Admin)',
          roles: ['admin']
        }
      },
      {
        path: 'reportes',
        name: 'admin-reports',
        component: AdminReports,
        meta: {
          title: 'Centro de Reportes',
          subtitle: 'Estadísticas agregadas y exportación de datos'
        }
      },
      {
        path: 'paginas',
        name: 'admin-pages',
        component: AdminPages,
        meta: {
          title: 'Arquitectura de Paginación',
          subtitle: 'Inspección técnica de schemas/pagina.py y Pagina[T]'
        }
      }
    ]
  },

  // Redirección para rutas no encontradas
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

// Guardia de navegación para seguridad y autenticación
router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} — Serenidad`
  }

  const token = localStorage.getItem('serenidad_access_token')
  const user = JSON.parse(localStorage.getItem('serenidad_user') || 'null')

  // Redireccionar si el usuario ya está autenticado y visita /admin/login
  if (to.meta.guestOnly && token && user) {
    if (user.rol === 'admin' || user.rol === 'bibliotecario') {
      return next('/admin')
    }
  }

  // Verificar si la ruta requiere autenticación
  const matchedAuth = to.matched.some(record => record.meta.requiresAuth)
  if (matchedAuth) {
    if (!token || !user) {
      return next({
        path: '/admin/login',
        query: { redirect: to.fullPath }
      })
    }

    // Verificar roles permitidos
    const requiredRoles = to.meta.roles || to.matched.find(r => r.meta.roles)?.meta.roles
    if (requiredRoles && !requiredRoles.includes(user.rol)) {
      // Si requiere rol específico que el usuario no tiene (ej. usuarios requiere admin y es biblio)
      return next('/admin')
    }
  }

  next()
})

export default router
