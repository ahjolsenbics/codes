import { computed, reactive, ref, watch, type Ref } from 'vue'

/** 把长列表切成固定页，页码超出时自动收回。 */
export function usePager(source: Ref<any[]>, size = 8) {
  const page = ref(1)
  const pages = computed(() => Math.max(1, Math.ceil(source.value.length / size)))
  const items = computed(() => {
    const p = Math.min(Math.max(1, page.value), pages.value)
    const start = (p - 1) * size
    return source.value.slice(start, start + size)
  })
  const total = computed(() => source.value.length)

  watch(pages, (n) => {
    if (page.value > n) page.value = n
  })

  return reactive({
    page,
    pages,
    items,
    total,
    size,
    reset() {
      page.value = 1
    },
  })
}
