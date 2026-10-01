<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appApi, setAppToken } from '../api'
import { isAppAuthed } from '../auth'
import {
  brand,
  cargo,
  cargoClass,
  company,
  countryName,
  entity,
  kycLabel,
  ledgerLabel,
  loadStatus,
  money,
  modeLabel,
  orderStatus,
  packing,
  party,
  phrase,
  place,
  portLabel,
  portName,
  quoteLabel,
  remarkText,
  tone,
  waitMin,
} from '../fmt'
import { CARGO_OPTIONS, DEST_CITIES, ORIGIN_CITIES } from '../geo'
import { locale, setLocale, t, tf, type Locale } from '../i18n'

function chatLine(m: Record<string, any>) {
  const body = String(m.body || m.zh || '')
  if (body) {
    const localized = phrase(body)
    if (localized !== body) return localized
  }
  if (locale.value === 'en-US') return m.en || phrase(m.body) || ''
  if (locale.value === 'ru-RU') return m.ru || m.translated || phrase(m.body) || ''
  return m.zh || m.body || ''
}
import AppChatRow from '../components/AppChatRow.vue'
import Flag from '../components/Flag.vue'
import PayMark from '../components/PayMark.vue'
import AppGlyph from '../components/AppGlyph.vue'
import Pager from '../components/Pager.vue'
import OrderTrackMap from '../components/OrderTrackMap.vue'
import PayQr from '../components/PayQr.vue'
import BrandMark from '../components/BrandMark.vue'
import WorkLoadCard from '../components/WorkLoadCard.vue'
import WorkNav from '../components/WorkNav.vue'
import KycPreview from '../components/KycPreview.vue'
import { usePager } from '../usePager'
const props = defineProps<{ role: 'shipper' | 'driver' }>()
let current: any = appApi
const client = new Proxy(appApi, {
  get(_target, key) {
    const value = current[key]
    return typeof value === 'function' ? value.bind(current) : value
  },
})
const router = useRouter()
const tab = ref(0)
const screen = ref<'main' | 'load' | 'order' | 'chat' | 'publish' | 'estimate' | 'ports' | 'deposit' | 'kyc' | 'credit' | 'waybill' | 'review' | 'settings' | 'quotes' | 'assign' | 'notes' | 'vehicles' | 'lanes'>('main')
const err = ref('')
const busy = ref(false)
const me = ref<any>(null)
const loads = ref<any[]>([])
const orders = ref<any[]>([])
const chats = ref<any[]>([])
const invites = ref<any[]>([])
const detail = ref<any>(null)
const messages = ref<any[]>([])
const cid = ref('')
const draft = ref('')
const estimate = ref<any>(null)
const ports = ref<any[]>([])
const deposit = ref<any>(null)
const kyc = ref<any>(null)
const credit = ref<any>(null)
const filter = ref('')
const orderFilter = ref('')
const chatPeer = ref('')
const chatLane = ref('')
const msgBox = ref<HTMLElement | null>(null)
const quoteAmt = ref(17000)
const estFrom = ref('乌鲁木齐')
const estTo = ref('阿拉木图')
const reported = ref('')
const quoteSort = ref<'price' | 'credit' | 'truck'>('price')
const armQuote = ref('')
const locOn = ref(true)
const notifyOn = ref(true)
const quietOn = ref(false)
const stars = ref(5)
const reviewTags = ref<string[]>(['on_time'])
const reviewComment = ref('')
const payIntent = ref<any>(null)
const payLeft = ref(0)
const drivers = ref<any[]>([])
const pickedDrivers = ref<string[]>([])
const notes = ref<any[]>([])
const unread = ref(0)
const vehicles = ref<any[]>([])
const lanes = ref<any[]>([])
const plateDraft = ref('新A·')
const truckLen = ref(13.5)
const truckTon = ref(32)
const truckBody = ref('van')
const truckBrand = ref('一汽解放')
const truckVin = ref('')
const truckAxles = ref(6)
const truckInspect = ref('2027-03-31')
const truckInsurance = ref('2026-12-18')
const laneFrom = ref('乌鲁木齐')
const laneTo = ref('阿拉木图')
const pwdDraft = ref('')
const signData = ref('')
const drawing = ref(false)
const unlockedPhone = ref('')
const notifySms = ref(true)
const syncedAt = ref('')
const statusFilter = ref('')
const cargoFilter = ref('')
const truckFilter = ref('')
const LOAD_STATUSES = ['draft', 'pending_review', 'published', 'matching', 'dealt', 'in_transit', 'completed', 'cancelled']
let pollTimer = 0
const mapRoute = computed(() => {
  const r = detail.value?.route || []
  if (r.length && typeof r[0] === 'object' && r[0].lat) return r
  return [
    { lat: 43.8256, lng: 87.6168, name: '乌鲁木齐' },
    { lat: 44.2143, lng: 80.4189, name: '霍尔果斯' },
    { lat: 43.238, lng: 76.8512, name: '阿拉木图' },
  ]
})

const form = reactive({
  origin: '乌鲁木齐',
  dest: '阿拉木图',
  loadTime: '2026-09-20 08:00',
  cargoName: '机械零件',
  weightT: 18,
  volumeM3: 50,
  matchMode: 'bid',
  expectPrice: 18000,
  grabPrice: 18500,
  receiver: '阿依古丽',
  receiverPhone: '+7 7070001122',
  remark: '',
  hazmat: false,
  deadlineHours: 24,
  truckLength: 13.5,
  packing: 'pallet',
  cargoClass: 'general',
})
const pubStep = ref(1)
const loadFrom = ref('')
const loadTo = ref('')
const loadSort = ref<'new' | 'price'>('new')
const quoteNote = ref('')
const quoteEta = ref('2026-09-22 18:00')
const payAmount = ref(2000)
const payChannel = ref('wechat')
const estTruck = ref('13.5')
const estCargo = ref('general')
const estWeight = ref(18)
const reportStatus = ref('congested')
const reportWait = ref(90)
const kycKind = ref('enterprise')
const kycCompany = ref('')
const kycLegal = ref('')
const kycIdNo = ref('')
const kycGreenNo = ref('')
const kycGreenExp = ref('')
const kycCustoms = ref('')
const kycFiles = ref<Record<string, string>>({})
const KYC_FILE: Record<string, string> = {
  business_license: '/kyc/biz.svg',
  operator_id: '/kyc/agent.svg',
  id_card: '/kyc/id.svg',
  id_card_front: '/kyc/id.svg',
  id_card_hold: '/kyc/id.svg',
  license: '/kyc/license.svg',
  vehicle: '/kyc/vehicle.svg',
  road_permit: '/kyc/permit.svg',
  tir: '/kyc/green.svg',
  green_card: '/kyc/green.svg',
  truck_front: '/kyc/vehicle.svg',
  truck_side: '/kyc/vehicle.svg',
  truck_box: '/kyc/vehicle.svg',
  biz: '/kyc/biz.svg',
  agent: '/kyc/agent.svg',
  auth: '/kyc/auth.svg',
}
const SHIPPER_KYC = {
  enterprise: ['business_license', 'operator_id'],
  forwarder: ['business_license', 'operator_id'],
  personal: ['id_card_front'],
} as const
const DRIVER_KYC = ['id_card', 'id_card_hold', 'license', 'vehicle', 'road_permit', 'tir', 'green_card', 'truck_front', 'truck_side', 'truck_box']
const shipper = computed(() => props.role === 'shipper')
const requiredKyc = computed(() => (shipper.value ? [...(SHIPPER_KYC[kycKind.value as keyof typeof SHIPPER_KYC] || SHIPPER_KYC.enterprise)] : DRIVER_KYC))
const kycOk = computed(() => String(me.value?.kycStatus || '') === 'approved')
const tabs = computed(() =>
  shipper.value
    ? [
        { key: 'tab.home', icon: 'home' },
        { key: 'tab.loads', icon: 'loads' },
        { key: 'tab.orders', icon: 'orders' },
        { key: 'tab.chat', icon: 'chat' },
        { key: 'tab.me', icon: 'me' },
      ]
    : [
        { key: 'tab.home', icon: 'home' },
        { key: 'tab.find', icon: 'loads' },
        { key: 'tab.orders', icon: 'orders' },
        { key: 'tab.chat', icon: 'chat' },
        { key: 'tab.me', icon: 'me' },
      ],
)

const visibleLoads = computed(() => {
  let list = loads.value
  if (filter.value) list = list.filter((x) => x.matchMode === filter.value)
  if (statusFilter.value) list = list.filter((x) => x.status === statusFilter.value)
  if (cargoFilter.value) list = list.filter((x) => String(x.cargoName).includes(cargoFilter.value))
  if (truckFilter.value) list = list.filter((x) => Number(x.truckLength) === Number(truckFilter.value))
  if (loadFrom.value) list = list.filter((x) => String(x.origin).includes(loadFrom.value))
  if (loadTo.value) list = list.filter((x) => String(x.dest).includes(loadTo.value))
  const sorted = [...list]
  if (loadSort.value === 'price') {
    sorted.sort((a, b) => Number(a.expectPrice || a.grabPrice || 0) - Number(b.expectPrice || b.grabPrice || 0))
  }
  return sorted
})

const liveOrders = computed(() =>
  orders.value.filter((x) => ['wait_load', 'loading', 'in_transit', 'wait_confirm'].includes(x.status)),
)
const matchingLoads = computed(() => loads.value.filter((x) => x.status === 'matching' || Number(x.quoteCount) > 0))
const homeLoads = computed(() => {
  const ranked = [...loads.value].sort((a, b) => Number(b.quoteCount || 0) - Number(a.quoteCount || 0))
  return ranked
})
const liveInvites = computed(() =>
  invites.value.filter((x) => {
    if (x.status && x.status !== 'pending') return false
    const raw = x.expiresAt
    if (!raw) return true
    const ms = new Date(raw).getTime() - Date.now()
    return !Number.isNaN(ms) && ms > 0
  }),
)
const homePorts = computed(() => ports.value.slice(0, 4))
const homeNotes = computed(() => notes.value.slice(0, 5))
const statusCounts = computed(() => {
  const map: Record<string, number> = {}
  for (const x of loads.value) map[x.status] = (map[x.status] || 0) + 1
  return map
})

const ORDER_STEPS = ['wait_load', 'loading', 'in_transit', 'wait_confirm', 'completed']

const visibleOrders = computed(() => {
  const f = orderFilter.value
  if (!f) return orders.value
  if (f === 'live') {
    return orders.value.filter((x) => ['wait_load', 'loading', 'in_transit', 'wait_confirm'].includes(x.status))
  }
  if (f === 'wait_load') return orders.value.filter((x) => x.status === 'wait_load' || x.status === 'loading')
  return orders.value.filter((x) => x.status === f)
})

const loadsPager = usePager(visibleLoads, 12)
const ordersPager = usePager(visibleOrders, 10)
const portsPager = usePager(ports, 8)
const homeLoadsPager = usePager(homeLoads, 8)
const notesPager = usePager(notes, 8)
const vehiclesPager = usePager(vehicles, 8)
const depositLedgers = computed(() => deposit.value?.ledgers || [])
const ledgerPager = usePager(depositLedgers, 8)
const chatsPager = usePager(chats, 12)
watch(filter, () => loadsPager.reset())
watch(statusFilter, () => loadsPager.reset())
watch(cargoFilter, () => loadsPager.reset())
watch(truckFilter, () => loadsPager.reset())
watch(loadFrom, () => loadsPager.reset())
watch(loadTo, () => loadsPager.reset())
watch(loadSort, () => loadsPager.reset())
watch(orderFilter, () => ordersPager.reset())

const title = computed(() => {
  if (screen.value === 'main') return t(tabs.value[tab.value].key)
  if (screen.value === 'load') return t('tab.loads')
  if (screen.value === 'order') return t('tab.orders')
  if (screen.value === 'chat') return party(chatPeer.value) || t('tab.chat')
  if (screen.value === 'publish') return t('app.publish')
  if (screen.value === 'estimate') return t('app.estimate')
  if (screen.value === 'ports') return t('app.ports')
  if (screen.value === 'deposit') return t('app.deposit')
  if (screen.value === 'kyc') return t('app.kyc')
  if (screen.value === 'waybill') return t('app.waybill')
  if (screen.value === 'review') return t('app.review')
  if (screen.value === 'settings') return t('app.settings')
  if (screen.value === 'quotes') return t('app.quotes')
  if (screen.value === 'assign') return t('app.assignPick')
  if (screen.value === 'notes') return t('app.notes')
  if (screen.value === 'vehicles') return t('app.vehicles')
  if (screen.value === 'lanes') return t('app.lanes')
  return t('app.credit')
})

const orderDock = computed(() => {
  const d = detail.value
  if (!d) {
    return { primary: null as null | { action: string; label: string }, extra: null as null | { kind: 'simulate' | 'review'; label: string } }
  }
  if (!shipper.value && d.status === 'wait_load') return { primary: { action: 'start_load', label: t('app.startLoad') }, extra: null }
  if (!shipper.value && d.status === 'loading') return { primary: { action: 'start_transit', label: t('app.startTransit') }, extra: null }
  if (!shipper.value && d.status === 'in_transit') {
    return { primary: { action: 'arrive', label: t('app.arrive') }, extra: { kind: 'simulate' as const, label: t('app.simulate') } }
  }
  if (shipper.value && d.status === 'wait_confirm') return { primary: { action: 'confirm_receive', label: t('app.confirm') }, extra: null }
  if (d.status === 'completed') return { primary: null, extra: { kind: 'review' as const, label: t('app.review') } }
  return { primary: null, extra: null }
})

function nextHint(order: Record<string, any>) {
  const s = String(order.status || '')
  if (!shipper.value) {
    if (s === 'wait_load') return t('app.startLoad')
    if (s === 'loading') return t('app.startTransit')
    if (s === 'in_transit') return t('app.arrive')
    return ''
  }
  if (s === 'wait_confirm') return t('app.confirm')
  if (s === 'completed') return t('app.review')
  return ''
}

function orderStepOn(status: string, step: string) {
  if (status === 'completed') return true
  const a = ORDER_STEPS.indexOf(step)
  const b = ORDER_STEPS.indexOf(status)
  return a >= 0 && b >= 0 && a <= b
}

function scrollChat() {
  nextTick(() => {
    const el = msgBox.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

/** vue-tsc 不会因 v-if 收窄 computed 字段，动作必须先取出再调用。 */
function actOrderPrimary() {
  const action = orderDock.value.primary?.action
  const id = detail.value?.id
  if (!action || !id) return
  void run(() => client.orderAction(id, action))
}

async function boot() {
  if (!isAppAuthed()) {
    setAppToken(null)
    await router.push({ path: '/login', query: { role: props.role } })
    return
  }
  try {
    me.value = await client.me()
    if (me.value?.role && me.value.role !== props.role) {
      setAppToken(null)
      await router.push({ path: '/login', query: { role: props.role } })
      return
    }
    await refresh()
  } catch (e) {
    const msg = String(e)
    err.value = msg
    setAppToken(null)
    await router.push({ path: '/login', query: { role: props.role } })
  }
}

async function refresh() {
  const [l, o, c, profile, dep, portData, kycData] = await Promise.all([
    shipper.value ? client.loads(true) : client.loads(false),
    client.orders(),
    client.conversations(),
    client.me(),
    client.deposit().catch(() => deposit.value),
    client.ports().catch(() => ({ items: ports.value })),
    client.kyc().catch(() => kyc.value),
  ])
  me.value = profile
  loads.value = l.items || []
  orders.value = o.items || []
  chats.value = c.items || []
  if (dep) deposit.value = dep
  ports.value = portData?.items || ports.value
  if (kycData) applyKyc(kycData)
  if (!shipper.value) {
    const [inv, veh, ln] = await Promise.all([
      client.invites(),
      client.vehicles().catch(() => ({ items: vehicles.value })),
      client.lanes().catch(() => ({ items: lanes.value })),
    ])
    invites.value = inv.items || []
    vehicles.value = veh.items || []
    lanes.value = ln.items || []
  }
  try {
    const n = await client.notifications()
    notes.value = n.items || []
    unread.value = n.unread || 0
  } catch {
    unread.value = 0
  }
  markSynced()
}

function applyKyc(data: any) {
  kyc.value = data
  kycKind.value = data.kind === 'forwarder' || data.kind === 'personal' ? data.kind : data.kind === 'driver' ? 'enterprise' : (data.kind || 'enterprise')
  kycCompany.value = data.company || me.value?.name || ''
  kycLegal.value = kycLegal.value || me.value?.name || ''
  kycGreenNo.value = data.greenCardNo || ''
  kycGreenExp.value = data.greenCardExpires || ''
  kycCustoms.value = data.customs || ''
  const files: Record<string, string> = { ...kycFiles.value }
  for (const row of data.credentials || []) {
    if (row.kind && row.fileUrl) files[row.kind] = row.fileUrl
    if (row.kind === 'biz') files.business_license = row.fileUrl
    if (row.kind === 'agent') files.operator_id = row.fileUrl
    if (row.kind === 'drive') files.license = row.fileUrl
  }
  kycFiles.value = files
}

function markSynced() {
  syncedAt.value = new Date().toLocaleTimeString(locale.value === 'en-US' ? 'en-US' : locale.value === 'ru-RU' ? 'ru-RU' : 'zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

async function silentRefresh() {
  if (busy.value || !isAppAuthed()) return
  try {
    await refresh()
    if (cid.value && screen.value === 'chat') {
      const data = await client.messages(cid.value)
      messages.value = data.items || []
    }
    if (detail.value?.id && screen.value === 'load') {
      detail.value = await client.loadDetail(detail.value.id)
    }
    if (detail.value?.id && screen.value === 'order') {
      detail.value = await client.orderDetail(detail.value.id)
    }
  } catch {
    /* 轮询失败不打断当前操作 */
  }
}

function onVis() {
  if (document.visibilityState === 'visible') void silentRefresh()
}

onMounted(() => {
  void boot()
  pollTimer = window.setInterval(() => {
    if (document.visibilityState === 'hidden') return
    void silentRefresh()
  }, 8000)
  document.addEventListener('visibilitychange', onVis)
})
onUnmounted(() => {
  window.clearInterval(pollTimer)
  document.removeEventListener('visibilitychange', onVis)
})

function inviteLeft(inv: Record<string, any>) {
  const raw = inv.expiresAt
  if (!raw) return t('app.inviteLeft')
  const ms = new Date(raw).getTime() - Date.now()
  if (Number.isNaN(ms) || ms <= 0) return t('work.expired')
  const h = Math.max(1, Math.ceil(ms / 3600000))
  return tf('work.hoursLeft', { n: h })
}

function fmtWhen(raw: unknown) {
  const s = String(raw || '')
  if (!s) return ''
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  const tag = locale.value === 'en-US' ? 'en-US' : locale.value === 'ru-RU' ? 'ru-RU' : 'zh-CN'
  return d.toLocaleString(tag, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function run(fn: () => Promise<any>) {
  busy.value = true
  err.value = ''
  try {
    await fn()
    await refresh()
    if (detail.value?.id && screen.value === 'load') detail.value = await client.loadDetail(detail.value.id)
    if (detail.value?.id && screen.value === 'order') detail.value = await client.orderDetail(detail.value.id)
  } catch (e) {
    err.value = String(e)
    console.error('App 操作失败', e)
  } finally {
    busy.value = false
  }
}

async function openLoad(id: string) {
  detail.value = await client.loadDetail(id)
  screen.value = 'load'
}

async function openOrder(id: string) {
  unlockedPhone.value = ''
  detail.value = await client.orderDetail(id)
  screen.value = 'order'
}

async function openConv(id: string) {
  cid.value = id
  const c = chats.value.find((x) => x.id === id)
  if (c) {
    chatPeer.value = c.peerName || chatPeer.value
    chatLane.value = c.lane || chatLane.value
  }
  const data = await client.messages(id)
  messages.value = data.items || []
  screen.value = 'chat'
  scrollChat()
}

async function openChat(loadId?: string) {
  const conv = loadId ? await client.openChat(loadId) : chats.value[0]
  if (!conv?.id) return
  if (loadId && detail.value) {
    const load = detail.value.load || detail.value
    chatPeer.value = shipper.value ? detail.value.driver?.name || '' : detail.value.shipper?.name || ''
    if (load?.origin) chatLane.value = `${place(load.origin)} → ${place(load.dest)}`
  }
  await openConv(conv.id)
}

async function openOrderChat() {
  const loadId = detail.value?.load?.id || detail.value?.loadId
  if (!loadId) return
  await openChat(loadId)
}

async function send() {
  const text = draft.value.trim()
  if (!text || !cid.value) return
  if (/1\d{10}|微信|whatsapp|telegram|\+\d[\d\s-]{7,}/i.test(text)) {
    err.value = t('app.sensitive')
    return
  }
  await client.send(cid.value, text)
  draft.value = ''
  const data = await client.messages(cid.value)
  messages.value = data.items || []
  scrollChat()
}

const sortedQuotes = computed(() => {
  const list = [...(detail.value?.quotes || [])]
  list.sort((a, b) => {
    if (quoteSort.value === 'credit') return Number(b.driver?.credit || 0) - Number(a.driver?.credit || 0)
    if (quoteSort.value === 'truck') return Number(b.driver?.vehicles?.[0]?.lengthM || 0) - Number(a.driver?.vehicles?.[0]?.lengthM || 0)
    return Number(a.amount) - Number(b.amount)
  })
  return list
})

function peerPhone(order: Record<string, any>) {
  if (unlockedPhone.value) return unlockedPhone.value
  const person = shipper.value ? order.driver : order.shipper
  const raw = String(person?.phone || '')
  if (!raw) return ''
  return raw.replace(/(\d{3})\d{4}(\d+)/, '$1****$2')
}

function navHref(kind: 'amap' | 'yandex') {
  const city = place(detail.value?.load?.dest || '')
  const q = encodeURIComponent(city)
  return kind === 'amap' ? `https://uri.amap.com/search?keyword=${q}` : `https://yandex.com/maps/?text=${q}`
}

function sourceLine(m: Record<string, any>) {
  const shown = chatLine(m)
  const zh = String(m.zh || '')
  if (!zh || zh === shown) return ''
  return zh
}

async function quoteNow() {
  if (!detail.value?.id) return
  const res = await client.quote(detail.value.id, quoteAmt.value, { eta: quoteEta.value, remark: quoteNote.value })
  if (res?.error === 'cap') {
    err.value = t('app.cap')
    return
  }
  detail.value = await client.loadDetail(detail.value.id)
}

async function grabNow() {
  if (!detail.value?.id) return
  const res = await client.grab(detail.value.id)
  if (res?.error === 'cap') {
    err.value = t('app.cap')
    return
  }
  if (res?.status === 'pending' || res?.holdId) {
    err.value = t('app.holdWait')
    detail.value = await client.loadDetail(detail.value.id)
    return
  }
  screen.value = 'main'
  tab.value = 2
  await refresh()
}

async function confirmQuote(id: string) {
  if (armQuote.value !== id) {
    armQuote.value = id
    return
  }
  await run(() => client.choose(detail.value.id, id))
  armQuote.value = ''
  screen.value = 'main'
  tab.value = 2
}

function openEstimate() {
  screen.value = 'estimate'
}

async function runEstimate() {
  const data = await client.estimate(estFrom.value, estTo.value, {
    truck: `${estTruck.value}x32`,
    cargo: estCargo.value,
    weight: estWeight.value,
  })
  if (data?.needLogin) {
    err.value = t('app.needLoginEst')
    return
  }
  estimate.value = data
}

async function showPorts() {
  const data = await client.ports()
  ports.value = data.items || []
  screen.value = 'ports'
}

async function showDeposit() {
  deposit.value = await client.deposit()
  screen.value = 'deposit'
}

async function showKyc() {
  const data = await client.kyc()
  applyKyc(data)
  screen.value = 'kyc'
}

async function showCredit() {
  if (!me.value?.id) return
  credit.value = await client.credit(me.value.id)
  screen.value = 'credit'
}

async function publish() {
  if (form.hazmat) {
    err.value = t('app.hazmatHint')
    return
  }
  await run(() =>
    client.publish({
      origin: form.origin,
      dest: form.dest,
      originCountry: 'CN',
      destCountry: form.dest === '莫斯科' || form.dest === '新西伯利亚' ? 'RU' : 'KZ',
      loadTime: form.loadTime,
      cargoName: form.cargoName,
      weightT: form.weightT,
      volumeM3: form.volumeM3,
      matchMode: form.matchMode,
      expectPrice: form.expectPrice,
      floorPrice: Math.round(form.expectPrice * 0.85),
      grabPrice: form.grabPrice,
      receiverName: form.receiver,
      receiverPhone: form.receiverPhone,
      remark: form.remark,
      hazmat: form.hazmat,
      deadlineHours: form.deadlineHours,
      truckLength: form.truckLength,
      packing: form.packing,
      cargoClass: form.cargoClass,
      photos: [],
    }),
  )
  screen.value = 'main'
  tab.value = 1
}

const payChannels = ['wechat', 'alipay', 'unionpay', 'kaspi']

function credKind(kind: string) {
  if (kind === 'business_license' || kind === 'biz') return 'biz'
  if (kind === 'operator_id' || kind === 'agent') return 'agent'
  if (kind === 'drive') return 'license'
  if (kind === 'green') return 'green_card'
  if (kind === 'truck_photo') return 'truck_front'
  return kind || 'vehicle'
}

function credRow(kind: string) {
  const list = kyc.value?.credentials || []
  const aliases: Record<string, string[]> = {
    business_license: ['business_license', 'biz'],
    operator_id: ['operator_id', 'agent'],
    license: ['license', 'drive'],
    green_card: ['green_card', 'green'],
    truck_front: ['truck_front', 'truck_photo'],
    id_card_front: ['id_card_front', 'id_card'],
  }
  const keys = aliases[kind] || [kind]
  return list.find((c: any) => keys.includes(c.kind)) || null
}

function bodyLabel(v: string) {
  return v === 'reefer' ? t('app.bodyReefer') : t('app.bodyVan')
}

async function unlockPeer() {
  const id = shipper.value ? detail.value?.driver?.id : detail.value?.shipper?.id
  if (!id) return
  const res = await client.unlockPhone(id)
  unlockedPhone.value = res.phone || ''
}

async function topupNow(channel = payChannel.value) {
  await run(async () => {
    const res = await client.topup(channel, Number(payAmount.value) || 200)
    if (res?.exempt) {
      deposit.value = await client.deposit()
      return
    }
    payIntent.value = res
    payLeft.value = 42
    const timer = window.setInterval(() => {
      payLeft.value -= 1
      if (payLeft.value <= 0) window.clearInterval(timer)
    }, 1000)
  })
}

async function confirmPayNow() {
  if (!payIntent.value?.intentId) return
  await run(async () => {
    await client.confirmPay(payIntent.value.intentId)
    payIntent.value = null
    deposit.value = await client.deposit()
  })
}

function toggleTag(tag: string) {
  if (reviewTags.value.includes(tag)) reviewTags.value = reviewTags.value.filter((x) => x !== tag)
  else reviewTags.value = [...reviewTags.value, tag]
}

async function submitReview() {
  if (!detail.value?.id) return
  await run(() => client.review(detail.value.id, stars.value, reviewTags.value.join(','), reviewComment.value || 'ok'))
  screen.value = 'main'
  tab.value = 2
}

function onSign(e: MouseEvent) {
  const canvas = e.currentTarget as HTMLCanvasElement
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const r = canvas.getBoundingClientRect()
  if (!drawing.value) {
    ctx.beginPath()
    ctx.moveTo(e.clientX - r.left, e.clientY - r.top)
    drawing.value = true
    return
  }
  ctx.lineTo(e.clientX - r.left, e.clientY - r.top)
  ctx.strokeStyle = '#10283f'
  ctx.lineWidth = 2
  ctx.stroke()
}

function endSign(e: MouseEvent) {
  drawing.value = false
  const canvas = e.currentTarget as HTMLCanvasElement
  signData.value = canvas.toDataURL('image/png')
}

function clearSign() {
  signData.value = ''
}

async function signNow() {
  if (!detail.value?.id) return
  await run(() => client.signWaybill(detail.value.id, signData.value, 'signed on web'))
}

function printWaybill() {
  window.print()
}

async function openAssign() {
  const data = await client.drivers()
  drivers.value = data.items || []
  screen.value = 'assign'
}

async function sendAssign() {
  if (!detail.value?.id || !pickedDrivers.value.length) return
  await run(() => client.assign(detail.value.id, pickedDrivers.value, '优先走霍尔果斯'))
  screen.value = 'load'
}

async function showNotes() {
  const data = await client.notifications()
  notes.value = data.items || []
  unread.value = data.unread || 0
  screen.value = 'notes'
  await client.readNotes()
  unread.value = 0
}

async function showVehicles() {
  const data = await client.vehicles()
  vehicles.value = data.items || []
  screen.value = 'vehicles'
}

async function addTruck() {
  await client.addVehicle(plateDraft.value, {
    lengthM: truckLen.value,
    tonnage: truckTon.value,
    bodyType: truckBody.value,
    brand: truckBrand.value,
    vin: truckVin.value,
    axles: truckAxles.value,
    inspectExpires: truckInspect.value,
    insuranceExpires: truckInsurance.value,
  })
  plateDraft.value = '新A·'
  truckVin.value = ''
  await showVehicles()
}

async function showLanes() {
  const data = await client.lanes()
  lanes.value = data.items || []
  screen.value = 'lanes'
}

async function addLaneNow() {
  await client.addLane(laneFrom.value, laneTo.value)
  await showLanes()
}

async function savePwd() {
  if (!pwdDraft.value) return
  await client.saveSettings({ password: pwdDraft.value, notifyPush: notifyOn.value, quietHours: quietOn.value })
  pwdDraft.value = ''
}

function lightClass(v: string) {
  if (v === 'expired' || v === 'd1') return 'bad'
  if (v === 'd7' || v === 'd30') return 'warn'
  return 'ok'
}

async function submitKycNow() {
  await run(async () => {
    const items = requiredKyc.value.map((kind) => ({
      kind,
      fileUrl: kycFiles.value[kind] || KYC_FILE[kind] || '/kyc/id.svg',
      expiresAt: kind === 'green_card' ? kycGreenExp.value : '',
      extra:
        kind === 'green_card'
          ? { no: kycGreenNo.value, expires: kycGreenExp.value, customs: kycCustoms.value }
          : {},
    }))
    await client.submitKyc({
      kind: shipper.value ? kycKind.value : 'driver',
      company: kycCompany.value,
      legalName: kycLegal.value,
      idNumber: kycIdNo.value,
      items,
    })
    applyKyc(await client.kyc())
    me.value = await client.me()
  })
}

function pickKycFile(kind: string, url: string) {
  kycFiles.value = { ...kycFiles.value, [kind]: url }
}

function onKycFile(kind: string, e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  pickKycFile(kind, URL.createObjectURL(file))
}

async function reportNow(id: string) {
  await run(async () => {
    await client.reportPort(id, '/covers/building.svg', reportStatus.value, reportWait.value)
    reported.value = id
  })
}

function logout() {
  setAppToken(null)
  router.push('/')
}

function back() {
  screen.value = 'main'
}

function goTab(i: number) {
  tab.value = i
  screen.value = 'main'
  pubStep.value = 1
}
</script>

<template>
  <div class="page">
    <WorkNav
      :role="role"
      :name="me?.name"
      :kyc="me?.kycStatus"
      :credit="me?.credit"
      :unread="unread"
      :synced-at="syncedAt"
      :show-back="screen !== 'main'"
      :title="title"
      @back="back"
      @notes="showNotes"
    />
    <div class="workbar">
      <div class="wrap bar">
        <nav class="tabs">
          <button v-for="(item, i) in tabs" :key="item.key" type="button" :class="{ on: tab === i && screen === 'main' }" @click="goTab(i)">
            {{ t(item.key) }}
          </button>
        </nav>
        <div class="meta">
          <span>{{ tf('work.liveCount', { n: liveOrders.length }) }}</span>
          <span>{{ tf('work.boardCount', { n: loads.length }) }}</span>
        </div>
      </div>
    </div>
    <p v-if="err" class="wrap err">{{ err }}</p>
    <div v-if="me?.kycStatus && me.kycStatus !== 'approved'" class="note-banner-wrap">
      <div class="note-banner">
        <span>{{ kycLabel(me.kycStatus) }} · {{ t('app.submitKyc') }}</span>
        <button type="button" class="btn btn-line btn-sm" @click="showKyc">{{ t('app.kyc') }}</button>
      </div>
    </div>

    <div class="wrap stage">
      <main v-if="screen === 'main' && tab === 0" class="pad desk">
        <section class="hero">
          <div class="hero-copy">
            <small>{{ shipper ? t('role.shipper') : t('role.driver') }}</small>
            <h1>{{ party(me?.name) || (shipper ? t('role.shipper') : t('role.driver')) }}</h1>
          </div>
          <div class="kpi">
            <div><b>{{ matchingLoads.length }}</b><span>{{ t('work.matching') }}</span></div>
            <div><b>{{ liveOrders.length }}</b><span>{{ t('work.liveOrders') }}</span></div>
            <div><b>{{ unread }}</b><span>{{ t('work.inbox') }}</span></div>
            <div><b>{{ deposit?.available ?? '—' }}</b><span>{{ t('app.deposit') }}</span></div>
            <div><b>{{ me?.credit ?? 0 }}</b><span>{{ t('app.credit') }}</span></div>
          </div>
        </section>
        <div class="entry-row">
          <button v-if="shipper" class="entry main" type="button" :disabled="!kycOk" @click="screen = 'publish'; pubStep = 1">
            {{ t('app.publish') }}
          </button>
          <button v-else class="entry main" type="button" @click="goTab(1)">{{ t('tab.find') }}</button>
          <button class="entry" type="button" @click="openEstimate">{{ t('app.estimate') }}</button>
          <button class="entry" type="button" @click="showPorts">{{ t('app.ports') }}</button>
        </div>
        <div class="desk-grid">
          <div>
            <div v-if="!shipper && liveInvites.length" class="block">
              <p class="label">{{ t('app.invites') }}</p>
              <article v-for="inv in liveInvites.slice(0, 3)" :key="inv.id" class="card invite">
                <div>
                  <strong class="lane-b"><Flag :code="inv.load?.originCountry" />{{ place(inv.load?.origin) }} <span>→</span> <Flag :code="inv.load?.destCountry" />{{ place(inv.load?.dest) }}</strong>
                  <p>{{ cargo(inv.load?.cargoName) }} · {{ t('work.invitePending') }} · {{ phrase(inv.message) || t('app.inviteLeft') }}</p>
                </div>
                <div class="acts tight">
                  <button class="btn btn-green" :disabled="busy || !kycOk" @click="run(() => client.replyInvite(inv.id, true))">{{ t('app.accept') }}</button>
                  <small class="invite-left">{{ inviteLeft(inv) }}</small>
                  <button class="btn btn-line" :disabled="busy" @click="run(() => client.replyInvite(inv.id, false))">{{ t('app.decline') }}</button>
                </div>
              </article>
            </div>
            <div class="label-row">
              <p class="label">{{ shipper ? t('work.myLoads') : t('work.recommended') }}</p>
              <button class="link" type="button" @click="goTab(1)">{{ t('work.seeAll') }}</button>
            </div>
            <div class="card-stack">
              <WorkLoadCard v-for="x in homeLoadsPager.items" :key="x.id" :item="x" @click="openLoad(x.id)" />
              <p v-if="!homeLoads.length" class="muted empty">{{ t('common.empty') }}</p>
              <Pager v-model:page="homeLoadsPager.page" :pages="homeLoadsPager.pages" :total="homeLoadsPager.total" :size="homeLoadsPager.size" />
            </div>
            <div v-if="liveOrders.length" class="block">
              <div class="label-row">
                <p class="label">{{ t('work.liveOrders') }}</p>
                <button class="link" type="button" @click="goTab(2)">{{ t('work.seeAll') }}</button>
              </div>
              <article v-for="x in liveOrders.slice(0, 4)" :key="x.id" class="card order-mini" @click="openOrder(x.id)">
                <div>
                  <strong class="lane-b"><Flag :code="x.load?.originCountry" />{{ place(x.load?.origin) }} <span>→</span> <Flag :code="x.load?.destCountry" />{{ place(x.load?.dest) }}</strong>
                  <p>{{ cargo(x.load?.cargoName) }} · {{ party(shipper ? x.driver?.name : x.shipper?.name) }}</p>
                </div>
                <span class="pill" :class="tone(x.status)">{{ orderStatus(x.status) }}</span>
                <em>{{ money(x.freight) }}</em>
              </article>
            </div>
          </div>
          <aside>
            <p class="label">{{ t('app.quick') }}</p>
            <div class="grid">
              <button class="tile" type="button" @click="showDeposit">
                <AppGlyph name="wallet" /><span>{{ t('app.deposit') }}</span>
                <small>{{ deposit?.available ?? 0 }}</small>
              </button>
              <button class="tile" type="button" @click="showKyc">
                <AppGlyph name="shield" /><span>{{ t('app.kyc') }}</span>
              </button>
              <button class="tile" type="button" @click="showCredit">
                <AppGlyph name="star" /><span>{{ t('app.credit') }}</span>
              </button>
              <button class="tile" type="button" @click="showNotes">
                <AppGlyph name="chat" /><span>{{ t('app.notes') }}</span>
                <small v-if="unread">{{ unread }}</small>
              </button>
            </div>
            <p class="label">{{ t('app.ports') }}</p>
            <article v-for="p in homePorts" :key="p.id" class="card port-mini" @click="showPorts">
              <div>
                <strong>{{ portName(p) }}</strong>
                <p>{{ p.stale ? t('app.stale') : portLabel(p.status) }} · {{ waitMin(p.waitMin) }}</p>
              </div>
              <span class="pill" :class="tone(p.stale ? 'stale' : p.status)">{{ p.stale ? t('app.stale') : portLabel(p.status) }}</span>
            </article>
            <p class="label">{{ t('app.notes') }}</p>
            <article v-for="n in homeNotes" :key="n.id" class="card note-mini" :class="{ unread: !n.read }" @click="showNotes">
              <strong>{{ phrase(n.title) }}</strong>
              <p>{{ phrase(n.body) }}</p>
            </article>
          </aside>
        </div>
      </main>

      <main v-else-if="screen === 'main' && tab === 1" class="pad">
        <div class="filters">
          <button type="button" :class="{ on: !filter }" @click="filter = ''">{{ t('app.filterAll') }}</button>
          <button type="button" :class="{ on: filter === 'bid' }" @click="filter = 'bid'">{{ t('mode.bid') }}</button>
          <button type="button" :class="{ on: filter === 'grab' }" @click="filter = 'grab'">{{ t('mode.grab') }}</button>
          <button type="button" :class="{ on: filter === 'assign' }" @click="filter = 'assign'">{{ t('mode.assign') }}</button>
        </div>
        <div v-if="shipper" class="filters wrap-chips">
          <button type="button" :class="{ on: !statusFilter }" @click="statusFilter = ''">{{ t('app.filterAll') }} {{ loads.length }}</button>
          <button
            v-for="st in LOAD_STATUSES"
            v-show="statusCounts[st]"
            :key="st"
            type="button"
            :class="{ on: statusFilter === st }"
            @click="statusFilter = st"
          >
            {{ loadStatus(st) }} {{ statusCounts[st] }}
          </button>
        </div>
        <div class="lane-filters">
          <select v-model="loadFrom" class="field">
            <option value="">{{ t('search.from') }}</option>
            <option v-for="city in ORIGIN_CITIES" :key="'o'+city" :value="city">{{ place(city) }}</option>
          </select>
          <select v-model="loadTo" class="field">
            <option value="">{{ t('search.to') }}</option>
            <option v-for="city in DEST_CITIES" :key="'d'+city" :value="city">{{ place(city) }}</option>
          </select>
          <select v-model="cargoFilter" class="field">
            <option value="">{{ t('col.cargo') }}</option>
            <option v-for="name in CARGO_OPTIONS" :key="name" :value="name">{{ cargo(name) }}</option>
          </select>
          <select v-model="truckFilter" class="field">
            <option value="">{{ t('app.truck') }}</option>
            <option value="13.5">13.5m / 32t</option>
            <option value="17.5">17.5m / 40t</option>
          </select>
          <button type="button" class="btn btn-line btn-sm" :class="{ on: loadSort === 'new' }" @click="loadSort = 'new'">{{ t('app.sortNew') }}</button>
          <button type="button" class="btn btn-line btn-sm" :class="{ on: loadSort === 'price' }" @click="loadSort = 'price'">{{ t('app.sortPrice') }}</button>
        </div>
        <div class="card-stack board-cards">
          <WorkLoadCard
            v-for="x in loadsPager.items"
            :key="x.id"
            :item="x"
            @click="openLoad(x.id)"
          />
          <p v-if="!visibleLoads.length" class="muted empty">{{ t('common.empty') }}</p>
          <Pager v-model:page="loadsPager.page" :pages="loadsPager.pages" :total="loadsPager.total" :size="loadsPager.size" />
        </div>
      </main>

      <main v-else-if="screen === 'main' && tab === 2" class="pad orders">
        <div class="filters">
          <button type="button" :class="{ on: !orderFilter }" @click="orderFilter = ''">{{ t('app.filterAll') }}</button>
          <button type="button" :class="{ on: orderFilter === 'live' }" @click="orderFilter = 'live'">{{ t('app.orderLive') }}</button>
          <button type="button" :class="{ on: orderFilter === 'wait_load' }" @click="orderFilter = 'wait_load'">{{ orderStatus('wait_load') }}</button>
          <button type="button" :class="{ on: orderFilter === 'in_transit' }" @click="orderFilter = 'in_transit'">{{ orderStatus('in_transit') }}</button>
          <button type="button" :class="{ on: orderFilter === 'completed' }" @click="orderFilter = 'completed'">{{ orderStatus('completed') }}</button>
        </div>
        <div class="board">
          <table>
            <thead>
              <tr>
                <th>{{ t('app.orderId') }}</th>
                <th>{{ t('col.lane') }}</th>
                <th>{{ t('col.cargo') }}</th>
                <th>{{ t('col.status') }}</th>
                <th class="num">{{ t('app.freight') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="x in ordersPager.items" :key="x.id" @click="openOrder(x.id)">
                <td class="id">{{ x.id }}</td>
                <td>
                  <b class="lane-b"><Flag :code="x.load?.originCountry" />{{ place(x.load?.origin) }} <span>→</span> <Flag :code="x.load?.destCountry" />{{ place(x.load?.dest) }}</b>
                  <small>{{ party(shipper ? x.driver?.name : x.shipper?.name) }}</small>
                </td>
                <td>{{ cargo(x.load?.cargoName) }} · {{ x.load?.weightT || '—' }}t</td>
                <td><span class="pill" :class="tone(x.status)">{{ orderStatus(x.status) }}</span></td>
                <td class="num">{{ money(x.freight) }}</td>
                <td class="next">{{ nextHint(x) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!visibleOrders.length" class="muted empty">{{ t('app.noOrders') }}</p>
          <Pager v-model:page="ordersPager.page" :pages="ordersPager.pages" :total="ordersPager.total" :size="ordersPager.size" />
        </div>
      </main>

      <main v-else-if="screen === 'main' && tab === 3" class="pad chats">
        <div class="inbox">
          <AppChatRow v-for="c in chatsPager.items" :key="c.id" :item="c" @click="openConv(c.id)" />
          <p v-if="!chats.length" class="muted empty">{{ t('app.noChats') }}</p>
          <Pager v-model:page="chatsPager.page" :pages="chatsPager.pages" :total="chatsPager.total" :size="chatsPager.size" />
        </div>
      </main>

      <main v-else-if="screen === 'main' && tab === 4" class="pad">
        <section class="hero">
          <div class="hero-copy">
            <small>{{ shipper ? t('role.shipper') : t('role.driver') }}</small>
            <h1>{{ party(me?.name) }}</h1>
            <p>{{ me?.phone }}</p>
          </div>
          <div class="kpi">
            <div><b>{{ kycLabel(me?.kycStatus) }}</b><span>{{ t('app.kyc') }}</span></div>
            <div><b>{{ me?.credit ?? 0 }}</b><span>{{ t('app.credit') }}</span></div>
            <div><b>{{ deposit?.available ?? 0 }}</b><span>{{ t('app.deposit') }}</span></div>
            <div><b>{{ vehicles.length || notes.length }}</b><span>{{ shipper ? t('app.notes') : t('app.vehicles') }}</span></div>
          </div>
        </section>
        <div class="account-grid">
          <button class="tile" type="button" @click="showDeposit">
            <AppGlyph name="wallet" /><span>{{ t('app.deposit') }}</span>
            <small>{{ deposit?.available ?? 0 }} / {{ deposit?.frozen ?? 0 }}</small>
          </button>
          <button class="tile" type="button" @click="showKyc">
            <AppGlyph name="shield" /><span>{{ t('app.kyc') }}</span>
            <small>{{ kycLabel(me?.kycStatus) }}</small>
          </button>
          <button v-if="!shipper" class="tile" type="button" @click="showVehicles">
            <AppGlyph name="loads" /><span>{{ t('app.vehicles') }}</span>
            <small>{{ vehicles.length }}</small>
          </button>
          <button v-if="!shipper" class="tile" type="button" @click="showLanes">
            <AppGlyph name="flag" /><span>{{ t('app.lanes') }}</span>
            <small>{{ lanes.length }}</small>
          </button>
          <button class="tile" type="button" @click="showCredit">
            <AppGlyph name="star" /><span>{{ t('app.credit') }}</span>
            <small>{{ me?.credit ?? 0 }}</small>
          </button>
          <button class="tile" type="button" @click="showPorts">
            <AppGlyph name="flag" /><span>{{ t('app.ports') }}</span>
            <small>{{ ports.length }}</small>
          </button>
          <button class="tile" type="button" @click="openEstimate">
            <AppGlyph name="calc" /><span>{{ t('app.estimate') }}</span>
          </button>
          <button class="tile" type="button" @click="screen = 'settings'">
            <AppGlyph name="gear" /><span>{{ t('app.settings') }}</span>
          </button>
        </div>
        <button class="row danger" type="button" @click="logout">{{ t('dash.logout') }}</button>
      </main>

      <main v-else-if="screen === 'load' && detail" class="pad">
        <div class="hero compact">
          <h2 class="lane-b"><Flag :code="detail.originCountry" />{{ place(detail.origin) }} <span>→</span> <Flag :code="detail.destCountry" />{{ place(detail.dest) }}</h2>
          <p>{{ countryName(detail.originCountry) }} → {{ countryName(detail.destCountry) }} · {{ detail.loadTime }}</p>
          <p><b>{{ money(detail.expectPrice || detail.grabPrice) }}</b> · {{ modeLabel(detail.matchMode) }} <span v-if="detail.bidDeadline">· {{ fmtWhen(detail.bidDeadline) }}</span></p>
        </div>
        <div class="kv-grid">
          <div><span>{{ t('col.cargo') }}</span><b>{{ cargo(detail.cargoName) }}</b></div>
          <div><span>{{ t('app.weight') }}</span><b>{{ detail.weightT }} t</b></div>
          <div><span>{{ t('app.volume') }}</span><b>{{ detail.volumeM3 || '—' }} m³</b></div>
          <div><span>{{ t('app.packing') }}</span><b>{{ packing(detail.packing) }}</b></div>
          <div><span>{{ t('app.truck') }}</span><b>{{ detail.truckLength || 13.5 }}m / {{ detail.truckTonnage || 32 }}t</b></div>
          <div><span>{{ cargoClass('general') }}</span><b>{{ cargoClass(detail.cargoClass) }}</b></div>
          <div v-if="detail.shipper?.company || detail.shipper?.name"><span>{{ t('role.shipper') }}</span><b>{{ detail.shipper?.company ? company(detail.shipper.company) : party(detail.shipper?.name) }}</b></div>
          <div v-if="detail.receiverName"><span>{{ t('app.receiver') }}</span><b>{{ entity(detail.receiverName) }} {{ detail.receiverPhone || '' }}</b></div>
        </div>
        <p v-if="detail.remark" class="muted">{{ remarkText(detail.remark) }}</p>
        <div class="acts">
          <template v-if="!shipper && detail.matchMode === 'bid'">
            <label class="inline">{{ t('app.amount') }}
              <input v-model.number="quoteAmt" class="field" type="number" />
            </label>
            <label class="inline">{{ t('app.eta') }}
              <input v-model="quoteEta" class="field" />
            </label>
            <label class="inline">{{ t('app.quoteNote') }}
              <input v-model="quoteNote" class="field" />
            </label>
            <p v-if="detail.lowestQuote" class="muted">{{ t('corr.rate') }} · {{ money(detail.lowestQuote) }}</p>
            <button class="btn btn-green" :disabled="busy || !kycOk" @click="quoteNow">{{ t('app.quote') }}</button>
          </template>
          <button v-if="!shipper && detail.matchMode === 'grab'" class="btn btn-amber" :disabled="busy || !kycOk" @click="grabNow">{{ t('app.grab') }}</button>
          <div v-if="shipper && (detail.holds || []).some((h: any) => h.status === 'pending')" class="hold-box">
            <p>{{ t('app.holdWait') }} · {{ money((detail.holds || []).find((h: any) => h.status === 'pending')?.freight) }}</p>
            <button class="btn btn-green" type="button" :disabled="busy" @click="run(() => client.confirmGrab(detail.id))">{{ t('app.confirmGrab') }}</button>
            <button class="btn btn-line" type="button" :disabled="busy" @click="run(() => client.cancelGrab(detail.id))">{{ t('app.cancelGrab') }}</button>
          </div>
          <button v-if="shipper && detail.matchMode === 'assign'" class="btn btn-navy" type="button" @click="openAssign">{{ t('app.assignPick') }}</button>
          <button v-if="shipper" class="btn btn-line" @click="run(() => client.offline(detail.id))">{{ t('app.offline') }}</button>
          <button v-if="shipper" class="btn btn-line" @click="run(() => client.copyLoad(detail.id))">{{ t('app.copy') }}</button>
          <button class="btn btn-line" @click="openChat(detail.id)">{{ t('app.chat') }}</button>
        </div>
        <div v-if="shipper && sortedQuotes.length" class="filters">
          <button type="button" :class="{ on: quoteSort === 'price' }" @click="quoteSort = 'price'">{{ t('corr.rate') }}</button>
          <button type="button" :class="{ on: quoteSort === 'credit' }" @click="quoteSort = 'credit'">{{ t('app.credit') }}</button>
          <button type="button" :class="{ on: quoteSort === 'truck' }" @click="quoteSort = 'truck'">{{ t('app.truck') }}</button>
        </div>
        <article v-for="q in sortedQuotes" :key="q.id" class="card quote-card">
          <div>
            <strong>{{ party(q.driver?.name) || q.driverId }} · {{ money(q.amount) }}</strong>
            <p>
              {{ quoteLabel(q.status) }} · {{ t('app.credit') }} {{ q.driver?.credit }}
              <span v-if="q.driver?.vehicles?.[0]"> · {{ brand(q.driver.vehicles[0].brand) || t('app.truck') }} {{ q.driver.vehicles[0].lengthM }}m / {{ q.driver.vehicles[0].tonnage }}t</span>
            </p>
            <p v-if="q.eta || q.remark" class="muted">{{ q.eta }} {{ phrase(q.remark) }}</p>
          </div>
          <button v-if="shipper" class="btn btn-green" @click="confirmQuote(q.id)">{{ armQuote === q.id ? t('app.confirmDeal') : t('app.choose') }}</button>
        </article>
      </main>

      <main v-else-if="screen === 'order' && detail" class="order-screen">
        <div class="order-scroll">
          <section class="route-card">
            <div class="city">
              <em>{{ t('app.pick') }}</em>
              <div>
                <b class="lane-b"><Flag :code="detail.load?.originCountry" />{{ place(detail.load?.origin) }}</b>
                <p>{{ countryName(detail.load?.originCountry) }}</p>
              </div>
            </div>
            <div class="city">
              <em class="drop">{{ t('app.drop') }}</em>
              <div>
                <b class="lane-b"><Flag :code="detail.load?.destCountry" />{{ place(detail.load?.dest) }}</b>
                <p>{{ countryName(detail.load?.destCountry) }}</p>
              </div>
            </div>
            <footer>
              <span class="pill" :class="tone(detail.status)">{{ orderStatus(detail.status) }}</span>
              <strong>{{ money(detail.freight) }}</strong>
            </footer>
          </section>
          <div class="party">
            <div>
              <small>{{ t('role.driver') }}</small>
              <b>{{ party(detail.driver?.name) || '—' }}</b>
              <p v-if="shipper && peerPhone(detail)">{{ peerPhone(detail) }}</p>
              <button v-if="shipper && Number(me?.credit || 0) >= 120 && detail.driver?.id && !unlockedPhone" class="link" type="button" @click="unlockPeer">{{ t('app.unlockPhone') }}</button>
            </div>
            <div>
              <small>{{ t('role.shipper') }}</small>
              <b>{{ party(detail.shipper?.name) || '—' }}</b>
              <p v-if="!shipper && peerPhone(detail)">{{ peerPhone(detail) }}</p>
            </div>
          </div>
          <div class="acts">
            <button class="btn btn-line" type="button" @click="locOn = !locOn">{{ locOn ? t('app.locOn') : t('app.locOff') }}</button>
            <a class="btn btn-line" :href="navHref('amap')" target="_blank" rel="noreferrer">{{ t('app.navAmap') }}</a>
            <a class="btn btn-line" :href="navHref('yandex')" target="_blank" rel="noreferrer">{{ t('app.navYandex') }}</a>
          </div>
          <ol class="steps">
            <li v-for="s in ORDER_STEPS" :key="s" :class="{ on: orderStepOn(detail.status, s), cur: detail.status === s }">
              <i />
              <span>{{ orderStatus(s) }}</span>
            </li>
          </ol>
          <div class="map">
            <OrderTrackMap
              :route="mapRoute"
              :track="detail.track || []"
              :live="locOn && detail.status === 'in_transit'"
              :origin="place(detail.load?.origin)"
              :dest="place(detail.load?.dest)"
            />
          </div>
          <button class="row" type="button" @click="screen = 'waybill'">{{ t('app.waybill') }} · {{ detail.waybill?.signed ? t('app.signed') : t('app.unsigned') }}</button>
        </div>
        <div class="order-dock">
          <button class="dock-chat" type="button" @click="openOrderChat">{{ t('app.chat') }}</button>
          <button
            v-if="orderDock.extra?.kind === 'simulate'"
            class="btn btn-line"
            type="button"
            :disabled="busy"
            @click="run(() => client.simulate(detail.id))"
          >{{ orderDock.extra?.label }}</button>
          <button
            v-if="orderDock.primary"
            class="btn btn-green"
            type="button"
            :disabled="busy"
            @click="actOrderPrimary"
          >{{ orderDock.primary?.label }}</button>
          <button
            v-else-if="orderDock.extra?.kind === 'review'"
            class="btn btn-green"
            type="button"
            :disabled="busy"
            @click="screen = 'review'"
          >{{ orderDock.extra?.label }}</button>
        </div>
      </main>

      <main v-else-if="screen === 'chat'" class="im">
        <div ref="msgBox" class="im-msgs">
          <div
            v-for="m in messages"
            :key="m.id"
            class="bubble"
            :class="{ mine: m.senderId === me?.id }"
          >
            <p>{{ chatLine(m) }}</p>
            <small v-if="sourceLine(m)">{{ t('app.original') }} {{ sourceLine(m) }}</small>
          </div>
        </div>
        <form class="im-bar" @submit.prevent="send">
          <div class="phrases">
            <button type="button" @click="draft = t('phrase.load')">{{ t('phrase.loadShort') }}</button>
            <button type="button" @click="draft = t('phrase.docs')">{{ t('phrase.docsShort') }}</button>
            <button type="button" @click="draft = t('phrase.deposit')">{{ t('phrase.depositShort') }}</button>
          </div>
          <input v-model="draft" class="field" :placeholder="t('app.inputHint')" />
          <button class="send" type="submit" :disabled="!draft.trim()">{{ t('app.send') }}</button>
        </form>
      </main>

      <main v-else-if="screen === 'publish'" class="pad form">
        <ol class="steps-form">
          <li v-for="n in 4" :key="n" :class="{ on: pubStep === n, done: pubStep > n }">{{ t('app.step' + n) }}</li>
        </ol>
        <template v-if="pubStep === 1">
          <div class="form-grid">
          <label>{{ t('search.from') }}
            <select v-model="form.origin" class="field">
              <option v-for="city in ORIGIN_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          <label>{{ t('search.to') }}
            <select v-model="form.dest" class="field">
              <option v-for="city in DEST_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          <label>{{ t('search.date') }} <input v-model="form.loadTime" class="field" /></label>
          </div>
        </template>
        <template v-else-if="pubStep === 2">
          <div class="form-grid">
          <label>{{ t('col.cargo') }}
            <select v-model="form.cargoName" class="field">
              <option v-for="name in CARGO_OPTIONS" :key="name" :value="name">{{ cargo(name) }}</option>
            </select>
          </label>
          <label>{{ t('app.weight') }} <input v-model.number="form.weightT" class="field" type="number" /></label>
          <label>{{ t('app.volume') }} <input v-model.number="form.volumeM3" class="field" type="number" /></label>
          <label>{{ t('app.packing') }}
            <select v-model="form.packing" class="field">
              <option value="pallet">{{ packing('pallet') }}</option>
              <option value="carton">{{ packing('carton') }}</option>
              <option value="crate">{{ packing('crate') }}</option>
              <option value="bulk">{{ packing('bulk') }}</option>
            </select>
          </label>
          <label>{{ cargoClass('general') }}
            <select v-model="form.cargoClass" class="field">
              <option value="general">{{ cargoClass('general') }}</option>
              <option value="reefer">{{ cargoClass('reefer') }}</option>
              <option value="equipment">{{ cargoClass('equipment') }}</option>
            </select>
          </label>
          <label class="check"><input v-model="form.hazmat" type="checkbox" /> {{ t('app.hazmat') }}</label>
          </div>
        </template>
        <template v-else-if="pubStep === 3">
          <div class="form-grid">
          <label>{{ t('app.receiver') }} <input v-model="form.receiver" class="field" /></label>
          <label>{{ t('login.phone') }} <input v-model="form.receiverPhone" class="field" /></label>
          <label>{{ t('app.truck') }}
            <select v-model.number="form.truckLength" class="field">
              <option :value="9.6">9.6 m / 20 t</option>
              <option :value="13.5">13.5 m / 32 t</option>
              <option :value="17.5">17.5 m / 40 t</option>
            </select>
          </label>
          </div>
        </template>
        <template v-else>
          <div class="form-grid">
          <label>{{ t('col.match') }}
            <select v-model="form.matchMode" class="field">
              <option value="bid">{{ t('mode.bid') }}</option>
              <option value="grab">{{ t('mode.grab') }}</option>
              <option value="assign">{{ t('mode.assign') }}</option>
            </select>
          </label>
          <label>{{ t('corr.rate') }} <input v-model.number="form.expectPrice" class="field" type="number" /></label>
          <label>{{ t('app.floor') }} <input class="field" type="number" :value="Math.round(form.expectPrice * 0.85)" readonly /></label>
          <label>{{ t('app.deadline') }} <input v-model.number="form.deadlineHours" class="field" type="number" /></label>
          </div>
        </template>
        <div class="acts tight">
          <button v-if="pubStep > 1" class="btn btn-line" type="button" @click="pubStep -= 1">{{ t('app.prevStep') }}</button>
          <button v-if="pubStep < 4" class="btn btn-navy" type="button" @click="pubStep += 1">{{ t('app.nextStep') }}</button>
          <template v-else>
            <button class="btn btn-line" :disabled="busy" @click="run(() => client.publish({ ...form, photos: [], draft: true, originCountry: 'CN', destCountry: form.dest === '莫斯科' || form.dest === '新西伯利亚' ? 'RU' : 'KZ', floorPrice: Math.round(form.expectPrice * 0.85) }))">{{ t('app.draft') }}</button>
            <button class="btn btn-green" :disabled="busy || !kycOk" @click="publish">{{ t('app.publish') }}</button>
          </template>
        </div>
      </main>

      <main v-else-if="screen === 'estimate'" class="pad form">
        <div class="form-grid">
          <label>{{ t('search.from') }}
            <select v-model="estFrom" class="field">
              <option v-for="city in ORIGIN_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          <label>{{ t('search.to') }}
            <select v-model="estTo" class="field">
              <option v-for="city in DEST_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          <label>{{ t('app.truck') }}
            <select v-model="estTruck" class="field">
              <option value="9.6">9.6 m</option>
              <option value="13.5">13.5 m</option>
              <option value="17.5">17.5 m</option>
            </select>
          </label>
          <label>{{ t('col.cargo') }}
            <select v-model="estCargo" class="field">
              <option value="general">{{ cargoClass('general') }}</option>
              <option value="reefer">{{ cargoClass('reefer') }}</option>
              <option value="equipment">{{ cargoClass('equipment') }}</option>
            </select>
          </label>
          <label>{{ t('app.weight') }}
            <input v-model.number="estWeight" class="field" type="number" min="1" step="0.5" />
          </label>
        </div>
        <button class="btn btn-navy" type="button" @click="runEstimate">{{ t('app.estimate') }}</button>
        <div v-if="estimate" class="hero compact">
          <div class="kpi">
            <div><b>{{ estimate.totalKm }}</b><span>km</span></div>
            <div><b>{{ estimate.hours }}</b><span>h</span></div>
            <div><b>{{ estimate.feeLow }}–{{ estimate.feeHigh }}</b><span>CNY</span></div>
          </div>
          <p class="label">{{ t('app.estSeg') }}</p>
          <div class="seg-bar">
            <i class="dom" :style="{ flex: Math.max(1, Number(estimate.domesticKm) || 1) }" />
            <i class="brd" :style="{ flex: Math.max(1, Number(estimate.borderKm) || 1) }" />
            <i class="for" :style="{ flex: Math.max(1, Number(estimate.foreignKm) || 1) }" />
          </div>
          <p>{{ t('app.domestic') }} {{ estimate.domesticKm }} km · {{ t('app.border') }} {{ estimate.borderKm }} km · {{ t('app.foreign') }} {{ estimate.foreignKm }} km</p>
          <p>{{ t('port.title') }} {{ estimate.port }}</p>
          <b>{{ t('app.refFee') }} {{ estimate.feeLow }} – {{ estimate.feeHigh }} CNY</b>
          <p>{{ t('app.refOnly') }}</p>
        </div>
      </main>

      <main v-else-if="screen === 'ports'" class="pad">
        <p v-if="reported" class="ok">{{ t('port.reported') }}</p>
        <div class="board">
          <table>
            <thead>
              <tr>
                <th>{{ t('port.title') }}</th>
                <th>{{ t('col.status') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in portsPager.items" :key="p.id">
                <td>
                  <b class="lane-b"><Flag v-for="c in String(p.corridor || p.country || '').split('-')" :key="c" :code="c" />{{ portName(p) }}</b>
                  <small>{{ countryName(p.country) }} · {{ Number(p.waitMin) > 0 ? waitMin(p.waitMin) : t('port.noWait') }}</small>
                </td>
                <td><span class="pill" :class="tone(p.stale ? 'stale' : p.status)">{{ p.stale ? t('app.stale') : portLabel(p.status) }}</span></td>
                <td>
                  <template v-if="!shipper">
                    <select v-model="reportStatus" class="field sm">
                      <option value="smooth">{{ portLabel('smooth') }}</option>
                      <option value="slow">{{ portLabel('slow') }}</option>
                      <option value="congested">{{ portLabel('congested') }}</option>
                    </select>
                    <input v-model.number="reportWait" class="field sm" type="number" min="0" />
                    <button class="btn btn-line btn-sm" @click="reportNow(p.id)">{{ t('port.report') }}</button>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-model:page="portsPager.page" :pages="portsPager.pages" :total="portsPager.total" :size="portsPager.size" />
      </main>

      <main v-else-if="screen === 'deposit'" class="pad">
        <div class="hero compact">
          <p>{{ t('app.available') }}</p>
          <b>{{ deposit?.available ?? 0 }}</b>
          <p>{{ t('app.frozen') }} {{ deposit?.frozen ?? 0 }} <span v-if="deposit?.exempt">· {{ t('app.exempt') }}</span></p>
        </div>
        <div class="form-grid">
          <label>{{ t('app.depositAmt') }}
            <input v-model.number="payAmount" class="field" type="number" min="200" step="100" />
          </label>
          <label>{{ t('pay.wechat') }}
            <select v-model="payChannel" class="field">
              <option v-for="ch in payChannels" :key="ch" :value="ch">{{ t('pay.' + ch) }}</option>
            </select>
          </label>
        </div>
        <div class="filters">
          <button v-for="n in [500, 2000, 5000, 10000]" :key="n" type="button" :class="{ on: payAmount === n }" @click="payAmount = n">{{ n }}</button>
        </div>
        <button class="btn btn-green" type="button" :disabled="busy" @click="topupNow()">{{ t('app.topup') }}</button>
        <div v-if="payIntent" class="pay-modal">
          <p class="label">{{ t('app.waitingPay') }} · {{ payLeft }}s</p>
          <PayQr :value="String(payIntent.qr || payIntent.intentId)" :channel="payIntent.channel" />
          <p>{{ t('pay.' + (payIntent.channel || 'wechat')) }} · {{ payIntent.amount }} CNY</p>
          <p class="muted">{{ t('app.paySheet') }}</p>
          <button class="btn btn-green" type="button" @click="confirmPayNow">{{ t('app.paid') }}</button>
        </div>
        <div class="pays">
          <button v-for="ch in payChannels" :key="ch" type="button" class="pay" :disabled="busy" @click="topupNow(ch)">
            <PayMark :name="ch" />
            <span>{{ t('pay.' + ch) }}</span>
          </button>
        </div>
        <p class="label">{{ t('app.ledger') }}</p>
        <div class="board">
          <table>
            <thead>
              <tr>
                <th>{{ t('app.ledger') }}</th>
                <th class="num">{{ t('app.depositAmt') }}</th>
                <th>{{ t('col.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in ledgerPager.items" :key="l.id">
                <td>
                  <div class="payline">
                    <PayMark :name="l.channel || 'wechat'" />
                    <div>
                      <strong>{{ ledgerLabel(l.kind) }}</strong>
                      <p>{{ t('pay.' + (l.channel || 'wechat')) }}</p>
                    </div>
                  </div>
                </td>
                <td class="num">{{ l.amount }}</td>
                <td><span class="pill" :class="tone(l.status === 'pending' ? 'pending' : 'ok')">{{ l.status === 'pending' ? t('ops.kaspi') : ledgerLabel(l.kind) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-model:page="ledgerPager.page" :pages="ledgerPager.pages" :total="ledgerPager.total" :size="ledgerPager.size" />
      </main>

      <main v-else-if="screen === 'kyc'" class="pad">
        <div class="hero compact kyc-hero">
          <div>
            <span class="pill" :class="tone(kyc?.status || me?.kycStatus)">{{ kycLabel(kyc?.status || me?.kycStatus) }}</span>
            <p v-if="kycCompany">{{ company(kycCompany) }}</p>
            <p v-if="kycGreenNo">{{ t('cred.green_card') }} · {{ kycGreenNo }}</p>
          </div>
          <div class="right">
            <b v-if="kyc?.portPoints != null">{{ kyc.portPoints }}</b>
            <p>{{ t('app.portPoints') }}</p>
          </div>
        </div>
        <div class="form-grid">
          <label v-if="shipper">{{ t('app.entityKind') }}
            <select v-model="kycKind" class="field">
              <option value="enterprise">{{ t('kind.enterprise') }}</option>
              <option value="forwarder">{{ t('kind.forwarder') }}</option>
              <option value="personal">{{ t('kind.personal') }}</option>
            </select>
          </label>
          <label v-if="shipper && kycKind !== 'personal'">{{ t('ops.kycCompany') }}
            <input v-model="kycCompany" class="field" />
          </label>
          <label v-if="shipper && kycKind === 'personal'">{{ t('login.name') }}
            <input v-model="kycLegal" class="field" />
          </label>
          <label v-if="shipper && kycKind === 'personal'">{{ t('app.idNo') }}
            <input v-model="kycIdNo" class="field" />
          </label>
          <label v-if="!shipper">{{ t('cred.green_card') }}
            <input v-model="kycGreenNo" class="field" />
          </label>
          <label v-if="!shipper">{{ t('app.greenExpire') }}
            <input v-model="kycGreenExp" class="field" placeholder="2027-06-30" />
          </label>
          <label v-if="!shipper">{{ t('app.customs') }}
            <input v-model="kycCustoms" class="field" />
          </label>
        </div>
        <p v-if="kyc?.frozen" class="err">{{ phrase(kyc.frozenReason) }}</p>
        <div class="docs-grid">
          <article v-for="kind in requiredKyc" :key="kind" class="doc-row">
            <KycPreview :kind="credKind(kind)" :status="credRow(kind)?.status || 'none'" :src="kycFiles[kind] || credRow(kind)?.fileUrl || KYC_FILE[kind]" />
            <div>
              <strong>{{ t('cred.' + credKind(kind)) }}</strong>
              <p>{{ kycLabel(credRow(kind)?.status || 'none') }}</p>
              <label class="file-pick">{{ t('app.filePick') }}
                <input type="file" accept="image/*,.pdf" @change="onKycFile(kind, $event)" />
              </label>
            </div>
            <em class="lamp" :class="lightClass(credRow(kind)?.light || (credRow(kind)?.status === 'approved' ? 'ok' : 'warn'))">●</em>
          </article>
        </div>
        <button class="btn btn-green" :disabled="busy" @click="submitKycNow">{{ t('app.submitKyc') }}</button>
      </main>

      <main v-else-if="screen === 'credit'" class="pad">
        <div class="hero compact">
          <b>{{ credit?.user?.credit ?? me?.credit }}</b>
          <p>{{ t('app.level') }} {{ credit?.level || 'A' }} · {{ t('app.ontime') }} {{ Math.round((credit?.ontime || 0) * 100) }}% · {{ t('app.complaints') }} {{ credit?.complaints ?? 0 }}</p>
        </div>
        <article v-for="(r, i) in credit?.records || []" :key="i" class="card">
          <div>
            <strong>{{ t('credit.' + r.reason) }}</strong>
            <p>{{ r.orderId }}</p>
          </div>
          <em>{{ r.delta }}</em>
        </article>
      </main>

      <main v-else-if="screen === 'waybill' && detail" class="pad waybill-print">
        <div class="wb-head">
          <BrandMark />
          <div>
            <p class="label">{{ t('app.waybill') }}</p>
            <h2>{{ detail.waybill?.id || detail.id }}</h2>
          </div>
          <span class="stamp" :class="{ on: detail.waybill?.signed }">{{ detail.waybill?.signed ? t('app.signedOk') : t('app.unsigned') }}</span>
        </div>
        <h2 class="lane-b"><Flag :code="detail.load?.originCountry" />{{ place(detail.load?.origin) }} <span>→</span> <Flag :code="detail.load?.destCountry" />{{ place(detail.load?.dest) }}</h2>
        <dl class="sheet">
          <div><dt>{{ t('role.shipper') }}</dt><dd>{{ party(detail.shipper?.name) || '—' }}</dd></div>
          <div><dt>{{ t('role.driver') }}</dt><dd>{{ party(detail.driver?.name) || '—' }}</dd></div>
          <div><dt>{{ t('app.freight') }}</dt><dd>{{ money(detail.freight) }}</dd></div>
          <div><dt>{{ t('app.deposit') }}</dt><dd class="dep"><span>¥200</span><PayMark name="wechat" /><PayMark name="alipay" /><PayMark name="unionpay" /><PayMark name="kaspi" /></dd></div>
          <div><dt>{{ t('app.signed') }}</dt><dd>{{ detail.waybill?.signed ? t('app.signedOk') : t('app.unsigned') }}</dd></div>
        </dl>
        <div class="photos" v-if="detail.waybill?.loadPhoto || detail.waybill?.deliverPhoto">
          <figure v-if="detail.waybill?.loadPhoto"><img :src="detail.waybill.loadPhoto" alt="" /><figcaption>{{ t('app.loaded') }}</figcaption></figure>
          <figure v-if="detail.waybill?.deliverPhoto"><img :src="detail.waybill.deliverPhoto" alt="" /><figcaption>{{ t('app.dropped') }}</figcaption></figure>
        </div>
        <p class="label">{{ t('app.signPad') }}</p>
        <canvas class="sign" width="520" height="140" @mousedown="onSign" @mousemove="onSign" @mouseup="endSign" />
        <img v-if="detail.waybill?.signData" class="sign-img" :src="detail.waybill.signData" alt="" />
        <div class="acts">
          <button class="btn btn-line" type="button" @click="clearSign">{{ t('app.clearSign') }}</button>
          <button class="btn btn-line" type="button" @click="printWaybill">{{ t('app.print') }}</button>
          <button v-if="shipper && !detail.waybill?.signed" class="btn btn-green" type="button" @click="signNow">{{ t('app.sign') }}</button>
        </div>
      </main>

      <main v-else-if="screen === 'review'" class="pad form">
        <h2>{{ t('app.review') }}</h2>
        <div class="stars">
          <button v-for="n in 5" :key="n" type="button" :class="{ on: stars >= n }" @click="stars = n">★</button>
        </div>
        <div class="filters">
          <button type="button" :class="{ on: reviewTags.includes('on_time') }" @click="toggleTag('on_time')">{{ t('review.onTime') }}</button>
          <button type="button" :class="{ on: reviewTags.includes('truck') }" @click="toggleTag('truck')">{{ t('review.truck') }}</button>
          <button type="button" :class="{ on: reviewTags.includes('clear') }" @click="toggleTag('clear')">{{ t('review.clear') }}</button>
        </div>
        <textarea v-model="reviewComment" class="field" rows="3" />
        <button class="btn btn-green" type="button" :disabled="busy || !detail?.id" @click="submitReview">{{ t('app.review') }}</button>
      </main>

      <main v-else-if="screen === 'quotes'" class="pad">
        <article v-for="q in detail?.quotes || []" :key="q.id" class="card">
          <div>
            <strong>{{ party(q.driver?.name) || q.driverId }} · {{ money(q.amount) }}</strong>
            <p>{{ quoteLabel(q.status) }} · {{ t('app.credit') }} {{ q.driver?.credit }}</p>
          </div>
          <button v-if="shipper" class="btn btn-green" @click="run(() => client.choose(detail.id, q.id))">{{ t('app.choose') }}</button>
        </article>
        <p v-if="!(detail?.quotes || []).length" class="muted">{{ t('common.empty') }}</p>
      </main>

      <main v-else-if="screen === 'settings'" class="pad">
        <p class="label">{{ t('app.settings') }}</p>
        <div class="lang-switch">
          <button type="button" :class="{ on: locale === 'zh-CN' }" @click="setLocale('zh-CN' as Locale)">中文</button>
          <button type="button" :class="{ on: locale === 'en-US' }" @click="setLocale('en-US' as Locale)">EN</button>
          <button type="button" :class="{ on: locale === 'ru-RU' }" @click="setLocale('ru-RU' as Locale)">RU</button>
        </div>
        <button class="row menu" type="button" @click="notifyOn = !notifyOn; client.saveSettings({ notifyPush: notifyOn })"><span>{{ t('app.notify') }}</span><em>{{ notifyOn ? 'ON' : 'OFF' }}</em></button>
        <button class="row menu" type="button" @click="notifySms = !notifySms; client.saveSettings({ notifySms })"><span>{{ t('app.notifySms') }}</span><em>{{ notifySms ? 'ON' : 'OFF' }}</em></button>
        <button class="row menu" type="button" @click="quietOn = !quietOn; client.saveSettings({ quietHours: quietOn })"><span>{{ t('app.quiet') }}</span><em>{{ quietOn ? 'ON' : 'OFF' }}</em></button>
        <div class="form tight">
          <label>{{ t('app.password') }}
            <input v-model="pwdDraft" class="field" type="password" :placeholder="t('login.pwdHint')" />
          </label>
          <button class="btn btn-line" type="button" @click="savePwd">{{ t('app.password') }}</button>
        </div>
        <a class="row menu" href="/about" target="_blank"><span>{{ t('app.agreements') }}</span><i>›</i></a>
        <button class="row danger" type="button" @click="run(() => client.cancelAccount()).then(logout)">{{ t('app.cancelAcc') }}</button>
        <p class="muted">{{ t('app.cancelAccHint') }}</p>
        <button class="row danger" type="button" @click="logout">{{ t('dash.logout') }}</button>
      </main>

      <main v-else-if="screen === 'assign'" class="pad">
        <p class="label">{{ t('app.assignPick') }}</p>
        <article v-for="d in drivers" :key="d.id" class="card">
          <label class="check">
            <input type="checkbox" :value="d.id" v-model="pickedDrivers" />
            <div>
              <strong>{{ party(d.name) }} · {{ t('app.credit') }} {{ d.credit }}</strong>
              <p>{{ countryName(d.country) }} · {{ (d.vehicles || []).map((v: any) => `${v.plate} ${v.lengthM || ''}m`).join(' / ') || t('app.truck') }}</p>
            </div>
          </label>
        </article>
        <button class="btn btn-green" type="button" :disabled="!pickedDrivers.length" @click="sendAssign">{{ t('app.assignSend') }}</button>
      </main>

      <main v-else-if="screen === 'notes'" class="pad">
        <article v-for="n in notesPager.items" :key="n.id" class="card" :class="{ unread: !n.read }">
          <div>
            <strong>{{ phrase(n.title) }}</strong>
            <p>{{ phrase(n.body) }}</p>
          </div>
          <em>{{ fmtWhen(n.at || n.createdAt) }}</em>
        </article>
        <p v-if="!notes.length" class="muted">{{ t('common.empty') }}</p>
        <Pager v-model:page="notesPager.page" :pages="notesPager.pages" :total="notesPager.total" :size="notesPager.size" />
      </main>

      <main v-else-if="screen === 'vehicles'" class="pad">
        <article v-for="v in vehiclesPager.items" :key="v.id" class="card fleet">
          <div class="plate">{{ v.plate }}</div>
          <div>
            <strong>{{ brand(v.brand) || t('app.truck') }} · {{ bodyLabel(v.bodyType) }}</strong>
            <p>{{ v.lengthM }}m · {{ v.tonnage }}t · {{ t('app.axles') }} {{ v.axles || 6 }} · {{ t('app.diesel') }}</p>
            <p v-if="v.vin">VIN {{ v.vin }}</p>
            <p>{{ t('app.inspect') }} {{ v.inspectExpires || '—' }} · {{ t('app.insurance') }} {{ v.insuranceExpires || '—' }}</p>
          </div>
          <span class="pill ok">{{ t('app.truckActive') }}</span>
        </article>
        <p v-if="!vehicles.length" class="muted">{{ t('common.empty') }}</p>
        <Pager v-model:page="vehiclesPager.page" :pages="vehiclesPager.pages" :total="vehiclesPager.total" :size="vehiclesPager.size" />
        <div class="form">
          <div class="form-grid">
            <label>{{ t('app.addVehicle') }} <input v-model="plateDraft" class="field" /></label>
            <label>{{ t('app.brand') }} <input v-model="truckBrand" class="field" /></label>
            <label>{{ t('app.truck') }}
              <select v-model.number="truckLen" class="field">
                <option :value="9.6">9.6 m</option>
                <option :value="13.5">13.5 m</option>
                <option :value="17.5">17.5 m</option>
              </select>
            </label>
            <label>t <input v-model.number="truckTon" class="field" type="number" /></label>
            <label>{{ t('app.bodyVan') }}
              <select v-model="truckBody" class="field">
                <option value="van">{{ t('app.bodyVan') }}</option>
                <option value="reefer">{{ t('app.bodyReefer') }}</option>
              </select>
            </label>
            <label>{{ t('app.axles') }} <input v-model.number="truckAxles" class="field" type="number" /></label>
            <label>{{ t('app.vin') }} <input v-model="truckVin" class="field" /></label>
            <label>{{ t('app.inspect') }} <input v-model="truckInspect" class="field" /></label>
            <label>{{ t('app.insurance') }} <input v-model="truckInsurance" class="field" /></label>
          </div>
          <button class="btn btn-green" type="button" @click="addTruck">{{ t('app.addVehicle') }}</button>
        </div>
      </main>

      <main v-else-if="screen === 'lanes'" class="pad">
        <article v-for="ln in lanes" :key="ln.id" class="card">
          <strong class="lane-b">{{ place(ln.origin) }} <span>→</span> {{ place(ln.dest) }}</strong>
          <span class="pill ok">ON</span>
        </article>
        <div class="form">
          <div class="form-grid">
          <label>{{ t('search.from') }}
            <select v-model="laneFrom" class="field">
              <option v-for="city in ORIGIN_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          <label>{{ t('search.to') }}
            <select v-model="laneTo" class="field">
              <option v-for="city in DEST_CITIES" :key="city" :value="city">{{ place(city) }}</option>
            </select>
          </label>
          </div>
          <button class="btn btn-green" type="button" @click="addLaneNow">{{ t('app.addLane') }}</button>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--paper);
  color: var(--ink);
}
.workbar {
  position: sticky;
  top: 64px;
  z-index: 40;
  background: rgba(255,255,255,.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line);
}
.workbar .bar {
  min-height: 56px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.workbar .tabs { display: flex; gap: 4px; flex: 1; min-width: 0; overflow: auto; }
.workbar .tabs button {
  border: 0;
  background: transparent;
  height: 40px;
  padding: 0 14px;
  border-radius: 8px;
  font-weight: 650;
  font-size: 15px;
  color: var(--ink-soft);
  white-space: nowrap;
}
.workbar .tabs button.on,
.workbar .tabs button:hover { background: #f4f1ea; color: var(--ink); }
.workbar .meta {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--muted);
  font-size: 13px;
}
.workbar .meta strong { color: var(--navy-2); font-size: 15px; }
.back {
  border: 0;
  background: none;
  font-size: 15px;
  font-weight: 650;
  color: var(--navy);
  white-space: nowrap;
}
.stage { padding: 18px 0 8px; min-width: 0; }
.pad { padding: 0 0 40px; }
.pad h2 { font-size: 26px; letter-spacing: -0.03em; margin: 4px 0 8px; }
.hint { margin: 0 0 12px; color: var(--muted); font-size: 13px; }
.entry-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 22px; }
.entry {
  text-align: center;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 15px;
  font-weight: 650;
  box-shadow: 0 8px 24px rgba(16, 24, 40, 0.04);
}
.entry.main { background: var(--navy); color: #fff; border-color: var(--navy); }
.entry:disabled { opacity: .55; }
.lane-filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px; }
.lane-filters .field { width: auto; min-width: 140px; height: 36px; }
.lane-filters .btn.on { border-color: var(--navy); color: var(--navy); }
.steps-form {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  margin: 0 0 16px;
  padding: 0;
}
.steps-form li {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 650;
  color: var(--muted);
  background: #f7f9fc;
}
.steps-form li.on { background: var(--navy); color: #fff; border-color: var(--navy); }
.steps-form li.done { color: var(--signal-ink); background: var(--signal-soft); border-color: #cde8d8; }
.hero {
  position: relative;
  overflow: hidden;
  color: #1c2430;
  border-radius: 18px;
  padding: 22px 26px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 26px;
  background: #ffffff;
  border: 1px solid #e3e8ef;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.05);
}
.desk-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 24vw);
  gap: 28px;
  align-items: start;
}
.desk-grid aside { position: sticky; top: 140px; }
.card-stack { display: grid; gap: 10px; }
.label-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 4px 0 10px; }
.label-row .label { margin: 0; }
.order-mini, .port-mini, .invite {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  cursor: pointer;
}
.order-mini em { font-style: normal; font-weight: 700; white-space: nowrap; }
.note-mini { cursor: pointer; }
.note-mini p { margin: 4px 0 0; color: #5c6b7a; font-size: 12px; }
.tile small { display: block; margin-top: 4px; color: #5c6b7a; font-size: 12px; }
.wrap-chips { flex-wrap: wrap; }
.board-cards { background: transparent; border: 0; box-shadow: none; overflow: visible; }
.quote-card { align-items: flex-start; }
.hero-copy, .kpi { position: relative; }
.hero.compact { display: block; }
.hero h1 { margin: 4px 0 0; font-size: 28px; font-weight: 650; letter-spacing: -0.03em; }
.hero p, .hero small { color: #5c6b7a; }
.hero small { letter-spacing: 0.08em; font-size: 12px; }
.hero.compact { padding: 28px 26px; }
.hero.compact b { font-size: 42px; letter-spacing: -0.04em; font-variant-numeric: tabular-nums; }
.kpi { display: flex; width: auto; background: transparent; border-radius: 0; padding: 0; }
.kpi div { min-width: 88px; padding: 0 22px; border-right: 1px solid #e3e8ef; }
.kpi div:first-child { padding-left: 0; }
.kpi div:last-child { border: 0; }
.kpi b { display: block; font-size: 26px; font-family: var(--font-num); font-variant-numeric: tabular-nums; }
.kpi span { font-size: 12px; color: #5c6b7a; }
.label {
  margin: 0 0 10px;
  color: #5c6b7a;
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.04em;
}
.stack { display: grid; gap: 8px; }
.board {
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.05);
}
.board table { width: 100%; border-collapse: collapse; }
.board th {
  text-align: left;
  padding: 12px 16px;
  background: #f7f9fc;
  color: #5c6b7a;
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.04em;
  border-bottom: 1px solid #e3e8ef;
}
.board td { padding: 15px 18px; border-top: 1px solid #eef2f6; font-size: 14px; vertical-align: middle; }
.board tbody tr { cursor: pointer; }
.board tbody tr:hover { background: #f7f9fc; }
.lane-b { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; font-weight: 650; }
.lane-b span { color: #8ea0b2; font-weight: 500; }
.dep { display: flex; align-items: center; justify-content: flex-end; gap: 6px; flex-wrap: wrap; }
.board small, .board .id { display: block; margin-top: 3px; color: #5c6b7a; font-size: 12px; font-weight: 500; }
.board .num { text-align: right; font-variant-numeric: tabular-nums; font-weight: 650; white-space: nowrap; color: #1c2430; }
.board .next { color: var(--navy); font-size: 13px; font-weight: 650; white-space: nowrap; }
.board .empty, .inbox .empty { padding: 28px 16px; }
.inbox {
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.05);
}
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.tile:last-child:nth-child(odd) { grid-column: 1 / -1; }
.tile, .row {
  border: 1px solid #e3e8ef;
  background: #ffffff;
  border-radius: 12px;
  padding: 14px 14px;
  text-align: left;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1c2430;
  min-height: 52px;
}
.tile:hover, .row:hover { border-color: #c9d4ea; background: #fff; }
.tile.primary {
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
}
.card {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 16px 18px;
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 14px;
  margin-bottom: 8px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(16, 24, 40, 0.04);
}
.card p, .muted { color: var(--color-secondary); font-size: 13px; margin: 4px 0; }
.card em { font-style: normal; font-weight: 700; color: var(--color-primary); font-family: var(--font-num); }
.right { display: grid; justify-items: end; gap: 6px; }
.acts { display: grid; gap: 8px; margin: 12px 0; }
.acts.tight { grid-auto-flow: column; }
.me {
  background: #ffffff;
  border: 1px solid #e3e8ef;
  color: #1c2430;
  border-radius: 18px;
  padding: 22px 24px;
  margin-bottom: 14px;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.05);
}
.me b { font-size: 26px; letter-spacing: -0.03em; }
.row { width: 100%; margin-bottom: 8px; }
.row.danger { color: var(--color-danger); }
.err { color: var(--color-danger); padding: 8px 0; font-size: 12px; text-align: center; }
.note-banner-wrap {
  display: flex;
  justify-content: center;
  padding: 12px 16px 0;
}
.note-banner {
  margin: 0;
  width: auto;
  max-width: min(720px, 100%);
  padding: 10px 18px;
  border-radius: 12px;
  background: #fff8e8;
  border: 1px solid #e6d7b8;
  color: #5c4a32;
  font-size: 13px;
  display: inline-flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
  margin-bottom: 14px;
}
.form-grid label { display: grid; gap: 6px; font-size: 13px; color: #5c6b7a; font-weight: 650; }
.account-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.account-grid .tile {
  flex-direction: column;
  align-items: flex-start;
  min-height: 96px;
  gap: 6px;
}
.kv-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px 16px;
  margin: 0 0 16px;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 14px;
}
.kv-grid div { display: grid; gap: 4px; }
.kv-grid span { color: #5c6b7a; font-size: 12px; }
.kv-grid b { font-size: 15px; }
.docs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.doc-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 14px;
}
.doc-row > div { flex: 1; min-width: 0; }
.file-pick { display: grid; gap: 6px; font-size: 12px; color: #5c6b7a; }
.file-pick input { font-size: 12px; }
.field.sm { height: 32px; min-width: 88px; width: auto; }
.ok { color: var(--color-success); }
.sheet { margin: 12px 0; }
.sheet div { display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-top: 1px solid #e4e0d6; font-size: 13px; }
.sheet dt { color: #6b7280; }
.sheet dd { margin: 0; font-weight: 650; }
.stars { font-size: 22px; letter-spacing: 4px; color: #8d6a32; }
.phrases { display: flex; gap: 6px; grid-column: 1 / -1; overflow: auto; }
.phrases button { border: 1px solid #e4e0d6; background: #fff; border-radius: 99px; font-size: 11px; padding: 4px 8px; white-space: nowrap; }
.im-bar { grid-template-columns: 1fr auto; }
.im-bar .phrases { grid-column: 1 / -1; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.filters button {
  border: 1px solid #e3e8ef;
  background: #ffffff;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  white-space: nowrap;
  color: #3d4a5c;
}
.filters button.on { background: var(--navy); color: #fff; border-color: var(--navy); }
.chats { padding-top: 8px; }
.pad.chats { padding-left: 16px; padding-right: 16px; }
.order-screen, .im {
  min-height: 0;
  display: grid;
  grid-template-rows: 1fr auto;
}
.im {
  width: min(920px, calc(100% - 64px));
  height: calc(100% - 36px);
  margin: 18px auto;
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 18px 44px rgba(16, 24, 40, 0.06);
}
.order-scroll { overflow: auto; padding: 16px 16px 12px; }
.route-card, .party {
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  padding: 16px 18px;
  margin-bottom: 12px;
  box-shadow: 0 10px 28px rgba(16, 24, 40, 0.04);
}
.route-card .city { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 12px; }
.route-card em {
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  font-style: normal;
  font-size: 11px;
  font-weight: 700;
  background: #e7f1ea;
  color: #2f6b4f;
}
.route-card em.drop { background: var(--navy); color: #fff; }
.route-card b { display: block; font-size: 18px; }
.route-card p { margin: 2px 0 0; color: var(--color-secondary); font-size: 12px; }
.route-card footer { display: flex; justify-content: space-between; align-items: center; }
.route-card strong { font-family: var(--font-num); font-size: 20px; color: #1c2430; }
.party { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.party small { display: block; color: #8a958c; font-size: 11px; letter-spacing: 0.08em; }
.party b { font-size: 14px; }
.steps {
  list-style: none;
  display: flex;
  margin: 4px 0 12px;
  padding: 12px 8px;
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  overflow-x: auto;
}
.steps li {
  flex: 1;
  min-width: 64px;
  display: grid;
  justify-items: center;
  gap: 6px;
  position: relative;
  color: #8a958c;
  font-size: 11px;
}
.steps li:not(:last-child)::after {
  content: "";
  position: absolute;
  top: 7px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e4e0d6;
}
.steps li i {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #e4e0d6;
  z-index: 1;
}
.steps li.on { color: var(--navy); font-weight: 650; }
.steps li.on i { background: var(--navy); }
.steps li.on:not(:last-child)::after { background: var(--navy); }
.steps li.cur i { box-shadow: 0 0 0 4px rgba(47, 107, 79, 0.18); }
.order-dock {
  display: flex;
  gap: 8px;
  padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1px solid #e3e8ef;
}
.dock-chat, .order-dock .btn { flex: 1; }
.dock-chat {
  border: 1px solid #e3e8ef;
  background: #fff;
  border-radius: 10px;
  font-weight: 650;
}
.im-msgs {
  overflow: auto;
  padding: 16px 14px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.bubble {
  max-width: 78%;
  align-self: flex-start;
  background: #f4f7fb;
  border: 1px solid #e3e8ef;
  border-radius: 16px 16px 16px 4px;
  padding: 10px 12px;
}
.bubble p { margin: 0; font-size: 15px; line-height: 1.45; }
.bubble small { display: block; margin-top: 4px; color: var(--color-secondary); font-size: 11px; }
.bubble.mine {
  align-self: flex-end;
  background: var(--navy);
  color: #fff;
  border-color: var(--navy);
  border-radius: 16px 16px 4px 16px;
}
.bubble.mine small { color: rgba(255,255,255,.72); }
.im-bar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1px solid #e3e8ef;
}
.im-bar .field { border-radius: 22px; padding: 10px 14px; }
.send {
  border: 0;
  background: var(--navy);
  color: #fff;
  border-radius: 22px;
  padding: 0 16px;
  font-weight: 700;
}
.send:disabled { opacity: 0.4; }
.map {
  height: 240px;
  margin: 12px 0;
  border-radius: 12px;
  overflow: hidden;
}
.tl { margin: 0; padding: 0 0 0 18px; color: var(--color-secondary); font-size: 13px; }
.form {
  display: grid;
  gap: 12px;
  max-width: 920px;
  background: #ffffff;
  border: 1px solid #e3e8ef;
  border-radius: 18px;
  padding: 22px 24px 26px;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.05);
}
.field {
  border: 1px solid #e3e8ef;
  border-radius: 10px;
  height: 42px;
  background: #fff;
}
.field:focus { outline: 2px solid rgba(31, 75, 153, 0.16); border-color: var(--navy); }
.pays { display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 12px; width: 100%; margin: 16px 0 18px; }
.pay {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 56px;
  padding: 0 14px;
  border: 1px solid #e3e8ef;
  border-radius: 12px;
  background: #fff;
  font-weight: 650;
  color: #1c2430;
}
.pay:hover { border-color: #c5d4ee; }
.payline { display: flex; align-items: center; gap: 10px; }
.payline p { margin: 2px 0 0; }
.pname { display: flex; align-items: center; gap: 6px; }
.menu i, .menu em { margin-left: auto; color: #8ea0b2; font-style: normal; font-size: 18px; }
.menu em { font-size: 12px; font-weight: 700; color: var(--navy); }
.check { display: flex; align-items: center; gap: 8px; font-weight: 650; }
.invite-left { color: #5c6b7a; font-size: 12px; }
.form label, .inline { display: grid; gap: 6px; font-size: 13px; color: var(--color-secondary); }
.btn { height: 36px; padding: 0 14px; font-size: 13px; }
.bell {
  position: relative; border: 1px solid var(--line, #e3e8ef); background: #fff;
  border-radius: 999px; height: 32px; padding: 0 12px; font-size: 12px; font-weight: 700;
}
.bell i {
  position: absolute; top: -6px; right: -4px; min-width: 16px; height: 16px; padding: 0 4px;
  background: #c62828; color: #fff; border-radius: 99px; font-style: normal; font-size: 10px; line-height: 16px;
}
.hold-box { display: grid; gap: 8px; padding: 12px; border: 1px solid #f1d7a6; background: #fff8e8; border-radius: 12px; }
.photos { display: flex; gap: 8px; flex-wrap: wrap; }
.photos img { width: 88px; height: 64px; object-fit: cover; border-radius: 8px; border: 1px solid #e3e8ef; }
.sign { width: 100%; max-width: 520px; height: 140px; border: 1px dashed #c5d0dc; border-radius: 12px; background: #fafbfd; cursor: crosshair; }
.form.tight { padding: 16px 18px; margin-top: 12px; }
.card.fleet { align-items: flex-start; }
.plate {
  flex: none;
  min-width: 108px;
  padding: 8px 10px;
  border: 2px solid var(--navy);
  border-radius: 8px;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-align: center;
  background: #f4f7fb;
}
.card.doc { justify-content: flex-start; }
.card.doc img { width: 76px; height: 54px; object-fit: cover; border-radius: 8px; border: 1px solid #e3e8ef; }
.card.doc div { flex: 1; min-width: 0; }
.warn-card { border-color: #f1d7a6; background: #fff8e8; }
.kyc-hero { align-items: flex-start; }
.seg-bar { display: flex; height: 8px; border-radius: 99px; overflow: hidden; margin: 8px 0 10px; background: #eef1f6; }
.seg-bar i { display: block; min-width: 8px; }
.seg-bar .dom { background: var(--navy); }
.seg-bar .brd { background: #d97706; }
.seg-bar .for { background: #1f9d55; }
.photos.pick { gap: 8px; }
.photos.pick button { padding: 0; border: 2px solid transparent; border-radius: 10px; background: none; }
.photos.pick button.on { border-color: var(--navy); }
.card.unread { border-color: #c9d4ea; background: #f7f9fc; }
.wb-head { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }
.stamp {
  margin-left: auto;
  border: 2px solid #c5d0dc;
  color: #8ea0b2;
  border-radius: 8px;
  padding: 6px 10px;
  font-weight: 800;
  transform: rotate(-8deg);
}
.stamp.on { border-color: #1f9d55; color: #1f9d55; }
.sign-img { max-width: 240px; height: 72px; object-fit: contain; border: 1px dashed #c5d0dc; border-radius: 8px; }
.pay-modal {
  display: grid;
  justify-items: center;
  text-align: center;
  gap: 6px;
  border: 1px solid #e3e8ef;
  border-radius: 16px;
  padding: 16px;
  background: #fff;
  margin-bottom: 12px;
}
.stars button { border: 0; background: transparent; font-size: 22px; color: #d7dde6; }
.stars button.on { color: #e6a817; }
.lamp { font-style: normal; font-size: 18px; }
.lamp.ok, em.ok { color: #1f9d55; }
.lamp.warn, em.warn { color: #d97706; }
.lamp.bad, em.bad { color: #c62828; }
.link { border: 0; background: none; color: var(--navy); font-size: 12px; padding: 0; }
@media (max-width: 1100px) {
  .desk-grid, .entry-row { grid-template-columns: 1fr; }
  .hero { flex-direction: column; align-items: stretch; }
  .kpi { width: 100%; flex-wrap: wrap; }
  .kpi div { min-width: 0; flex: 1; padding: 8px 12px; }
  .pays { grid-template-columns: 1fr 1fr; }
  .party, .grid { grid-template-columns: 1fr; }
  .steps-form { grid-template-columns: 1fr 1fr; }
  .account-grid { grid-template-columns: 1fr 1fr; }
  .kv-grid, .docs-grid { grid-template-columns: 1fr; }
}
@media (max-width: 900px) {
  .workbar { top: 64px; }
  .workbar .bar { flex-wrap: wrap; padding: 8px 0; }
  .workbar .meta { width: 100%; margin: 0; }
  .form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .pays { grid-template-columns: 1fr; }
  .account-grid { grid-template-columns: 1fr; }
}
</style>
