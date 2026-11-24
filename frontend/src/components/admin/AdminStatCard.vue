<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'forest', // 'forest', 'gold', 'wine', 'emerald'
    validator: (v) => ['forest', 'gold', 'wine', 'emerald', 'amber'].includes(v)
  }
})
</script>

<template>
  <div class="admin-stat-card" :class="`variant-${variant}`">
    <div class="stat-body">
      <div class="stat-info">
        <span class="stat-title">{{ title }}</span>
        <div class="stat-value">{{ value }}</div>
        <span v-if="subtitle" class="stat-subtitle">{{ subtitle }}</span>
      </div>
      <div class="stat-icon-wrapper">
        <slot name="icon"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-stat-card {
  background-color: var(--color-surface, #FFFEFA);
  border: 1px solid var(--color-border, #E5E0D4);
  border-radius: 12px;
  padding: 1.25rem 1.4rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
  overflow: hidden;
}

.admin-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(52, 72, 61, 0.06);
}

.stat-body {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7a7062;
  margin-bottom: 0.4rem;
}

.stat-value {
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--color-forest, #34483D);
  line-height: 1.1;
  margin-bottom: 0.35rem;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: #8c8273;
}

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Variantes cromáticas acordes al sistema */
.variant-forest .stat-icon-wrapper {
  background-color: rgba(52, 72, 61, 0.08);
  color: var(--color-forest, #34483D);
}

.variant-gold .stat-icon-wrapper {
  background-color: rgba(196, 154, 98, 0.14);
  color: #a4763c;
}

.variant-emerald .stat-icon-wrapper {
  background-color: #ecfdf5;
  color: #059669;
}

.variant-wine .stat-icon-wrapper {
  background-color: #fef2f2;
  color: #dc2626;
}

.variant-amber .stat-icon-wrapper {
  background-color: #fffbeb;
  color: #d97706;
}
</style>
