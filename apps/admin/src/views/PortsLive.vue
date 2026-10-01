<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AbilityPage from '../components/AbilityPage.vue'
import Flag from '../components/Flag.vue'
import Pager from '../components/Pager.vue'
import { corridorRate, portLabel, tone, waitMin } from '../fmt'
import { place, portName } from '../geo'
import { t, tf } from '../i18n'
import { useMarket } from '../useMarket'
import { usePager } from '../usePager'

const route = useRoute()
const { market } = useMarket()
const corridor = ref('')
const status = ref('')
const open = ref(String(route.query.id || 'khorgos'))
const grades = ['smooth', 'slow', 'congested', 'heavy', 'closed']

watch(() => route.query.id, (id) => {
  if (id) open.value = String(id)
})

const ports = computed(() => {
  return (market.value.ports || []).filter((p: any) => {
    if (corridor.value && !String(p.corridor || '').includes(corridor.value)) return false
    if (status.value && p.status !== status.value) return false
    return true
  })
})
const pager = usePager(ports, 8)
watch([corridor, status], () => pager.reset())
const focus = computed(() => ports.value.find((p: any) => p.id === open.value) || pager.items[0] || null)
const waitMax = computed(() => Math.max(60, ...(market.value.ports || []).map((p: any) => Number(p.waitMin) || 0)))

function stale(p: any) {
  const t0 = String(p.updated || '')
  return p.status !== 'closed' && (t0.startsWith('08') || t0.startsWith('09') || t0.startsWith('12'))
}

function hours(p: any) {
  if (p.status === 'closed') return t('port.hoursClosed')
  if (String(p.id).includes('rail')) return '00:00–24:00'
  return t('port.hoursN')
}

function trend(p: any) {
  const n = Number(p.waitMin) || 20
  return [0.62, 0.7, 0.78, 0.88, 0.96, 1].map((f, i) => ({ i, v: Math.round(n * f) }))
}

const related = computed(() => {
  if (!focus.value) return []
  const name = focus.value.nameZh || ''
  return (market.value.corridors || []).filter((c: any) => {
    if (name.includes('霍尔果斯')) return String(c.from).includes('霍尔果斯') || String(c.to).includes('霍尔果斯')
    if (name.includes('阿拉山口')) return String(c.from).includes('阿拉山口')
    if (name.includes('伊尔克什坦')) return String(c.from).includes('喀什')
    if (name.includes('巴克图')) return String(c.to).includes('阿斯塔纳')
    return String(c.from + c.to).includes(name.slice(0, 2))
  }).slice(0, 5)
})

function barColor(st: string) {
  if (st === 'smooth') return '#12805c'
  if (st === 'slow') return '#c9a36a'
  if (st === 'congested' || st === 'heavy') return '#b42318'
  return '#98a2b3'
}
</script>

<template>
  <AbilityPage :title="t('nav.portsLive')" :lead="t('mod.port.lead')">
    <div class="filters">
      <div class="seg">
        <button type="button" :class="{ on: corridor === '' }" @click="corridor = ''">{{ t('app.filterAll') }}</button>
        <button type="button" :class="{ on: corridor === 'KZ' }" @click="corridor = 'KZ'"><Flag code="cn" /><Flag code="kz" /> CN–KZ</button>
        <button type="button" :class="{ on: corridor === 'RU' }" @click="corridor = 'RU'"><Flag code="cn" /><Flag code="ru" /> CN–RU</button>
        <button type="button" :class="{ on: corridor === 'KG' }" @click="corridor = 'KG'"><Flag code="cn" /><Flag code="kg" /> CN–KG</button>
      </div>
      <div class="seg">
        <button type="button" :class="{ on: status === '' }" @click="status = ''">{{ t('app.filterAll') }}</button>
        <button v-for="g in grades" :key="g" type="button" :class="{ on: status === g }" @click="status = g">
          <span class="dot" :class="tone(g)" />{{ portLabel(g) }}
        </button>
      </div>
    </div>

    <p class="count">{{ tf('trip.count', { n: ports.length, m: (market.ports || []).length }) }}</p>

    <div class="split">
      <div class="pane list-pane">
        <div class="list">
          <button
            v-for="p in pager.items"
            :key="p.id"
            type="button"
            :class="{ on: focus && focus.id === p.id }"
            @click="open = p.id"
          >
            <div class="row">
              <b><Flag v-for="c in String(p.corridor || '').split('-')" :key="c" :code="c" />{{ portName(p) }}</b>
              <span class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</span>
            </div>
            <i class="bar"><em :style="{ width: Math.min(100, Math.round((Number(p.waitMin) / waitMax) * 100)) + '%', background: barColor(p.status) }" /></i>
            <div class="meta">
              <span>{{ Number(p.waitMin) > 0 ? waitMin(p.waitMin) : t('port.noWait') }}</span>
              <span>{{ stale(p) ? t('port.stale') : tf('site.portUpdated', { t: p.updated || '—' }) }}</span>
            </div>
          </button>
          <p v-if="!ports.length" class="empty">{{ t('tool.empty') }}</p>
        </div>
        <Pager v-model:page="pager.page" :pages="pager.pages" :total="pager.total" :size="pager.size" />
      </div>

      <article v-if="focus" class="pane detail">
        <div class="top">
          <div>
            <p class="kicker">{{ focus.corridor }}</p>
            <h2><Flag v-for="c in String(focus.corridor || '').split('-')" :key="c" :code="c" size="md" />{{ portName(focus) }}</h2>
          </div>
          <span class="pill" :class="tone(focus.status)">{{ portLabel(focus.status) }}</span>
        </div>
        <strong>{{ Number(focus.waitMin) > 0 ? waitMin(focus.waitMin) : t('port.noWait') }}</strong>
        <div class="wait"><i :style="{ width: Math.min(100, Math.round((Number(focus.waitMin) / waitMax) * 100)) + '%', background: barColor(focus.status) }" /></div>
        <div class="facts">
          <div><span>{{ t('port.hours') }}</span><b>{{ hours(focus) }}</b></div>
          <div><span>{{ t('trip.updated') }}</span><b>{{ stale(focus) ? t('port.stale') : focus.updated }}</b></div>
          <div><span>{{ t('port.reportAt') }}</span><b>{{ focus.updated }} · {{ t('port.sourceOps') }}</b></div>
        </div>
        <h3>{{ t('port.trend') }}</h3>
        <div class="trend">
          <div v-for="x in trend(focus)" :key="x.i">
            <i :style="{ height: Math.max(12, Math.round((x.v / waitMax) * 90)) + 'px', background: barColor(focus.status) }" />
            <small>{{ x.v }}</small>
          </div>
        </div>
        <p class="note">{{ t('mod.port.grade') }}</p>
        <p class="note">{{ t('mod.port.report') }}</p>
        <h3>{{ t('port.related') }}</h3>
        <div class="related">
          <router-link
            v-for="c in related"
            :key="c.from + c.to"
            :to="{ path: '/estimate', query: { from: c.from, to: c.to } }"
          >
            <b>{{ place(c.from) }} → {{ place(c.to) }}</b>
            <span>{{ c.km }} km · {{ corridorRate(c) }}</span>
          </router-link>
        </div>
      </article>
    </div>
  </AbilityPage>
</template>

<style scoped>
.filters { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.seg button { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #98a2b3; }
.dot.ok { background: #12805c; }
.dot.warn { background: #c9a36a; }
.dot.bad { background: #b42318; }
.count { margin: 0 0 12px; color: var(--muted); font-size: 13px; }
.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  align-items: stretch;
  height: min(72vh, 760px);
  min-height: 440px;
}
.pane {
  min-height: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.list-pane { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 10px 10px 8px; }
.list { display: grid; gap: 8px; flex: 1; min-height: 0; overflow: auto; padding-right: 4px; }
.list button {
  text-align: left; background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
}
.list button.on { border-color: var(--navy); box-shadow: 0 0 0 1px var(--navy); }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.row b { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; }
.bar, .wait { display: block; height: 6px; background: #eef1f6; border-radius: 99px; overflow: hidden; margin: 8px 0; }
.bar em, .wait i { display: block; height: 100%; border-radius: 99px; }
.meta { display: flex; justify-content: space-between; color: var(--muted); font-size: 12px; }
.detail { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 20px; overflow: auto; }
.top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.kicker { margin: 0; color: var(--muted); font-size: 12px; letter-spacing: 0.04em; }
.detail h2 { display: flex; align-items: center; gap: 8px; margin: 4px 0 0; font-size: 22px; }
.detail strong { display: block; margin: 14px 0 8px; font-size: 32px; color: var(--navy-2); letter-spacing: -0.03em; }
.facts { display: grid; gap: 8px; margin: 12px 0 16px; }
.facts div { display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-top: 1px solid var(--line-soft); }
.facts span { color: var(--muted); font-size: 13px; }
.detail h3 { margin: 8px 0 10px; font-size: 14px; color: var(--ink-soft); }
.trend { display: flex; align-items: flex-end; gap: 10px; height: 110px; padding: 8px 4px 0; }
.trend div { flex: 1; display: grid; justify-items: center; align-content: end; gap: 6px; }
.trend i { display: block; width: 100%; max-width: 28px; border-radius: 6px 6px 2px 2px; }
.trend small { color: var(--muted); font-size: 11px; }
.note { margin: 0 0 8px; color: var(--muted); font-size: 13px; line-height: 1.55; }
.related { display: grid; gap: 8px; }
.related a { display: grid; gap: 2px; border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; }
.related a:hover { border-color: var(--navy); }
.related span { color: var(--muted); font-size: 13px; }
.empty { color: var(--muted); }
@media (max-width: 1100px) {
  .split { grid-template-columns: 1fr; height: auto; min-height: 0; }
  .pane { height: min(52vh, 520px); }
}
</style>
