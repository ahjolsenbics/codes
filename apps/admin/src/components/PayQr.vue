<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ value: string; channel?: string }>()

const cells = computed(() => {
  const n = 21
  const seed = props.value || 'yunmm-pay'
  let h = 2166136261
  for (let i = 0; i < seed.length; i++) h = Math.imul(h ^ seed.charCodeAt(i), 16777619)
  const on = (x: number, y: number) => {
    const finder =
      (x < 7 && y < 7) || (x >= n - 7 && y < 7) || (x < 7 && y >= n - 7)
    if (finder) {
      const lx = x < 7 ? x : x >= n - 7 ? x - (n - 7) : x
      const ly = y < 7 ? y : y >= n - 7 ? y - (n - 7) : y
      return lx === 0 || ly === 0 || lx === 6 || ly === 6 || (lx >= 2 && lx <= 4 && ly >= 2 && ly <= 4)
    }
    return ((h + x * 17 + y * 31 + x * y) >>> 0) % 3 !== 0
  }
  const out: { x: number; y: number; on: boolean }[] = []
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) out.push({ x, y, on: on(x, y) })
  }
  return out
})
</script>

<template>
  <div class="qr" :class="channel">
    <i v-for="(c, i) in cells" :key="i" :class="{ on: c.on }" />
  </div>
</template>

<style scoped>
.qr {
  width: 148px;
  height: 148px;
  display: grid;
  grid-template-columns: repeat(21, 1fr);
  grid-template-rows: repeat(21, 1fr);
  padding: 8px;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 10px;
  box-shadow: 0 10px 24px rgba(16, 24, 40, 0.06);
}
.qr i { display: block; background: transparent; }
.qr i.on { background: #10283f; }
.qr.wechat i.on { background: #07c160; }
.qr.alipay i.on { background: #1677ff; }
.qr.kaspi i.on { background: #f14635; }
</style>
