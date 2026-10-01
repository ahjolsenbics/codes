<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AbilityPage from '../components/AbilityPage.vue'
import Flag from '../components/Flag.vue'
import Pager from '../components/Pager.vue'
import { canonPlace, cargoClass, DEST_CITIES, ORIGIN_CITIES, place, portName } from '../geo'
import { corridorRate, money, portLabel, tone, waitMin } from '../fmt'
import { isAppAuthed } from '../auth'
import { t, tf } from '../i18n'
import { corridorQuote } from '../siteData'
import { useMarket } from '../useMarket'
import { usePager } from '../usePager'

const route = useRoute()
const { market } = useMarket()
const form = reactive({
  from: String(route.query.from || '乌鲁木齐'),
  to: String(route.query.to || '阿拉木图'),
  truck: '',
  cargoClass: '',
  weightT: '',
})
const copied = ref(false)
const faq = ref('')
const used = ref(Number(localStorage.getItem('yunmm_est_n') || 0))
const gated = computed(() => used.value >= 2 && !isAppAuthed())
const cities = computed(() => [...new Set([...ORIGIN_CITIES, ...DEST_CITIES, ...(market.value.corridors || []).flatMap((c: any) => [c.from, c.to])])])

const quote = computed(() => corridorQuote(
  market.value.corridors || [],
  canonPlace(form.from),
  canonPlace(form.to),
  {
    truck: form.truck || undefined,
    cargoClass: form.cargoClass || undefined,
    weightT: form.weightT ? Number(form.weightT) : undefined,
  },
))

const lanePorts = computed(() => {
  const q = quote.value
  if (!q) return []
  const from = String(q.from)
  const to = String(q.to)
  const ids = new Set<string>()
  if (/霍尔果斯|阿拉木图|阿斯塔纳|奇姆肯特|塔拉兹|塔尔迪库尔干/.test(from + to)) ids.add('khorgos')
  if (/阿拉山口|莫斯科|新西伯利亚|圣彼得堡/.test(from + to)) ids.add('alashankou')
  if (/喀什|奥什|安集延|塔什干/.test(from + to)) ids.add('irkeshtam')
  if (/阿斯塔纳|石河子/.test(from + to)) ids.add('bakhty')
  if (/昌吉|都拉塔/.test(from + to)) ids.add('dulata')
  if (/莫斯科|圣彼得堡/.test(to)) ids.add('manzhouli')
  return (market.value.ports || []).filter((p: any) => ids.has(p.id)).slice(0, 4)
})

watch(() => [form.from, form.to], () => {
  copied.value = false
  if (gated.value) return
  used.value += 1
  localStorage.setItem('yunmm_est_n', String(used.value))
})

function pick(c: any) {
  form.from = c.from
  form.to = c.to
}

function swap() {
  const a = form.from
  form.from = form.to
  form.to = a
}

async function copyRange() {
  if (!quote.value) return
  const text = `${place(quote.value.from)} → ${place(quote.value.to)}  ${money(quote.value.feeLow)} – ${money(quote.value.feeHigh)}  ${quote.value.km} km`
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
  } catch {
    copied.value = false
  }
}

const trucks = ['9.6', '13.5', '17.5']
const classes = ['general', 'reefer', 'equipment']
const lanes = computed(() => market.value.corridors || [])
const pager = usePager(lanes, 12)
</script>

<template>
  <AbilityPage :title="t('nav.estimate')" :lead="t('mod.est.lead')">
    <div class="layout">
      <form class="panel form" @submit.prevent>
        <label class="label">{{ t('search.from') }}
          <input class="field" list="est-cities" :value="place(form.from)" @input="form.from = canonPlace(($event.target as HTMLInputElement).value)" />
        </label>
        <button type="button" class="swap" @click="swap">⇄</button>
        <label class="label">{{ t('search.to') }}
          <input class="field" list="est-cities" :value="place(form.to)" @input="form.to = canonPlace(($event.target as HTMLInputElement).value)" />
        </label>
        <datalist id="est-cities">
          <option v-for="city in cities" :key="city" :value="place(city)" />
        </datalist>
        <label class="label">{{ t('est.truck') }}
          <select v-model="form.truck" class="field">
            <option value="">{{ t('est.anyTruck') }}</option>
            <option v-for="len in trucks" :key="len" :value="len">{{ len }} m</option>
          </select>
        </label>
        <label class="label">{{ t('est.class') }}
          <select v-model="form.cargoClass" class="field">
            <option value="">{{ t('est.anyClass') }}</option>
            <option v-for="c in classes" :key="c" :value="c">{{ cargoClass(c) }}</option>
          </select>
        </label>
        <label class="label grow">{{ t('est.weight') }}
          <input v-model="form.weightT" class="field" inputmode="decimal" placeholder="t" />
        </label>
      </form>

      <article v-if="gated" class="panel result">
        <p>{{ t('est.needLogin') }}</p>
        <router-link class="btn btn-green" :to="{ path: '/login', query: { next: '/estimate' } }">{{ t('auth.login') }}</router-link>
      </article>
      <article v-else-if="quote" class="panel result">
        <div class="result-top">
          <div>
            <p class="lane-name">{{ place(quote.from) }} → {{ place(quote.to) }}</p>
            <strong>{{ money(quote.feeLow) }} – {{ money(quote.feeHigh) }}</strong>
          </div>
          <button type="button" class="btn btn-line btn-sm" @click="copyRange">{{ copied ? t('est.copied') : t('est.share') }}</button>
        </div>
        <div class="band">
          <i :style="{ width: Math.min(92, 48 + quote.factor * 18) + '%' }" />
        </div>
        <div class="nums">
          <div><span>{{ t('site.rateKm') }}</span><b>{{ quote.km }} km</b></div>
          <div><span>{{ t('corr.rate') }}</span><b>{{ corridorRate(quote) }}</b></div>
          <div><span>{{ t('site.rateWait') }}</span><b>{{ waitMin(quote.waitMin) }}</b></div>
          <div><span>{{ t('site.rateHours') }}</span><b>{{ tf('site.rateHoursN', { n: quote.hours }) }}</b></div>
        </div>
        <div class="segs">
          <div v-for="s in quote.segments" :key="s.key">
            <span>{{ t('est.seg' + (s.key === 'domestic' ? 'Domestic' : s.key === 'port' ? 'Port' : 'Foreign')) }}</span>
            <b>{{ s.km }} km</b>
            <i :style="{ width: Math.round((s.km / quote.km) * 100) + '%' }" />
          </div>
        </div>
        <p class="meta">{{ t('est.drive') }} {{ quote.driveHours }} h · {{ t('est.wait') }} {{ quote.waitHours }} h · {{ t('est.factor') }} ×{{ quote.factor }}</p>
        <small>{{ t('app.refOnly') }}</small>
        <div v-if="lanePorts.length" class="ports">
          <p>{{ t('est.portsOnLane') }}</p>
          <router-link v-for="p in lanePorts" :key="p.id" :to="'/ports?id=' + p.id">
            <Flag v-for="c in String(p.corridor || '').split('-')" :key="c" :code="c" />
            {{ portName(p) }}
            <span class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</span>
          </router-link>
        </div>
      </article>
      <p v-else class="miss">{{ t('site.rateEmpty') }}</p>
    </div>

    <h2>{{ t('mod.est.tabLanes') }}</h2>
    <div class="lanes">
      <button
        v-for="c in pager.items"
        :key="c.from + c.to"
        type="button"
        :class="{ on: form.from === c.from && form.to === c.to }"
        @click="pick(c)"
      >
        <b>{{ place(c.from) }} → {{ place(c.to) }}</b>
        <span>{{ c.km }} km · {{ corridorRate(c) }}</span>
      </button>
    </div>
    <Pager v-model:page="pager.page" :pages="pager.pages" :total="pager.total" :size="pager.size" />

    <h2>{{ t('mod.est.tabHow') }}</h2>
    <p class="how">{{ t('mod.est.how') }}</p>
    <p class="how muted">{{ t('mod.est.seg') }}</p>
    <div class="faq">
      <button type="button" :class="{ on: faq === '1' }" @click="faq = faq === '1' ? '' : '1'">
        <b>{{ t('mod.est.faq1.q') }}</b>
        <p v-if="faq === '1'">{{ t('mod.est.faq1.a') }}</p>
      </button>
      <button type="button" :class="{ on: faq === '2' }" @click="faq = faq === '2' ? '' : '2'">
        <b>{{ t('mod.est.faq2.q') }}</b>
        <p v-if="faq === '2'">{{ t('mod.est.faq2.a') }}</p>
      </button>
    </div>
  </AbilityPage>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 340px minmax(0, 1fr); gap: 16px; margin-bottom: 28px; align-items: start; }
.panel { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 18px; }
.form { display: grid; gap: 12px; }
.swap {
  width: 42px; height: 36px; margin: -4px auto;
  border: 1px solid var(--line); background: #f7f9fc; border-radius: 10px; color: var(--muted);
}
.result-top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.lane-name { margin: 0; color: var(--muted); font-weight: 650; }
.result strong { display: block; margin: 6px 0 12px; font-size: 30px; color: var(--navy-2); letter-spacing: -0.03em; }
.band { height: 8px; background: #eef1f6; border-radius: 99px; overflow: hidden; margin-bottom: 14px; }
.band i { display: block; height: 100%; background: linear-gradient(90deg, #12805c, #c9a36a); border-radius: 99px; }
.nums { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }
.nums div, .segs div { border: 1px solid var(--line-soft); background: #f7f9fc; border-radius: 12px; padding: 10px 12px; }
.nums span, .segs span { display: block; color: var(--muted); font-size: 12px; }
.nums b, .segs b { display: block; margin-top: 4px; font-size: 15px; }
.segs { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 10px; }
.segs i { display: block; height: 4px; margin-top: 8px; background: #12805c; border-radius: 99px; max-width: 100%; }
.meta { margin: 12px 0 6px; color: var(--ink-soft); font-size: 13px; }
.result small, .miss { color: var(--brass); }
.ports { margin-top: 14px; display: grid; gap: 8px; }
.ports p { margin: 0; font-size: 13px; font-weight: 650; color: var(--ink-soft); }
.ports a {
  display: flex; align-items: center; gap: 8px;
  border: 1px solid var(--line); border-radius: 10px; padding: 8px 10px; background: #fff;
}
.ports a:hover { border-color: var(--navy); }
h2 { margin: 8px 0 12px; font-size: 18px; color: var(--navy-2); }
.lanes { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 28px; }
.lanes button { text-align: left; background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; }
.lanes button.on, .lanes button:hover { border-color: var(--navy); }
.lanes b { display: block; margin-bottom: 4px; font-size: 14px; }
.lanes span { color: var(--muted); font-size: 13px; }
.how { margin: 0 0 8px; color: var(--ink-soft); max-width: 78ch; }
.how.muted { color: var(--muted); font-size: 14px; margin-bottom: 14px; }
.faq { display: grid; gap: 8px; }
.faq button { text-align: left; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
.faq button.on { border-color: var(--navy); }
.faq p { margin: 8px 0 0; color: var(--muted); font-size: 14px; }
@media (max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
}
@media (max-width: 720px) {
  .nums, .segs, .lanes { grid-template-columns: 1fr 1fr; }
  .result-top { flex-wrap: wrap; }
}
</style>
