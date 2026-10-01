<script setup lang="ts">
import { cargo, countryName, entity, loadStatus, money, modeLabel, place, quotesLabel, tone } from '../fmt'
import Flag from './Flag.vue'
import { t } from '../i18n'

defineProps<{ item: Record<string, any> }>()
</script>

<template>
  <article class="row">
    <div class="lane">
      <div>
        <strong>{{ place(item.origin) }}</strong>
        <small><Flag :code="item.originCountry" />{{ countryName(item.originCountry) }}</small>
      </div>
      <i />
      <div>
        <strong>{{ place(item.dest) }}</strong>
        <small><Flag :code="item.destCountry" />{{ countryName(item.destCountry) }}</small>
      </div>
    </div>
    <p class="meta">
      {{ cargo(item.cargoName) }} · {{ item.weightT }}t · {{ item.truckLength || '13.7' }}m · {{ item.loadTime }}
    </p>
    <div class="tags">
      <span class="pill" :class="tone(item.status)">{{ loadStatus(item.status) }}</span>
      <span class="pill">{{ modeLabel(item.matchMode) }}</span>
      <span v-if="item.quoteCount" class="pill">{{ quotesLabel(item.quoteCount) }}</span>
      <span v-if="item.company" class="who">{{ entity(item.company) }}</span>
    </div>
    <div class="price">
      <em>{{ money(item.expectPrice || item.grabPrice) }}</em>
      <small>{{ t('corr.rate') }}</small>
    </div>
  </article>
</template>

<style scoped>
.row {
  display: grid;
  grid-template-columns: minmax(240px, 1.3fr) 1.4fr auto 120px;
  gap: 12px;
  align-items: center;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 12px 14px;
}
.row:hover { border-color: #cfc8b8; }
.lane { display: flex; align-items: center; gap: 10px; }
.lane strong { display: block; font-size: 15px; }
.lane small { color: var(--muted); font-size: 11px; display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.lane i {
  width: 28px; height: 1px; background: #c8c2b4; position: relative; flex: none;
}
.lane i::after {
  content: "";
  position: absolute; right: 0; top: -3px;
  border: 4px solid transparent; border-left-color: #8d6a32;
}
.meta, .who { margin: 0; color: var(--muted); font-size: 13px; }
.tags { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.price { text-align: right; }
.price em { display: block; font-style: normal; font-weight: 650; font-size: 16px; font-variant-numeric: tabular-nums; }
.price small { color: var(--muted); font-size: 11px; }
@media (max-width: 980px) {
  .row { grid-template-columns: 1fr auto; }
  .meta, .tags { grid-column: 1 / -1; }
  .lane { flex-wrap: wrap; }
}
</style>
