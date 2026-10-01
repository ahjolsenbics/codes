import { onMounted, ref } from 'vue'
import { api } from './api'
import { FALLBACK_MARKET } from './catalog'

/** 公开页货盘：接口失败时仍用本地盘口，避免页面空掉。 */
export function useMarket() {
  const market = ref<any>({ ...FALLBACK_MARKET })

  onMounted(async () => {
    try {
      const live = await api.market()
      if (live) {
        market.value = {
          ...FALLBACK_MARKET,
          ...live,
          items: live.items?.length ? live.items : FALLBACK_MARKET.items,
          trucks: live.trucks?.length ? live.trucks : FALLBACK_MARKET.trucks,
          ports: live.ports?.length ? live.ports : FALLBACK_MARKET.ports,
          corridors: live.corridors?.length ? live.corridors : FALLBACK_MARKET.corridors,
        }
      }
    } catch (e) {
      console.error('货盘展示数据加载失败，使用演示盘口', e)
    }
  })

  return { market }
}
