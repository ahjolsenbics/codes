import { getAppToken, setAppToken } from './api'

/** 有效工作台令牌为 demo.{role}.{userId}，旧的 demo-shipper 兜底令牌不算登录。 */
export function isAppAuthed(): boolean {
  const token = getAppToken() || ''
  const parts = token.split('.')
  return parts.length === 3 && parts[0] === 'demo' && Boolean(parts[1]) && Boolean(parts[2])
}

export function appRoleFromToken(): 'shipper' | 'driver' | null {
  if (!isAppAuthed()) return null
  const role = (getAppToken() || '').split('.')[1]
  return role === 'driver' ? 'driver' : role === 'shipper' ? 'shipper' : null
}

export function appHome(): string {
  return appRoleFromToken() === 'driver' ? '/app/driver' : '/app/shipper'
}

export function clearInvalidAppToken() {
  const token = getAppToken() || ''
  if (token && !isAppAuthed()) setAppToken(null)
}

export function loginPath(query: Record<string, string> = {}) {
  return { path: '/login', query }
}

/** 货主端 / 司机端入口：已登录且角色匹配则进工作台，否则带角色去登录。 */
export function deskPath(role: 'shipper' | 'driver') {
  if (isAppAuthed() && appRoleFromToken() === role) return `/app/${role}`
  return { path: '/login', query: { role, next: `/app/${role}` } }
}
