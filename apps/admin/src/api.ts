const OPS_KEY = 'yunmm_ops_token'
const APP_KEY = 'yunmm_app_token'

export function getOpsToken(): string | null {
  return localStorage.getItem(OPS_KEY)
}

export function setOpsToken(token: string | null) {
  if (token) localStorage.setItem(OPS_KEY, token)
  else localStorage.removeItem(OPS_KEY)
}

export function getAppToken(): string | null {
  return localStorage.getItem(APP_KEY)
}

export function setAppToken(token: string | null) {
  if (token) localStorage.setItem(APP_KEY, token)
  else localStorage.removeItem(APP_KEY)
}

/** 运营台沿用旧名，避免控制台代码大面积改调用。 */
export function getToken(): string | null {
  return getOpsToken()
}

export function setToken(token: string | null) {
  setOpsToken(token)
}

async function call(path: string, init: RequestInit, token: string | null) {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const res = await fetch(path, { ...init, headers, signal: AbortSignal.timeout(15000) })
  const data = await res.json()
  if (!res.ok) throw new Error(JSON.stringify(data.detail ?? data))
  return data
}

function ops(path: string, init: RequestInit = {}) {
  return call(path, init, getOpsToken())
}

function app(path: string, init: RequestInit = {}) {
  return call(path, init, getAppToken())
}

export const api = {
  demoLogin: (role: 'admin' | 'shipper' | 'driver' = 'admin') =>
    call('/api/v1/auth/demo-login', { method: 'POST', body: JSON.stringify({ role }) }, null),
  smsSend: (phone: string, zone = '+86') =>
    call('/api/v1/auth/sms/send', { method: 'POST', body: JSON.stringify({ phone, zone }) }, null),
  smsLogin: (phone: string, code: string, role: 'shipper' | 'driver') =>
    call('/api/v1/auth/sms/login', { method: 'POST', body: JSON.stringify({ phone, code, role }) }, null),
  passwordLogin: (phone: string, password: string, role: 'shipper' | 'driver') =>
    call('/api/v1/auth/password', { method: 'POST', body: JSON.stringify({ phone, password, role }) }, null),
  register: (body: Record<string, unknown>) =>
    call('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(body) }, null),
  me: () => ops('/api/v1/auth/me'),
  market: () => call('/api/v1/public/market', {}, getAppToken()),
  dashboard: () => ops('/api/v1/admin/dashboard'),
  users: () => ops('/api/v1/admin/users'),
  patchUser: (id: string, disabled: boolean) =>
    ops(`/api/v1/admin/users/${id}`, { method: 'POST', body: JSON.stringify({ disabled }) }),
  kyc: () => ops('/api/v1/admin/kyc'),
  reviewKyc: (id: string, passFlag: boolean, reason = '') =>
    ops(`/api/v1/admin/kyc/${id}`, { method: 'POST', body: JSON.stringify({ passFlag, reason }) }),
  loads: () => ops('/api/v1/admin/loads'),
  reviewLoad: (id: string, approve: boolean) =>
    ops(`/api/v1/admin/loads/${id}/review`, { method: 'POST', body: JSON.stringify({ approve }) }),
  orders: () => ops('/api/v1/admin/orders'),
  deposits: () => ops('/api/v1/admin/deposits'),
  disputes: () => ops('/api/v1/admin/disputes'),
  ruleDispute: (id: string, liableUserId: string, verdict: string) =>
    ops(`/api/v1/admin/disputes/${id}/rule`, { method: 'POST', body: JSON.stringify({ liableUserId, verdict, deduct: true }) }),
  blacklist: () => ops('/api/v1/admin/blacklist'),
  addBlack: (userId: string, reason: string) =>
    ops('/api/v1/admin/blacklist', { method: 'POST', body: JSON.stringify({ userId, reason }) }),
  ports: () => ops('/api/v1/admin/ports'),
  setPort: (id: string, status: string, waitMin: number) =>
    ops(`/api/v1/admin/ports/${id}`, { method: 'POST', body: JSON.stringify({ status, waitMin }) }),
  approveReport: (id: number, passFlag: boolean) =>
    ops(`/api/v1/admin/ports/reports/${id}`, { method: 'POST', body: JSON.stringify({ passFlag }) }),
  config: () => ops('/api/v1/admin/config'),
  saveConfig: (items: Record<string, string>) =>
    ops('/api/v1/admin/config', { method: 'PUT', body: JSON.stringify({ items }) }),
  i18n: () => ops('/api/v1/admin/i18n'),
  announcements: () => ops('/api/v1/admin/announcements'),
  createAnn: (title: string, body: string, audience = 'all') =>
    ops('/api/v1/admin/announcements', { method: 'POST', body: JSON.stringify({ title, body, audience }) }),
  audit: () => ops('/api/v1/admin/audit'),
  refund: (ledgerId: number) =>
    ops('/api/v1/admin/deposits/refund', { method: 'POST', body: JSON.stringify({ ledgerId }) }),
  kaspiConfirm: (id: number) =>
    ops(`/api/v1/admin/deposits/${id}/kaspi`, { method: 'POST', body: '{}' }),
  disputeEvidence: (id: string, note: string) =>
    ops(`/api/v1/admin/disputes/${id}/evidence`, { method: 'POST', body: JSON.stringify({ note }) }),
  disputeReview: (id: string) =>
    ops(`/api/v1/admin/disputes/${id}/review`, { method: 'POST', body: '{}' }),
  i18nMissing: () => ops('/api/v1/admin/i18n/missing'),
  i18nImport: (items: Record<string, string>[]) =>
    ops('/api/v1/admin/i18n/import', { method: 'POST', body: JSON.stringify({ items }) }),
}

export const appApi = {
  me: () => app('/api/v1/auth/me'),
  loads: (mine = false) => app(mine ? '/api/v1/loads/mine' : '/api/v1/loads'),
  loadDetail: (id: string) => app(`/api/v1/loads/${id}`),
  publish: (body: Record<string, unknown>) =>
    app('/api/v1/loads', { method: 'POST', body: JSON.stringify(body) }),
  quote: (id: string, amount: number, extra: Record<string, unknown> = {}) =>
    app(`/api/v1/loads/${id}/quotes`, { method: 'POST', body: JSON.stringify({ amount, ...extra }) }),
  grab: (id: string) => app(`/api/v1/loads/${id}/grab`, { method: 'POST', body: '{}' }),
  choose: (loadId: string, quoteId: string) =>
    app(`/api/v1/loads/${loadId}/choose`, { method: 'POST', body: JSON.stringify({ quoteId }) }),
  offline: (id: string) => app(`/api/v1/loads/${id}/offline`, { method: 'POST', body: '{}' }),
  copyLoad: (id: string) => app(`/api/v1/loads/${id}/copy`, { method: 'POST', body: '{}' }),
  confirmGrab: (id: string) => app(`/api/v1/loads/${id}/grab/confirm`, { method: 'POST', body: '{}' }),
  cancelGrab: (id: string) => app(`/api/v1/loads/${id}/grab/cancel`, { method: 'POST', body: '{}' }),
  assign: (id: string, driverIds: string[], message = '') =>
    app(`/api/v1/loads/${id}/assign`, { method: 'POST', body: JSON.stringify({ driverIds, message }) }),
  drivers: () => app('/api/v1/drivers'),
  signWaybill: (id: string, signData = '', comment = '') =>
    app(`/api/v1/orders/${id}/waybill/sign`, { method: 'POST', body: JSON.stringify({ signData, comment }) }),
  review: (id: string, stars = 5, tags = 'on_time', comment = 'ok') =>
    app(`/api/v1/orders/${id}/reviews`, { method: 'POST', body: JSON.stringify({ stars, tags, comment }) }),
  orders: () => app('/api/v1/orders'),
  orderDetail: (id: string) => app(`/api/v1/orders/${id}`),
  orderAction: (id: string, action: string) =>
    app(`/api/v1/orders/${id}/actions`, { method: 'POST', body: JSON.stringify({ action }) }),
  simulate: (id: string) => app(`/api/v1/orders/${id}/track/simulate`, { method: 'POST', body: '{}' }),
  conversations: () => app('/api/v1/conversations'),
  openChat: (loadId: string) =>
    app('/api/v1/conversations/open', { method: 'POST', body: JSON.stringify({ loadId }) }),
  messages: (cid: string) => app(`/api/v1/conversations/${cid}/messages`),
  send: (cid: string, text: string) =>
    app(`/api/v1/conversations/${cid}/messages`, { method: 'POST', body: JSON.stringify({ body: text, kind: 'text' }) }),
  deposit: () => app('/api/v1/deposits/me'),
  topup: (channel = 'wechat', amount = 200) =>
    app('/api/v1/deposits/topup', { method: 'POST', body: JSON.stringify({ amount, channel }) }),
  confirmPay: (intentId: number) =>
    app('/api/v1/deposits/confirm', { method: 'POST', body: JSON.stringify({ intentId }) }),
  ports: () => app('/api/v1/ports'),
  reportPort: (id: string, photoUrl = '/covers/building.svg', status = 'congested', waitMin = 90) =>
    app(`/api/v1/ports/${id}/report`, { method: 'POST', body: JSON.stringify({ status, waitMin, photoUrl, lat: 44.21, lng: 80.42 }) }),
  estimate: (origin: string, dest: string, extra: Record<string, unknown> = {}) =>
    app('/api/v1/estimate', { method: 'POST', body: JSON.stringify({ origin, dest, truck: '13.5x32', cargo: 'general', ...extra }) }),
  kyc: () => app('/api/v1/kyc/me'),
  submitKyc: (body: Record<string, unknown> = {}) =>
    app('/api/v1/kyc/submit', { method: 'POST', body: JSON.stringify({ kind: 'enterprise', company: '', items: [], ...body }) }),
  credit: (userId: string) => app(`/api/v1/users/${userId}/credit`),
  invites: () => app('/api/v1/invites'),
  replyInvite: (id: string, accept: boolean) =>
    app(`/api/v1/invites/${id}/reply`, { method: 'POST', body: JSON.stringify({ accept }) }),
  notifications: () => app('/api/v1/notifications'),
  readNotes: () => app('/api/v1/notifications/read', { method: 'POST', body: '{}' }),
  vehicles: () => app('/api/v1/vehicles'),
  addVehicle: (plate: string, extra: Record<string, unknown> = {}) =>
    app('/api/v1/vehicles', { method: 'POST', body: JSON.stringify({ plate, lengthM: 13.5, tonnage: 32, ...extra }) }),
  saveSettings: (body: Record<string, unknown>) =>
    app('/api/v1/settings', { method: 'POST', body: JSON.stringify(body) }),
  cancelAccount: () => app('/api/v1/account/cancel', { method: 'POST', body: '{}' }),
  lanes: () => app('/api/v1/lanes'),
  addLane: (origin: string, dest: string) =>
    app('/api/v1/lanes', { method: 'POST', body: JSON.stringify({ origin, dest }) }),
  unlockPhone: (userId: string) => app(`/api/v1/users/${userId}/phone`),
}
