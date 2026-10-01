<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getOpsToken, setAppToken } from '../api'
import { appRoleFromToken, deskPath, isAppAuthed } from '../auth'
import { t } from '../i18n'
import BrandMark from './BrandMark.vue'
import LangSwitch from './LangSwitch.vue'

const route = useRoute()
const authedOps = computed(() => Boolean(getOpsToken()))
const authedApp = computed(() => isAppAuthed())
const myRole = computed(() => appRoleFromToken())
const shipperTo = computed(() => deskPath('shipper'))
const driverTo = computed(() => deskPath('driver'))

function logoutApp() {
  setAppToken(null)
  window.location.href = '/'
}
const open = ref(false)
const lang = ref<{ close: () => void } | null>(null)

const modules = [
  { to: '/board', key: 'nav.market' },
  { to: '/estimate', key: 'nav.estimate' },
  { to: '/ports', key: 'nav.portsLive' },
  { to: '/waybill', key: 'nav.waybill' },
  { to: '/tracking', key: 'nav.tracking' },
  { to: '/match', key: 'nav.match' },
  { to: '/connect', key: 'nav.connect' },
]

function on(path: string) {
  return route.path === path
}

function toggleAbility(event: MouseEvent) {
  event.stopPropagation()
  lang.value?.close()
  open.value = !open.value
}

function close() {
  open.value = false
}

onMounted(() => document.addEventListener('click', close))
onUnmounted(() => document.removeEventListener('click', close))
</script>

<template>
  <header class="nav">
    <div class="wrap bar">
      <router-link to="/" class="brand">
        <BrandMark :size="32" />
        <span>
          <b>{{ t('brand.name') }}</b>
          <small>{{ t('brand.tag') }}</small>
        </span>
      </router-link>
      <nav>
        <div class="drop" @click.stop>
          <button type="button" :class="{ on: open }" :aria-expanded="open" @click="toggleAbility">
            {{ t('nav.ability') }}
          </button>
          <div v-show="open" class="menu">
            <router-link v-for="item in modules" :key="item.to" :to="item.to" @click="open = false">
              {{ t(item.key) }}
            </router-link>
          </div>
        </div>
        <router-link to="/board" :class="{ on: on('/board') }">{{ t('nav.market') }}</router-link>
        <router-link to="/estimate" :class="{ on: on('/estimate') }">{{ t('nav.estimate') }}</router-link>
        <router-link to="/ports" :class="{ on: on('/ports') }">{{ t('nav.portsLive') }}</router-link>
        <router-link to="/about" :class="{ on: on('/about') }">{{ t('nav.about') }}</router-link>
      </nav>
      <div class="right">
        <LangSwitch ref="lang" @open="open = false" />
        <router-link class="ghost" :class="{ on: route.path.startsWith('/app/shipper') }" :to="shipperTo">{{ t('nav.shipperDesk') }}</router-link>
        <router-link class="ghost" :class="{ on: route.path.startsWith('/app/driver') }" :to="driverTo">{{ t('nav.driverDesk') }}</router-link>
        <template v-if="authedApp">
          <span class="role-tag">{{ myRole === 'driver' ? t('role.driver') : t('role.shipper') }}</span>
          <button type="button" class="ghost" @click="logoutApp">{{ t('dash.logout') }}</button>
        </template>
        <template v-else>
          <router-link class="ghost" to="/login">{{ t('auth.login') }}</router-link>
          <router-link class="enter" to="/login?mode=register">{{ t('auth.register') }}</router-link>
        </template>
        <router-link class="ops" :to="authedOps ? '/console' : '/ops/login'">{{ t('nav.console') }}</router-link>
      </div>
    </div>
  </header>
</template>

<style scoped>
.nav {
  position: sticky; top: 0; z-index: 80;
  background: rgba(255,255,255,.94); backdrop-filter: blur(12px);
  border-bottom: 1px solid #e3e8ef;
}
.bar { height: 68px; display: flex; align-items: center; gap: 18px; }
.brand { display: flex; align-items: center; gap: 10px; min-width: 168px; color: #1c2430; }
.brand b { display: block; font-size: 15px; line-height: 1.1; }
.brand small { display: block; color: #5c6b7a; font-size: 11px; }
nav { display: flex; gap: 4px; flex: 1; align-items: center; }
nav > a, .drop > button {
  border: 0; background: transparent; padding: 8px 14px; font-size: 16px; color: #3d4a5c; border-radius: 8px; font-weight: 650;
  white-space: nowrap; flex: none;
}
nav > a.on, nav > a:hover, .drop > button.on { color: #1c2430; background: #f4f1ea; }
.drop { position: relative; }
.menu {
  position: absolute; top: calc(100% + 6px); left: 0; z-index: 20;
  min-width: 168px; display: grid;
  background: #fff; border: 1px solid #e3e8ef; border-radius: 14px; padding: 6px;
  box-shadow: 0 16px 36px rgba(16, 40, 63, 0.12);
}
.menu a { display: block; padding: 9px 14px; border-radius: 10px; font-size: 14px; font-weight: 650; color: #1c2430; }
.menu a:hover { background: #f4f7fb; }
.right { display: flex; align-items: center; gap: 8px; }
.ghost, .enter, .ops {
  display: inline-flex; align-items: center; justify-content: center;
  height: 36px; padding: 0 14px; border-radius: 10px;
  font-size: 16px; font-weight: 650; letter-spacing: 0;
}
.enter {
  background: linear-gradient(180deg, #eef6f1, #dceee4);
  color: #0e6a4c;
  border: 1px solid #cde8d8;
}
.enter:hover { background: linear-gradient(180deg, #e6f4ee, #d0e8d9); }
.ops {
  background: linear-gradient(180deg, #f7f4ee, #efe6d4);
  color: #8d6a32;
  border: 1px solid #ead9b6;
}
.ops:hover { background: linear-gradient(180deg, #f4f1ea, #eadfc8); }
.ghost {
  border: 1px solid #e3e8ef;
  background: #fff;
  color: #344054;
}
.ghost:hover { background: #f7f9fc; }
.ghost.on { border-color: #12395f; color: #12395f; background: #f4f7fb; }
.role-tag {
  display: inline-flex; align-items: center; height: 28px; padding: 0 10px;
  border-radius: 999px; background: #e6f4ee; color: #0e6a4c; font-size: 12px; font-weight: 700;
}
@media (max-width: 1366px) {
  .bar { gap: 12px; }
  nav > a, .drop > button { font-size: 15px; padding: 8px 10px; }
  .ghost, .enter, .ops { font-size: 15px; padding: 0 12px; }
}
@media (max-width: 1180px) {
  .bar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    height: auto;
    padding: 8px 0 10px;
    gap: 6px 12px;
  }
  .brand { min-width: 0; }
  .brand small { display: none; }
  .right { grid-column: 2; grid-row: 1; }
  nav {
    grid-column: 1 / -1;
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none;
  }
  nav::-webkit-scrollbar { display: none; }
  nav > a, .drop > button { font-size: 15px; padding: 8px 12px; }
  .menu { position: fixed; top: 108px; left: 16px; right: 16px; width: auto; }
}
@media (max-width: 720px) {
  .enter { padding: 0 10px; }
  .menu { left: 12px; right: 12px; top: 96px; }
  .ghost, .enter, .ops { font-size: 14px; height: 34px; }
}
</style>
