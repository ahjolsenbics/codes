<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, setOpsToken } from '../api'
import { t } from '../i18n'
import AppGlyph from '../components/AppGlyph.vue'
import BrandMark from '../components/BrandMark.vue'
import LangSwitch from '../components/LangSwitch.vue'

const router = useRouter()
const route = useRoute()
const operator = ref('王敏')
const menuOpen = ref(false)

watch(() => route.path, () => { menuOpen.value = false })

onMounted(async () => {
  try {
    const me = await api.me()
    if (me?.name) operator.value = me.name
  } catch (e) {
    console.error('运营身份读取失败', e)
  }
})

const groups = [
  {
    key: 'ops.gOps',
    items: [
      { to: '/console', key: 'dash.title', icon: 'home' },
      { to: '/console/users', key: 'nav.users', icon: 'me' },
      { to: '/console/kyc', key: 'nav.kyc', icon: 'shield' },
      { to: '/console/loads', key: 'nav.loads', icon: 'loads' },
      { to: '/console/orders', key: 'nav.orders', icon: 'orders' },
    ],
  },
  {
    key: 'ops.gRisk',
    items: [
      { to: '/console/deposits', key: 'nav.deposits', icon: 'wallet' },
      { to: '/console/disputes', key: 'nav.disputes', icon: 'chat' },
      { to: '/console/blacklist', key: 'nav.blacklist', icon: 'ban' },
    ],
  },
  {
    key: 'ops.gCorr',
    items: [{ to: '/console/ports', key: 'nav.ports', icon: 'flag' }],
  },
  {
    key: 'ops.gSys',
    items: [
      { to: '/console/config', key: 'nav.config', icon: 'gear' },
      { to: '/console/i18n', key: 'nav.i18n', icon: 'globe' },
      { to: '/console/announcements', key: 'nav.ann', icon: 'bell' },
      { to: '/console/audit', key: 'nav.audit', icon: 'orders' },
    ],
  },
]

function logout() {
  setOpsToken(null)
  router.push('/ops/login')
}
</script>

<template>
  <div class="layout">
    <div v-if="menuOpen" class="shade" @click="menuOpen = false" />
    <aside :class="{ open: menuOpen }">
      <router-link to="/" class="brand">
        <BrandMark :size="28" on-dark />
        <span>
          <b>{{ t('brand.name') }}</b>
          <small>{{ t('ops.bench') }}</small>
        </span>
      </router-link>
      <div v-for="g in groups" :key="g.key" class="group">
        <small>{{ t(g.key) }}</small>
        <router-link
          v-for="item in g.items"
          :key="item.to"
          :to="item.to"
          :class="{ on: route.path === item.to }"
        >
          <AppGlyph :name="item.icon" />
          {{ t(item.key) }}
        </router-link>
      </div>
    </aside>
    <section>
      <header>
        <div class="who">
          <button class="menu-btn inner" type="button" aria-label="菜单" @click="menuOpen = !menuOpen">☰</button>
          <i>{{ operator.slice(0, 1) }}</i>
          <div>
            <b>{{ operator }}</b>
            <span>{{ t('dash.welcome') }}</span>
          </div>
        </div>
        <div class="acts">
          <LangSwitch />
          <router-link to="/board">{{ t('nav.market') }}</router-link>
          <button type="button" @click="logout">{{ t('dash.logout') }}</button>
        </div>
      </header>
      <main><router-view /></main>
    </section>
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; display: grid; grid-template-columns: 248px minmax(0, 1fr); }
aside { background: var(--navy-2); color: #c8d6e6; padding: 20px 14px; }
.menu-btn {
  display: none;
  width: 36px; height: 36px;
  border: 1px solid var(--line); border-radius: 9px;
  background: #fff; font-size: 18px; line-height: 1;
}
.shade { display: none; }
.brand { display: flex; align-items: center; gap: 10px; color: #fff; padding: 4px 4px 22px; text-decoration: none; }
.brand b { display: block; font-weight: 750; font-size: 16px; line-height: 1.2; }
.brand small { display: block; color: #6fc59b; font-weight: 500; font-size: 12px; }
.group { margin-bottom: 18px; }
.group small {
  display: block;
  padding: 6px 12px;
  color: rgba(200, 214, 230, 0.5);
  font-size: 11px;
  letter-spacing: 0.1em;
}
aside a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 9px;
  color: #c8d6e6;
  font-size: 14px;
}
aside a.on { background: rgba(255, 255, 255, 0.12); color: #fff; font-weight: 650; }
aside a:hover { background: rgba(255, 255, 255, 0.07); color: #fff; }
section { background: var(--paper); min-width: 0; }
header {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: #fff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 10;
}
header b { display: block; font-size: 15px; }
header span { color: var(--muted); font-size: 13px; }
.who { display: flex; align-items: center; gap: 10px; }
.who i {
  width: 36px; height: 36px; border-radius: 10px;
  display: grid; place-items: center;
  background: var(--navy); color: #f3d7a1; font-style: normal; font-weight: 750;
}
.acts { display: flex; gap: 10px; align-items: center; }
.acts > a, .acts > button {
  height: 36px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: #fff;
  display: inline-flex;
  align-items: center;
  font-size: 14px;
  color: var(--ink-soft);
}
.acts > a:hover, .acts > button:hover { border-color: #c9d2e0; }
main { padding: 26px 28px 56px; min-width: 0; }
@media (max-width: 1100px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  .menu-btn { display: inline-grid; place-items: center; }
  .shade {
    display: block;
    position: fixed; inset: 0;
    background: rgba(12, 24, 40, 0.4);
    z-index: 30;
  }
  aside {
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: min(248px, 86vw);
    z-index: 40;
    transform: translateX(-100%);
    transition: transform .2s ease;
    overflow: auto;
  }
  aside.open { transform: none; }
  header { height: auto; min-height: 68px; padding: 10px 16px; flex-wrap: wrap; gap: 8px; }
  .acts { flex-wrap: wrap; justify-content: flex-end; }
  main { padding: 16px 16px 48px; }
}
</style>
