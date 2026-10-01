<script setup lang="ts">
import { t } from '../i18n'
import { useBack } from '../useBack'

const props = defineProps<{ to?: string; label?: string }>()
const { back } = useBack(() => props.to || '/')
</script>

<template>
  <button type="button" class="back" @click="back">
    <span aria-hidden="true">←</span>
    {{ label || t('common.back') }}
  </button>
</template>

<style scoped>
.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: none;
  color: var(--navy);
  font-size: 14px;
  font-weight: 650;
  padding: 0;
  margin: 0 0 10px;
  cursor: pointer;
}
.back:hover { color: var(--signal-ink); }
</style>
