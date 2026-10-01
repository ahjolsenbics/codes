<script setup lang="ts">
import { t } from '../i18n'
import SiteBack from '../components/SiteBack.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SiteNav from '../components/SiteNav.vue'

const endpoints = [
  ['POST', '/api/v1/auth/demo-login', 'api.e1'],
  ['GET', '/api/v1/public/market', 'api.e2'],
  ['GET', '/api/v1/loads', 'api.e3'],
  ['POST', '/api/v1/loads/{id}/quotes', 'api.e4'],
  ['POST', '/api/v1/loads/{id}/grab', 'api.e5'],
  ['POST', '/api/v1/orders/{id}/actions', 'api.e6'],
  ['GET', '/api/v1/orders/{id}/track', 'api.e7'],
  ['POST', '/api/v1/estimate', 'api.e8'],
]
</script>

<template>
  <div>
    <SiteNav />
    <section class="hero">
      <div class="wrap">
        <SiteBack to="/connect" :label="t('common.back')" />
        <p class="kicker">developer.timocom.com · ati.su/landings/api-ati</p>
        <h1>{{ t('api.pageTitle') }}</h1>
        <p>{{ t('api.pageLead') }}</p>
        <code>Authorization: Bearer demo.{role}.{userId}</code>
      </div>
    </section>
    <main class="wrap">
      <table>
        <thead>
            <tr><th>{{ t('col.method') }}</th><th>Path</th><th>{{ t('api.meaning') }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in endpoints" :key="e[1]">
            <td><span class="pill">{{ e[0] }}</span></td>
            <td><code>{{ e[1] }}</code></td>
            <td>{{ t(e[2]) }}</td>
          </tr>
        </tbody>
      </table>
      <p class="note">{{ t('api.note') }}</p>
    </main>
    <SiteFooter />
  </div>
</template>

<style scoped>
.hero { background: #102c48; color: #fff; padding: 64px 0 48px; }
.kicker { color: #9db8a6; letter-spacing: 0.08em; font-size: 12px; }
h1 { font-size: 36px; margin: 8px 0; }
.hero p { color: #c5d0dc; max-width: 640px; }
code { background: rgba(255,255,255,.08); padding: 8px 10px; border-radius: 6px; display: inline-block; }
main { padding: 32px 0 64px; }
table { width: 100%; border-collapse: collapse; background: #fff; }
th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--color-border); font-size: 13px; }
td code { background: #f5f7fa; color: var(--color-primary); }
.note { color: var(--color-secondary); }
</style>
