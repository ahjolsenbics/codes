/** 运营后台在接口不可用时的演示数据，操作只改内存。 */
import { RAW_FALLBACK_MARKET as FALLBACK_MARKET } from './catalog'
import { PUBLIC_BILLS } from './siteData'

const db: Record<string, any> = {
  '/console': {
    kycPending: 4,
    loadsPending: 6,
    orders: 128,
    disputesOpen: 2,
    depositIn: 186400,
    kycPassRate: 0.86,
    dealRate: 0.41,
    disputeRate: 0.03,
    usersByCountry: [
      { country: 'KZ', count: 214 },
      { country: 'RU', count: 168 },
      { country: 'CN', count: 86 },
      { country: 'KG', count: 42 },
    ],
    ordersByStatus: [
      { status: 'wait_load', count: 18 },
      { status: 'in_transit', count: 27 },
      { status: 'completed', count: 74 },
      { status: 'dispute', count: 2 },
    ],
    kycQueue: [
      { id: 'u3', name: '谢尔盖·奥尔洛夫', role: 'driver', kycStatus: 'pending' },
      { id: 'u-zq', name: '张倩', role: 'shipper', kycStatus: 'pending' },
      { id: 'u7', name: '达尼亚尔·斯马古洛夫', role: 'driver', kycStatus: 'pending' },
      { id: 'u15', name: '古丽娜·阿赫梅托娃', role: 'shipper', kycStatus: 'pending' },
    ],
    loadQueue: [
      { id: 'L-18420', origin: '乌鲁木齐', dest: '阿拉木图', originCountry: 'CN', destCountry: 'KZ', cargoName: '机械零件', weightT: 18.4, matchMode: 'bid', status: 'pending_review' },
      { id: 'L-18390', origin: '霍尔果斯', dest: '比什凯克', originCountry: 'CN', destCountry: 'KG', cargoName: '电子产品', weightT: 8.2, matchMode: 'bid', status: 'pending_review' },
      { id: 'L-18366', origin: '伊宁', dest: '阿拉木图', originCountry: 'CN', destCountry: 'KZ', cargoName: '冷链食品', weightT: 16, matchMode: 'grab', status: 'pending_review' },
    ],
    series: [
      { day: '09-24', orders: 12 },
      { day: '09-25', orders: 18 },
      { day: '09-26', orders: 15 },
      { day: '09-27', orders: 21 },
      { day: '09-28', orders: 17 },
      { day: '09-29', orders: 24 },
      { day: '09-30', orders: 19 },
    ],
    liveOrders: [
      { id: 'O-22018', lane: '乌鲁木齐 → 阿拉木图', shipperName: '赵建军', driverName: '努尔兰·别科夫', status: 'in_transit', freight: 18600 },
      { id: 'O-22041', lane: '奎屯 → 阿斯塔纳', shipperName: '阿斯卡尔·叶先诺夫', driverName: '叶尔博拉特·努尔拉诺夫', status: 'wait_load', freight: 21400 },
      { id: 'O-21966', lane: '霍尔果斯 → 比什凯克', shipperName: '古丽娜·阿赫梅托娃', driverName: '伊万·索科洛夫', status: 'wait_confirm', freight: 11200 },
    ],
  },
  '/console/users': {
    items: [
      { id: 'u1', role: 'shipper', name: '赵建军', phone: '138****1001', kycStatus: 'approved', credit: 128, disabled: false, country: 'CN', company: '新疆丝路跨境物流有限公司' },
      { id: 'u2', role: 'driver', name: '努尔兰·别科夫', phone: '+7 701****101', kycStatus: 'approved', credit: 132, disabled: false, country: 'KZ', company: '阿勒泰车队' },
      { id: 'u3', role: 'driver', name: '谢尔盖·奥尔洛夫', phone: '+7 701****441', kycStatus: 'pending', credit: 98, disabled: false, country: 'RU', company: '绿卡车队' },
      { id: 'u4', role: 'shipper', name: '古丽娜·阿赫梅托娃', phone: '+7 727****2208', kycStatus: 'approved', credit: 104, disabled: false, country: 'KZ', company: '阿拉木图通达货代' },
      { id: 'u5', role: 'shipper', name: '安娜·库兹涅佐娃', phone: '+7 495****7730', kycStatus: 'approved', credit: 108, disabled: false, country: 'RU', company: '新西伯利亚欧亚物流' },
      { id: 'u6', role: 'driver', name: '叶尔博拉特·努尔拉诺夫', phone: '+7 701****612', kycStatus: 'approved', credit: 126, disabled: false, country: 'KZ', company: '阿勒泰车队' },
      { id: 'u7', role: 'driver', name: '达尼亚尔·斯马古洛夫', phone: '+7 701****281', kycStatus: 'pending', credit: 117, disabled: false, country: 'KZ', company: '克州跨境' },
      { id: 'u8', role: 'shipper', name: '阿斯卡尔·叶先诺夫', phone: '+7 717****4402', kycStatus: 'approved', credit: 118, disabled: false, country: 'KZ', company: '阿斯塔纳公路运贸' },
      { id: 'u9', role: 'shipper', name: '奥莉加·斯米尔诺娃', phone: '+7 495****5510', kycStatus: 'approved', credit: 121, disabled: false, country: 'RU', company: '莫斯科东方专线' },
      { id: 'u10', role: 'driver', name: '吴斌', phone: '136****8821', kycStatus: 'approved', credit: 141, disabled: false, country: 'CN', company: '绿卡车队' },
      { id: 'u11', role: 'shipper', name: '努尔苏丹·卡里莫夫', phone: '+996 555****2290', kycStatus: 'approved', credit: 109, disabled: false, country: 'KG', company: '比什凯克口岸物流' },
      { id: 'u12', role: 'driver', name: '艾达尔·别科夫', phone: '+7 777****902', kycStatus: 'approved', credit: 115, disabled: false, country: 'KZ', company: '阿斯塔纳承运' },
      { id: 'u13', role: 'shipper', name: '叶卡捷琳娜·诺维科娃', phone: '+7 343****6618', kycStatus: 'approved', credit: 101, disabled: false, country: 'RU', company: '叶卡捷琳堡接货中心' },
      { id: 'u14', role: 'driver', name: '德米特里·沃尔科夫', phone: '+7 701****118', kycStatus: 'rejected', credit: 88, disabled: false, country: 'RU', company: '绿卡车队' },
      { id: 'u15', role: 'shipper', name: '马拉特·伊萨耶夫', phone: '+7 725****3301', kycStatus: 'approved', credit: 112, disabled: false, country: 'KZ', company: '奇姆肯特仓配' },
      { id: 'u16', role: 'shipper', name: '张倩', phone: '+86 138****1011', kycStatus: 'pending', credit: 96, disabled: false, country: 'CN', company: '待审货代工作室' },
    ],
  },
  '/console/kyc': {
    users: [
      {
        id: 'u-zq',
        role: 'shipper',
        name: '张倩',
        phone: '+86 13800001011',
        company: '待审货代工作室',
        kind: 'forwarder',
        kycStatus: 'pending',
        credentials: [
          { id: 'c-zq-biz', kind: 'biz', status: 'pending', fileUrl: '/kyc/biz.svg' },
          { id: 'c-zq-auth', kind: 'auth', status: 'pending', fileUrl: '/kyc/auth.svg' },
        ],
      },
      {
        id: 'u3',
        role: 'driver',
        name: '谢尔盖·奥尔洛夫',
        phone: '+7 701****441',
        kycStatus: 'pending',
        greenCardNo: 'KZ-GL-44190',
        greenCardExpires: '2026-10-02',
        customs: '霍尔果斯海关',
        credentials: [
          { id: 'c1', kind: 'license', status: 'approved', fileUrl: '/kyc/license.svg' },
          { id: 'c2', kind: 'green_card', status: 'pending', fileUrl: '/kyc/green.svg' },
          { id: 'c1b', kind: 'id_card', status: 'pending', fileUrl: '/kyc/id.svg' },
          { id: 'c1c', kind: 'vehicle', status: 'pending', fileUrl: '/kyc/vehicle.svg' },
        ],
      },
      {
        id: 'u5',
        role: 'shipper',
        name: '安娜·库兹涅佐娃',
        phone: '+7 495****7730',
        company: '新西伯利亚欧亚物流',
        kycStatus: 'pending',
        credentials: [
          { id: 'c3', kind: 'biz', status: 'pending', fileUrl: '/kyc/biz.svg' },
          { id: 'c4', kind: 'auth', status: 'pending', fileUrl: '/kyc/auth.svg' },
        ],
      },
      {
        id: 'u7',
        role: 'driver',
        name: '达尼亚尔·斯马古洛夫',
        phone: '+7 701****281',
        kycStatus: 'pending',
        company: '克州跨境',
        greenCardNo: 'KZ-GL-22811',
        greenCardExpires: '2027-03-18',
        customs: '伊尔克什坦海关',
        credentials: [
          { id: 'c5', kind: 'license', status: 'pending', fileUrl: '/kyc/license.svg' },
          { id: 'c6', kind: 'vehicle', status: 'pending', fileUrl: '/kyc/vehicle.svg' },
          { id: 'c5b', kind: 'id_card', status: 'pending', fileUrl: '/kyc/id.svg' },
          { id: 'c5c', kind: 'green_card', status: 'pending', fileUrl: '/kyc/green.svg' },
        ],
      },
      {
        id: 'u14',
        role: 'driver',
        name: '德米特里·沃尔科夫',
        phone: '+7 7010001011',
        kycStatus: 'rejected',
        company: '绿卡车队',
        greenCardNo: 'GC-0011',
        greenCardExpires: '2027-06-30',
        customs: '乌鲁木齐海关',
        credentials: [
          { id: 'c-dv-lic', kind: 'license', status: 'pending', fileUrl: '/kyc/license.svg' },
          { id: 'c-dv-gc', kind: 'green_card', status: 'pending', fileUrl: '/kyc/green.svg' },
          { id: 'c-dv-id', kind: 'id_card', status: 'pending', fileUrl: '/kyc/id.svg' },
          { id: 'c-dv-veh', kind: 'vehicle', status: 'pending', fileUrl: '/kyc/vehicle.svg' },
        ],
      },
      {
        id: 'u8',
        role: 'shipper',
        name: '阿依古丽·萨德科娃',
        phone: '+7 727****4402',
        company: '阿拉木图果蔬冷链',
        kycStatus: 'pending',
        credentials: [
          { id: 'c7', kind: 'biz', status: 'pending', fileUrl: '/kyc/biz.svg' },
          { id: 'c8', kind: 'agent', status: 'approved', fileUrl: '/kyc/agent.svg' },
        ],
      },
      {
        id: 'u13',
        role: 'shipper',
        name: '叶卡捷琳娜·诺维科娃',
        phone: '+7 343****6618',
        company: '叶卡捷琳堡接货中心',
        kycStatus: 'pending',
        credentials: [
          { id: 'c9', kind: 'biz', status: 'pending', fileUrl: '/kyc/biz.svg' },
        ],
      },
    ],
  },
  '/console/loads': {
    items: FALLBACK_MARKET.items.map((x, i) => ({
      ...x,
      status: i < 6 ? 'pending_review' : x.status,
    })),
  },
  '/console/orders': {
    items: PUBLIC_BILLS.map((b) => ({
      id: b.id,
      lane: `${b.origin} → ${b.dest}`,
      origin: b.origin,
      dest: b.dest,
      originCountry: b.originCountry,
      destCountry: b.destCountry,
      cargoName: b.cargo,
      weightT: b.weightT,
      shipperName: b.company,
      driverName: b.carrier,
      status: b.status,
      freight: b.freight,
      matchMode: b.mode,
      loadTime: b.lastAt,
    })),
  },
  '/console/deposits': {
    accounts: [
      { userId: 'u1', name: '赵建军', available: 800, frozen: 200 },
      { userId: 'u2', name: '努尔兰·别科夫', available: 600, frozen: 200 },
      { userId: 'u5', name: '安娜·库兹涅佐娃', available: 400, frozen: 200 },
      { userId: 'u6', name: '叶尔博拉特·努尔拉诺夫', available: 1200, frozen: 0 },
      { userId: 'u9', name: '奥莉加·斯米尔诺娃', available: 300, frozen: 200 },
      { userId: 'u10', name: '吴斌', available: 900, frozen: 400 },
      { userId: 'u11', name: '努尔苏丹·卡里莫夫', available: 500, frozen: 200 },
      { userId: 'u12', name: '艾达尔·别科夫', available: 0, frozen: 200 },
      { userId: 'u3', name: '谢尔盖·奥尔洛夫', available: 0, frozen: 0 },
    ],
    ledgers: [
      { id: 'l1', userId: 'u1', name: '赵建军', kind: 'pay', amount: 1000, channel: 'alipay', orderId: '' },
      { id: 'l2', userId: 'u2', name: '努尔兰·别科夫', kind: 'pay', amount: 200, channel: 'kaspi', orderId: '' },
      { id: 'l3', userId: 'u1', name: '赵建军', kind: 'freeze', amount: 200, channel: 'wechat', orderId: 'O-22018' },
      { id: 'l4', userId: 'u5', name: '安娜·库兹涅佐娃', kind: 'pay', amount: 600, channel: 'wechat', orderId: '' },
      { id: 'l5', userId: 'u5', name: '安娜·库兹涅佐娃', kind: 'freeze', amount: 200, channel: 'wechat', orderId: 'O-22041' },
      { id: 'l6', userId: 'u10', name: '吴斌', kind: 'pay', amount: 1300, channel: 'alipay', orderId: '' },
      { id: 'l7', userId: 'u10', name: '吴斌', kind: 'freeze', amount: 400, channel: 'alipay', orderId: 'O-21880' },
      { id: 'l8', userId: 'u9', name: '奥莉加·斯米尔诺娃', kind: 'pay', amount: 500, channel: 'wechat', orderId: '' },
      { id: 'l9', userId: 'u6', name: '叶尔博拉特·努尔拉诺夫', kind: 'unfreeze', amount: 200, channel: 'wechat', orderId: 'O-21744' },
      { id: 'l10', userId: 'u11', name: '努尔苏丹·卡里莫夫', kind: 'pay', amount: 700, channel: 'alipay', orderId: '' },
      { id: 'l11', userId: 'u12', name: '艾达尔·别科夫', kind: 'pay', amount: 200, channel: 'kaspi', orderId: '' },
      { id: 'l12', userId: 'u2', name: '努尔兰·别科夫', kind: 'freeze', amount: 200, channel: 'kaspi', orderId: 'O-21966' },
    ],
    pending: [
      { id: 901, userId: 'u12', name: '艾达尔·别科夫', amount: 200, channel: 'kaspi', status: 'pending' },
      { id: 902, userId: 'u2', name: '努尔兰·别科夫', amount: 200, channel: 'kaspi', status: 'pending' },
    ],
  },
  '/console/disputes': {
    items: [
      { id: 'd1', reason: '货损，箱体进水', orderId: 'ord_dispute_01', status: 'open', openerId: 'u1', evidence: [
        { note: '箱体进水照片，底部托盘受潮', url: '/covers/building.svg', by: '赵建军' },
        { note: '装货时车厢干燥', url: '/covers/machine.svg', by: '谢尔盖·奥尔洛夫' },
      ] },
      { id: 'd2', reason: '超时未装货', orderId: 'O-21770', status: 'open', openerId: 'u2', evidence: [] },
    ],
  },
  '/console/blacklist': {
    items: [
      { userId: 'b1', name: '某车队', reason: '累计违约 3 次' },
      { userId: 'b2', name: '空号货主', reason: '货源虚假联系方式' },
      { userId: 'b3', name: '过期绿卡承运', reason: '绿卡过期仍接单' },
      { userId: 'b4', name: '重复支付账户', reason: '保证金流水异常' },
    ],
  },
  '/console/ports': {
    ports: FALLBACK_MARKET.ports.map((p) => ({ ...p })),
    reports: [
      { id: 'r1', portId: 'khorgos', status: 'congested', waitMin: 220, at: '14:08' },
      { id: 'r2', portId: 'bakhty', status: 'heavy', waitMin: 400, at: '13:52' },
      { id: 'r3', portId: 'manzhouli', status: 'slow', waitMin: 180, at: '13:40' },
    ],
  },
  '/console/config': {
    items: {
      depositCny: 200,
      bidHours: 24,
      pickHours: 48,
      grabConfirmMin: 30,
      assignCap: 5,
      liveOrderCap: 3,
      phoneUnlockCredit: 120,
      rate_base_cnkz: 18,
      truck_factor_175: 1.15,
      cargo_factor_reefer: 1.35,
      estimate_cache_days: 7,
      estimate_anon_limit: 2,
    },
  },
  '/console/i18n': {
    items: [
      { key: 'app.deposit', zh: '保证金', ru: 'Депозит', en: 'Deposit' },
      { key: 'port.slow', zh: '缓行', ru: 'Замедление', en: 'Slow' },
      { key: 'app.refOnly', zh: '参考价，非报价', ru: 'Справочно, не оферта', en: 'Reference, not a quote' },
      { key: 'mode.bid', zh: '竞价', ru: 'Торги', en: 'Bid' },
      { key: 'mode.grab', zh: '抢单', ru: 'Захват', en: 'Grab' },
      { key: 'mode.assign', zh: '指派', ru: 'Назначение', en: 'Assign' },
      { key: 'st.in_transit', zh: '运输中', ru: 'В пути', en: 'In transit' },
      { key: 'st.wait_load', zh: '待装货', ru: 'Ожидает погрузку', en: 'Awaiting load' },
      { key: 'nav.ports', zh: '口岸', ru: 'КПП', en: 'Borders' },
      { key: 'ops.bench', zh: '运营台', ru: 'Операции', en: 'Ops desk' },
      { key: 'port.congested', zh: '拥堵', ru: 'Затор', en: 'Congested' },
      { key: 'col.freight', zh: '运费', ru: 'Фрахт', en: 'Freight' },
    ],
    missing: ['port.stale'],
    missingCount: 1,
  },
  '/console/announcements': {
    items: [
      { id: 'a1', title: '霍尔果斯夜间抽检', locale: 'zh-CN', body: '22:00 后入境增加开箱比例，预计等待增加 40 分钟。' },
      { id: 'a2', title: 'Khorgos night inspection', locale: 'en-US', body: 'Extra inspections after 22:00. Expect +40 min wait.' },
      { id: 'a3', title: 'Ночной досмотр в Хоргосе', locale: 'ru-RU', body: 'После 22:00 досмотр чаще. Ожидание +40 мин.' },
      { id: 'a4', title: '保证金到账延迟说明', locale: 'zh-CN', body: 'Kaspi 到账可能延迟 30 分钟，重复支付请联系运营。' },
      { id: 'a5', title: '阿拉山口畅行', locale: 'zh-CN', body: '今日排队回落到 70 分钟，长途车优先走阿拉山口。' },
      { id: 'a6', title: '绿卡临期提醒', locale: 'zh-CN', body: '10 月内到期的绿卡请在资质页更新，过期不能接单。' },
    ],
  },
  '/console/audit': {
    items: [
      { id: 'g1', action: 'kyc.pass', target: 'u2', at: '09-26 14:12' },
      { id: 'g2', action: 'load.reject', target: 'L-18102', at: '09-26 11:40' },
      { id: 'g3', action: 'port.report', target: 'khorgos', at: '09-26 09:05' },
      { id: 'g4', action: 'kyc.reject', target: 'u4', at: '09-25 16:22' },
      { id: 'g5', action: 'load.pass', target: 'L-18341', at: '09-25 10:08' },
      { id: 'g6', action: 'user.disable', target: 'u4', at: '09-25 16:24' },
      { id: 'g7', action: 'dispute.rule', target: 'd0', at: '09-24 19:40' },
      { id: 'g8', action: 'port.set', target: 'alashankou', at: '09-24 08:16' },
      { id: 'g9', action: 'ann.publish', target: 'a1', at: '09-23 21:00' },
      { id: 'g10', action: 'config.save', target: 'bidHours', at: '09-23 11:12' },
      { id: 'g11', action: 'load.pass', target: 'L-18411', at: '09-22 15:33' },
      { id: 'g12', action: 'kyc.pass', target: 'u6', at: '09-22 09:18' },
    ],
  },
}

export function demoConsole(path: string) {
  return structuredClone(db[path] || { items: [] })
}

export function demoMutate(kind: string, id: string, extra?: any) {
  if (kind === 'user') {
    const u = db['/console/users'].items.find((x: any) => x.id === id)
    if (u) u.disabled = !u.disabled
  }
  if (kind === 'kyc') {
    const u = db['/console/kyc'].users.find((x: any) => x.id === id)
    if (u) u.kycStatus = extra ? 'approved' : 'rejected'
    db['/console'].kycPending = Math.max(0, db['/console'].kycPending - 1)
  }
  if (kind === 'load') {
    const x = db['/console/loads'].items.find((row: any) => row.id === id)
    if (x) x.status = extra ? 'published' : 'rejected'
  }
  if (kind === 'dispute') {
    const d = db['/console/disputes'].items.find((row: any) => row.id === id)
    if (d) d.status = 'completed'
  }
  if (kind === 'port') {
    const p = db['/console/ports'].ports.find((row: any) => row.id === id)
    if (p) {
      const spec = extra && typeof extra === 'object' ? extra : { status: 'smooth', waitMin: 20 }
      p.status = spec.status || 'smooth'
      p.waitMin = Number(spec.waitMin ?? 20)
      p.updated = '14:40'
    }
  }
  if (kind === 'report') {
    db['/console/ports'].reports = db['/console/ports'].reports.filter((row: any) => row.id !== id)
  }
  if (kind === 'ann') {
    db['/console/announcements'].items.unshift({ id: `a-${Date.now()}`, title: String(extra || 'Notice'), locale: 'zh-CN' })
  }
  db['/console/audit'].items.unshift({ id: `g-${Date.now()}`, action: kind, target: id, at: '09-26 22:40' })
}
