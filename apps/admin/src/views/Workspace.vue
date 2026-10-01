<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { demoConsole, demoMutate } from '../demoOps'
import { cargo, company, countryName, customs, entity, kycLabel, laneText, ledgerLabel, loadStatus, money, modeLabel, orderStatus, party, phrase, place, portLabel, portName, tone, waitMin } from '../fmt'
import { t } from '../i18n'
import Flag from '../components/Flag.vue'
import KycPreview from '../components/KycPreview.vue'
import Pager from '../components/Pager.vue'
import PayMark from '../components/PayMark.vue'
import { usePager } from '../usePager'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const payload = ref<any>(null)
const demo = ref(false)

const loaders: Record<string, () => Promise<any>> = {
  '/console': () => api.dashboard(),
  '/console/users': () => api.users(),
  '/console/kyc': () => api.kyc(),
  '/console/loads': () => api.loads(),
  '/console/orders': () => api.orders(),
  '/console/deposits': () => api.deposits(),
  '/console/disputes': () => api.disputes(),
  '/console/blacklist': () => api.blacklist(),
  '/console/ports': () => api.ports(),
  '/console/config': () => api.config(),
  '/console/i18n': () => api.i18n(),
  '/console/announcements': () => api.announcements(),
  '/console/audit': () => api.audit(),
}

const titles: Record<string, string> = {
  '/console': 'console.overview',
  '/console/users': 'nav.users',
  '/console/kyc': 'nav.kyc',
  '/console/loads': 'nav.loads',
  '/console/orders': 'nav.orders',
  '/console/deposits': 'nav.deposits',
  '/console/disputes': 'nav.disputes',
  '/console/blacklist': 'nav.blacklist',
  '/console/ports': 'nav.ports',
  '/console/config': 'nav.config',
  '/console/i18n': 'nav.i18n',
  '/console/announcements': 'nav.ann',
  '/console/audit': 'nav.audit',
}

const rejectReason = ref<Record<string, string>>({})
const openId = ref('')
const query = ref('')
const statusFilter = ref('')
const flow = ref('matching')
const flows = ['published', 'matching', 'dealt', 'wait_load', 'loading', 'in_transit', 'wait_confirm', 'completed', 'dispute']
const portStatus = ref('smooth')
const portWait = ref(20)
const portGrades = ['smooth', 'slow', 'congested', 'heavy', 'closed']

async function reload() {
  const keep = String(route.query.id || openId.value || '')
  loading.value = true
  error.value = ''
  try {
    payload.value = await loaders[route.path]()
    demo.value = false
  } catch (e) {
    payload.value = demoConsole(route.path)
    demo.value = true
    error.value = ''
    console.error('运营接口不可用，使用演示台账', e)
  } finally {
    loading.value = false
    if (keep) openId.value = keep
  }
}

onMounted(reload)
watch(() => route.path, () => {
  query.value = ''
  statusFilter.value = String(route.query.status || '')
  openId.value = String(route.query.id || '')
  reload()
})
watch(() => route.query.id, (id) => {
  if (id) openId.value = String(id)
})

const title = computed(() => t(titles[route.path] ?? 'dash.title'))
const pageLead = computed(() => t('ops.page.' + (route.path === '/console' ? 'console' : route.path.replace('/console/', ''))))
const orderRail = ['dealt', 'wait_load', 'loading', 'in_transit', 'wait_confirm', 'completed']
const queues = [
  { to: '/console/kyc', title: 'nav.kyc', field: 'kycPending', hint: 'ops.queue.kyc' },
  { to: '/console/loads', title: 'nav.loads', field: 'loadsPending', hint: 'ops.queue.loads' },
  { to: '/console/disputes', title: 'nav.disputes', field: 'disputesOpen', hint: 'ops.queue.disputes' },
  { to: '/console/ports', title: 'nav.ports', field: '', hint: 'ops.queue.ports' },
]

function cfgText(prefix: string, key: unknown) {
  const id = `${prefix}${key}`
  const value = t(id)
  return value === id ? String(key ?? '') : value
}

function matchQuery(row: Record<string, unknown>, keys: string[]) {
  const s = query.value.trim().toLowerCase()
  if (!s) return true
  return keys.some((k) => String(row[k] ?? '').toLowerCase().includes(s))
}

function asList(v: unknown): any[] {
  return Array.isArray(v) ? v : []
}

const KYC_FALLBACK: Record<string, string> = {
  biz: '/kyc/biz.svg',
  auth: '/kyc/auth.svg',
  agent: '/kyc/agent.svg',
  business_license: '/kyc/biz.svg',
  operator_id: '/kyc/agent.svg',
  id_card: '/kyc/id.svg',
  id_card_front: '/kyc/id.svg',
  id_card_hold: '/kyc/id.svg',
  license: '/kyc/license.svg',
  drive: '/kyc/license.svg',
  vehicle: '/kyc/vehicle.svg',
  green_card: '/kyc/green.svg',
  green: '/kyc/green.svg',
  road_permit: '/kyc/permit.svg',
  tir: '/kyc/green.svg',
  truck_photo: '/kyc/vehicle.svg',
  truck_front: '/kyc/vehicle.svg',
  truck_side: '/kyc/vehicle.svg',
  truck_box: '/kyc/vehicle.svg',
}

function canonKind(kind: string) {
  if (kind === 'drive') return 'license'
  if (kind === 'green') return 'green_card'
  if (kind === 'business_license') return 'biz'
  if (kind === 'operator_id') return 'agent'
  if (kind === 'truck_photo') return 'truck_front'
  return kind
}

function kycDocs(user: any) {
  const required = user?.role === 'driver'
    ? ['id_card', 'id_card_hold', 'license', 'vehicle', 'road_permit', 'tir', 'green_card', 'truck_front', 'truck_side', 'truck_box']
    : user?.kind === 'personal'
      ? ['id_card_front']
      : ['biz', 'agent']
  const have = new Map<string, any>()
  for (const c of user?.credentials || []) {
    const kind = canonKind(String(c.kind || ''))
    have.set(kind, { ...c, kind })
  }
  const kinds = [...new Set([...required, ...have.keys()])]
  return kinds.map((kind) => {
    const row = have.get(kind) || { id: `miss-${user.id}-${kind}`, kind, status: user?.kycStatus || 'pending', fileUrl: '' }
    return { ...row, kind, fileUrl: row.fileUrl || KYC_FALLBACK[kind] || '/kyc/id.svg' }
  })
}

const userRows = computed(() => asList(payload.value?.items).filter((u: any) => matchQuery(u, ['name', 'phone', 'id', 'role', 'company'])))
const kycRows = computed(() => asList(payload.value?.users).filter((u: any) => matchQuery(u, ['name', 'phone', 'id', 'role', 'company'])).slice().sort((a: any, b: any) => Number(b.kycStatus === 'pending') - Number(a.kycStatus === 'pending')))
const loadRows = computed(() => asList(payload.value?.items).filter((x: any) => {
  const statusOk = !statusFilter.value || x.status === statusFilter.value
  return statusOk && matchQuery(x, ['id', 'origin', 'dest', 'cargoName', 'company'])
}))
const orderRows = computed(() => asList(payload.value?.items).filter((x: any) => {
  const statusOk = !statusFilter.value || x.status === statusFilter.value
  return statusOk && matchQuery(x, ['id', 'lane', 'shipperName', 'driverName', 'origin', 'dest'])
}))
const disputeRows = computed(() => asList(payload.value?.items).filter((d: any) => matchQuery(d, ['id', 'reason', 'orderId'])))
const portRows = computed(() => asList(payload.value?.ports).filter((p: any) => {
  const statusOk = !statusFilter.value || p.status === statusFilter.value
  return statusOk && matchQuery(p, ['id', 'nameZh', 'nameEn', 'corridor'])
}))
const accountRows = computed(() => asList(payload.value?.accounts).filter((a: any) => matchQuery(a, ['name', 'userId'])))
const blackRows = computed(() => asList(payload.value?.items).filter((b: any) => matchQuery(b, ['name', 'reason'])))
const annRows = computed(() => asList(payload.value?.items).filter((a: any) => matchQuery(a, ['title', 'locale', 'body'])))
const auditRows = computed(() => asList(payload.value?.items).filter((x: any) => matchQuery(x, ['action', 'target', 'id'])))
const i18nRows = computed(() => asList(payload.value?.items).filter((x: any) => matchQuery(x, ['key', 'zh', 'en', 'ru'])))
const cfgRows = computed(() => {
  const items = payload.value?.items
  if (!items || Array.isArray(items)) return []
  return Object.entries(items).map(([k, v]) => ({ id: String(k), key: k, value: v }))
})

const usersPager = usePager(userRows, 8)
const kycPager = usePager(kycRows, 6)
const loadsPager = usePager(loadRows, 8)
const ordersPager = usePager(orderRows, 8)
const disputesPager = usePager(disputeRows, 8)
const portsPager = usePager(portRows, 8)
const accountsPager = usePager(accountRows, 8)
const blackPager = usePager(blackRows, 8)
const annPager = usePager(annRows, 8)
const auditPager = usePager(auditRows, 10)
const i18nPager = usePager(i18nRows, 10)
const cfgPager = usePager(cfgRows, 10)

watch([query, statusFilter], () => {
  usersPager.reset()
  kycPager.reset()
  loadsPager.reset()
  ordersPager.reset()
  disputesPager.reset()
  portsPager.reset()
  accountsPager.reset()
  blackPager.reset()
  annPager.reset()
  auditPager.reset()
  i18nPager.reset()
})

const focusUser = computed(() => userRows.value.find((u: any) => u.id === openId.value) || usersPager.items[0] || null)
const focusKyc = computed(() => kycRows.value.find((u: any) => u.id === openId.value) || kycPager.items[0] || null)
const focusLoad = computed(() => loadRows.value.find((x: any) => x.id === openId.value) || loadsPager.items[0] || null)
const focusOrder = computed(() => orderRows.value.find((x: any) => x.id === openId.value) || ordersPager.items[0] || null)
const focusDispute = computed(() => disputeRows.value.find((d: any) => d.id === openId.value) || disputesPager.items[0] || null)
const focusPort = computed(() => portRows.value.find((p: any) => p.id === openId.value) || portsPager.items[0] || null)
const focusAccount = computed(() => accountRows.value.find((a: any) => a.userId === openId.value) || accountsPager.items[0] || null)
const focusBlack = computed(() => blackRows.value.find((b: any) => b.userId === openId.value) || blackPager.items[0] || null)
const focusAnn = computed(() => annRows.value.find((a: any) => a.id === openId.value) || annPager.items[0] || null)

const accountLedgers = computed(() => {
  const id = focusAccount.value?.userId
  const all = payload.value?.ledgers || []
  if (!id) return all
  return all.filter((l: any) => l.userId === id || l.name === focusAccount.value?.name)
})
const portReports = computed(() => (payload.value?.reports || []).filter((r: any) => !focusPort.value || r.portId === focusPort.value.id))

watch(focusPort, (p) => {
  if (!p) return
  portStatus.value = p.status
  portWait.value = Number(p.waitMin) || 0
}, { immediate: true })

function pick(id: string) {
  openId.value = id
}

function openQueue(path: string, id?: string) {
  router.push(id ? { path, query: { id } } : path)
}

const countryMax = computed(() => Math.max(1, ...(payload.value?.usersByCountry || []).map((x: any) => Number(x.count) || 0)))
const statusMax = computed(() => Math.max(1, ...(payload.value?.ordersByStatus || []).map((x: any) => Number(x.count) || 0)))
const seriesMax = computed(() => Math.max(1, ...(payload.value?.series || []).map((x: any) => Number(x.orders) || 0)))
const evidenceNote = ref('')
const annAudience = ref('all')
const cfgDraft = ref<Record<string, string>>({})

watch(() => payload.value?.items, (items) => {
  if (route.path === '/console/config' && items && typeof items === 'object' && !Array.isArray(items)) {
    cfgDraft.value = { ...items }
  }
})

function exportCsv() {
  const rows = payload.value?.series || []
  const csv = ['day,orders', ...rows.map((x: any) => `${x.day},${x.orders}`)].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'yunmm-dashboard.csv'
  a.click()
}

async function saveCfg() {
  await api.saveConfig(cfgDraft.value)
  await reload()
}

async function act(kind: string, id: string, extra?: unknown) {
  if (!demo.value) {
    try {
      if (kind === 'user') await api.patchUser(id, Boolean(extra))
      else if (kind === 'kyc') await api.reviewKyc(id, Boolean(extra), String(rejectReason.value[id] || ''))
      else if (kind === 'load') await api.reviewLoad(id, Boolean(extra))
      else if (kind === 'dispute') await api.ruleDispute(id, String(extra || ''), 'ruled')
      else if (kind === 'port') {
        const spec = extra && typeof extra === 'object' ? extra as { status?: string; waitMin?: number } : { status: 'smooth', waitMin: 20 }
        await api.setPort(id, spec.status || 'smooth', Number(spec.waitMin ?? 20))
      }
      else if (kind === 'report') await api.approveReport(Number(id), true)
      else if (kind === 'ann') await api.createAnn('Notice', 'Demo announcement', String(extra || annAudience.value || 'all'))
      else if (kind === 'kaspi') await api.kaspiConfirm(Number(id))
      else if (kind === 'refund') await api.refund(Number(id))
      else if (kind === 'evidence') await api.disputeEvidence(id, String(extra || evidenceNote.value))
      else if (kind === 'review') await api.disputeReview(id)
      await reload()
      return
    } catch (e) {
      demo.value = true
      console.error('运营操作改走演示台账', e)
    }
  }
  demoMutate(kind, id, extra)
  payload.value = demoConsole(route.path)
}

async function rejectUser(id: string) {
  const reason = (rejectReason.value[id] || '').trim()
  if (!reason) {
    error.value = t('ops.needRejectReason')
    return
  }
  await act('kyc', id, false)
}

function pct(n: unknown) {
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  return `${Math.round(v * 1000) / 10}%`
}

function savePort() {
  if (!focusPort.value) return
  act('port', focusPort.value.id, { status: portStatus.value, waitMin: portWait.value })
}

const deskPaths = [
  '/console/users',
  '/console/kyc',
  '/console/loads',
  '/console/orders',
  '/console/deposits',
  '/console/disputes',
  '/console/blacklist',
  '/console/ports',
  '/console/announcements',
]
</script>

<template>
  <div>
    <div class="head">
      <div>
        <h1>{{ title }}</h1>
        <p class="sub">{{ pageLead }}</p>
      </div>
      <p v-if="loading">{{ t('common.loading') }}</p>
      <button v-if="route.path === '/console'" class="btn btn-line" type="button" @click="exportCsv">{{ t('ops.export') }}</button>
    </div>
    <p v-if="error" class="err">{{ error }}</p>

    <template v-if="route.path === '/console' && payload">
      <div class="kpis">
        <router-link v-for="x in [
          ['/console/kyc', 'kpi.kycPending', payload.kycPending, 'kpi.kycPendingHint'],
          ['/console/loads', 'kpi.loadsPending', payload.loadsPending, 'kpi.loadsPendingHint'],
          ['/console/orders', 'kpi.orders', payload.orders, 'kpi.ordersHint'],
          ['/console/disputes', 'kpi.disputesOpen', payload.disputesOpen, 'kpi.disputesOpenHint'],
          ['/console/deposits', 'kpi.depositIn', money(payload.depositIn), 'kpi.depositInHint'],
        ]" :key="x[1]" :to="String(x[0])">
          <small>{{ t(String(x[1])) }}</small>
          <strong>{{ x[2] }}</strong>
          <em>{{ t(String(x[3])) }}</em>
        </router-link>
      </div>
      <div class="rates">
        <span>{{ t('kpi.kycPass') }} <b>{{ pct(payload.kycPassRate) }}</b></span>
        <span>{{ t('kpi.dealRate') }} <b>{{ pct(payload.dealRate) }}</b></span>
        <span>{{ t('kpi.disputeRate') }} <b>{{ pct(payload.disputeRate) }}</b></span>
      </div>
      <div class="ops-split">
        <section>
          <h3>{{ t('ops.kycQueue') }}</h3>
          <button v-for="u in payload.kycQueue || []" :key="u.id" type="button" class="queue-row" @click="openQueue('/console/kyc', u.id)">
            <div>
              <b>{{ party(u.name) }}</b>
              <span>{{ t('role.' + u.role) }}</span>
            </div>
            <em class="pill" :class="tone(u.kycStatus)">{{ kycLabel(u.kycStatus) }}</em>
          </button>
          <router-link class="go" to="/console/kyc">{{ t('ops.goHandle') }}</router-link>
        </section>
        <section>
          <h3>{{ t('ops.loadQueue') }}</h3>
          <button v-for="x in payload.loadQueue || []" :key="x.id" type="button" class="queue-row" @click="openQueue('/console/loads', x.id)">
            <div>
              <b>{{ place(x.origin) }} → {{ place(x.dest) }}</b>
              <span>{{ cargo(x.cargoName) }} · {{ x.weightT }}t · {{ x.id }}</span>
            </div>
            <em class="pill" :class="tone(x.status)">{{ loadStatus(x.status) }}</em>
          </button>
          <router-link class="go" to="/console/loads">{{ t('ops.goHandle') }}</router-link>
        </section>
      </div>
      <section class="machine live-box">
        <h3>{{ t('ops.liveOrders') }}</h3>
        <button v-for="o in payload.liveOrders || []" :key="o.id" type="button" class="queue-row" @click="openQueue('/console/orders', o.id)">
          <div>
            <b>{{ o.id }} · {{ laneText(o.lane) }}</b>
            <span>{{ entity(o.shipperName) }} / {{ party(o.driverName) }}</span>
          </div>
          <div class="live-meta">
            <span class="pill" :class="tone(o.status)">{{ orderStatus(o.status) }}</span>
            <strong>{{ money(o.freight) }}</strong>
          </div>
        </button>
        <router-link class="go" to="/console/orders">{{ t('ops.goHandle') }}</router-link>
      </section>
      <div class="work">
        <article v-for="q in queues" :key="q.to">
          <button type="button" @click="openQueue(q.to)">
            <span>{{ t(q.title) }}</span>
            <strong v-if="q.field">{{ payload[q.field] }}</strong>
          </button>
          <div class="work-body">
            <p>{{ t(q.hint) }}</p>
            <router-link :to="q.to">{{ t('ops.goHandle') }}</router-link>
          </div>
        </article>
      </div>
      <section class="machine">
        <h3>{{ t('ops.series') }}</h3>
        <div class="series">
          <div v-for="x in payload.series || []" :key="x.day" class="col">
            <i><b :style="{ height: Math.round((Number(x.orders) / seriesMax) * 100) + '%' }" /></i>
            <span>{{ x.day }}</span>
            <em>{{ x.orders }}</em>
          </div>
        </div>
      </section>
      <div class="split">
        <section>
          <h3>{{ t('ops.byCountry') }}</h3>
          <div v-for="x in payload.usersByCountry" :key="x.country" class="bar">
            <span class="cname"><Flag :code="x.country" />{{ countryName(x.country) }}</span>
            <i><b :style="{ width: Math.round((Number(x.count) / countryMax) * 100) + '%' }" /></i>
            <em>{{ x.count }}</em>
          </div>
        </section>
        <section>
          <h3>{{ t('ops.pipeline') }}</h3>
          <button v-for="x in payload.ordersByStatus" :key="x.status" type="button" class="bar" @click="openQueue('/console/orders')">
            <span class="pill" :class="tone(x.status)">{{ orderStatus(x.status) }}</span>
            <i><b :style="{ width: Math.round((Number(x.count) / statusMax) * 100) + '%' }" /></i>
            <em>{{ x.count }}</em>
          </button>
        </section>
      </div>
      <section class="machine">
        <h3>{{ t('ops.machine') }}</h3>
        <div class="flows">
          <button v-for="s in flows" :key="s" type="button" :class="{ on: flow === s }" @click="flow = s">{{ orderStatus(s) }}</button>
        </div>
        <p>{{ t('ops.flow.' + flow) }}</p>
      </section>
    </template>

    <div v-if="deskPaths.includes(route.path)" class="toolbar">
      <input v-model="query" class="field" :placeholder="t('ops.searchPh')" />
      <select v-if="route.path === '/console/loads'" v-model="statusFilter" class="field slim">
        <option value="">{{ t('ops.filter') }}</option>
        <option v-for="s in ['pending_review', 'published', 'matching']" :key="s" :value="s">{{ loadStatus(s) }}</option>
      </select>
      <select v-else-if="route.path === '/console/orders'" v-model="statusFilter" class="field slim">
        <option value="">{{ t('ops.filter') }}</option>
        <option v-for="s in orderRail" :key="s" :value="s">{{ orderStatus(s) }}</option>
      </select>
      <select v-else-if="route.path === '/console/ports'" v-model="statusFilter" class="field slim">
        <option value="">{{ t('ops.filter') }}</option>
        <option v-for="s in portGrades" :key="s" :value="s">{{ portLabel(s) }}</option>
      </select>
    </div>

    <div v-if="route.path === '/console/users' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="u in usersPager.items" :key="u.id" type="button" class="hit" :class="{ on: focusUser && focusUser.id === u.id }" @click="pick(u.id)">
          <div>
            <b>{{ party(u.name) }}</b>
            <span>{{ t('role.' + u.role) }} · {{ u.phone }}</span>
          </div>
          <em class="pill" :class="tone(u.kycStatus)">{{ kycLabel(u.kycStatus) }}</em>
        </button>
        <p v-if="!userRows.length" class="empty">{{ t('ops.noDetail') }}</p>
        <Pager v-model:page="usersPager.page" :pages="usersPager.pages" :total="usersPager.total" :size="usersPager.size" />
      </aside>
      <article v-if="focusUser" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusUser.id }}</p>
              <h2>{{ party(focusUser.name) }}</h2>
            </div>
            <span class="pill" :class="tone(focusUser.kycStatus)">{{ kycLabel(focusUser.kycStatus) }}</span>
          </div>
          <p class="note">{{ t('ops.userHint') }}</p>
          <div class="kv">
            <div><span>{{ t('col.role') }}</span><b>{{ t('role.' + focusUser.role) }}</b></div>
            <div><span>{{ t('col.phone') }}</span><b>{{ focusUser.phone }}</b></div>
            <div><span>{{ t('col.credit') }}</span><b>{{ focusUser.credit }}</b></div>
            <div><span>{{ t('ops.company') }}</span><b>{{ focusUser.company ? company(focusUser.company) : party(focusUser.name) }}</b></div>
            <div><span>{{ t('col.kyc') }}</span><b>{{ kycLabel(focusUser.kycStatus) }}</b></div>
            <div v-if="focusUser.country"><span>{{ t('ops.country') }}</span><b class="cname"><Flag :code="focusUser.country" />{{ countryName(focusUser.country) }}</b></div>
          </div>
        </div>
        <div class="desk-acts">
          <button class="btn btn-line" @click="act('user', focusUser.id, !focusUser.disabled)">
            {{ focusUser.disabled ? t('act.enable') : t('act.disable') }}
          </button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/kyc' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="u in kycPager.items" :key="u.id" type="button" class="hit" :class="{ on: focusKyc && focusKyc.id === u.id }" @click="pick(u.id)">
          <div>
            <b>{{ party(u.name) }}</b>
            <span>{{ t('role.' + u.role) }} · {{ u.phone }}</span>
            <span v-if="u.company">{{ company(u.company) }}</span>
          </div>
          <em class="pill" :class="tone(u.kycStatus)">{{ kycLabel(u.kycStatus) }}</em>
        </button>
        <Pager v-model:page="kycPager.page" :pages="kycPager.pages" :total="kycPager.total" :size="kycPager.size" />
      </aside>
      <article v-if="focusKyc" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ t('role.' + focusKyc.role) }} · {{ focusKyc.phone }}</p>
              <h2>{{ party(focusKyc.name) }}</h2>
            </div>
            <span class="pill" :class="tone(focusKyc.kycStatus)">{{ kycLabel(focusKyc.kycStatus) }}</span>
          </div>
          <p v-if="focusKyc.company" class="note">{{ t('ops.kycCompany') }} {{ company(focusKyc.company) }}{{ focusKyc.kind ? ' · ' + t('kind.' + focusKyc.kind) : '' }}</p>
          <p v-if="focusKyc.greenCardNo" class="note">{{ t('ops.greenCard') }} {{ focusKyc.greenCardNo }} / {{ focusKyc.greenCardExpires }} / {{ customs(focusKyc.customs) }}</p>
          <div class="docs">
            <KycPreview v-for="c in kycDocs(focusKyc)" :key="c.id" :kind="c.kind" :status="c.status" :src="c.fileUrl" />
          </div>
          <h3>{{ t('ops.kycCheck') }}</h3>
          <ul class="checks">
            <li>{{ t('ops.kycCheck1') }}</li>
            <li>{{ t('ops.kycCheck2') }}</li>
            <li>{{ t('ops.kycCheck3') }}</li>
          </ul>
        </div>
        <div class="desk-acts">
          <input v-model="rejectReason[focusKyc.id]" :placeholder="t('ops.rejectReason')" />
          <button class="btn btn-green" @click="act('kyc', focusKyc.id, true)">{{ t('act.pass') }}</button>
          <button class="btn btn-line" @click="rejectUser(focusKyc.id)">{{ t('act.reject') }}</button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/loads' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="x in loadsPager.items" :key="x.id" type="button" class="hit" :class="{ on: focusLoad && focusLoad.id === x.id }" @click="pick(x.id)">
          <div>
            <b>{{ place(x.origin) }} → {{ place(x.dest) }}</b>
            <span>{{ cargo(x.cargoName) }} · {{ x.weightT }}t · {{ x.id }}</span>
          </div>
          <em class="pill" :class="tone(x.status)">{{ loadStatus(x.status) }}</em>
        </button>
        <Pager v-model:page="loadsPager.page" :pages="loadsPager.pages" :total="loadsPager.total" :size="loadsPager.size" />
      </aside>
      <article v-if="focusLoad" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusLoad.id }}</p>
              <h2 class="lane"><Flag :code="focusLoad.originCountry" />{{ place(focusLoad.origin) }} → <Flag :code="focusLoad.destCountry" />{{ place(focusLoad.dest) }}</h2>
            </div>
            <span class="pill" :class="tone(focusLoad.status)">{{ loadStatus(focusLoad.status) }}</span>
          </div>
          <p class="note">{{ t('ops.loadHint') }}</p>
          <div class="kv">
            <div><span>{{ t('col.cargo') }}</span><b>{{ cargo(focusLoad.cargoName) }}</b></div>
            <div><span>{{ t('ops.weight') }}</span><b>{{ focusLoad.weightT }} t</b></div>
            <div><span>{{ t('col.match') }}</span><b>{{ modeLabel(focusLoad.matchMode) }}</b></div>
            <div><span>{{ t('ops.price') }}</span><b>{{ money(focusLoad.expectPrice || focusLoad.grabPrice) }}</b></div>
            <div><span>{{ t('ops.company') }}</span><b>{{ company(focusLoad.company) || '—' }}</b></div>
            <div><span>{{ t('col.status') }}</span><b>{{ loadStatus(focusLoad.status) }}</b></div>
          </div>
        </div>
        <div class="desk-acts">
          <button class="btn btn-green" @click="act('load', focusLoad.id, true)">{{ t('act.pass') }}</button>
          <button class="btn btn-line" @click="act('load', focusLoad.id, false)">{{ t('act.reject') }}</button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/orders' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="x in ordersPager.items" :key="x.id" type="button" class="hit" :class="{ on: focusOrder && focusOrder.id === x.id }" @click="pick(x.id)">
          <div>
            <b>{{ x.id }}</b>
            <span>{{ laneText(x.lane) || (place(x.origin) + ' → ' + place(x.dest)) }}</span>
          </div>
          <em class="pill" :class="tone(x.status)">{{ orderStatus(x.status) }}</em>
        </button>
        <Pager v-model:page="ordersPager.page" :pages="ordersPager.pages" :total="ordersPager.total" :size="ordersPager.size" />
      </aside>
      <article v-if="focusOrder" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusOrder.id }} · {{ modeLabel(focusOrder.matchMode) }}</p>
              <h2>{{ laneText(focusOrder.lane) || (place(focusOrder.origin) + ' → ' + place(focusOrder.dest)) }}</h2>
            </div>
            <span class="pill" :class="tone(focusOrder.status)">{{ orderStatus(focusOrder.status) }}</span>
          </div>
          <p class="note">{{ t('ops.orderHint') }}</p>
          <div class="kv">
            <div><span>{{ t('ops.company') }}</span><b>{{ entity(focusOrder.shipperName) }}</b></div>
            <div><span>{{ t('ops.carrier') }}</span><b>{{ party(focusOrder.driverName) }}</b></div>
            <div><span>{{ t('col.freight') }}</span><b>{{ money(focusOrder.freight) }}</b></div>
            <div v-if="focusOrder.weightT"><span>{{ t('ops.weight') }}</span><b>{{ focusOrder.weightT }} t</b></div>
          </div>
          <ol class="rail">
            <li v-for="s in orderRail" :key="s" :class="{ on: s === focusOrder.status, done: orderRail.indexOf(s) < orderRail.indexOf(focusOrder.status) }">{{ orderStatus(s) }}</li>
          </ol>
          <p class="note">{{ t('ops.nextStep') }} · {{ t('ops.flow.' + focusOrder.status) }}</p>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/deposits' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="a in accountsPager.items" :key="a.userId" type="button" class="hit" :class="{ on: focusAccount && focusAccount.userId === a.userId }" @click="pick(a.userId)">
          <div>
            <b>{{ party(a.name) }}</b>
            <span>{{ t('app.available') }} {{ a.available }} · {{ t('app.frozen') }} {{ a.frozen }}</span>
          </div>
        </button>
        <Pager v-model:page="accountsPager.page" :pages="accountsPager.pages" :total="accountsPager.total" :size="accountsPager.size" />
      </aside>
      <article v-if="focusAccount" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusAccount.userId }}</p>
              <h2>{{ party(focusAccount.name) }}</h2>
            </div>
          </div>
          <p class="note">{{ t('ops.depositHint') }}</p>
          <div class="kv">
            <div><span>{{ t('app.available') }}</span><b>{{ focusAccount.available }}</b></div>
            <div><span>{{ t('app.frozen') }}</span><b>{{ focusAccount.frozen }}</b></div>
          </div>
          <h3>{{ t('ops.ledgerTitle') }}</h3>
          <table class="mini">
            <tr v-for="l in accountLedgers" :key="l.id">
              <td>{{ ledgerLabel(l.kind) }}</td>
              <td>{{ l.amount }}</td>
              <td class="ch"><PayMark :name="l.channel || 'wechat'" /><span>{{ t('pay.' + (l.channel || 'wechat')) }}</span></td>
              <td>{{ l.status || 'ok' }}</td>
              <td>{{ l.orderId || '—' }}</td>
            </tr>
          </table>
          <div v-if="(payload.pending || []).length" class="kaspi">
            <h3>{{ t('ops.kaspi') }}</h3>
            <article v-for="p in payload.pending" :key="p.id" class="report">
              <div>
                <b>{{ party(p.name) }} · {{ p.amount }}</b>
                <span>{{ t('pay.' + (p.channel || 'kaspi')) }}</span>
              </div>
              <div class="acts">
                <button class="btn btn-green" @click="act('kaspi', String(p.id))">{{ t('ops.confirmPay') }}</button>
                <button class="btn btn-line" @click="act('refund', String(p.id))">{{ t('ops.refund') }}</button>
              </div>
            </article>
          </div>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/disputes' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="d in disputesPager.items" :key="d.id" type="button" class="hit" :class="{ on: focusDispute && focusDispute.id === d.id }" @click="pick(d.id)">
          <div>
            <b>{{ phrase(d.reason) }}</b>
            <span>{{ d.orderId }}</span>
          </div>
          <em class="pill" :class="tone(d.status)">{{ orderStatus(d.status) }}</em>
        </button>
        <Pager v-model:page="disputesPager.page" :pages="disputesPager.pages" :total="disputesPager.total" :size="disputesPager.size" />
      </aside>
      <article v-if="focusDispute" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusDispute.orderId }}</p>
              <h2>{{ phrase(focusDispute.reason) }}</h2>
            </div>
            <span class="pill" :class="tone(focusDispute.status)">{{ orderStatus(focusDispute.status) }}</span>
          </div>
          <p class="note">{{ t('ops.flow.dispute') }}</p>
          <ol class="checks">
            <li>{{ t('st.dispute') }}</li>
            <li>{{ t('act.rule') }}</li>
            <li>{{ t('st.completed') }}</li>
          </ol>
          <div v-if="(focusDispute.evidence || []).length" class="evidence">
            <h3>{{ t('ops.evidence') }}</h3>
            <article v-for="(e, i) in focusDispute.evidence" :key="i" class="report">
              <img v-if="e.url" :src="e.url" alt="" />
              <div>
                <b>{{ phrase(e.note) || e.url }}</b>
                <span>{{ party(e.by) }}</span>
              </div>
            </article>
          </div>
          <input v-model="evidenceNote" :placeholder="t('ops.evidence')" />
        </div>
        <div class="desk-acts">
          <button class="btn btn-line" @click="act('evidence', focusDispute.id)">{{ t('ops.evidence') }}</button>
          <button class="btn btn-navy" @click="act('dispute', focusDispute.id, focusDispute.openerId)">{{ t('act.rule') }}</button>
          <button class="btn btn-line" @click="act('review', focusDispute.id)">{{ t('ops.superReview') }}</button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/blacklist' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="b in blackPager.items" :key="b.userId" type="button" class="hit" :class="{ on: focusBlack && focusBlack.userId === b.userId }" @click="pick(b.userId)">
          <div>
            <b>{{ entity(b.name) }}</b>
            <span>{{ phrase(b.reason) }}</span>
          </div>
        </button>
        <Pager v-model:page="blackPager.page" :pages="blackPager.pages" :total="blackPager.total" :size="blackPager.size" />
      </aside>
      <article v-if="focusBlack" class="desk-detail">
        <div class="desk-body">
          <h2>{{ entity(focusBlack.name) }}</h2>
          <p class="note">{{ t('ops.page.blacklist') }}</p>
          <div class="kv">
            <div><span>{{ t('ops.auditTarget') }}</span><b>{{ focusBlack.userId }}</b></div>
            <div><span>{{ t('col.status') }}</span><b>{{ phrase(focusBlack.reason) }}</b></div>
          </div>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/ports' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="p in portsPager.items" :key="p.id" type="button" class="hit" :class="{ on: focusPort && focusPort.id === p.id }" @click="pick(p.id)">
          <div>
            <b class="cname"><Flag v-for="c in String(p.corridor || p.country || '').split('-')" :key="c" :code="c" />{{ portName(p) }}</b>
            <span>{{ waitMin(p.waitMin) }}</span>
          </div>
          <em class="pill" :class="tone(p.status)">{{ portLabel(p.status) }}</em>
        </button>
        <Pager v-model:page="portsPager.page" :pages="portsPager.pages" :total="portsPager.total" :size="portsPager.size" />
      </aside>
      <article v-if="focusPort" class="desk-detail">
        <div class="desk-body">
          <div class="top">
            <div>
              <p class="kicker">{{ focusPort.corridor }}</p>
              <h2 class="cname"><Flag v-for="c in String(focusPort.corridor || '').split('-')" :key="c" :code="c" />{{ portName(focusPort) }}</h2>
            </div>
            <span class="pill" :class="tone(focusPort.status)">{{ portLabel(focusPort.status) }}</span>
          </div>
          <p class="note">{{ t('ops.queue.ports') }}</p>
          <div class="kv">
            <div><span>{{ t('ops.waitEdit') }}</span><b>{{ waitMin(focusPort.waitMin) }}</b></div>
            <div><span>{{ t('trip.updated') }}</span><b>{{ focusPort.updated || '—' }}</b></div>
          </div>
          <div class="port-edit">
            <label>{{ t('ops.statusEdit') }}
              <select v-model="portStatus" class="field">
                <option v-for="g in portGrades" :key="g" :value="g">{{ portLabel(g) }}</option>
              </select>
            </label>
            <label>{{ t('ops.waitEdit') }}
              <input v-model.number="portWait" class="field" type="number" min="0" />
            </label>
          </div>
          <div v-if="portReports.length">
            <h3>{{ t('ops.reports') }}</h3>
            <article v-for="r in portReports" :key="r.id" class="report">
              <div>
                <b>{{ portLabel(r.status) }}</b>
                <span>{{ r.at || '' }} · {{ waitMin(r.waitMin) }}</span>
              </div>
              <button class="btn btn-line" @click="act('report', r.id)">{{ t('act.confirm') }}</button>
            </article>
          </div>
        </div>
        <div class="desk-acts">
          <button class="btn btn-green" @click="savePort">{{ t('ops.savePort') }}</button>
          <button class="btn btn-line" @click="act('port', focusPort.id, { status: 'smooth', waitMin: 20 })">{{ t('act.markSmooth') }}</button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/announcements' && payload" class="desk">
      <aside class="desk-list">
        <button v-for="a in annPager.items" :key="a.id" type="button" class="hit" :class="{ on: focusAnn && focusAnn.id === a.id }" @click="pick(a.id)">
          <div>
            <b>{{ phrase(a.title) }}</b>
            <span>{{ a.locale }}</span>
          </div>
        </button>
        <Pager v-model:page="annPager.page" :pages="annPager.pages" :total="annPager.total" :size="annPager.size" />
      </aside>
      <article v-if="focusAnn" class="desk-detail">
        <div class="desk-body">
          <p class="kicker">{{ focusAnn.locale }}</p>
          <h2>{{ phrase(focusAnn.title) }}</h2>
          <p class="note">{{ phrase(focusAnn.body) || t('ops.page.announcements') }}</p>
          <label>{{ t('ops.audience') }}
            <select v-model="annAudience" class="field">
              <option value="all">all</option>
              <option value="shipper">shipper</option>
              <option value="driver">driver</option>
            </select>
          </label>
        </div>
        <div class="desk-acts">
          <button class="btn btn-navy" @click="act('ann', 'new', annAudience)">{{ t('act.publishAnn') }}</button>
        </div>
      </article>
    </div>

    <div v-if="route.path === '/console/config' && payload" class="rates">
      <h3>{{ t('ops.rates') }}</h3>
      <div class="rate-kpis">
        <div><span>{{ t('ops.rateBase') }}</span><b>{{ cfgDraft.rate_base_cnkz || '18' }}</b></div>
        <div><span>{{ t('ops.truckFactor') }}</span><b>{{ cfgDraft.truck_factor_175 || '1.15' }}</b></div>
        <div><span>{{ t('ops.reeferFactor') }}</span><b>{{ cfgDraft.cargo_factor_reefer || '1.35' }}</b></div>
        <div><span>{{ t('ops.cacheTtl') }}</span><b>{{ cfgDraft.estimate_cache_days || '7' }}</b></div>
        <div><span>{{ t('ops.anonLimit') }}</span><b>{{ cfgDraft.estimate_anon_limit || '2' }}</b></div>
      </div>
    </div>
    <table v-if="route.path === '/console/config' && payload" class="grid cfg">
      <tr v-for="row in cfgPager.items" :key="row.id">
        <td>
          <b>{{ cfgText('cfg.', row.key) }}</b>
          <small>{{ cfgText('cfg.h.', row.key) }}</small>
        </td>
        <td class="num">
          <input class="field" v-model="cfgDraft[row.key]" />
        </td>
      </tr>
    </table>
    <button v-if="route.path === '/console/config'" class="btn btn-green" type="button" @click="saveCfg">{{ t('ops.saveCfg') }}</button>
    <Pager v-if="route.path === '/console/config'" v-model:page="cfgPager.page" :pages="cfgPager.pages" :total="cfgPager.total" :size="cfgPager.size" />

    <p v-if="route.path === '/console/i18n' && payload" class="note">{{ t('ops.missing') }} · {{ payload.missingCount || (payload.missing || []).length }}</p>
    <ul v-if="route.path === '/console/i18n' && (payload?.missing || []).length" class="missing">
      <li v-for="k in payload.missing" :key="k">{{ k }}</li>
    </ul>
    <table v-if="route.path === '/console/i18n' && payload" class="grid">
      <thead><tr><th>key</th><th>zh</th><th>ru</th><th>en</th></tr></thead>
      <tbody>
        <tr v-for="x in i18nPager.items" :key="x.key"><td>{{ x.key }}</td><td>{{ x.zh }}</td><td>{{ x.ru }}</td><td>{{ x.en }}</td></tr>
      </tbody>
    </table>
    <a v-if="route.path === '/console/i18n'" class="btn btn-line" href="/api/v1/admin/i18n.csv">{{ t('ops.export') }}</a>
    <Pager v-if="route.path === '/console/i18n'" v-model:page="i18nPager.page" :pages="i18nPager.pages" :total="i18nPager.total" :size="i18nPager.size" />

    <table v-if="route.path === '/console/audit' && payload" class="grid">
      <thead><tr><th>{{ t('ops.auditAct') }}</th><th>{{ t('ops.auditTarget') }}</th><th>{{ t('ops.auditAt') }}</th></tr></thead>
      <tbody>
        <tr v-for="x in auditPager.items" :key="x.id"><td>{{ x.action }}</td><td>{{ x.target }}</td><td>{{ x.at }}</td></tr>
      </tbody>
    </table>
    <Pager v-if="route.path === '/console/audit'" v-model:page="auditPager.page" :pages="auditPager.pages" :total="auditPager.total" :size="auditPager.size" />
  </div>
</template>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 16px; flex-wrap: wrap; }
h1 { margin: 0; font-size: 26px; }
.sub { margin: 6px 0 0; max-width: 72ch; color: var(--muted); font-size: 14px; }
.err { color: var(--color-danger); }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.kpis a {
  background: linear-gradient(180deg, #ffffff, #f4f7fb);
  border: 1px solid var(--line);
  border-radius: var(--radius-l);
  padding: 18px;
  transition: border-color .15s, box-shadow .15s;
}
.kpis a:nth-child(1) { background: linear-gradient(180deg, #ffffff, #eaf1fe); }
.kpis a:nth-child(2) { background: linear-gradient(180deg, #ffffff, #e6f4ee); }
.kpis a:nth-child(3) { background: linear-gradient(180deg, #ffffff, #fdf3e0); }
.kpis a:nth-child(4) { background: linear-gradient(180deg, #ffffff, #fdeceb); }
.kpis a:nth-child(5) { background: linear-gradient(180deg, #ffffff, #f7f4ee); }
.kpis a:hover { border-color: #cde8d8; box-shadow: var(--shadow-s); }
.kpis small, .kpis em { color: var(--muted); font-size: 12px; font-style: normal; }
.kpis strong { display: block; margin: 6px 0 2px; font-size: 28px; color: #1c2430; font-variant-numeric: tabular-nums; }
.kpis a:nth-child(1) strong { color: #2563eb; }
.kpis a:nth-child(2) strong { color: #12805c; }
.kpis a:nth-child(3) strong { color: #b7791f; }
.kpis a:nth-child(4) strong { color: #b42318; }
.kpis a:nth-child(5) strong { color: #8d6a32; }
.ops-split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.ops-split section, .live-box {
  background: #fff; border: 1px solid var(--line); border-radius: var(--radius-l); overflow: hidden;
}
.ops-split h3, .live-box h3 { margin: 0; padding: 12px 16px 6px; font-size: 14px; }
.queue-row {
  width: 100%; display: flex; justify-content: space-between; align-items: center; gap: 12px;
  border: 0; background: transparent; text-align: left; padding: 10px 16px;
  border-top: 1px solid var(--line-soft);
}
.queue-row:hover { background: #f7f9fc; }
.queue-row b { display: block; font-size: 14px; }
.queue-row span { display: block; color: var(--muted); font-size: 12px; margin-top: 2px; }
.queue-row em { font-style: normal; }
.go { display: inline-block; margin: 8px 16px 14px; color: var(--signal-ink); font-weight: 700; font-size: 13px; }
.live-meta { display: flex; align-items: center; gap: 10px; }
.live-meta strong { font-variant-numeric: tabular-nums; color: var(--navy); }
.cname { display: inline-flex; align-items: center; gap: 6px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.toolbar .field { max-width: 320px; }
.field.slim { max-width: 180px; }
.rates { display: flex; gap: 10px; margin: 14px 0; flex-wrap: wrap; }
.rates span {
  background: linear-gradient(180deg, #ffffff, #e6f4ee);
  border: 1px solid #cde8d8; border-radius: 999px;
  padding: 6px 12px; color: var(--color-secondary); font-size: 13px;
}
.rates span:nth-child(2) { background: linear-gradient(180deg, #ffffff, #eaf1fe); border-color: #d5e3fb; }
.rates span:nth-child(3) { background: linear-gradient(180deg, #ffffff, #fdf3e0); border-color: #ead9b6; }
.rates b { color: #1c2430; }
.work { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }
.work article { background: linear-gradient(180deg, #ffffff, #f7f9fc); border: 1px solid var(--line); border-radius: var(--radius-l); overflow: hidden; }
.work button { width: 100%; border: 0; background: transparent; text-align: left; padding: 14px 16px; }
.work span { display: block; color: var(--color-secondary); font-size: 12px; }
.work strong { display: block; margin-top: 4px; font-size: 24px; color: var(--navy); font-variant-numeric: tabular-nums; }
.work-body { padding: 0 16px 14px; }
.work-body p { margin: 0 0 8px; color: var(--ink-soft); font-size: 13px; }
.work-body a { color: var(--signal-ink); font-weight: 700; font-size: 13px; }
.split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.split section, .grid, .machine {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-l);
  overflow: hidden;
}
.split h3, .machine h3 { margin: 0; padding: 12px 14px 0; font-size: 14px; }
.bar {
  width: calc(100% - 28px);
  margin: 8px 14px;
  display: grid;
  grid-template-columns: 118px 1fr 36px;
  gap: 8px;
  align-items: center;
  border: 0;
  background: transparent;
  text-align: left;
  padding: 0;
}
.bar i { display: block; height: 9px; background: #eef1f6; border-radius: 99px; overflow: hidden; }
.bar b { display: block; height: 100%; background: var(--signal); border-radius: 99px; }
.bar em { font-style: normal; font-weight: 700; }
.machine { margin-top: 16px; padding-bottom: 14px; }
.flows { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 14px; }
.flows button { border: 1px solid var(--line); background: #fff; border-radius: 999px; padding: 6px 12px; font-size: 13px; color: var(--ink-soft); }
.flows button.on { background: linear-gradient(180deg, #eef6f1, #dceee4); color: #0e6a4c; border-color: #cde8d8; }
.machine p { margin: 0 14px; }
.series { display: flex; align-items: flex-end; gap: 10px; height: 140px; padding: 12px 16px 8px; }
.series .col { flex: 1; display: grid; grid-template-rows: 1fr auto auto; justify-items: center; height: 100%; gap: 4px; }
.series i { display: block; width: 100%; max-width: 28px; background: #eef1f6; border-radius: 8px 8px 0 0; overflow: hidden; height: 100%; position: relative; }
.series b { position: absolute; left: 0; right: 0; bottom: 0; background: var(--signal, #1f4b99); display: block; }
.series span, .series em { font-size: 11px; color: var(--muted); }
.series em { font-style: normal; font-weight: 700; color: var(--navy); }
.desk {
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(0, 1.15fr);
  gap: 16px;
  align-items: stretch;
  height: min(68vh, 640px);
  min-height: 440px;
}
.desk-list, .desk-detail {
  min-height: 0;
  height: 100%;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius-l);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.desk-list { padding: 8px; overflow: auto; }
.hit {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  border: 1px solid transparent;
  background: transparent;
  text-align: left;
  padding: 10px 12px;
  border-radius: 12px;
}
.hit:hover { background: #f7f9fc; }
.hit.on { border-color: #cde8d8; background: #eef6f1; }
.hit b { display: block; font-size: 14px; }
.hit span { display: block; color: var(--muted); font-size: 12px; margin-top: 2px; }
.hit em { font-style: normal; flex: 0 0 auto; }
.desk-detail { padding: 0; }
.desk-body { flex: 1; min-height: 0; overflow: auto; padding: 20px; }
.desk-acts {
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
  padding: 12px 16px; border-top: 1px solid var(--line-soft); background: #fafbfd;
}
.desk-acts input { flex: 1; min-width: 160px; height: 36px; border: 1px solid var(--line); border-radius: 8px; padding: 0 10px; }
.top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.kicker { margin: 0; color: var(--muted); font-size: 12px; }
.desk-detail h2 { margin: 4px 0 0; font-size: 22px; }
.lane { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.note { margin: 12px 0; color: var(--muted); font-size: 13px; line-height: 1.55; }
.kv { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0; }
.kv div { border: 1px solid var(--line-soft); background: #f7f9fc; border-radius: 12px; padding: 10px 12px; }
.kv span { display: block; color: var(--muted); font-size: 12px; }
.kv b { display: block; margin-top: 4px; font-size: 14px; }
.checks { margin: 8px 0 12px; padding-left: 18px; color: var(--ink-soft); font-size: 13px; }
.rail { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 8px 0; padding: 0; }
.rail li { padding: 4px 8px; border-radius: 999px; background: #fff; border: 1px solid var(--line); color: var(--muted); font-size: 12px; }
.rail li.on { background: linear-gradient(180deg, #eef6f1, #dceee4); color: #0e6a4c; border-color: #cde8d8; }
.rail li.done { color: #157a40; border-color: #cde8d8; }
.docs { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; }
.docs figure { width: 200px; margin: 0; }
.docs img { width: 200px; height: 132px; object-fit: contain; border-radius: 8px; border: 1px solid var(--color-border); background: #f5f7fa; }
.no-photo { width: 200px; height: 132px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--color-secondary); border: 1px dashed var(--color-border); border-radius: 6px; }
.docs figcaption { font-size: 11px; color: var(--color-secondary); margin-top: 4px; }
.port-edit { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.port-edit label { display: grid; gap: 6px; font-size: 13px; color: var(--muted); }
.report { display: flex; justify-content: space-between; gap: 12px; align-items: center; border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; margin-top: 8px; }
.report span { display: block; color: var(--muted); font-size: 12px; }
.mini { width: 100%; border-collapse: collapse; }
.mini td { padding: 8px 0; border-bottom: 1px solid var(--line-soft); font-size: 13px; }
.ch { display: flex; align-items: center; gap: 8px; }
.empty { color: var(--muted); padding: 16px; }
.cfg td b, .cfg td small { display: block; }
.cfg td small { color: var(--muted); font-weight: 400; margin-top: 2px; }
.cfg .num { font-variant-numeric: tabular-nums; font-weight: 750; font-size: 16px; }
.rates { background: #fff; border: 1px solid var(--line); border-radius: var(--radius-l); padding: 16px 18px; margin-bottom: 16px; }
.rate-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 10px; }
.rate-kpis div { background: #f7f9fc; border-radius: 12px; padding: 12px 14px; }
.rate-kpis span { display: block; font-size: 12px; color: var(--muted); }
.rate-kpis b { font-size: 22px; letter-spacing: -0.03em; }
.missing { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; list-style: none; margin: 0 0 12px; }
.missing li { border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; font-size: 12px; color: #c62828; background: #fff; }
.evidence img { width: 72px; height: 52px; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); }
.grid { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 13px 16px; font-size: 14px; border-bottom: 1px solid var(--line-soft); }
th {
  color: var(--muted); font-weight: 600; font-size: 12px; letter-spacing: .04em;
  background: #fafbfd; border-bottom: 1px solid var(--line);
}
.btn { height: 36px; padding: 0 14px; font-size: 13px; }
@media (max-width: 1100px) {
  .split, .ops-split, .desk { grid-template-columns: 1fr; }
  .desk { height: auto; min-height: 0; }
  .desk-list, .desk-detail { height: min(52vh, 520px); }
  .kv, .port-edit { grid-template-columns: 1fr; }
}
@media (max-width: 900px) {
  .kpis, .work { grid-template-columns: 1fr 1fr; }
  table.grid { display: block; overflow-x: auto; }
  .bar { grid-template-columns: minmax(80px, 1fr) 1fr auto; }
}
@media (max-width: 640px) {
  .kpis, .work { grid-template-columns: 1fr; }
  .head { display: grid; }
}
</style>
