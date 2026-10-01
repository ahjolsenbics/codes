import { onMounted, ref } from 'vue'
import { api } from './api'
import { isAppAuthed } from './auth'
import { FALLBACK_MARKET, RAW_FALLBACK_MARKET, stripPrivate } from './catalog'

function fallbackMarket() {
  return isAppAuthed() ? { ...RAW_FALLBACK_MARKET } : { ...FALLBACK_MARKET }
}

function redactList(rows: any[] | undefined, authed: boolean) {
  const list = rows || []
  return authed ? list : list.map((row) => stripPrivate(row))
}

/** 公开页货盘：接口失败时仍用本地盘口，避免页面空掉。未登录一律去掉报价与主体信息。 */
export function useMarket() {
  const market = ref<any>({ ...fallbackMarket() })

  onMounted(async () => {
    const base = fallbackMarket()
    const authed = isAppAuthed()
    try {
      const live = await api.market()
      if (live) {
        market.value = {
          ...base,
          ...live,
          items: redactList(live.items?.length ? live.items : base.items, authed),
          trucks: redactList(live.trucks?.length ? live.trucks : base.trucks, authed),
          ports: live.ports?.length ? live.ports : base.ports,
          corridors: live.corridors?.length ? live.corridors : base.corridors,
        }
        return
      }
    } catch (e) {
      console.error('货盘展示数据加载失败，使用演示盘口', e)
    }
    market.value = {
      ...base,
      items: redactList(base.items, authed),
      trucks: redactList(base.trucks, authed),
    }
  })

  return { market }
}
