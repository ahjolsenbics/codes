<script setup lang="ts">
import { computed } from 'vue'
import { kycLabel } from '../fmt'
import { t } from '../i18n'

const props = defineProps<{ kind: string; status?: string; src?: string }>()

const label = computed(() => {
  const key = `cred.${props.kind}`
  const value = t(key)
  return value === key ? props.kind : value
})

const tone = computed(() => {
  if (['green_card', 'green', 'tir', 'license', 'drive', 'road_permit'].includes(props.kind)) return 'green'
  if (['biz', 'business_license', 'auth'].includes(props.kind)) return 'warm'
  if (['vehicle', 'truck_photo', 'plate'].includes(props.kind)) return 'slate'
  return 'blue'
})
</script>

<template>
  <figure class="doc">
    <a class="paper" :class="tone" :href="src || undefined" target="_blank" rel="noreferrer">
      <header>{{ label }}</header>
      <div class="body">
        <i class="photo" />
        <div class="lines">
          <b /><b /><b /><b />
        </div>
      </div>
      <em>KYC</em>
    </a>
    <figcaption>{{ label }} · {{ kycLabel(status || 'pending') }}</figcaption>
  </figure>
</template>

<style scoped>
.doc { width: 200px; margin: 0; }
.paper {
  position: relative;
  display: block;
  height: 132px;
  border-radius: 10px;
  border: 1px solid var(--line);
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff, #f7f9fc);
  color: inherit;
}
.paper header {
  height: 28px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: #2563eb;
}
.paper.green header { background: #12805c; }
.paper.warm header { background: #b7791f; }
.paper.slate header { background: #667085; }
.body { display: flex; gap: 10px; padding: 12px 10px; }
.photo {
  width: 46px;
  height: 58px;
  border-radius: 6px;
  background: #e7eef8;
  flex: none;
}
.paper.green .photo { background: #d7efe0; }
.paper.warm .photo { background: #fdf3e0; }
.paper.slate .photo { background: #eef1f6; }
.lines { flex: 1; display: grid; gap: 8px; align-content: start; padding-top: 4px; }
.lines b { display: block; height: 6px; border-radius: 99px; background: #e3e8ef; }
.lines b:first-child { width: 86%; background: #c5d0dc; }
.lines b:nth-child(2) { width: 74%; }
.lines b:nth-child(3) { width: 80%; }
.lines b:nth-child(4) { width: 58%; }
em {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 34px;
  height: 34px;
  border: 2px solid currentColor;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 8px;
  font-style: normal;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: #2563eb;
  opacity: 0.45;
}
.paper.green em { color: #12805c; }
.paper.warm em { color: #b7791f; }
.paper.slate em { color: #667085; }
figcaption { font-size: 11px; color: var(--color-secondary); margin-top: 6px; }
</style>
