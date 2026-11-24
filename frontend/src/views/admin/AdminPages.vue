<script setup>
import { FileCode, Database, CheckCircle2, Layers, Cpu, Compass } from 'lucide-vue-next'
</script>

<template>
  <div class="admin-module-page">
    <div class="module-header">
      <div>
        <h2 class="module-title">Arquitectura de Paginación del Sistema</h2>
        <p class="module-subtitle">Inspección técnica del esquema Pagina[T] y el motor de paginación REST</p>
      </div>
    </div>

    <div class="architecture-card">
      <div class="card-icon-header">
        <FileCode :size="32" class="primary-icon" />
        <div>
          <h3 class="arch-title">Esquema Genérico Pagina[T] (Pydantic Generic)</h3>
          <p class="arch-desc">
            En el backend de Serenidad, <code>schemas/pagina.py</code> no define páginas web CMS estáticas,
            sino el contenedor genérico de paginación que estandariza las respuestas de todos los recursos del catálogo.
          </p>
        </div>
      </div>

      <div class="code-preview-box">
        <div class="code-header">backend/app/schemas/pagina.py</div>
        <pre class="code-content"><code>from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class Pagina(BaseModel, Generic[T]):
    """Esquema genérico para respuestas paginadas estándar."""
    items: list[T] = Field(description="Lista de elementos de la página actual")
    total: int = Field(ge=0, description="Cantidad total de registros encontrados")
    skip: int = Field(ge=0, description="Cantidad de registros omitidos")
    limit: int = Field(ge=1, description="Límite máximo de registros solicitados por página")</code></pre>
      </div>

      <div class="arch-grid">
        <div class="arch-item">
          <div class="item-icon-box">
            <Layers :size="20" />
          </div>
          <div class="item-text">
            <h4 class="item-title">Contenedor Tipado Universal</h4>
            <p class="item-desc">
              Permite que endpoints como <code>/autores</code>, <code>/categorias</code>, <code>/socios</code>, <code>/prestamos</code> y <code>/usuarios</code> compartan la misma estructura de paginación.
            </p>
          </div>
        </div>

        <div class="arch-item">
          <div class="item-icon-box">
            <Database :size="20" />
          </div>
          <div class="item-text">
            <h4 class="item-title">Optimización en Base de Datos</h4>
            <p class="item-desc">
              Aplica <code>OFFSET</code> (skip) y <code>LIMIT</code> directamente en PostgreSQL junto a una consulta <code>count()</code> para evitar sobrecargar la memoria.
            </p>
          </div>
        </div>

        <div class="arch-item">
          <div class="item-icon-box">
            <Cpu :size="20" />
          </div>
          <div class="item-text">
            <h4 class="item-title">Integración en Componentes Vue</h4>
            <p class="item-desc">
              El componente <code>AdminTable.vue</code> consume las propiedades <code>items</code>, <code>total</code>, <code>skip</code> y <code>limit</code> de forma transparente.
            </p>
          </div>
        </div>

        <div class="arch-item">
          <div class="item-icon-box">
            <CheckCircle2 :size="20" />
          </div>
          <div class="item-text">
            <h4 class="item-title">Sin CMS Inexistente</h4>
            <p class="item-desc">
              No se inventaron tablas ni operaciones ficticias para páginas web estáticas, preservando la fidelidad total al modelo del backend.
            </p>
          </div>
        </div>
      </div>
    </div>
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

.architecture-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-icon-header {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
}

.primary-icon {
  color: var(--color-gold, #C49A62);
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.arch-title {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  margin: 0 0 0.35rem 0;
}

.arch-desc {
  font-size: 0.88rem;
  color: #5d5345;
  line-height: 1.5;
  margin: 0;
}

.arch-desc code {
  background-color: #FAF8F2;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--color-border, #E5E0D4);
  font-size: 0.82rem;
  color: var(--color-forest, #34483D);
}

.code-preview-box {
  background-color: #1e2922;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}

.code-header {
  background-color: #16201a;
  padding: 0.55rem 1rem;
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--color-gold, #C49A62);
  border-bottom: 1px solid #2d3e33;
}

.code-content {
  padding: 1rem;
  margin: 0;
  overflow-x: auto;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.82rem;
  color: #e5e7eb;
  line-height: 1.45;
}

.arch-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .arch-grid {
    grid-template-columns: 1fr;
  }
}

.arch-item {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 1rem;
  background-color: #FAF8F2;
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 8px;
}

.item-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: var(--color-forest, #34483D);
  color: var(--color-gold, #C49A62);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-forest, #34483D);
  margin: 0 0 0.25rem 0;
}

.item-desc {
  font-size: 0.8rem;
  color: #7a7062;
  line-height: 1.4;
  margin: 0;
}
</style>
