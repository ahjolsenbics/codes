<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Flag from '../components/Flag.vue'
import LoadCard from '../components/LoadCard.vue'
import LoadModal from '../components/LoadModal.vue'
import Pager from '../components/Pager.vue'
import SiteBack from '../components/SiteBack.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SiteNav from '../components/SiteNav.vue'
import { corridorRate, portLabel, tone, waitMin } from '../fmt'
import { canonPlace, DEST_CITIES, ORIGIN_CITIES, place, portName } from '../geo'
import { t, tf } from '../i18n'
import { useMarket } from '../useMarket'
import { usePager } from '../usePager'

const route = useRoute()
const router = useRouter()
const { market } = useMarket()

const kind = ref<'loads' | 'trucks'>(route.query.kind === 'trucks' ? 'trucks' : 'loads')
const filters = reactive({
  from: String(route.query.from || ''),
  to: String(route.query.to || ''),
  mode: '',
  country: '',
  weight: '',
})
const sort = ref<'new' | 'price' | 'weight'>('new')
const openId = ref('')

watch(() => route.query, (q) => {
  if (q.id) {
    openId.value = String(q.id)
    const next: Record<string, string> = {}
    if (q.from) next.from = String(q.from)
    if (q.to) next.to = String(q.to)
    if (q.kind) next.kind = String(q.kind)
    router.replace({ path: '/board', query: next })
    return
  }
  filters.from = String(q.from || '')
  filters.to = String(q.to || '')
  kind.value = q.kind === 'trucks' ? 'trucks' : 'loads'
}, { immediate: true })

const cities = computed(() => [...new Set([...ORIGIN_CITIES, ...DEST_CITIES])])
const countries = computed(() => {
  const set = new Set<string>()
  for (const row of [...(market.value.items || []), ...(market.value.trucks || [])]) {
    if (row.destCountry) set.add(row.destCountry)
  }
  return [...set]
})

const rows = computed(() => {
  const source = kind.value === 'trucks' ? market.value.trucks || [] : market.value.items || []
  const list = source.filter((x: any) => {
    const qFrom = canonPlace(filters.from)
    const qTo = canonPlace(filters.to)
    const okFrom = !filters.from || String(x.origin).includes(qFrom) || place(x.origin).toLowerCase().includes(filters.from.toLowerCase())
    const okTo = !filters.to || String(x.dest).includes(qTo) || place(x.dest).toLowerCase().includes(filters.to.toLowerCase())
    const okMode = !filters.mode || x.matchMode === filters.mode
    const okCountry = !filters.country || x.destCountry === filters.country
    const w = Number(x.weightT)
    const okWeight = !filters.weight
      || (filters.weight === 'light' && w <= 10)
      || (filters.weight === 'mid' && w > 10 && w <= 18)
      || (filters.weight === 'heavy' && w > 18)
    return okFrom && okTo && okMode && okCountry && okWeight
  })
  const sorted = [...list]
  if (sort.value === 'price') sorted.sort((a, b) => (b.expectPrice || b.grabPrice || 0) - (a.expectPrice || a.grabPrice || 0))
  if (sort.value === 'weight') sorted.sort((a, b) => Number(b.weightT) - Number(a.weightT))
  return sorted
})

const pager = usePager(rows, 8)
const lanes = computed(() => (market.value.corridors || []).slice(0, 6))
const ports = computed(() => (market.value.ports || []).slice(0, 5))
const trucks = ['tent', 'reefer', 'box', 'flat', 'container', 'tank'] as const

watch([filters, kind, sort], () => { pager.reset() }, { deep: true })

function apply() {
  router.replace({ path: '/board', query: { from: filters.from, to: filters.to, kind: kind.value } })
}

function reset() {
  filters.from = ''
  filters.to = ''
  filters.mode = ''
  filters.country = ''
  filters.weight = ''
  apply()
}

function swap() {
  const a = filters.from
  filters.from = filters.to
  filters.to = a
  apply()
}

function useLane(c: any) {
  filters.from = c.from
  filters.to = c.to
  apply()
}

function open(id: string) {
  openId.value = id
}
</script>

<template>
  <div>
    <SiteNav />

    <header class="head">
      <div class="wrap">
        <SiteBack to="/" />
        <h1>{{ kind === 'trucks' ? t('board.trucks') : t('board.loads') }}</h1>
        <div class="seg">
          <button type="button" :class="{ on: kind === 'loads' }" @click="kind = 'loads'; apply()">{{ t('board.loads') }}</button>
          <button type="button" :class="{ on: kind === 'trucks' }" @click="kind = 'trucks'; apply()">{{ t('board.trucks') }}</button>
        </div>
      </div>
    </header>

    <div class="wrap bar">
      <form class="search" @submit.prevent="apply">
        <label class="label">{{ t('search.from') }}
          <input class="field" list="board-cities" :value="place(filters.from)" @input="filters.from = canonPlace(($event.target as HTMLInputElement).value)" />
        </label>
        <button type="button" class="swap" :title="t('board.reset')" @click="swap">⇄</button>
        <label class="label">{{ t('search.to') }}
          <input class="field" list="board-cities" :value="place(filters.to)" @input="filters.to = canonPlace(($event.target as HTMLInputElement).value)" />
        </label>
        <label class="label">{{ t('col.match') }}
          <select v-model="filters.mode" class="field">
            <option value="">{{ t('desk.allModes') }}</option>
            <option value="bid">{{ t('mode.bid') }}</option>
            <option value="grab">{{ t('mode.grab') }}</option>
            <option value="assign">{{ t('mode.assign') }}</option>
          </select>
        </label>
        <label class="label">{{ t('app.weight') }}
          <select v-model="filters.weight" class="field">
            <option value="">{{ t('desk.weightAll') }}</option>
            <option value="light">{{ t('desk.weightLight') }}</option>
            <option value="mid">{{ t('desk.weightMid') }}</option>
            <option value="heavy">{{ t('desk.weightHeavy') }}</option>
          </select>
        </label>
        <button class="btn btn-blue" type="submit">{{ t('search.loads') }}</button>
        <datalist id="board-cities">
          <option v-for="city in cities" :key="city" :value="place(city)" />
        </datalist>
      </form>
      <div class="chips-row">
        <button v-for="c in countries" :key="c" type="button" class="chip" :class="{ on: filters.country === c }" @click="filters.country = filters.country === c ? '' : c">
          <Flag :code="c" />{{ c }}
        </button>
        <button type="button" class="chip ghost" @click="reset">{{ t('board.reset') }}</button>
      </div>
    </div>

    <main class="wrap grid">
      <section>
        <div class="count">
          <b>{{ tf('board.found', { n: rows.length }) }}</b>
          <div class="seg small">
            <button type="button" :class="{ on: sort === 'new' }" @click="sort = 'new'">{{ t('board.sortNew') }}</button>
            <button type="button" :class="{ on: sort === 'price' }" @click="sort = 'price'">{{ t('board.sortPrice') }}</button>
            <button type="button" :class="{ on: sort === 'weight' }" @click="sort = 'weight'">{{ t('board.sortWeight') }}</button>
          </div>
        </div>

        <div class="list">
          <button v-for="item in pager.items" :key="item.id" type="button" class="row" @click="open(item.id)">
            <LoadCard :item="item" :active="openId === item.id" />
          </button>
        </div>
        <p v-if="!rows.length" class="empty">{{ t('board.empty') }}</p>
        <Pager v-model:page="pager.page" :pages="pager.pages" :total="pager.total" :size="pager.size" />
      </section>

      <aside>
        <div class="cta">
          <h3>{{ t('board.postLoad') }}</h3>
          <p>{{ t('board.postLead') }}</p>
          <router-link class="btn btn-blue" to="/match">{{ t('nav.match') }}</router-link>
        </div>

        <div class="card side">
          <h4>{{ t('board.hotLanes') }}</h4>
          <button v-for="c in lanes" :key="c.from + c.to" type="button" @click="useLane(c)">
            <span>{{ place(c.from) }} → {{ place(c.to) }}</span>
            <small>{{ corridorRate(c) }}</small>
          </button>
        </div>

        <div class="card side">
          <h4>{{ t('board.portNow') }}</h4>
          <router-link v-for="p in ports" :key="p.id" to="/ports">
            <span><Flag v-for="c in String(p.corridor || '').split('-')" :key="c" :code="c" />{{ portName(p) }}</span>
            <em class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</em>
            <small>{{ Number(p.waitMin) > 0 ? waitMin(p.waitMin) : t('port.noWait') }}</small>
          </router-link>
        </div>

        <div class="card side fx">
          <h4>{{ t('home.fx') }}</h4>
          <div class="fx-row"><span>CNY / KZT</span><b>72.41</b></div>
          <div class="fx-row"><span>CNY / RUB</span><b>11.86</b></div>
          <div class="fx-row"><span>KZT / RUB</span><b>0.164</b></div>
          <small>{{ t('home.fxNote') }}</small>
        </div>

        <div class="card side">
          <h4>{{ t('board.truckTypes') }}</h4>
          <div class="tags">
            <span v-for="k in trucks" :key="k" class="chip">{{ t('truck.' + k) }}</span>
          </div>
        </div>
      </aside>
    </main>
    <SiteFooter />
    <LoadModal v-if="openId" :id="openId" @close="openId = ''" @select="open" />
  </div>
</template>

<style scoped>
.head { background: linear-gradient(180deg, #eef3fa, var(--paper)); border-bottom: 1px solid var(--line); padding: 22px 0 20px; }
.crumb { display: flex; gap: 8px; color: var(--muted); font-size: 13px; }
.crumb b { color: var(--ink-soft); font-weight: 650; }
.head h1 { margin: 8px 0 14px; }
.bar { margin-top: 18px; }
.search {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 10px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-l);
  padding: 16px;
  box-shadow: var(--shadow-s);
}
.search .label { flex: 1 1 160px; min-width: 140px; }
.search .btn { flex: 0 0 auto; }
.swap { height: 42px; flex: 0 0 42px; border: 1px solid var(--line); background: #fff; border-radius: 10px; color: var(--muted); }
.chips-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 0; }
.chips-row .chip { border: 1px solid transparent; cursor: pointer; }
.chips-row .chip.on { background: var(--navy); color: #fff; }
.chips-row .ghost { background: transparent; border-color: var(--line); }
.grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 22vw); gap: 22px; padding: 22px 0 64px; align-items: start; }
.count { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.count b { font-size: 15px; }
.seg.small button { height: 28px; padding: 0 12px; font-size: 13px; }
.list { display: grid; gap: 10px; }
.row { border: 0; background: transparent; padding: 0; text-align: left; display: block; width: 100%; min-width: 0; }
.empty { color: var(--muted); padding: 32px 0; }
aside { display: grid; gap: 14px; position: sticky; top: 88px; }
.cta { background: var(--navy); color: #fff; border-radius: var(--radius-l); padding: 20px; }
.cta h3 { color: #fff; }
.cta p { margin: 8px 0 14px; color: #c8d6e6; font-size: 14px; }
.cta .btn { width: 100%; }
.side { padding: 16px 18px; }
.side h4 { margin-bottom: 10px; }
.side button, .side a {
  width: 100%; display: grid; grid-template-columns: 1fr auto; gap: 4px 10px;
  border: 0; background: transparent; text-align: left; padding: 9px 0; border-top: 1px solid var(--line-soft);
  align-items: center;
}
.side button span, .side a span { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; }
.side small { grid-column: 1 / -1; color: var(--muted); }
.fx-row { display: flex; justify-content: space-between; padding: 8px 0; border-top: 1px solid var(--line-soft); font-size: 14px; }
.fx-row b { font-variant-numeric: tabular-nums; }
.fx small { display: block; margin-top: 8px; color: #8d6a32; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
@media (max-width: 1180px) {
  .grid { grid-template-columns: 1fr; }
  aside { position: static; }
}
@media (max-width: 720px) {
  .search { padding: 12px; }
}
</style>
