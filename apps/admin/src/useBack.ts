import { useRouter } from 'vue-router'

/** 有浏览历史则回到上一页（含滚动位置），否则进入 fallback。 */
export function useBack(fallback: string | (() => string) = '/') {
  const router = useRouter()

  function back() {
    const to = typeof fallback === 'function' ? fallback() : fallback
    if (typeof window !== 'undefined' && window.history.state?.back != null) {
      router.back()
      return
    }
    router.push(to)
  }

  return { back }
}
