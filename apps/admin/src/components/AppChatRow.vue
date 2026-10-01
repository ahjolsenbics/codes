<script setup lang="ts">
import { computed } from 'vue'
import { laneText, party } from '../fmt'
import Flag from './Flag.vue'
import { locale, t } from '../i18n'

const props = defineProps<{ item: Record<string, any> }>()
defineEmits<{ click: [] }>()

const name = computed(() => party(props.item.peerName) || t('app.chatPeer'))
const initial = computed(() => name.value.slice(0, 1))
const last = computed(() => {
  const m = props.item.last
  if (!m) return t('common.emptyGeneric')
  if (locale.value === 'en-US') return String(m.en || m.body || t('common.emptyGeneric'))
  if (locale.value === 'ru-RU') return String(m.ru || m.translated || m.body || t('common.emptyGeneric'))
  return String(m.zh || m.body || t('common.emptyGeneric'))
})
const hue = computed(() => {
  const s = name.value
  let n = 0
  for (let i = 0; i < s.length; i++) n = (n + s.charCodeAt(i) * 17) % 360
  return n
})
const time = computed(() => {
  const raw = props.item.last?.at
  if (!raw) return ''
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return ''
  const now = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  if (d.toDateString() === now.toDateString()) return `${hh}:${mm}`
  return `${d.getMonth() + 1}/${d.getDate()}`
})
</script>

<template>
  <article class="row" @click="$emit('click')">
    <div class="avatar" :style="{ background: `hsl(${hue} 28% 32%)` }">{{ initial }}</div>
    <div class="mid">
      <div class="line">
        <b>{{ name }}</b>
        <time v-if="time">{{ time }}</time>
        <i v-else-if="item.unread" class="dot" />
      </div>
      <p v-if="item.lane" class="lane"><Flag :code="item.originCountry" /><Flag :code="item.destCountry" />{{ laneText(item.lane) }}</p>
      <p class="last">{{ last }}</p>
    </div>
  </article>
</template>

<style scoped>
.row {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 12px;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid #eef2f6;
  cursor: pointer;
}
.row:last-child { border-bottom: 0; }
.row:hover { background: #f7f9fc; }
.avatar {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 18px;
}
.line { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; }
.line b { font-size: 15px; font-weight: 650; }
time { color: #8a958c; font-size: 11px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #1f4b99; justify-self: end; }
.lane, .last { margin: 2px 0 0; font-size: 12px; color: #667085; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lane { display: flex; align-items: center; gap: 5px; color: #1f4b99; font-weight: 600; }
</style>
