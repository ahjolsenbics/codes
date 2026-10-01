<script setup lang="ts">
import Flag from './Flag.vue'
import { isAppAuthed } from '../auth'
import { cargo, company, countryName, loadStatus, modeLabel, money, place, quotesLabel, tone } from '../fmt'
import { t } from '../i18n'

defineProps<{ item: Record<string, any>; active?: boolean }>()
const authed = isAppAuthed
</script>

<template>
  <article class="load" :class="{ on: active, hot: item.matchMode === 'grab' }">
    <div class="when">
      <b>{{ String(item.loadTime || '').split(' ')[0] || '—' }}</b>
      <small>{{ String(item.loadTime || '').split(' ')[1] || '' }}</small>
    </div>
    <div class="body">
      <div class="tags">
        <span class="pill" :class="tone(item.status)">{{ loadStatus(item.status) }}</span>
        <span class="pill info">{{ modeLabel(item.matchMode) }}</span>
        <span v-if="item.verified" class="pill ok">{{ t('card.verified') }}</span>
        <span v-if="authed() && item.quoteCount" class="pill">{{ quotesLabel(item.quoteCount) }}</span>
        <small class="id">{{ item.id }}</small>
      </div>

      <div class="lane">
        <span class="city"><Flag :code="item.originCountry" />{{ place(item.origin) }}</span>
        <i class="arrow" />
        <span class="city"><Flag :code="item.destCountry" />{{ place(item.dest) }}</span>
      </div>

      <p class="meta">
        <span>{{ countryName(item.originCountry) }} → {{ countryName(item.destCountry) }}</span>
      </p>

      <div class="chips">
        <span class="chip">{{ item.weightT }} t</span>
        <span v-if="item.volumeM3" class="chip">{{ item.volumeM3 }} m³</span>
        <span class="chip">{{ item.truckLength || '13.7' }} m</span>
        <span class="chip">{{ cargo(item.cargoName) }}</span>
      </div>

      <p v-if="authed() && item.company" class="who">
        {{ company(item.company) }}
        <em v-if="item.credit">{{ t('tool.credit') }} {{ item.credit }}</em>
      </p>
    </div>

    <div class="side">
      <strong v-if="authed() && (item.expectPrice || item.grabPrice)">{{ money(item.expectPrice || item.grabPrice) }}</strong>
      <strong v-else class="lock">{{ t('auth.loginForDetail') }}</strong>
      <small>{{ authed() ? t('corr.rate') : t('auth.needLogin') }}</small>
      <span class="btn btn-blue btn-sm">{{ t('site.open') }}</span>
    </div>
  </article>
</template>

<style scoped>
.load {
  position: relative;
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr) 168px;
  min-width: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-l);
  overflow: hidden;
  transition: border-color .15s, box-shadow .15s;
}
.when {
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 2px;
  background: #f7f9fc;
  border-right: 1px solid var(--line-soft);
  color: var(--navy);
  padding: 12px 6px;
}
.when b { font-size: 13px; font-variant-numeric: tabular-nums; }
.when small { color: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.load::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--blue);
}
.load.hot::before { background: var(--brass); }
.load:hover { border-color: #c9d2e0; box-shadow: var(--shadow-s); }
.load.on { border-color: var(--navy); box-shadow: var(--shadow-s); }
.body { padding: 14px 16px; display: grid; gap: 8px; min-width: 0; }
.tags { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.id { margin-left: auto; color: var(--faint); font-variant-numeric: tabular-nums; }
.lane { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; font-size: 19px; font-weight: 700; color: var(--ink); min-width: 0; }
.city { display: inline-flex; align-items: center; gap: 7px; min-width: 0; }
.arrow { position: relative; width: 38px; height: 2px; background: #cdd9ea; border-radius: 99px; flex: none; }
.arrow::after {
  content: ""; position: absolute; right: -1px; top: -3px;
  border: 4px solid transparent; border-left-color: #9db6d8;
}
.meta { margin: 0; display: flex; flex-wrap: wrap; gap: 14px; color: var(--muted); font-size: 13px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.who { margin: 0; color: var(--ink-soft); font-size: 14px; }
.who em { margin-left: 8px; font-style: normal; color: var(--muted); }
.side {
  border-left: 1px solid var(--line-soft);
  background: #fbfcfe;
  padding: 16px;
  display: grid;
  align-content: center;
  justify-items: end;
  gap: 4px;
  text-align: right;
}
.side strong { font-size: 22px; color: var(--navy); font-variant-numeric: tabular-nums; }
.side strong.lock { font-size: 13px; font-weight: 700; color: #5c6b7a; }
.side small { color: var(--muted); }
.side .btn { margin-top: 8px; }
@media (max-width: 980px) {
  .load { grid-template-columns: 72px minmax(0, 1fr); }
  .side { grid-column: 1 / -1; border-left: 0; border-top: 1px solid var(--line-soft); justify-items: start; text-align: left; }
}
@media (max-width: 520px) {
  .load { grid-template-columns: 1fr; }
  .when { border-right: 0; border-bottom: 1px solid var(--line-soft); grid-template-columns: auto auto; justify-content: start; padding: 10px 14px; }
  .lane { font-size: 16px; }
}
</style>
