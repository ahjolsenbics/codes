<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import CorridorMap from '../components/CorridorMap.vue'
import Flag from '../components/Flag.vue'
import LoadCard from '../components/LoadCard.vue'
import LoadModal from '../components/LoadModal.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SiteNav from '../components/SiteNav.vue'
import { cargo, place, portName } from '../geo'
import { compact, corridorRate, money, orderStatus, portLabel, tone, waitMin } from '../fmt'
import { t, tf } from '../i18n'
import { PUBLIC_BILLS } from '../siteData'
import { useMarket } from '../useMarket'
import { deskPath, isAppAuthed } from '../auth'

const router = useRouter()
const { market } = useMarket()
const authed = isAppAuthed
const shipperTo = computed(() => deskPath('shipper'))
const driverTo = computed(() => deskPath('driver'))
const liveKind = ref<'loads' | 'trucks'>('loads')
const openId = ref('')
const liveRows = computed(() => liveKind.value === 'trucks' ? (market.value.trucks || []) : (market.value.items || []))
const ticker = computed(() => {
  const rows = market.value.items || []
  return [...rows, ...rows]
})
const sample = PUBLIC_BILLS[0]
const fx = [
  { pair: 'CNY / KZT', value: '72.41' },
  { pair: 'CNY / RUB', value: '11.86' },
  { pair: 'KZT / RUB', value: '0.164' },
]
const held = new Set<HTMLElement>()
const quiet = new Set<HTMLElement>()
const quietTimers = new Map<HTMLElement, number>()
const offset = new WeakMap<HTMLElement, number>()
let timer = 0

function pause(el: HTMLElement) {
  offset.set(el, el.scrollTop)
  quiet.add(el)
  window.clearTimeout(quietTimers.get(el))
  quietTimers.set(el, window.setTimeout(() => quiet.delete(el), 2200))
}

function tick() {
  document.querySelectorAll<HTMLElement>('.auto-scroll').forEach((el) => {
    if (held.has(el) || quiet.has(el)) return
    const max = el.scrollHeight - el.clientHeight
    if (max <= 2) return
    let y = (offset.get(el) ?? el.scrollTop) + 1
    if (y >= max) y = 0
    offset.set(el, y)
    el.scrollTop = y
  })
}

onMounted(async () => {
  await nextTick()
  document.querySelectorAll<HTMLElement>('.auto-scroll').forEach((el) => {
    el.addEventListener('wheel', () => pause(el), { passive: true })
    el.addEventListener('pointerdown', () => held.add(el))
    el.addEventListener('pointerup', () => { held.delete(el); pause(el) })
    el.addEventListener('pointercancel', () => { held.delete(el); pause(el) })
    el.addEventListener('touchstart', () => pause(el), { passive: true })
  })
  timer = window.setInterval(tick, 90)
})

onUnmounted(() => window.clearInterval(timer))

function openLane(c: any) {
  router.push({ path: '/board', query: { from: c.from, to: c.to } })
}

function openLoad(id: string) {
  openId.value = id
}
</script>

<template>
  <div class="page">
    <SiteNav />

    <section class="hero">
      <div class="wrap">
        <h1>
          {{ t('home.h1') }}
          <i>·</i>
          <small>{{ t('home.h1sub') }}</small>
        </h1>
        <div class="map"><CorridorMap /></div>
      </div>
    </section>

    <div class="ticker-wrap">
      <div class="wrap ticker" aria-hidden="true">
        <div class="track">
          <button v-for="(item, i) in ticker" :key="item.id + '-' + i" type="button" @click="openLoad(item.id)">
            <Flag :code="item.originCountry" />
            {{ place(item.origin) }}
            <em>→</em>
            <Flag :code="item.destCountry" />
            {{ place(item.dest) }}
            <span>{{ cargo(item.cargoName) }} · {{ item.weightT }}t</span>
            <b v-if="authed()">{{ money(item.expectPrice || item.grabPrice) }}</b>
            <b v-else>{{ t('auth.loginForDetail') }}</b>
          </button>
        </div>
      </div>
    </div>

    <section class="wrap why">
      <div class="why-panel">
        <h2>{{ t('why.title') }}</h2>
        <div class="why-points">
          <article v-for="key in ['m1', 'm2', 'm3', 'm4']" :key="key">
            <b>{{ t('why.' + key + '.t') }}</b>
            <p>{{ t('why.' + key + '.d') }}</p>
          </article>
        </div>
        <ol class="why-flow">
          <li v-for="n in [1, 2, 3]" :key="n">
            <em>{{ t('why.s' + n + '.n') }}</em>
            <div>
              <strong>{{ t('why.s' + n + '.t') }}</strong>
              <span>{{ t('why.s' + n + '.d') }}</span>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="wrap why">
      <div class="why-panel">
        <h2>{{ t('home.deskTitle') }}</h2>
        <div class="why-points">
          <article v-for="key in ['d1', 'd2', 'd3', 'd4']" :key="key">
            <b>{{ t('home.' + key + '.t') }}</b>
            <p>{{ t('home.' + key + '.d') }}</p>
          </article>
        </div>
        <ol class="why-flow desks-flow">
          <li>
            <em>01</em>
            <div>
              <strong>{{ t('nav.shipperDesk') }}</strong>
              <router-link :to="shipperTo">{{ t('apps.ctaShipper') }} →</router-link>
            </div>
          </li>
          <li>
            <em>02</em>
            <div>
              <strong>{{ t('nav.driverDesk') }}</strong>
              <router-link :to="driverTo">{{ t('apps.ctaDriver') }} →</router-link>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="facts wrap">
      <div>
        <b>{{ compact(market.loadsLive) }}</b>
        <span>{{ t('hero.statLoads') }}</span>
        <em>+{{ compact(market.loadsToday) }} {{ t('home.today') }}</em>
      </div>
      <div>
        <b>{{ compact(market.trucksLive) }}</b>
        <span>{{ t('hero.statTrucks') }}</span>
        <em>+{{ compact(market.trucksToday) }} {{ t('home.today') }}</em>
      </div>
      <div>
        <b>{{ compact(market.participantsLive) }}</b>
        <span>{{ t('hero.statUsers') }}</span>
        <em>{{ t('card.verified') }}</em>
      </div>
      <div>
        <b>{{ compact(market.tendersLive) }}</b>
        <span>{{ t('stat.tenders') }}</span>
        <em>{{ t('st.matching') }}</em>
      </div>
    </section>

    <section class="wrap board-sec">
      <div class="head">
        <h2>
          <i class="pulse" />
          {{ t('live.title') }}
        </h2>
        <div class="seg">
          <button type="button" :class="{ on: liveKind === 'loads' }" @click="liveKind = 'loads'">{{ t('stat.loads') }}</button>
          <button type="button" :class="{ on: liveKind === 'trucks' }" @click="liveKind = 'trucks'">{{ t('stat.trucks') }}</button>
        </div>
        <router-link to="/board">{{ t('live.all') }}</router-link>
      </div>
      <div class="list frame auto-scroll">
        <button v-for="item in liveRows" :key="item.id" type="button" @click="openLoad(item.id)">
          <LoadCard :item="item" :active="openId === item.id" />
        </button>
      </div>
    </section>

    <section class="wrap extras">
      <article class="panel">
        <header>
          <h2>{{ t('home.trips') }}</h2>
          <router-link to="/tracking">{{ t('nav.tracking') }}</router-link>
        </header>
        <div class="frame auto-scroll">
          <button v-for="b in PUBLIC_BILLS" :key="b.id" type="button" class="trip" @click="router.push({ path: '/tracking', query: { id: b.id } })">
            <div class="trip-top">
              <b>{{ b.id }}</b>
              <span class="pill" :class="tone(b.status)">{{ orderStatus(b.status) }}</span>
            </div>
            <div class="trip-lane">
              <span><Flag :code="b.originCountry" />{{ place(b.origin) }}</span>
              <i />
              <span><Flag :code="b.destCountry" />{{ place(b.dest) }}</span>
            </div>
            <div class="trip-foot">
              <small>{{ cargo(b.cargo) }}</small>
              <strong v-if="authed()">{{ money(b.freight) }}</strong>
              <strong v-else>{{ t('auth.needLogin') }}</strong>
            </div>
          </button>
        </div>
      </article>

      <article class="panel">
        <header>
          <h2>{{ t('port.title') }}</h2>
          <router-link to="/ports">{{ t('site.portMore') }}</router-link>
        </header>
        <ul class="frame rows auto-scroll">
          <li v-for="p in market.ports" :key="p.id" @click="router.push('/ports')">
            <div>
              <strong>
                <Flag v-for="c in String(p.corridor || p.country || '').split('-')" :key="c" :code="c" />
                {{ portName(p) }}
              </strong>
              <small>{{ p.updated || p.corridor }}</small>
            </div>
            <div class="st">
              <span class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</span>
              <em>{{ Number(p.waitMin) > 0 ? waitMin(p.waitMin) : t('port.noWait') }}</em>
            </div>
          </li>
        </ul>
      </article>

      <article class="panel">
        <header>
          <h2>{{ t('corr.title') }}</h2>
          <router-link to="/estimate">{{ t('nav.estimate') }}</router-link>
        </header>
        <div class="frame rows auto-scroll">
          <table>
            <thead>
              <tr><th>{{ t('col.lane') }}</th><th>km</th><th>{{ t('corr.rate') }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="c in market.corridors" :key="c.from + c.to" @click="openLane(c)">
                <td>{{ place(c.from) }} → {{ place(c.to) }}</td>
                <td class="num">{{ c.km }}</td>
                <td class="num">{{ corridorRate(c) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="wrap fx-bar">
      <h2>{{ t('home.fx') }}</h2>
      <div class="fx-row" v-for="row in fx" :key="row.pair">
        <span>{{ row.pair }}</span>
        <b>{{ row.value }}</b>
      </div>
      <small>{{ t('home.fxNote') }}</small>
    </section>

    <section class="show">
      <div class="wrap sheet">
        <div class="copy">
          <h2>{{ t('home.phoneTitle') }}</h2>
          <p>{{ t('home.phoneLead') }}</p>
        </div>
        <div class="phones">
          <div class="phone">
            <i class="island" />
            <div class="screen">
              <div class="status"><b>9:41</b><span>5G</span></div>
              <div class="appbar">
                <b>{{ sample.id }}</b>
                <em>{{ t('phone.live') }}</em>
              </div>
              <div class="mapline">
                <svg viewBox="0 0 240 120" aria-hidden="true">
                  <path d="M18 86 C70 86 78 34 128 34 S190 70 224 28" fill="none" stroke="#bfdbfe" stroke-width="7" stroke-linecap="round" />
                  <path class="dash" d="M18 86 C70 86 78 34 128 34 S190 70 224 28" fill="none" stroke="#1d4ed8" stroke-width="3" stroke-linecap="round" />
                  <circle cx="18" cy="86" r="6" fill="#0f766e" />
                  <circle cx="128" cy="34" r="5" fill="#d97706" />
                  <circle cx="224" cy="28" r="6" fill="#1d4ed8" />
                </svg>
                <small>{{ place('乌鲁木齐') }} → {{ place('阿拉木图') }} · 980 km</small>
              </div>
              <ol class="stops">
                <li><i /><div><b>{{ place('乌鲁木齐') }}</b><span>09-26 08:00 · {{ t('phone.load') }}</span></div></li>
                <li><i class="mid" /><div><b>{{ place('霍尔果斯') }}</b><span>{{ t('phone.slow') }} · {{ tf('port.waitMin', { n: 180 }) }}</span></div></li>
                <li><i class="end" /><div><b>{{ place('阿拉木图') }}</b><span>{{ t('phone.eta') }} 09-28 18:00</span></div></li>
              </ol>
              <article>
                <div class="chips"><span>18.4t</span><span>13.7m</span><span>{{ t('mode.bid') }}</span></div>
                <b>{{ t('phone.driver') }}</b>
                <p>{{ authed() ? '新A·D3821' : t('auth.loginForDetail') }}</p>
                <strong>{{ authed() ? money(sample.freight) : t('auth.loginForDetail') }}</strong>
              </article>
            </div>
          </div>
        </div>
      </div>
    </section>
    <SiteFooter />
    <LoadModal v-if="openId" :id="openId" @close="openId = ''" @select="openLoad" />
  </div>
</template>

<style scoped>
.hero { padding: 28px 0 0; }
.hero h1 {
  margin: 0 0 14px;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 10px;
  font-size: clamp(24px, 1.6vw + 14px, 40px);
  line-height: 1.2;
  letter-spacing: -0.03em;
  color: #10283f;
}
.hero h1 i {
  font-style: normal;
  font-weight: 500;
  color: #c9a36a;
  font-size: 22px;
}
.hero h1 small {
  font-size: 15px;
  font-weight: 550;
  letter-spacing: 0;
  color: #5c6b7a;
}
.map { height: clamp(240px, 32vh, 520px); position: relative; z-index: 0; isolation: isolate; overflow: hidden; }
.ticker-wrap {
  margin-top: 14px;
  border-top: 1px solid #e3e8ef;
  border-bottom: 1px solid #e3e8ef;
  background: #fff;
  overflow: hidden;
}
.ticker { overflow: hidden; }
.track {
  display: flex;
  gap: 8px;
  width: max-content;
  padding: 10px 0;
  animation: ticker 90s linear infinite;
}
.track:hover { animation-play-state: paused; }
.track button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 12px;
  border: 1px solid #e3e8ef;
  border-radius: 999px;
  background: #f7f9fc;
  font-size: 13px;
  white-space: nowrap;
  color: #1c2430;
}
.track button:hover { border-color: #10283f; background: #fff; }
.track em { font-style: normal; color: #9db6d8; }
.track span { color: #5c6b7a; }
.track b { color: #10283f; }
@keyframes ticker { to { transform: translateX(-50%); } }
.facts {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  padding: 28px 0 8px;
}
.facts div {
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  padding: 16px 16px 14px;
}
.facts b { display: block; font-size: 28px; color: var(--navy); font-variant-numeric: tabular-nums; letter-spacing: -0.03em; }
.facts span { display: block; margin-top: 4px; font-size: 13px; color: var(--ink-soft); }
.facts em { display: block; margin-top: 2px; font-size: 12px; font-style: normal; color: var(--signal-ink); }
.board-sec { padding: 20px 0 8px; }
.head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; }
.head h2, .panel header h2 { display: flex; align-items: center; gap: 8px; font-size: 20px; }
.head a, .panel header a { color: #157a40; font-weight: 700; font-size: 13px; }
.pulse {
  width: 8px; height: 8px; border-radius: 50%;
  background: #12805c;
  box-shadow: 0 0 0 0 rgba(18, 128, 92, 0.55);
  animation: ping 1.8s ease-out infinite;
}
@keyframes ping {
  70% { box-shadow: 0 0 0 8px rgba(18, 128, 92, 0); }
  100% { box-shadow: 0 0 0 0 rgba(18, 128, 92, 0); }
}
.seg { display: inline-flex; background: #eef1f6; border-radius: 999px; padding: 2px; }
.seg button {
  height: 28px; padding: 0 12px; border: 0; background: transparent;
  border-radius: 999px; font-size: 13px; font-weight: 650; color: #5c6b7a;
}
.seg button.on { background: #fff; color: #10283f; box-shadow: 0 1px 2px rgba(16,24,40,.08); }
.list { display: grid; gap: 10px; }
.list > button { border: 0; background: transparent; padding: 0; text-align: left; display: block; width: 100%; min-width: 0; }
.frame { max-height: 560px; overflow: auto; padding: 2px; }
.extras {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
  padding: 28px 0 8px;
}
.panel { background: #fff; border: 1px solid #e3e8ef; border-radius: 16px; overflow: hidden; min-height: 100%; min-width: 0; }
.panel header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px 8px;
}
.panel .frame {
  max-height: 280px; border: 0; border-radius: 0; padding: 0;
  scrollbar-width: none;
}
.panel .frame::-webkit-scrollbar { display: none; }
.trip:first-child { border-top: 0; }
.frame.rows thead th { position: sticky; top: 0; background: #fff; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 10px 14px; border-top: 1px solid #e3e8ef; font-size: 13px; }
th { color: #5c6b7a; font-size: 11px; font-weight: 650; letter-spacing: .04em; }
tbody tr { cursor: pointer; }
tbody tr:hover td { background: #f7f9fc; }
.num { font-variant-numeric: tabular-nums; }
.panel ul { list-style: none; margin: 0; padding: 0; }
.panel li {
  display: flex; justify-content: space-between; gap: 12px;
  padding: 10px 16px; border-top: 1px solid #e3e8ef; cursor: pointer;
}
.panel li:hover { background: #f7f9fc; }
.panel li strong { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.panel li small, .st em { display: block; color: #5c6b7a; font-style: normal; font-size: 12px; }
.st { text-align: right; }
.trip {
  width: 100%; text-align: left; background: transparent; border: 0;
  border-top: 1px solid #e3e8ef; padding: 12px 16px; display: grid; gap: 8px;
}
.trip:hover { background: #f7f9fc; }
.trip-top, .trip-lane, .trip-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.trip-lane { justify-content: flex-start; color: #1c2430; font-weight: 650; font-size: 13px; }
.trip-lane span { display: inline-flex; align-items: center; gap: 6px; }
.trip-lane i { width: 22px; height: 2px; background: #9ec5ff; border-radius: 99px; }
.trip-foot small { color: #5c6b7a; }
.trip-foot strong { color: #10283f; font-size: 13px; }
.fx-bar {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 28px;
  padding: 8px 0 4px;
}
.fx-bar h2 { margin: 0; font-size: 16px; }
.fx-bar .fx-row { display: flex; gap: 10px; font-size: 14px; }
.fx-bar b { font-variant-numeric: tabular-nums; }
.fx-bar small { color: #8d6a32; }
.why { padding: 22px 0 4px; }
.why-panel {
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 20px;
  padding: 22px 24px 8px;
}
.why-panel h2 { margin: 0 0 4px; font-size: 22px; letter-spacing: -0.02em; color: #1c2430; }
.why-points {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 12px;
  border-top: 1px solid #eef1f6;
}
.why-points article { padding: 14px 18px 14px 0; }
.why-points article:nth-child(odd) { padding-right: 22px; border-right: 1px solid #eef1f6; }
.why-points article:nth-child(even) { padding-left: 22px; padding-right: 0; }
.why-points article:nth-child(-n+2) { border-bottom: 1px solid #eef1f6; }
.why-points b { display: block; color: #1c2430; font-size: 15px; margin-bottom: 6px; }
.why-points p { margin: 0; color: #5c6b7a; font-size: 13px; line-height: 1.55; }
.why-flow {
  list-style: none;
  margin: 0;
  padding: 16px 0 12px;
  border-top: 1px solid #eef1f6;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px 28px;
}
.why-flow li {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: start;
  position: relative;
  min-width: 0;
}
.why-flow li:not(:last-child)::after {
  content: '';
  position: absolute;
  right: -16px;
  top: 12px;
  width: 8px;
  height: 8px;
  border-top: 2px solid #c5d0dc;
  border-right: 2px solid #c5d0dc;
  transform: rotate(45deg);
}
.why-flow em {
  font-style: normal;
  color: #12805c;
  font-size: 12px;
  font-weight: 750;
  margin-top: 2px;
}
.why-flow li:nth-child(2) em { color: #2563eb; }
.why-flow li:nth-child(3) em { color: #b7791f; }
.why-flow strong { display: block; font-size: 14px; }
.why-flow span { display: block; margin-top: 4px; color: #5c6b7a; font-size: 13px; line-height: 1.5; }
.desks-flow { grid-template-columns: 1fr 1fr; gap: 8px 48px; }
.desks-flow li:not(:last-child)::after { right: -28px; }
.desks-flow a {
  display: inline-block;
  margin-top: 6px;
  color: #0e6a4c;
  font-size: 13px;
  font-weight: 700;
}
.desks-flow a:hover { color: #094c36; }
@media (max-width: 900px) {
  .why-points { grid-template-columns: 1fr; }
  .why-points article,
  .why-points article:nth-child(odd),
  .why-points article:nth-child(even) {
    padding: 14px 0;
    border-right: 0;
    border-bottom: 1px solid #eef1f6;
  }
  .why-points article:last-child { border-bottom: 0; }
  .why-flow { grid-template-columns: 1fr; gap: 14px; }
  .why-flow li:not(:last-child)::after { display: none; }
}
.show { padding: 36px 0 88px; }
.sheet {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr);
  gap: clamp(24px, 3vw, 48px);
  align-items: center;
  background: #f3f5f8;
  border-radius: 28px;
  padding: clamp(28px, 4vw, 48px) clamp(20px, 3vw, 40px);
  min-height: clamp(420px, 48vh, 560px);
}
.copy { min-width: 0; }
.sheet h2 {
  margin: 0 0 12px;
  font-size: 32px;
  line-height: 1.2;
  letter-spacing: -0.03em;
  color: #152033;
}
.copy p {
  margin: 0;
  max-width: 46ch;
  color: #5c6b7a;
  font-size: 16px;
  line-height: 1.7;
}
.phones { display: flex; justify-content: center; min-height: 420px; overflow: hidden; }
.phone {
  position: relative;
  width: 250px; height: 510px; background: #0e0e10; border-radius: 38px; padding: 10px;
  box-shadow: 0 28px 50px rgba(16, 24, 40, 0.22);
  transform: rotate(14deg) scale(.86);
}
.island {
  position: absolute; top: 16px; left: 50%; width: 78px; height: 18px; margin-left: -39px;
  background: #0e0e10; border-radius: 12px; z-index: 2;
}
.screen {
  height: 100%; border-radius: 28px; overflow: hidden; display: flex; flex-direction: column;
  background: linear-gradient(180deg, #f7f4ee, #e7eef8 42%, #f4f7fb);
}
.status { display: flex; justify-content: space-between; padding: 16px 16px 4px; font-size: 12px; font-weight: 700; }
.appbar { display: flex; justify-content: space-between; align-items: center; padding: 2px 14px 8px; }
.appbar b { font-size: 13px; }
.appbar em { font-style: normal; font-size: 11px; font-weight: 700; color: #9a3412; background: #ffedd5; border-radius: 99px; padding: 2px 8px; }
.mapline {
  height: 118px; margin: 0 10px; border-radius: 12px; position: relative; overflow: hidden;
  background:
    radial-gradient(circle at 20% 70%, rgba(34, 197, 94, 0.18), transparent 28%),
    repeating-linear-gradient(90deg, transparent 0 22px, rgba(148, 163, 184, 0.35) 22px 23px),
    linear-gradient(160deg, #d7efe4, #dbe7f8);
}
.mapline svg { width: 100%; height: 78px; margin-top: 8px; }
.dash { stroke-dasharray: 6 6; animation: run 8s linear infinite; }
.mapline small { position: absolute; left: 8px; bottom: 8px; background: #fff; border-radius: 8px; padding: 3px 7px; font-size: 10px; }
.stops { list-style: none; margin: 8px 10px 0; padding: 8px 10px; background: #fff; border-radius: 12px; display: grid; gap: 7px; }
.stops li { display: flex; gap: 8px; }
.stops i { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #0f766e; flex: none; }
.stops i.mid { background: #d97706; }
.stops i.end { background: #1d4ed8; }
.stops b { display: block; font-size: 12px; }
.stops span { color: #5c6b7a; font-size: 10px; }
.screen article { margin: 8px 10px; background: #fff; border-radius: 12px; padding: 10px; }
.chips { display: flex; gap: 4px; margin-bottom: 6px; }
.chips span { background: #eef3fb; color: #1e3a8a; border-radius: 99px; font-size: 10px; padding: 2px 6px; font-weight: 650; }
.screen article b { font-size: 12px; }
.screen article p { margin: 3px 0 0; color: #5c6b7a; font-size: 11px; }
.screen article strong { display: block; margin-top: 4px; color: #9a3412; font-size: 15px; }
@keyframes run { to { stroke-dashoffset: -80; } }
@media (max-width: 1366px) {
  .hero h1 { font-size: clamp(22px, 2.2vw, 28px); }
  .extras { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
}
@media (max-width: 1280px) {
  .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 1040px) {
  .sheet, .extras { grid-template-columns: 1fr; }
  .map { height: 260px; }
  .phone { transform: rotate(8deg) scale(.8); }
  .hero h1 { font-size: 26px; }
  .hero h1 small { font-size: 13px; }
  .sheet { padding: 28px 20px; min-height: 0; gap: 20px; }
  .phones { min-height: 360px; }
  .why-panel { padding: 18px 16px 6px; }
}
@media (max-width: 720px) {
  .facts, .desk-grid { grid-template-columns: 1fr; }
  .map { height: 220px; }
  .phone { transform: none; }
  .hero { padding-top: 16px; }
  .phones { min-height: 0; }
  .sheet h2 { font-size: 24px; }
}
</style>
