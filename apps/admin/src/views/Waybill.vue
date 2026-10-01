<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AbilityPage from '../components/AbilityPage.vue'
import Pager from '../components/Pager.vue'
import TripCard from '../components/TripCard.vue'
import TripModal from '../components/TripModal.vue'
import { orderStatus } from '../fmt'
import { t, tf } from '../i18n'
import { PUBLIC_BILLS } from '../siteData'
import { usePager } from '../usePager'

const route = useRoute()
const router = useRouter()
const q = ref(String(route.query.q || ''))
const filter = ref(String(route.query.status || ''))
const openId = ref('')
const statuses = ['in_transit', 'loading', 'wait_load', 'wait_confirm', 'completed', 'dealt']

watch(() => route.query, (query) => {
  if (query.id) {
    openId.value = String(query.id)
    const next: Record<string, string> = {}
    if (query.q) next.q = String(query.q)
    if (query.status) next.status = String(query.status)
    router.replace({ path: '/waybill', query: next })
    return
  }
  q.value = String(query.q || '')
  filter.value = String(query.status || '')
}, { immediate: true })

watch([q, filter], () => {
  const query: Record<string, string> = {}
  if (q.value) query.q = q.value
  if (filter.value) query.status = filter.value
  const same = String(route.query.q || '') === (query.q || '')
    && String(route.query.status || '') === (query.status || '')
  if (!same && !route.query.id) router.replace({ path: '/waybill', query })
})

function openBill(id: string) {
  openId.value = id
}

const bills = computed(() => PUBLIC_BILLS.filter((b) => {
  if (filter.value && b.status !== filter.value) return false
  const s = q.value.trim().toUpperCase()
  if (s && !b.id.includes(s)) return false
  return true
}))
const pager = usePager(bills, 8)
watch([q, filter], () => pager.reset())
</script>

<template>
  <AbilityPage :title="t('nav.waybill')" :lead="t('mod.waybill.lead')" back-to="/">
    <div class="toolbar">
      <input v-model="q" class="field search" :placeholder="t('site.billPh')" />
      <div class="seg">
        <button type="button" :class="{ on: filter === '' }" @click="filter = ''">{{ t('trip.all') }}</button>
        <button v-for="s in statuses" :key="s" type="button" :class="{ on: filter === s }" @click="filter = s">{{ orderStatus(s) }}</button>
      </div>
    </div>
    <p class="count">{{ tf('trip.count', { n: bills.length, m: PUBLIC_BILLS.length }) }}</p>
    <div class="cards">
      <TripCard v-for="b in pager.items" :key="b.id" :bill="b" :active="openId === b.id" @open="openBill(b.id)" />
    </div>
    <Pager v-model:page="pager.page" :pages="pager.pages" :total="pager.total" :size="pager.size" />
    <p v-if="!bills.length" class="empty">{{ t('site.billMiss') }}</p>
    <TripModal v-if="openId" :id="openId" kind="waybill" @close="openId = ''" />
  </AbilityPage>
</template>

<style scoped>
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 10px; }
.search { max-width: 220px; }
.count { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.empty { color: var(--muted); }
@media (max-width: 560px) { .cards { grid-template-columns: 1fr; } .search { max-width: none; width: 100%; } }
</style>
