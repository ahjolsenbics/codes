<script setup lang="ts">
import { computed, ref } from 'vue'
import AbilityPage from '../components/AbilityPage.vue'
import Flag from '../components/Flag.vue'
import PayMark from '../components/PayMark.vue'
import { cargo, company, money, modeLabel, place } from '../fmt'
import { isAppAuthed } from '../auth'
import { t } from '../i18n'
import { useMarket } from '../useMarket'

const { market } = useMarket()
const authed = isAppAuthed
const mode = ref('bid')
const picked = ref('')
const tab = ref('rule')

const modes = [
  { key: 'bid', a: '24h', b: '48h' },
  { key: 'grab', aKey: 'match.flat', b: '30min' },
  { key: 'assign', a: '5', b: '24h' },
] as const

const samples = computed(() => (market.value.items || []).filter((x: any) => x.matchMode === mode.value).slice(0, 6))
</script>

<template>
  <AbilityPage :title="t('nav.match')" :lead="t('mod.match.lead')">
    <p class="mutex">{{ t('match.mutex') }}</p>
    <div class="modes">
      <button v-for="m in modes" :key="m.key" type="button" :class="{ on: mode === m.key }" @click="mode = m.key; picked = ''; tab = 'rule'">
        <span class="pill info">{{ t('mode.' + m.key) }}</span>
        <b>{{ t('site.rule.' + m.key + '.t') }}</b>
        <span>{{ t('site.rule.' + m.key + '.d') }}</span>
        <div class="clock">
          <em>{{ t('match.clock') }}</em>
          <strong>{{ 'aKey' in m ? t(m.aKey) : m.a }}</strong>
          <small>{{ m.b }}</small>
        </div>
      </button>
    </div>

    <article class="sheet">
      <div class="tabs">
        <button type="button" :class="{ on: tab === 'rule' }" @click="tab = 'rule'">{{ t('site.rule.' + mode + '.t') }}</button>
        <button type="button" :class="{ on: tab === 'deposit' }" @click="tab = 'deposit'">{{ t('mod.match.tabDeposit') }}</button>
        <button type="button" :class="{ on: tab === 'samples' }" @click="tab = 'samples'">{{ t('match.samples') }}</button>
      </div>
      <div v-if="tab === 'rule'" class="copy">
        <p>{{ t('site.rule.' + mode + '.x') }}</p>
      </div>
      <div v-else-if="tab === 'deposit'" class="copy">
        <p>{{ t('mod.match.deposit') }}</p>
        <p>{{ t('mod.match.credit') }}</p>
        <div class="pay">
          <span><PayMark name="wechat" />{{ t('pay.wechat') }}</span>
          <span><PayMark name="alipay" />{{ t('pay.alipay') }}</span>
          <span><PayMark name="unionpay" />{{ t('pay.unionpay') }}</span>
          <span><PayMark name="kaspi" />{{ t('pay.kaspi') }}</span>
        </div>
      </div>
      <div v-else class="loads">
        <router-link v-for="item in samples" :key="item.id" :to="'/board/' + item.id" :class="{ on: picked === item.id }" @click="picked = item.id">
          <div class="lane">
            <Flag :code="item.originCountry" />
            <b>{{ place(item.origin) }} → {{ place(item.dest) }}</b>
            <Flag :code="item.destCountry" />
          </div>
          <span>{{ cargo(item.cargoName) }} · {{ item.weightT }} t · {{ item.truckLength }} m</span>
          <strong v-if="authed()">{{ money(item.expectPrice || item.grabPrice) }}</strong>
          <strong v-else>{{ t('auth.loginForDetail') }}</strong>
          <small>{{ item.id }} · {{ authed() ? company(item.company) : t('auth.needLogin') }} · {{ modeLabel(item.matchMode) }}</small>
        </router-link>
        <p v-if="!samples.length" class="empty">{{ t('tool.empty') }}</p>
        <router-link class="more" to="/board">{{ t('match.openLoad') }}</router-link>
      </div>
    </article>
  </AbilityPage>
</template>

<style scoped>
.mutex { margin: -8px 0 16px; color: var(--brass); font-size: 13px; }
.modes { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 18px; }
.modes button {
  text-align: left; background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 16px;
  display: grid; gap: 8px; justify-items: start;
}
.modes button.on { border-color: var(--navy); box-shadow: 0 0 0 1px var(--navy); }
.modes b { font-size: 18px; color: var(--navy-2); }
.modes span { color: var(--muted); font-size: 13px; }
.clock {
  display: flex; align-items: baseline; gap: 8px; width: 100%;
  margin-top: 6px; padding-top: 10px; border-top: 1px solid var(--line-soft);
}
.clock em { font-style: normal; color: var(--muted); font-size: 12px; margin-right: auto; }
.clock strong { font-size: 20px; color: var(--navy); }
.clock small { color: var(--muted); }
.sheet { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 8px 20px 20px; }
.tabs { display: flex; gap: 4px; overflow-x: auto; border-bottom: 1px solid var(--line); margin: 0 -8px 16px; }
.tabs button {
  border: 0; background: none; height: 42px; padding: 0 14px; color: var(--muted); font-weight: 650;
  box-shadow: inset 0 -2px 0 transparent;
}
.tabs button.on { color: var(--navy); box-shadow: inset 0 -2px 0 var(--navy); }
.copy p { margin: 0 0 12px; color: var(--ink-soft); max-width: 78ch; line-height: 1.6; }
.pay { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
.pay span { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; background: #f7f9fc; font-size: 13px; }
.loads { display: grid; gap: 8px; }
.loads a {
  display: grid; grid-template-columns: 1fr auto; gap: 4px 16px;
  border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
}
.loads a.on, .loads a:hover { border-color: var(--navy); }
.lane { display: flex; align-items: center; gap: 8px; grid-column: 1 / -1; }
.loads span, .loads small { color: var(--muted); font-size: 13px; }
.loads small { grid-column: 1 / -1; }
.empty { color: var(--muted); }
.more { margin-top: 6px; color: var(--signal-ink); font-weight: 700; }
@media (max-width: 720px) { .modes { grid-template-columns: 1fr; } }
</style>
