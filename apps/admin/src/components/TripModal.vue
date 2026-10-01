<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import AuthGate from './AuthGate.vue'
import Flag from './Flag.vue'
import { isAppAuthed } from '../auth'
import { cargo, cargoClass, company, countryName, entity, money, modeLabel, orderStatus, packing, place, portLabel, portName, tone, waitMin } from '../fmt'
import { t, tf } from '../i18n'
import { findBill, PUBLIC_BILLS, billCreated, billFill, billStages, formatStageTime } from '../siteData'
import { useMarket } from '../useMarket'

const props = defineProps<{ id: string; kind: 'tracking' | 'waybill' }>()
const emit = defineEmits<{ close: [] }>()

const { market } = useMarket()
const authed = isAppAuthed
const mode = ref(props.kind)
const tab = ref('overview')
const stepAt = ref('')
const faq = ref('')

const bill = computed(() => findBill(props.id) || PUBLIC_BILLS[0])
const port = computed(() => (market.value.ports || []).find((p: any) => p.id === bill.value.port) || null)
const stages = computed(() => billStages(bill.value, Number(port.value?.waitMin) || 90))

watch(() => [props.id, props.kind], () => {
  mode.value = props.kind
  tab.value = 'overview'
  stepAt.value = ''
  faq.value = ''
})

function stageLabel(state: string) {
  if (state === 'done') return t('trip.done')
  if (state === 'now') return t('trip.now')
  return t('trip.wait')
}

function switchMode(next: 'tracking' | 'waybill') {
  mode.value = next
  tab.value = 'overview'
}

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
    <div class="mask" @click.self="emit('close')">
      <div class="dialog" role="dialog" aria-modal="true" :aria-label="bill.id">
        <header>
          <div>
            <p class="kicker">{{ mode === 'waybill' ? t('nav.waybill') : t('nav.tracking') }}</p>
            <h2>
              {{ bill.id }}
              <span class="pill" :class="tone(bill.status)">{{ orderStatus(bill.status) }}</span>
            </h2>
            <small>{{ place(bill.origin) }} → {{ place(bill.dest) }} · {{ billCreated(bill) }}</small>
          </div>
          <div class="acts">
            <button
              type="button"
              class="btn btn-sm"
              :class="mode === 'tracking' ? 'btn-navy' : 'btn-line'"
              @click="switchMode('tracking')"
            >{{ t('trip.toTrack') }}</button>
            <button
              type="button"
              class="btn btn-sm"
              :class="mode === 'waybill' ? 'btn-navy' : 'btn-line'"
              @click="switchMode('waybill')"
            >{{ t('trip.toWaybill') }}</button>
            <button type="button" class="btn btn-line btn-sm" @click="emit('close')">{{ t('trip.close') }}</button>
          </div>
        </header>

        <ol class="stages">
          <li v-for="(st, i) in stages" :key="st.key" :class="st.state">
            <div class="node">{{ i + 1 }}</div>
            <div v-if="i < stages.length - 1" class="line" :class="stages[i + 1].state" />
            <div class="body">
              <span class="pill" :class="st.state === 'done' ? 'ok' : st.state === 'now' ? 'warn' : 'mute'">{{ stageLabel(st.state) }} · {{ st.done }}/{{ st.total }}</span>
              <b>{{ t('trip.stage' + (st.key === 'load' ? 'Load' : st.key === 'gate' ? 'Gate' : 'Arrive')) }}</b>
              <em>{{ t('trip.yours') }} {{ formatStageTime(st.minutes) }}</em>
            </div>
          </li>
        </ol>

        <div class="tabs">
          <template v-if="mode === 'tracking'">
            <button type="button" :class="{ on: tab === 'overview' }" @click="tab = 'overview'">{{ t('trip.tabOverview') }}</button>
            <button type="button" :class="{ on: tab === 'nodes' }" @click="tab = 'nodes'">{{ t('trip.tabNodes') }}</button>
            <button type="button" :class="{ on: tab === 'port' }" @click="tab = 'port'">{{ t('trip.tabPort') }}</button>
            <button type="button" :class="{ on: tab === 'place' }" @click="tab = 'place'">{{ t('trip.tabPlace') }}</button>
          </template>
          <template v-else>
            <button type="button" :class="{ on: tab === 'overview' }" @click="tab = 'overview'">{{ t('trip.tabOverview') }}</button>
            <button type="button" :class="{ on: tab === 'cargo' }" @click="tab = 'cargo'">{{ t('trip.tabCargo') }}</button>
            <button type="button" :class="{ on: tab === 'sign' }" @click="tab = 'sign'">{{ t('trip.tabSign') }}</button>
            <button type="button" :class="{ on: tab === 'rule' }" @click="tab = 'rule'">{{ t('trip.tabRule') }}</button>
          </template>
        </div>

        <div v-if="tab === 'overview'" class="panel">
          <h3>{{ t('trip.basic') }}</h3>
          <div class="grid">
            <div><span>{{ t('trip.mode') }}</span><b>{{ modeLabel(bill.mode) }}</b></div>
            <div><span>{{ t('trip.no') }}</span><b>{{ bill.id }}</b></div>
            <div><span>{{ t('trip.created') }}</span><b>{{ billCreated(bill) }}</b></div>
            <div><span>{{ t('col.status') }}</span><b>{{ orderStatus(bill.status) }}</b></div>
            <template v-if="authed()">
              <div><span>{{ t('trip.pre') }}</span><b>{{ bill.preNo }}</b></div>
              <div><span>{{ t('trip.transit') }}</span><b>{{ bill.transitNo }}</b></div>
              <div><span>{{ t('col.freight') }}</span><b>{{ money(bill.freight) }}</b></div>
              <div v-if="mode === 'waybill'"><span>{{ t('trip.deposit') }}</span><b>¥{{ bill.deposit }}</b></div>
              <div v-else><span>{{ t('trip.eta') }}</span><b>{{ bill.eta }}</b></div>
            </template>
          </div>
          <AuthGate v-if="!authed()" compact />
          <h3>{{ t('trip.route') }}</h3>
          <div class="grid">
            <div><span>{{ t('trip.fromCountry') }}</span><b><Flag :code="bill.originCountry" />{{ countryName(bill.originCountry) }} · {{ place(bill.origin) }}</b></div>
            <div><span>{{ t('trip.exitCustoms') }}</span><b>{{ place(bill.customsFrom) }}</b></div>
            <div><span>{{ t('trip.entryCustoms') }}</span><b>{{ place(bill.customsTo) }}</b></div>
            <div><span>{{ t('trip.toCountry') }}</span><b><Flag :code="bill.destCountry" />{{ countryName(bill.destCountry) }} · {{ place(bill.dest) }}</b></div>
          </div>
          <template v-if="mode === 'waybill'">
            <h3>{{ t('trip.shipper') }} / {{ t('trip.carrier') }}</h3>
            <AuthGate v-if="!authed()" compact />
            <div v-else class="grid">
              <div><span>{{ t('trip.shipper') }}</span><b>{{ company(bill.company) }}</b></div>
              <div><span>{{ t('trip.carrier') }}</span><b>{{ entity(bill.carrier) }}</b></div>
              <div><span>{{ t('trip.plate') }}</span><b>{{ bill.plate }}</b></div>
              <div><span>{{ t('app.phoneMasked') }}</span><b>—</b></div>
            </div>
          </template>
        </div>

        <div v-else-if="tab === 'nodes' || tab === 'sign'" class="panel">
          <ol class="nodes">
            <li v-for="(s, i) in bill.steps" :key="s.at">
              <button type="button" :class="{ on: stepAt === s.at, now: i === bill.steps.length - 1 }" @click="stepAt = stepAt === s.at ? '' : s.at">
                <b>{{ orderStatus(s.status) }}</b>
                <span>{{ s.at }}</span>
              </button>
              <p v-if="stepAt === s.at">{{ t('ops.flow.' + s.status) }}</p>
            </li>
          </ol>
          <p v-if="mode === 'waybill'" class="note">{{ t('mod.waybill.nodes') }}</p>
        </div>

        <div v-else-if="tab === 'port'" class="panel">
          <template v-if="port">
            <div class="port-row">
              <b><Flag v-for="c in String(port.corridor || '').split('-')" :key="c" :code="c" />{{ portName(port) }}</b>
              <span class="pill" :class="tone(port.status)">{{ portLabel(port.status) }}</span>
            </div>
            <p>{{ Number(port.waitMin) > 0 ? waitMin(port.waitMin) : t('port.noWait') }} · {{ tf('site.portUpdated', { t: port.updated }) }}</p>
            <router-link class="more" :to="'/ports?id=' + port.id" @click="emit('close')">{{ t('site.portMore') }}</router-link>
          </template>
        </div>

        <div v-else-if="tab === 'place'" class="panel">
          <div class="fix">
            <span class="pill" :class="bill.shared ? 'ok' : 'warn'">{{ bill.shared ? t('trip.shared') : t('trip.unshared') }}</span>
            <div>
              <span>{{ t('trip.lastFix') }}</span>
              <b v-if="authed()">{{ place(bill.lastPoint) }} · {{ bill.lastAt }}</b>
              <b v-else>{{ t('auth.needLogin') }}</b>
            </div>
            <div>
              <span>{{ t('trip.carrier') }}</span>
              <b v-if="authed()">{{ entity(bill.carrier) }} · {{ bill.plate }}</b>
              <b v-else>{{ t('auth.needLogin') }}</b>
            </div>
          </div>
          <div class="track">
            <span><Flag :code="bill.originCountry" size="md" />{{ place(bill.origin) }}</span>
            <i class="path"><em :style="{ width: billFill(bill.status) + '%' }" /></i>
            <span><Flag :code="bill.destCountry" size="md" />{{ place(bill.dest) }}</span>
            <small>{{ port ? portName(port) : '—' }}</small>
          </div>
          <p class="note">{{ t('mod.tracking.place') }}</p>
        </div>

        <div v-else-if="tab === 'cargo'" class="panel">
          <div class="grid">
            <div><span>{{ t('col.cargo') }}</span><b>{{ cargo(bill.cargo) }}</b></div>
            <div><span>{{ t('detail.class') }}</span><b>{{ cargoClass(bill.cargoClass) }}</b></div>
            <div><span>{{ t('trip.weight') }}</span><b>{{ bill.weightT }} t</b></div>
            <div><span>{{ t('trip.volume') }}</span><b>{{ bill.volumeM3 }} m³</b></div>
            <div><span>{{ t('detail.packing') }}</span><b>{{ packing(bill.packing) }}</b></div>
            <div><span>{{ t('trip.length') }}</span><b>{{ bill.truckLength }} m</b></div>
          </div>
          <p class="note">{{ t('mod.waybill.fields') }}</p>
        </div>

        <div v-else-if="tab === 'rule'" class="panel">
          <p class="note">{{ t('mod.waybill.faq2.a') }}</p>
          <div class="faq">
            <button type="button" :class="{ on: faq === '1' }" @click="faq = faq === '1' ? '' : '1'">
              <b>{{ t('mod.waybill.faq1.q') }}</b>
              <p v-if="faq === '1'">{{ t('mod.waybill.faq1.a') }}</p>
            </button>
          </div>
        </div>
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
  width: min(1120px, calc(100% - clamp(12px, 3vw, 40px)));
  background: #fff;
  border-radius: 20px;
  padding: 22px 24px 26px;
  box-shadow: 0 24px 64px rgba(16, 24, 40, 0.22);
  margin: 4vh auto 24px;
}
header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; }
.kicker { margin: 0 0 4px; color: var(--muted); font-size: 12px; font-weight: 650; letter-spacing: 0.04em; }
h2 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 22px; color: var(--navy-2); flex-wrap: wrap; }
header small { color: var(--muted); }
.acts { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
.stages {
  list-style: none; margin: 0 0 16px; padding: 18px 12px 8px;
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;
  background: #f7faf8; border: 1px solid #e3eee8; border-radius: 16px;
}
.stages li { position: relative; display: grid; justify-items: center; text-align: center; gap: 8px; }
.node {
  width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center; font-weight: 750; color: #fff; background: #c5d0de; z-index: 1;
}
.stages li.done .node, .stages li.now .node { background: #12805c; }
.line { position: absolute; top: 18px; left: calc(50% + 22px); width: calc(100% - 8px); height: 3px; background: #d5dde8; }
.line.done, .line.now { background: #12805c; }
.body { display: grid; gap: 4px; justify-items: center; }
.body b { font-size: 14px; color: var(--navy-2); }
.body em { font-size: 12px; color: var(--muted); font-style: normal; }
.tabs { display: flex; gap: 4px; overflow: auto; border-bottom: 1px solid var(--line); margin-bottom: 16px; }
.tabs button {
  border: 0; background: none; height: 40px; padding: 0 14px; color: var(--muted); font-weight: 650; white-space: nowrap;
  box-shadow: inset 0 -2px 0 transparent;
}
.tabs button.on { color: var(--navy); box-shadow: inset 0 -2px 0 var(--navy); }
.panel h3 { margin: 0 0 10px; font-size: 15px; color: var(--navy-2); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 32px; margin-bottom: 18px; }
.grid div { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-top: 1px solid var(--line-soft); }
.grid span { color: var(--muted); font-size: 13px; }
.grid b { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; }
.nodes { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.nodes button { width: 100%; display: flex; justify-content: space-between; border: 0; background: #f4f7fb; border-radius: 12px; padding: 12px 14px; }
.nodes button.now { background: var(--navy); color: #fff; }
.nodes p { margin: 8px 4px 0; color: var(--ink-soft); font-size: 14px; }
.port-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.port-row b { display: inline-flex; align-items: center; gap: 6px; }
.more { color: var(--signal-ink); font-weight: 700; }
.fix { display: grid; gap: 10px; margin-bottom: 16px; }
.fix div { display: flex; justify-content: space-between; gap: 12px; }
.fix span { color: var(--muted); }
.track {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 10px 12px;
  background: #0f2740; color: #fff; border-radius: 14px; padding: 18px;
}
.track span { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; }
.path { position: relative; height: 4px; background: rgba(255,255,255,.18); border-radius: 99px; }
.path em { display: block; height: 100%; background: #3dd68c; border-radius: 99px; }
.track small { grid-column: 2; justify-self: center; color: #c9d6e4; font-size: 12px; }
.note { margin: 12px 0 0; color: var(--muted); font-size: 13px; max-width: 72ch; }
.faq button { width: 100%; text-align: left; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; margin-top: 10px; }
.faq p { margin: 8px 0 0; color: var(--muted); }
@media (max-width: 800px) {
  .stages, .grid { grid-template-columns: 1fr; }
  .line { display: none; }
  header { display: grid; }
  .dialog { padding: 16px 16px 20px; }
  .track { grid-template-columns: 1fr; text-align: center; }
  .track small { grid-column: 1; }
}
</style>
