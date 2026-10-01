<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ code?: string; size?: 'sm' | 'md' | 'lg' }>()
const src = computed(() => {
  const code = String(props.code || '').toLowerCase()
  if (code === 'cn' || code === 'kz' || code === 'ru' || code === 'kg' || code === 'pk' || code === 'uz' || code === 'us') return `/media/flags/${code}.svg`
  return ''
})
</script>

<template>
  <img v-if="src" class="flag" :class="props.size || 'sm'" :src="src" alt="" />
</template>

<style scoped>
.flag {
  width: 18px;
  height: 12px;
  object-fit: cover;
  border-radius: 2px;
  box-shadow: 0 0 0 1px rgba(28, 36, 48, 0.14);
  flex: none;
}
.flag.md { width: 24px; height: 16px; border-radius: 3px; }
.flag.lg { width: 32px; height: 22px; border-radius: 4px; }
</style>
