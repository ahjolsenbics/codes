<script setup lang="ts">
import { useRoute } from 'vue-router'
import { t } from '../i18n'

defineProps<{ compact?: boolean }>()
const route = useRoute()
</script>

<template>
  <div class="gate" :class="{ compact }">
    <b>{{ t('auth.gateTitle') }}</b>
    <p v-if="!compact">{{ t('auth.gateBody') }}</p>
    <div class="acts">
      <router-link class="btn btn-navy btn-sm" :to="{ path: '/login', query: { role: String(route.query.role || 'shipper'), next: route.fullPath } }">{{ t('auth.login') }}</router-link>
      <router-link class="btn btn-line btn-sm" :to="{ path: '/login', query: { mode: 'register', role: String(route.query.role || 'shipper'), next: route.fullPath } }">{{ t('auth.register') }}</router-link>
    </div>
  </div>
</template>

<style scoped>
.gate {
  border: 1px dashed #c5d0dc;
  background: #f7f9fc;
  border-radius: 14px;
  padding: 16px;
  display: grid;
  gap: 8px;
}
.gate.compact { padding: 10px 12px; }
.gate b { color: #10283f; }
.gate p { margin: 0; color: #5c6b7a; font-size: 13px; line-height: 1.5; }
.acts { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
