<script setup lang="ts">
import { ref } from 'vue'
import AbilityPage from '../components/AbilityPage.vue'
import { t } from '../i18n'

const open = ref('e2')
const copied = ref('')

const endpoints = [
  {
    id: 'e2',
    method: 'GET',
    path: '/api/v1/public/market',
    desc: 'api.e2',
    req: 'Authorization: Bearer <role-token>',
    res: `{
  "index": 1864,
  "loadsLive": 12847,
  "items": [
    { "id": "L-18420", "origin": "乌鲁木齐", "dest": "阿拉木图", "weightT": 18.4, "matchMode": "bid" }
  ]
}`,
  },
  {
    id: 'e3',
    method: 'GET',
    path: '/api/v1/loads',
    desc: 'api.e3',
    req: 'GET /api/v1/loads?origin=乌鲁木齐&dest=阿拉木图',
    res: `{ "items": [{ "id": "L-18420", "status": "matching", "quoteCount": 6 }] }`,
  },
  {
    id: 'e4',
    method: 'POST',
    path: '/api/v1/loads/{id}/quotes',
    desc: 'api.e4',
    req: `{ "price": 17800, "eta": "09-27 18:00", "note": "" }`,
    res: `{ "id": "Q-9012", "status": "open", "loadId": "L-18420" }`,
  },
  {
    id: 'e5',
    method: 'POST',
    path: '/api/v1/loads/{id}/grab',
    desc: 'api.e5',
    req: `{ "truckId": "T-9021" }`,
    res: `{ "locked": true, "confirmUntil": "30m", "orderId": "O-22041" }`,
  },
  {
    id: 'e6',
    method: 'POST',
    path: '/api/v1/orders/{id}/actions',
    desc: 'api.e6',
    req: `{ "action": "confirm_load" }`,
    res: `{ "id": "O-22018", "status": "in_transit" }`,
  },
  {
    id: 'e7',
    method: 'GET',
    path: '/api/v1/orders/{id}/track',
    desc: 'api.e7',
    req: 'GET /api/v1/orders/O-22018/track',
    res: `{ "shared": true, "lastPoint": "霍尔果斯", "lastAt": "09-26 21:14", "status": "in_transit" }`,
  },
  {
    id: 'e8',
    method: 'POST',
    path: '/api/v1/estimate',
    desc: 'api.e8',
    req: `{ "from": "乌鲁木齐", "to": "阿拉木图", "truckLength": "13.5", "cargoClass": "general" }`,
    res: `{ "km": 980, "feeLow": 15680, "feeHigh": 21560, "hours": 21, "refOnly": true }`,
  },
]

const current = () => endpoints.find((e) => e.id === open.value) || endpoints[0]

async function copyPath(path: string) {
  try {
    await navigator.clipboard.writeText(path)
    copied.value = path
  } catch {
    copied.value = ''
  }
}
</script>

<template>
  <AbilityPage :title="t('nav.connect')" :lead="t('mod.api.lead')">
    <ol class="steps">
      <li><b>1</b><span>{{ t('mod.api.flow1') }}</span></li>
      <li><b>2</b><span>{{ t('mod.api.flow2') }}</span></li>
      <li><b>3</b><span>{{ t('mod.api.flow3') }}</span></li>
      <li><b>4</b><span>{{ t('mod.api.flow4') }}</span></li>
    </ol>

    <div class="split">
      <div class="list">
        <button v-for="e in endpoints" :key="e.id" type="button" :class="{ on: open === e.id }" @click="open = e.id">
          <span class="pill" :class="e.method === 'GET' ? 'info' : 'ok'">{{ e.method }}</span>
          <code>{{ e.path }}</code>
          <small>{{ t(e.desc) }}</small>
        </button>
      </div>
      <article class="panel">
        <div class="top">
          <div>
            <span class="pill" :class="current().method === 'GET' ? 'info' : 'ok'">{{ current().method }}</span>
            <code>{{ current().path }}</code>
          </div>
          <button type="button" class="btn btn-line btn-sm" @click="copyPath(current().path)">
            {{ copied === current().path ? t('api.copied') : t('api.copy') }}
          </button>
        </div>
        <p>{{ t(current().desc) }}</p>
        <h3>{{ t('api.request') }}</h3>
        <pre>{{ current().req }}</pre>
        <h3>{{ t('api.response') }}</h3>
        <pre>{{ current().res }}</pre>
        <p class="auth">{{ t('api.auth') }}</p>
      </article>
    </div>
    <p class="note">{{ t('mod.api.note') }}</p>
    <div class="links">
      <router-link class="btn btn-navy btn-sm" to="/developers">{{ t('mod.api.open') }}</router-link>
      <router-link class="btn btn-line btn-sm" to="/board">{{ t('api.try') }}</router-link>
      <router-link class="btn btn-line btn-sm" to="/estimate">{{ t('nav.estimate') }}</router-link>
    </div>
  </AbilityPage>
</template>

<style scoped>
.steps {
  list-style: none; margin: 0 0 20px; padding: 0;
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
.steps li {
  display: grid; grid-template-columns: 32px 1fr; gap: 10px; align-items: start;
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
}
.steps b {
  width: 32px; height: 32px; border-radius: 50%; background: var(--navy); color: #fff;
  display: grid; place-items: center; font-size: 14px;
}
.split { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 14px; align-items: start; }
.list { display: grid; gap: 8px; }
.list button {
  display: grid; grid-template-columns: 64px 1fr; gap: 2px 10px; text-align: left;
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
}
.list button.on { border-color: var(--navy); box-shadow: 0 0 0 1px var(--navy); }
.list code { color: var(--navy-2); font-size: 13px; }
.list small { grid-column: 2; color: var(--muted); }
.panel { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 16px; position: sticky; top: 84px; }
.top { display: flex; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 8px; }
.top div { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.top code { font-size: 13px; color: var(--navy-2); }
.panel p { margin: 0 0 12px; color: var(--ink-soft); }
.panel h3 { margin: 10px 0 6px; font-size: 13px; color: var(--muted); }
pre {
  margin: 0; padding: 12px; background: #0f2740; color: #d7e6f5; border-radius: 10px;
  font-size: 12px; overflow: auto; line-height: 1.45;
}
.auth { margin-top: 12px; color: var(--muted); font-size: 12px; }
.note { margin: 16px 0 12px; color: var(--brass); font-size: 13px; max-width: 78ch; }
.links { display: flex; flex-wrap: wrap; gap: 8px; }
@media (max-width: 1100px) {
  .split { grid-template-columns: 1fr; }
  .panel { position: static; }
}
@media (max-width: 720px) {
  .steps { grid-template-columns: 1fr; }
}
</style>
