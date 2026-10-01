<script setup lang="ts">
import { computed } from 'vue'
import { setAppToken } from '../api'
import { kycLabel, party, tone } from '../fmt'
import { t } from '../i18n'
import BrandMark from './BrandMark.vue'
import LangSwitch from './LangSwitch.vue'

const props = defineProps<{
  role: 'shipper' | 'driver'
  name?: string
  kyc?: string
  credit?: number
  unread?: number
  syncedAt?: string
  showBack?: boolean
  title?: string
}>()

const emit = defineEmits<{ back: []; notes: [] }>()

const deskTitle = computed(() => (props.role === 'driver' ? t('work.driverDesk') : t('work.shipperDesk')))

function logout() {
  setAppToken(null)
  window.location.href = '/'
}
</script>

<template>
  <header class="wnav">
    <div class="wrap bar">
      <button v-if="showBack" class="back" type="button" @click="emit('back')">‹ {{ t('common.back') }}</button>
      <router-link v-else to="/" class="brand" :title="t('work.backSite')">
        <BrandMark :size="30" />
        <span>
          <b>{{ t('brand.name') }}</b>
          <small>{{ deskTitle }}</small>
        </span>
      </router-link>
      <strong v-if="showBack" class="screen-title">{{ title }}</strong>
      <p v-else class="who">
        <b>{{ party(name) || deskTitle }}</b>
        <span>{{ t('app.credit') }} {{ credit ?? '—' }}</span>
        <em v-if="kyc" class="pill" :class="tone(kyc)">{{ kycLabel(kyc) }}</em>
      </p>
      <div class="right">
        <small v-if="syncedAt" class="sync">{{ t('work.synced') }} {{ syncedAt }}</small>
        <button class="bell" type="button" @click="emit('notes')">
          {{ t('app.notes') }}<i v-if="unread">{{ unread }}</i>
        </button>
        <LangSwitch />
        <router-link class="ghost" to="/">{{ t('work.backSite') }}</router-link>
        <button type="button" class="ghost" @click="logout">{{ t('dash.logout') }}</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.wnav {
  position: sticky;
  top: 0;
  z-index: 80;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e3e8ef;
}
.bar {
  min-height: 64px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 168px;
  color: #1c2430;
}
.brand b { display: block; font-size: 15px; line-height: 1.1; }
.brand small { display: block; color: #5c6b7a; font-size: 11px; }
.who { margin: 0; flex: 1; min-width: 0; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.who b { font-size: 16px; }
.who span { color: #5c6b7a; font-size: 13px; }
.screen-title { flex: 1; font-size: 16px; }
.right { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.sync { color: #8ea0b2; font-size: 12px; white-space: nowrap; }
.ghost, .back, .bell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid #e3e8ef;
  background: #fff;
  color: #344054;
  font-size: 14px;
  font-weight: 650;
}
.back { border: 0; background: transparent; font-size: 15px; }
.bell { position: relative; }
.bell i {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 99px;
  background: #c2410c;
  color: #fff;
  font-size: 10px;
  font-style: normal;
  line-height: 16px;
}
@media (max-width: 900px) {
  .sync, .who span { display: none; }
  .brand small { display: none; }
  .ghost { padding: 0 10px; font-size: 13px; }
}
</style>
