/** 公开页可查询的运单节点。电话与证件不出现在这里。 */

export type BillStep = { status: string; at: string }

export type PublicBill = {
  id: string
  origin: string
  dest: string
  originCountry: string
  destCountry: string
  cargo: string
  freight: number
  mode: string
  status: string
  port: string
  steps: BillStep[]
  company: string
  carrier: string
  weightT: number
  volumeM3: number
  truckLength: string
  plate: string
  packing: string
  cargoClass: string
  km: number
  lastPoint: string
  lastAt: string
  eta: string
  deposit: number
  customsFrom: string
  customsTo: string
  preNo: string
  transitNo: string
  shared: boolean
}

const RAW = [
  {
    id: 'O-22018',
    origin: '乌鲁木齐',
    dest: '阿拉木图',
    originCountry: 'CN',
    destCountry: 'KZ',
    cargo: '机械零件',
    freight: 18600,
    mode: 'bid',
    status: 'in_transit',
    port: 'khorgos',
    steps: [
      { status: 'dealt', at: '09-26 09:10' },
      { status: 'wait_load', at: '09-26 11:20' },
      { status: 'loading', at: '09-26 16:05' },
      { status: 'in_transit', at: '09-26 18:40' },
    ],
    company: '天山机电',
    carrier: '努尔兰·别科夫',
    weightT: 18.4,
    volumeM3: 62,
    truckLength: '13.7',
    plate: '新A·D3821',
    packing: 'pallet',
    cargoClass: 'equipment',
    km: 980,
    lastPoint: '霍尔果斯',
    lastAt: '09-26 21:14',
    eta: '09-27 18:00',
    customsFrom: '霍尔果斯',
    customsTo: '阿拉木图',
    shared: true,
  },
  {
    id: 'O-22041',
    origin: '奎屯',
    dest: '阿斯塔纳',
    originCountry: 'CN',
    destCountry: 'KZ',
    cargo: '建材',
    freight: 21400,
    mode: 'grab',
    status: 'wait_load',
    port: 'khorgos',
    steps: [
      { status: 'dealt', at: '09-26 08:02' },
      { status: 'wait_load', at: '09-26 08:16' },
    ],
    company: '北屯建材',
    carrier: '叶尔博拉特·努尔拉诺夫',
    weightT: 22,
    volumeM3: 48,
    truckLength: '13.0',
    plate: '新A·B1906',
    packing: 'bulk',
    cargoClass: 'general',
    km: 1280,
    lastPoint: '奎屯',
    lastAt: '09-26 08:16',
    eta: '09-29 12:00',
    customsFrom: '霍尔果斯',
    customsTo: '阿斯塔纳',
    shared: false,
  },
  {
    id: 'O-21966',
    origin: '霍尔果斯',
    dest: '比什凯克',
    originCountry: 'CN',
    destCountry: 'KG',
    cargo: '电子产品',
    freight: 11200,
    mode: 'bid',
    status: 'wait_confirm',
    port: 'khorgos',
    steps: [
      { status: 'dealt', at: '09-24 10:12' },
      { status: 'wait_load', at: '09-24 14:00' },
      { status: 'in_transit', at: '09-25 01:30' },
      { status: 'wait_confirm', at: '09-26 19:48' },
    ],
    company: '霍尔果斯综保',
    carrier: '伊万·索科洛夫',
    weightT: 8.2,
    volumeM3: 36,
    truckLength: '9.6',
    plate: '新A·P6615',
    packing: 'carton',
    cargoClass: 'general',
    km: 520,
    lastPoint: '比什凯克',
    lastAt: '09-26 19:48',
    eta: '09-26 19:48',
    customsFrom: '霍尔果斯',
    customsTo: '比什凯克',
    shared: true,
  },
  {
    id: 'O-21912',
    origin: '喀什',
    dest: '奥什',
    originCountry: 'CN',
    destCountry: 'KG',
    cargo: '日用百货',
    freight: 9800,
    mode: 'bid',
    status: 'loading',
    port: 'irkeshtam',
    steps: [
      { status: 'dealt', at: '09-26 07:40' },
      { status: 'wait_load', at: '09-26 10:05' },
      { status: 'loading', at: '09-26 15:20' },
    ],
    company: '疏附商贸',
    carrier: '艾达尔·别科夫',
    weightT: 12.6,
    volumeM3: 54,
    truckLength: '9.6',
    plate: '新Q·F1108',
    packing: 'carton',
    cargoClass: 'general',
    km: 420,
    lastPoint: '喀什',
    lastAt: '09-26 15:20',
    eta: '09-27 11:00',
    customsFrom: '伊尔克什坦',
    customsTo: '奥什',
    shared: true,
  },
  {
    id: 'O-21880',
    origin: '阿拉山口',
    dest: '莫斯科',
    originCountry: 'CN',
    destCountry: 'RU',
    cargo: '汽车配件',
    freight: 42000,
    mode: 'assign',
    status: 'dealt',
    port: 'alashankou',
    steps: [{ status: 'dealt', at: '09-26 16:12' }],
    company: '口岸汽配',
    carrier: '努尔兰·卡西莫夫',
    weightT: 14.5,
    volumeM3: 70,
    truckLength: '13.7',
    plate: '新E·K2206',
    packing: 'crate',
    cargoClass: 'general',
    km: 4680,
    lastPoint: '阿拉山口',
    lastAt: '09-26 16:12',
    eta: '10-04 20:00',
    customsFrom: '阿拉山口',
    customsTo: '莫斯科',
    shared: false,
  },
  {
    id: 'O-21855',
    origin: '伊宁',
    dest: '阿拉木图',
    originCountry: 'CN',
    destCountry: 'KZ',
    cargo: '冷链食品',
    freight: 16800,
    mode: 'grab',
    status: 'in_transit',
    port: 'khorgos',
    steps: [
      { status: 'dealt', at: '09-25 19:08' },
      { status: 'loading', at: '09-26 06:40' },
      { status: 'in_transit', at: '09-26 09:15' },
    ],
    company: '伊犁冷链',
    carrier: '谢尔盖·奥尔洛夫',
    weightT: 16,
    volumeM3: 58,
    truckLength: '13.7',
    plate: '新F·C4412',
    packing: 'pallet',
    cargoClass: 'reefer',
    km: 378,
    lastPoint: '霍尔果斯',
    lastAt: '09-26 20:02',
    eta: '09-27 08:30',
    customsFrom: '霍尔果斯',
    customsTo: '阿拉木图',
    shared: true,
  },
  {
    id: 'O-21821',
    origin: '库尔勒',
    dest: '塔什干',
    originCountry: 'CN',
    destCountry: 'UZ',
    cargo: '棉纱',
    freight: 24600,
    mode: 'bid',
    status: 'wait_load',
    port: 'irkeshtam',
    steps: [
      { status: 'dealt', at: '09-26 12:30' },
      { status: 'wait_load', at: '09-26 13:02' },
    ],
    company: '巴州棉纺',
    carrier: '达尼亚尔·斯马古洛夫',
    weightT: 20,
    volumeM3: 64,
    truckLength: '13.0',
    plate: '新M·H7720',
    packing: 'pallet',
    cargoClass: 'general',
    km: 1860,
    lastPoint: '库尔勒',
    lastAt: '09-26 13:02',
    eta: '09-30 16:00',
    customsFrom: '伊尔克什坦',
    customsTo: '塔什干',
    shared: false,
  },
  {
    id: 'O-21790',
    origin: '哈密',
    dest: '新西伯利亚',
    originCountry: 'CN',
    destCountry: 'RU',
    cargo: '家具',
    freight: 38500,
    mode: 'bid',
    status: 'in_transit',
    port: 'alashankou',
    steps: [
      { status: 'dealt', at: '09-24 08:18' },
      { status: 'loading', at: '09-24 16:40' },
      { status: 'in_transit', at: '09-25 03:10' },
    ],
    company: '哈密家居',
    carrier: '阿列克谢·彼得罗夫',
    weightT: 11,
    volumeM3: 78,
    truckLength: '17.5',
    plate: '新B·K3088',
    packing: 'carton',
    cargoClass: 'general',
    km: 2860,
    lastPoint: '阿拉山口',
    lastAt: '09-26 11:40',
    eta: '09-30 09:00',
    customsFrom: '阿拉山口',
    customsTo: '新西伯利亚',
    shared: true,
  },
  {
    id: 'O-21744',
    origin: '石河子',
    dest: '阿斯塔纳',
    originCountry: 'CN',
    destCountry: 'KZ',
    cargo: '建材',
    freight: 23600,
    mode: 'grab',
    status: 'completed',
    port: 'bakhty',
    steps: [
      { status: 'dealt', at: '09-22 09:00' },
      { status: 'in_transit', at: '09-23 11:20' },
      { status: 'completed', at: '09-26 17:05' },
    ],
    company: '北屯建材',
    carrier: '吴斌',
    weightT: 24,
    volumeM3: 55,
    truckLength: '13.7',
    plate: '新A·D3821',
    packing: 'bulk',
    cargoClass: 'general',
    km: 1540,
    lastPoint: '阿斯塔纳',
    lastAt: '09-26 17:05',
    eta: '09-26 17:05',
    customsFrom: '巴克图',
    customsTo: '阿斯塔纳',
    shared: true,
  },
  {
    id: 'O-21708',
    origin: '霍尔果斯',
    dest: '圣彼得堡',
    originCountry: 'CN',
    destCountry: 'RU',
    cargo: '机械零件',
    freight: 51200,
    mode: 'assign',
    status: 'in_transit',
    port: 'khorgos',
    steps: [
      { status: 'dealt', at: '09-21 14:22' },
      { status: 'loading', at: '09-22 08:10' },
      { status: 'in_transit', at: '09-22 19:40' },
    ],
    company: '天山机电',
    carrier: '巴克特詹·托列乌奥夫',
    weightT: 17.6,
    volumeM3: 58,
    truckLength: '13.7',
    plate: '新E·K2206',
    packing: 'pallet',
    cargoClass: 'equipment',
    km: 5180,
    lastPoint: '阿斯塔纳',
    lastAt: '09-26 16:28',
    eta: '10-03 14:00',
    customsFrom: '霍尔果斯',
    customsTo: '圣彼得堡',
    shared: true,
  },
  {
    id: 'O-21672',
    origin: '昌吉',
    dest: '阿拉木图',
    originCountry: 'CN',
    destCountry: 'KZ',
    cargo: '日用百货',
    freight: 8600,
    mode: 'bid',
    status: 'wait_confirm',
    port: 'dulata',
    steps: [
      { status: 'dealt', at: '09-25 11:08' },
      { status: 'in_transit', at: '09-26 02:16' },
      { status: 'wait_confirm', at: '09-26 21:30' },
    ],
    company: '疏附商贸',
    carrier: '德米特里·沃尔科夫',
    weightT: 9.4,
    volumeM3: 42,
    truckLength: '9.6',
    plate: '新Q·L2290',
    packing: 'carton',
    cargoClass: 'general',
    km: 920,
    lastPoint: '阿拉木图',
    lastAt: '09-26 21:30',
    eta: '09-26 21:30',
    customsFrom: '都拉塔',
    customsTo: '阿拉木图',
    shared: true,
  },
  {
    id: 'O-21640',
    origin: '喀什',
    dest: '安集延',
    originCountry: 'CN',
    destCountry: 'UZ',
    cargo: '日用百货',
    freight: 10400,
    mode: 'bid',
    status: 'loading',
    port: 'irkeshtam',
    steps: [
      { status: 'dealt', at: '09-26 08:50' },
      { status: 'wait_load', at: '09-26 10:12' },
      { status: 'loading', at: '09-26 14:36' },
    ],
    company: '疏附商贸',
    carrier: '努尔兰·别科夫',
    weightT: 11.1,
    volumeM3: 48,
    truckLength: '9.6',
    plate: '新Q·L2290',
    packing: 'carton',
    cargoClass: 'general',
    km: 510,
    lastPoint: '喀什',
    lastAt: '09-26 14:36',
    eta: '09-27 20:00',
    customsFrom: '伊尔克什坦',
    customsTo: '安集延',
    shared: true,
  },
]

export const PUBLIC_BILLS: PublicBill[] = RAW.map((b) => {
  const tail = b.id.replace('O-', '')
  return {
    ...b,
    deposit: 200,
    preNo: `${b.destCountry}/260726/${tail}`,
    transitNo: `39857504/260726/${tail}`,
  }
})

export function findBill(raw: string) {
  const id = raw.trim().toUpperCase()
  return PUBLIC_BILLS.find((b) => b.id.toUpperCase() === id) || null
}

export function billCreated(bill: { steps?: BillStep[] }) {
  return bill.steps?.[0]?.at || ''
}

export function billFill(status: string) {
  if (status === 'completed') return 100
  if (status === 'wait_confirm') return 88
  if (status === 'in_transit') return 58
  if (status === 'loading') return 28
  if (status === 'wait_load') return 14
  return 8
}

export type TripStage = {
  key: 'load' | 'gate' | 'arrive'
  done: number
  total: number
  state: 'done' | 'now' | 'wait'
  minutes: number
}

export function billStages(bill: { status: string; port?: string }, waitMin = 90): TripStage[] {
  const s = bill.status
  const load: TripStage =
    s === 'dealt' || s === 'wait_load'
      ? { key: 'load', done: 0, total: 1, state: s === 'wait_load' ? 'now' : 'wait', minutes: 40 }
      : s === 'loading'
        ? { key: 'load', done: 1, total: 1, state: 'now', minutes: 55 }
        : { key: 'load', done: 1, total: 1, state: 'done', minutes: 48 }
  const gate: TripStage =
    s === 'in_transit'
      ? { key: 'gate', done: 1, total: 2, state: 'now', minutes: waitMin }
      : s === 'wait_confirm' || s === 'completed'
        ? { key: 'gate', done: 2, total: 2, state: 'done', minutes: waitMin }
        : { key: 'gate', done: 0, total: 2, state: 'wait', minutes: waitMin }
  const arrive: TripStage =
    s === 'completed'
      ? { key: 'arrive', done: 1, total: 1, state: 'done', minutes: 35 }
      : s === 'wait_confirm'
        ? { key: 'arrive', done: 0, total: 1, state: 'now', minutes: 25 }
        : { key: 'arrive', done: 0, total: 1, state: 'wait', minutes: 40 }
  return [load, gate, arrive]
}

export function formatStageTime(minutes: number) {
  if (minutes >= 60) {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return m ? `${h} h ${m} min` : `${h} h`
  }
  return `${minutes} min`
}

const TRUCK_FACTOR: Record<string, number> = { '9.6': 0.86, '13.0': 0.92, '13.5': 0.94, '13.7': 0.96, '17.5': 1 }
const CARGO_FACTOR: Record<string, number> = { general: 1, reefer: 1.22, equipment: 1.08 }

export function corridorQuote(
  corridors: any[],
  from: string,
  to: string,
  opts?: { truck?: string; cargoClass?: string; weightT?: number },
) {
  const a = from.trim()
  const b = to.trim()
  if (!a || !b) return null
  const hit = (corridors || []).find((c) => c.from === a && c.to === b)
    || (corridors || []).find((c) => String(c.from).includes(a) && String(c.to).includes(b))
  if (!hit || !hit.km || hit.rateLow == null || hit.rateHigh == null) return null
  const km = Number(hit.km)
  const truckF = TRUCK_FACTOR[String(opts?.truck || '')] ?? 1
  const cargoF = CARGO_FACTOR[String(opts?.cargoClass || '')] ?? 1
  const w = Number(opts?.weightT)
  const weightF = Number.isFinite(w) && w > 0 ? (w > 20 ? 1.06 : w < 10 ? 0.92 : 1) : 1
  const factor = Number((truckF * cargoF * weightF).toFixed(3))
  const domesticKm = Math.round(km * 0.34)
  const portKm = Math.max(18, Math.round(km * 0.08))
  const foreignKm = Math.max(0, km - domesticKm - portKm)
  const waitMin = Number(hit.waitMin || 0)
  const driveH = km / 55
  const waitH = waitMin / 60
  return {
    ...hit,
    factor,
    feeLow: Math.round(km * Number(hit.rateLow) * factor),
    feeHigh: Math.round(km * Number(hit.rateHigh) * factor),
    hours: Math.max(8, Math.round(driveH + waitH)),
    driveHours: Math.max(4, Math.round(driveH)),
    waitHours: Math.round(waitH * 10) / 10,
    segments: [
      { key: 'domestic', km: domesticKm },
      { key: 'port', km: portKm },
      { key: 'foreign', km: foreignKm },
    ],
  }
}
