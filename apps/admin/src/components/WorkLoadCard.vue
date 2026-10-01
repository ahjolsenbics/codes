<script setup lang="ts">
import { cargo, cargoClass, countryName, loadStatus, money, modeLabel, packing, place, tone } from '../fmt'
import { tf } from '../i18n'
import Flag from './Flag.vue'

defineProps<{
  item: Record<string, any>
  action?: string
}>()
defineEmits<{ click: [] }>()

function when(item: Record<string, any>) {
  const raw = String(item.loadTime || '')
  const [d, h] = raw.split(' ')
  return { d: d || '—', h: h || '' }
}
</script>

<template>
  <article class="lane-row" role="button" tabindex="0" @click="$emit('click')" @keydown.enter="$emit('click')">
    <div class="when">
      <b>{{ when(item).d }}</b>
      <small>{{ when(item).h }}</small>
    </div>
    <div class="mid">
      <div class="tags">
        <span class="pill" :class="tone(item.status)">{{ loadStatus(item.status) }}</span>
        <span class="pill info">{{ modeLabel(item.matchMode) }}</span>
        <small class="id">{{ item.id }}</small>
      </div>
      <div class="lane">
        <span><Flag :code="item.originCountry" />{{ place(item.origin) }}</span>
        <i />
        <span><Flag :code="item.destCountry" />{{ place(item.dest) }}</span>
      </div>
      <p>
        {{ countryName(item.originCountry) }} → {{ countryName(item.destCountry) }}
        · {{ cargo(item.cargoName) }}
        · {{ item.weightT }}t
        · {{ item.truckLength || 13.5 }}m / {{ item.truckTonnage || 32 }}t
        · {{ packing(item.packing) }}
        · {{ cargoClass(item.cargoClass) }}
      </p>
    </div>
    <div class="side">
      <strong>{{ money(item.expectPrice || item.grabPrice || item.lowestQuote) }}</strong>
      <small v-if="item.quoteCount">{{ tf('app.quoteCount', { n: item.quoteCount }) }}</small>
      <em v-if="action">{{ action }}</em>
    </div>
  </article>
</template>

<style scoped>
.lane-row {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr) 168px;
  min-width: 0;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  text-align: left;
}
.lane-row:hover { border-color: #c9d2e0; }
.when {
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 2px;
  background: #f7f9fc;
  border-right: 1px solid #eef1f6;
  color: #12395f;
  padding: 12px 6px;
}
.when b { font-size: 13px; font-variant-numeric: tabular-nums; }
.when small { color: #667085; font-size: 11px; }
.mid { padding: 12px 16px; min-width: 0; }
.tags { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.id { margin-left: auto; color: #98a2b3; font-variant-numeric: tabular-nums; }
.lane {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin: 8px 0 6px;
  font-size: 17px;
  font-weight: 700;
}
.lane i {
  width: 28px;
  height: 2px;
  background: #cdd9ea;
  flex: none;
  position: relative;
}
.lane i::after {
  content: '';
  position: absolute;
  right: -1px;
  top: -3px;
  border: 4px solid transparent;
  border-left-color: #9db6d8;
}
.mid p { margin: 0; color: #667085; font-size: 13px; }
.side {
  border-left: 1px solid #eef1f6;
  background: #fbfcfe;
  padding: 14px 16px;
  display: grid;
  align-content: center;
  justify-items: end;
  gap: 4px;
}
.side strong { font-size: 20px; color: #12395f; font-variant-numeric: tabular-nums; }
.side small, .side em { color: #667085; font-size: 12px; font-style: normal; }
@media (max-width: 720px) {
  .lane-row { grid-template-columns: 72px minmax(0, 1fr); }
  .side { grid-column: 1 / -1; border-left: 0; border-top: 1px solid #eef1f6; justify-items: start; flex-direction: row; }
}
</style>
