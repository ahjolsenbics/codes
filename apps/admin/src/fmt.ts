import { brand, cargo, cargoClass, company, countryName, customs, entity, laneText, packing, party, phrase, place, portName, remarkText } from './geo'
import { locale, t, tf, ts } from './i18n'

export { brand, cargo, cargoClass, company, countryName, customs, entity, laneText, packing, party, phrase, place, portName, remarkText }

export function money(n: unknown): string {
  locale.value
  const v = Number(n)
  if (!Number.isFinite(v) || v <= 0) return t('money.ask')
  const tag = locale.value === 'ru-RU' ? 'ru-RU' : locale.value === 'en-US' ? 'en-US' : 'zh-CN'
  return `¥${v.toLocaleString(tag)}`
}

export function modeLabel(mode: unknown): string {
  return ts('mode', mode)
}

export function loadStatus(status: unknown): string {
  return ts('st', status)
}

export function orderStatus(status: unknown): string {
  return ts('st', status)
}

export function kycLabel(status: unknown): string {
  return ts('st', status)
}

export function portLabel(status: unknown): string {
  const s = String(status || '')
  const key = `ps.${s}`
  const v = t(key)
  return v === key ? ts('st', s) : v
}

export function quoteLabel(status: unknown): string {
  return ts('q', status)
}

export function ledgerLabel(kind: unknown): string {
  return ts('ledger', kind)
}

export function waitMin(n: unknown): string {
  const v = Number(n)
  if (!Number.isFinite(v) || v <= 0) return t('port.noWait')
  return tf('port.waitMin', { n: v })
}

export function corridorRate(c: Record<string, any> | null | undefined): string {
  if (!c) return '—'
  if (c.rateKind === 'shuttle') return t('corr.shuttle')
  if (c.rateLow != null && c.rateHigh != null) return tf('corr.rateKm', { low: c.rateLow, high: c.rateHigh })
  return String(c.rate || '—')
}

export function corridorWait(c: Record<string, any> | null | undefined, ports: any[] = []): string {
  if (!c) return '—'
  if (c.waitStatus) return portLabel(c.waitStatus)
  if (c.waitPort) {
    const p = ports.find((x) => x.id === c.waitPort)
    const name = p ? portName(p) : place(c.waitPort)
    if (c.waitHours) return `${name} · ${tf('port.waitHours', { n: c.waitHours })}`
    if (c.waitMin) return `${name} · ${waitMin(c.waitMin)}`
    return name
  }
  if (c.waitMin) return waitMin(c.waitMin)
  return String(c.wait || '—')
}

export function tone(status: unknown): 'ok' | 'warn' | 'bad' | 'mute' {
  const s = String(status)
  if (['passed', 'approved', 'open', 'completed', 'smooth', 'matched', 'published', 'dealt', 'chosen', 'active'].includes(s)) return 'ok'
  if (['pending', 'pending_review', 'wait_confirm', 'wait_load', 'slow', 'in_transit', 'loading', 'matching', 'draft', 'heavy', 'stale'].includes(s)) return 'warn'
  if (['rejected', 'congested', 'closed', 'cancelled', 'disputed', 'dispute', 'blacklisted'].includes(s)) return 'bad'
  return 'mute'
}

export function compact(n: unknown): string {
  locale.value
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  const tag = locale.value === 'ru-RU' ? 'ru-RU' : locale.value === 'en-US' ? 'en-US' : 'zh-CN'
  return v.toLocaleString(tag)
}

export function quotesLabel(n: unknown): string {
  const v = Number(n) || 0
  return tf('card.quotes', { n: v })
}

export function truckKind(item: Record<string, any> | null | undefined): string {
  if (!item) return t('truck.tent')
  if (item.cargoClass === 'reefer') return t('truck.reefer')
  const len = String(item.truckLength || '')
  if (len === '9.6') return t('truck.box')
  if (len === '17.5') return t('truck.tent')
  return t('truck.tent')
}
