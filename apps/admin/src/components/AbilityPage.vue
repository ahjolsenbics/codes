<script setup lang="ts">
import SiteBack from './SiteBack.vue'
import SiteFooter from './SiteFooter.vue'
import SiteNav from './SiteNav.vue'

defineProps<{
  title: string
  lead?: string
  backTo?: string
  backLabel?: string
}>()
</script>

<template>
  <div class="ability">
    <SiteNav />
    <section class="wrap page">
      <SiteBack :to="backTo || '/'" :label="backLabel" />
      <header class="head">
        <div>
          <h1>{{ title }}</h1>
          <p v-if="lead" class="lead">{{ lead }}</p>
        </div>
        <div class="acts"><slot name="actions" /></div>
      </header>
      <slot />
    </section>
    <SiteFooter />
  </div>
</template>

<style scoped>
.page { padding: 22px 0 80px; }
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}
h1 { margin: 0; font-size: 28px; color: var(--navy-2); letter-spacing: -0.03em; }
.lead { margin: 8px 0 0; color: var(--muted); font-size: 15px; max-width: 68ch; line-height: 1.55; }
.acts { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
@media (max-width: 980px) {
  .head { align-items: start; }
  h1 { font-size: 24px; }
}
</style>
