<script setup lang="ts">
import { computed } from 'vue'
import { t, tf } from '../i18n'

const props = defineProps<{
  page: number
  pages: number
  total: number
  size: number
}>()

const emit = defineEmits<{ 'update:page': [n: number] }>()

const from = computed(() => (props.total ? (props.page - 1) * props.size + 1 : 0))
const to = computed(() => Math.min(props.total, props.page * props.size))

const nums = computed(() => {
  const pages = props.pages
  const cur = props.page
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1)
  const set = new Set([1, pages, cur, cur - 1, cur + 1, cur - 2, cur + 2])
  const sorted = [...set].filter((n) => n >= 1 && n <= pages).sort((a, b) => a - b)
  const out: Array<number | 'gap'> = []
  for (const n of sorted) {
    if (out.length) {
      const prev = out[out.length - 1]
      if (typeof prev === 'number' && n - prev > 1) out.push('gap')
    }
    out.push(n)
  }
  return out
})

function go(n: number) {
  if (n < 1 || n > props.pages || n === props.page) return
  emit('update:page', n)
}
</script>

<template>
  <nav v-if="total > size" class="pager" :aria-label="t('pager.label')">
    <span class="meta">{{ tf('pager.range', { a: from, b: to, n: total }) }}</span>
    <div class="btns">
      <button type="button" :disabled="page <= 1" @click="go(page - 1)">{{ t('pager.prev') }}</button>
      <button
        v-for="(n, i) in nums"
        :key="i"
        type="button"
        :disabled="n === 'gap'"
        :class="{ on: n === page, gap: n === 'gap' }"
        @click="n !== 'gap' && go(n)"
      >{{ n === 'gap' ? '…' : n }}</button>
      <button type="button" :disabled="page >= pages" @click="go(page + 1)">{{ t('pager.next') }}</button>
    </div>
  </nav>
</template>

<style scoped>
.pager {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 12px;
  padding: 10px 2px 0;
}
.meta { color: var(--muted); font-size: 13px; }
.btns { display: flex; flex-wrap: wrap; gap: 4px; }
.btns button {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 8px;
  font-size: 13px;
  color: var(--ink-soft);
}
.btns button:hover:not(:disabled) { border-color: var(--navy); color: var(--navy); }
.btns button.on { background: var(--navy); color: #fff; border-color: var(--navy); }
.btns button:disabled { opacity: 0.45; cursor: default; }
.btns button.gap { border: 0; background: transparent; min-width: 18px; padding: 0; }
</style>
