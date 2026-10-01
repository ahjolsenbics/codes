<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AbilityPage from '../components/AbilityPage.vue'
import Pager from '../components/Pager.vue'
import TripCard from '../components/TripCard.vue'
import TripModal from '../components/TripModal.vue'
import { money, orderStatus, place, tone } from '../fmt'
import { isAppAuthed } from '../auth'
import { t, tf } from '../i18n'
import { PUBLIC_BILLS, billCreated } from '../siteData'
import { usePager } from '../usePager'

const route = useRoute()
const router = useRouter()
const q = ref(String(route.query.q || ''))
const filter = ref(String(route.query.status || ''))
const view = ref(route.query.view === 'list' ? 'list' : 'grid')
const openId = ref('')
const authed = isAppAuthed
const statuses = ['in_transit', 'loading', 'wait_load', 'wait_confirm', 'completed', 'dealt']

watch(() => route.query, (query) => {
  if (query.id) {
    openId.value = String(query.id)
    const next: Record<string, string> = {}
    if (query.q) next.q = String(query.q)
    if (query.status) next.status = String(query.status)
    if (query.view) next.view = String(query.view)
    router.replace({ path: '/tracking', query: next })
    return
  }
  q.value = String(query.q || '')
  filter.value = String(query.status || '')
  view.value = query.view === 'list' ? 'list' : 'grid'
}, { immediate: true })

watch([q, filter, view], () => {
  const query: Record<string, string> = {}
  if (q.value) query.q = q.value
  if (filter.value) query.status = filter.value
  if (view.value === 'list') query.view = 'list'
  const same = String(route.query.q || '') === (query.q || '')
    && String(route.query.status || '') === (query.status || '')
    && String(route.query.view || '') === (query.view || '')
  if (!same && !route.query.id) router.replace({ path: '/tracking', query })
})

function openBill(id: string) {
  openId.value = id
}

const bills = computed(() => PUBLIC_BILLS.filter((b) => {
  if (filter.value && b.status !== filter.value) return false
  const s = q.value.trim().toUpperCase()
  if (s && !b.id.includes(s) && !b.origin.includes(q.value) && !b.dest.includes(q.value)) return false
  return true
}))
const pager = usePager(bills, 8)
watch([q, filter], () => pager.reset())
</script>

<template>
  <AbilityPage :title="t('nav.tracking')" :lead="t('mod.tracking.lead')" back-to="/">
    <div class="toolbar">
      <input v-model="q" class="field search" :placeholder="t('trip.search')" />
      <div class="seg">
        <button type="button" :class="{ on: filter === '' }" @click="filter = ''">{{ t('trip.all') }}</button>
        <button v-for="s in statuses" :key="s" type="button" :class="{ on: filter === s }" @click="filter = s">{{ orderStatus(s) }}</button>
      </div>
      <div class="seg">
        <button type="button" :class="{ on: view === 'grid' }" @click="view = 'grid'">{{ t('trip.grid') }}</button>
        <button type="button" :class="{ on: view === 'list' }" @click="view = 'list'">{{ t('trip.table') }}</button>
      </div>
    </div>
    <p class="count">{{ tf('trip.count', { n: bills.length, m: PUBLIC_BILLS.length }) }}</p>
    <div v-if="view === 'grid'" class="cards">
      <TripCard v-for="b in pager.items" :key="b.id" :bill="b" :active="openId === b.id" @open="openBill(b.id)" />
    </div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>{{ t('col.order') }}</th>
            <th>{{ t('col.lane') }}</th>
            <th>{{ t('col.status') }}</th>
            <th>{{ t('col.freight') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in pager.items" :key="b.id" :class="{ on: openId === b.id }" @click="openBill(b.id)">
            <td><b>{{ b.id }}</b><small>{{ billCreated(b) }}</small></td>
            <td>{{ place(b.origin) }} → {{ place(b.dest) }}</td>
            <td><span class="pill" :class="tone(b.status)">{{ orderStatus(b.status) }}</span></td>
            <td>{{ authed() ? money(b.freight) : t('auth.needLogin') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager v-model:page="pager.page" :pages="pager.pages" :total="pager.total" :size="pager.size" />
    <p v-if="!bills.length" class="empty">{{ t('tool.empty') }}</p>
    <TripModal v-if="openId" :id="openId" kind="tracking" @close="openId = ''" />
  </AbilityPage>
</template>

<style scoped>
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 10px; }
.search { max-width: 220px; }
.seg button { white-space: nowrap; }
.count { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.table-wrap { background: #fff; border: 1px solid var(--line); border-radius: 16px; overflow: auto; }
tr { cursor: pointer; }
tr.on td, tr:hover td { background: #f4f7fb; }
td small { display: block; color: var(--muted); font-size: 12px; }
.empty { color: var(--muted); }
@media (max-width: 560px) { .cards { grid-template-columns: 1fr; } .search { max-width: none; width: 100%; } }
</style>
