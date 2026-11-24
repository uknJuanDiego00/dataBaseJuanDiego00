<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import AdminSidebar from '../components/admin/AdminSidebar.vue'
import AdminHeader from '../components/admin/AdminHeader.vue'

const route = useRoute()
const isSidebarOpen = ref(false)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}
</script>

<template>
  <div class="admin-app-layout">
    <!-- Barra Lateral -->
    <AdminSidebar :is-open="isSidebarOpen" @close="closeSidebar" />

    <!-- Contenedor Principal -->
    <div class="admin-main-wrapper">
      <AdminHeader
        :title="route.meta.title || 'Panel de Administración'"
        :subtitle="route.meta.subtitle || ''"
        @toggle-sidebar="toggleSidebar"
      />

      <main class="admin-page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-app-layout {
  min-height: 100vh;
  background-color: var(--color-ivory, #F5F2E9);
  display: flex;
}

.admin-main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.25s ease;
}

@media (min-width: 901px) {
  .admin-main-wrapper {
    margin-left: 260px;
  }
}

.admin-page-content {
  flex: 1;
  padding: 1.75rem 2rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .admin-page-content {
    padding: 1rem;
  }
}
</style>
