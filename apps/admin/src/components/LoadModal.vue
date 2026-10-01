<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import AuthGate from './AuthGate.vue'
import Flag from './Flag.vue'
import LoadCard from './LoadCard.vue'
import { isAppAuthed } from '../auth'
import { corridorRate, loadStatus, modeLabel, money, portLabel, quotesLabel, tone, waitMin } from '../fmt'
import { cargo, cargoClass, company, countryName, packing, place, portName } from '../geo'
import { t } from '../i18n'
import { useMarket } from '../useMarket'

const props = defineProps<{ id: string }>()
const emit = defineEmits<{ close: []; select: [id: string] }>()

const { market } = useMarket()
const authed = isAppAuthed

const all = computed(() => [...(market.value.items || []), ...(market.value.trucks || [])])
const item = computed(() => all.value.find((x: any) => x.id === props.id) || all.value[0])

const corridor = computed(() => (market.value.corridors || []).find((c: any) =>
  String(c.from) === String(item.value?.origin) && String(c.to) === String(item.value?.dest)))

const ports = computed(() => (market.value.ports || []).filter((p: any) => {
  const code = String(p.corridor || '')
  return code.includes(item.value?.originCountry) && code.includes(item.value?.destCountry)
}).slice(0, 2))

const similar = computed(() => all.value
  .filter((x: any) => x.id !== item.value?.id && x.destCountry === item.value?.destCountry)
  .slice(0, 3))

const ruleKey = computed(() => {
  const m = item.value?.matchMode
  if (m === 'grab') return 'desk.ruleGrab'
  if (m === 'assign') return 'desk.ruleAssign'
  return 'desk.ruleBid'
})

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', onKey)
})
onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Teleport to="body">
    <div v-if="item" class="mask" @click.self="emit('close')">
      <div class="dialog" role="dialog" aria-modal="true" :aria-label="item.id">
        <header>
          <div>
            <p class="kicker">{{ item.id }}</p>
            <h2>
              <span><Flag :code="item.originCountry" />{{ place(item.origin) }}</span>
              <i class="arrow" />
              <span><Flag :code="item.destCountry" />{{ place(item.dest) }}</span>
            </h2>
            <div class="tags">
              <span class="pill" :class="tone(item.status)">{{ loadStatus(item.status) }}</span>
              <span class="pill info">{{ modeLabel(item.matchMode) }}</span>
              <small>{{ t('detail.posted') }} {{ item.loadTime }}</small>
            </div>
          </div>
          <button type="button" class="btn btn-line btn-sm" @click="emit('close')">{{ t('trip.close') }}</button>
        </header>

        <div class="grid">
          <section class="main">
            <article class="card card-pad">
              <div class="card-head">
                <h3>{{ t('detail.route') }}</h3>
                <span v-if="corridor" class="chip">{{ corridor.km }} km</span>
              </div>
              <ol class="route">
                <li>
                  <i class="dot start" />
                  <div>
                    <small>{{ t('detail.pickup') }}</small>
                    <b><Flag :code="item.originCountry" />{{ place(item.origin) }}</b>
                    <span>{{ item.loadTime }} · {{ countryName(item.originCountry) }}</span>
                  </div>
                </li>
                <li v-for="p in ports" :key="p.id">
                  <i class="dot mid" />
                  <div>
                    <small>{{ t('port.title') }}</small>
                    <b>{{ portName(p) }}</b>
                    <span>
                      <em class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</em>
                      {{ Number(p.waitMin) > 0 ? waitMin(p.waitMin) : t('port.noWait') }}
                    </span>
                  </div>
                </li>
                <li>
                  <i class="dot end" />
                  <div>
                    <small>{{ t('detail.drop') }}</small>
                    <b><Flag :code="item.destCountry" />{{ place(item.dest) }}</b>
                    <span>{{ countryName(item.destCountry) }}</span>
                  </div>
                </li>
              </ol>
            </article>

            <article class="card card-pad">
              <h3>{{ t('detail.cargo') }}</h3>
              <div class="facts">
                <div><small>{{ t('col.cargo') }}</small><b>{{ cargo(item.cargoName) }}</b></div>
                <div><small>{{ t('app.weight') }}</small><b>{{ item.weightT }} t</b></div>
                <div><small>{{ t('app.volume') }}</small><b>{{ item.volumeM3 || '—' }} m³</b></div>
                <div><small>{{ t('app.truck') }}</small><b>{{ item.truckLength || '—' }} m</b></div>
                <div v-if="item.packing"><small>{{ t('detail.packing') }}</small><b>{{ packing(item.packing) }}</b></div>
                <div v-if="item.cargoClass"><small>{{ t('detail.class') }}</small><b>{{ cargoClass(item.cargoClass) }}</b></div>
                <div v-if="String(item.id || '').startsWith('T-')">
                  <small>{{ t('tool.plate') }}</small>
                  <b>{{ authed() && item.plate ? item.plate : t('auth.needLogin') }}</b>
                </div>
                <div v-if="authed() && item.quoteCount"><small>{{ quotesLabel(item.quoteCount) }}</small><b>{{ item.quoteCount }}</b></div>
                <div v-if="corridor"><small>{{ t('corr.rate') }}</small><b>{{ corridorRate(corridor) }}</b></div>
                <div><small>{{ t('about.deposit') }}</small><b>¥200</b></div>
              </div>
            </article>

            <article class="card card-pad">
              <h3>{{ t('detail.rule') }}</h3>
              <p class="rule">{{ t(ruleKey) }}</p>
            </article>
          </section>

          <aside>
            <div class="card card-pad price">
              <template v-if="authed()">
                <small>{{ t('corr.rate') }}</small>
                <strong>{{ money(item.expectPrice || item.grabPrice) }}</strong>
                <p v-if="corridor" class="who">{{ corridor.km }} km · {{ corridorRate(corridor) }}</p>
                <router-link class="btn btn-blue" to="/match" @click="emit('close')">{{ modeLabel(item.matchMode) }}</router-link>
                <button type="button" class="btn btn-line" @click="emit('close')">{{ t('detail.back') }}</button>
              </template>
              <AuthGate v-else />
            </div>

            <div class="card card-pad">
              <h4>{{ t('detail.shipper') }}</h4>
              <AuthGate v-if="!authed()" compact />
              <template v-else>
                <p class="who">{{ company(item.company) || '—' }}</p>
                <div class="kv"><span>{{ t('tool.credit') }}</span><b>{{ item.credit || '—' }}</b></div>
                <div class="kv"><span>{{ t('col.kyc') }}</span><b>{{ item.verified ? t('card.verified') : '—' }}</b></div>
                <div class="kv"><span>{{ t('col.phone') }}</span><b>{{ t('app.phoneMasked') }}</b></div>
                <div class="kv"><span>{{ t('col.match') }}</span><b>{{ modeLabel(item.matchMode) }}</b></div>
              </template>
            </div>

            <div class="card card-pad">
              <h4>{{ t('about.deposit') }}</h4>
              <p class="who">{{ t('site.rule.deposit.d') }}</p>
            </div>
          </aside>
        </div>

        <section v-if="similar.length" class="similar">
          <h3>{{ t('detail.similar') }}</h3>
          <div class="list">
            <button v-for="row in similar" :key="row.id" type="button" @click="emit('select', row.id)">
              <LoadCard :item="row" />
            </button>
          </div>
        </section>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(12, 24, 40, 0.46);
  display: grid;
  place-items: start center;
  padding: 16px 12px 28px;
  overflow: auto;
}
.dialog {
  width: min(1320px, calc(100% - clamp(12px, 3vw, 40px)));
  background: #fff;
  border-radius: 20px;
  padding: 22px 24px 26px;
  box-shadow: 0 24px 64px rgba(16, 24, 40, 0.22);
  margin: 4vh auto 24px;
}
header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 18px; flex-wrap: wrap; }
.kicker { margin: 0 0 4px; color: var(--muted); font-size: 12px; font-weight: 650; letter-spacing: 0.04em; }
h2 { display: flex; align-items: center; gap: 14px; margin: 0; font-size: 22px; color: var(--navy-2); flex-wrap: wrap; }
h2 span { display: inline-flex; align-items: center; gap: 8px; }
.arrow { position: relative; width: 46px; height: 2px; background: #b9cbe2; flex: none; }
.arrow::after { content: ""; position: absolute; right: -1px; top: -4px; border: 5px solid transparent; border-left-color: #8fa9cc; }
.tags { display: flex; align-items: center; gap: 8px; color: var(--muted); margin-top: 8px; }
.grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(240px, 22vw); gap: 16px; align-items: start; }
.main { display: grid; gap: 12px; }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.route { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.route li { display: grid; grid-template-columns: 22px 1fr; gap: 12px; padding: 10px 0; position: relative; }
.route li:not(:last-child)::before {
  content: ""; position: absolute; left: 10px; top: 26px; bottom: -6px; width: 2px; background: var(--line);
}
.dot { width: 12px; height: 12px; border-radius: 50%; margin: 7px 0 0 5px; background: var(--signal); }
.dot.mid { background: var(--brass); }
.dot.end { background: var(--blue); }
.route small { display: block; color: var(--muted); font-size: 12px; }
.route b { display: inline-flex; align-items: center; gap: 7px; margin: 2px 0; font-size: 16px; }
.route span { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 13px; }
.facts { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; margin-top: 14px; }
.facts div { border-top: 1px solid var(--line-soft); padding-top: 10px; }
.facts small { display: block; color: var(--muted); font-size: 12px; }
.facts b { font-size: 16px; }
.rule { margin: 10px 0 0; color: var(--ink-soft); }
aside { display: grid; gap: 12px; }
.price small { color: var(--muted); }
.price strong { display: block; margin: 4px 0 14px; font-size: 32px; color: var(--navy); font-variant-numeric: tabular-nums; }
.price .btn { width: 100%; margin-bottom: 8px; }
.who { margin: 10px 0 12px; color: var(--ink-soft); }
.kv { display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-top: 1px solid var(--line-soft); font-size: 14px; }
.kv span { color: var(--muted); }
.similar { margin-top: 18px; }
.similar h3 { margin: 0 0 12px; font-size: 16px; color: var(--navy-2); }
.list { display: grid; gap: 10px; }
.list button { border: 0; background: transparent; padding: 0; text-align: left; display: block; cursor: pointer; }
@media (max-width: 1040px) {
  .grid, .facts { grid-template-columns: 1fr; }
  .dialog { padding: 16px 16px 20px; }
  .card-head { flex-wrap: wrap; }
}
</style>
