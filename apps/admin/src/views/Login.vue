<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, setAppToken } from '../api'
import { isAppAuthed } from '../auth'
import { t } from '../i18n'
import SiteNav from '../components/SiteNav.vue'

const route = useRoute()
const router = useRouter()
const role = ref<'shipper' | 'driver'>(route.query.role === 'driver' ? 'driver' : 'shipper')
const zone = ref('+86')
const phone = ref('')
const code = ref('')
const password = ref('')
const confirm = ref('')
const name = ref('')
const agree = ref(false)
const mode = ref<'sms' | 'pwd'>('sms')
const registering = computed(() => String(route.query.mode || '') === 'register')
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const hint = ref('')
const wait = ref(0)

onMounted(() => {
  if (isAppAuthed() && !registering.value) {
    const next = route.query.next
    router.replace(typeof next === 'string' && next.startsWith('/') ? next : '/')
  }
})

watch(() => route.query.role, (next) => {
  if (next === 'driver' || next === 'shipper') role.value = next
})

watch(role, () => {
  error.value = ''
})

const dest = computed(() => {
  const next = route.query.next
  if (typeof next === 'string' && next.startsWith('/') && !next.startsWith('//')) return next
  return '/'
})

function failMessage(e: unknown) {
  const raw = e instanceof Error ? e.message : String(e)
  try {
    const parsed = JSON.parse(raw)
    return typeof parsed === 'string' ? parsed : raw
  } catch {
    return raw || t('auth.failed')
  }
}

async function sendCode() {
  if (wait.value > 0) return
  sending.value = true
  error.value = ''
  try {
    const data = await api.smsSend(`${zone.value} ${phone.value}`, zone.value)
    hint.value = t('login.sent').replace('{code}', String(data.demoCode || '000000'))
    wait.value = 60
    const timer = window.setInterval(() => {
      wait.value -= 1
      if (wait.value <= 0) window.clearInterval(timer)
    }, 1000)
  } catch (e) {
    error.value = failMessage(e)
  } finally {
    sending.value = false
  }
}

async function enter() {
  loading.value = true
  error.value = ''
  try {
    if (registering.value) {
      if (password.value !== confirm.value) {
        error.value = t('auth.pwdMismatch')
        return
      }
      if (!agree.value) {
        error.value = t('auth.needAgree')
        return
      }
      const data = await api.register({
        phone: `${zone.value}${phone.value}`,
        zone: zone.value,
        code: code.value,
        password: password.value,
        role: role.value,
        name: name.value,
        agree: true,
      })
      setAppToken(data.token)
    } else if (mode.value === 'pwd') {
      const data = await api.passwordLogin(`${zone.value}${phone.value}`, password.value, role.value)
      setAppToken(data.token)
    } else {
      const data = await api.smsLogin(`${zone.value}${phone.value}`, code.value, role.value)
      setAppToken(data.token)
    }
    await router.push(dest.value)
  } catch (e) {
    error.value = failMessage(e)
  } finally {
    loading.value = false
  }
}

function goMode(next: 'login' | 'register') {
  const query: Record<string, string> = { role: role.value }
  if (typeof route.query.next === 'string' && route.query.next.startsWith('/')) query.next = route.query.next
  if (next === 'register') query.mode = 'register'
  router.replace({ path: '/login', query })
}
</script>

<template>
  <div class="page">
    <SiteNav />
    <div class="wrap split">
      <aside class="story">
        <h1>{{ t('brand.tag') }}</h1>
        <p>{{ t('login.sideBody') }}</p>
      </aside>
      <form class="panel" @submit.prevent="enter">
        <div class="head">
          <h2>{{ registering ? t('auth.register') : t('auth.login') }}</h2>
          <p>{{ registering ? t('auth.registerLead') : t('login.lead') }}</p>
        </div>
        <div class="roles">
          <button type="button" :class="{ on: role === 'shipper' }" @click="role = 'shipper'">{{ t('role.shipper') }}</button>
          <button type="button" :class="{ on: role === 'driver' }" @click="role = 'driver'">{{ t('role.driver') }}</button>
        </div>
        <div v-if="!registering" class="roles">
          <button type="button" :class="{ on: mode === 'sms' }" @click="mode = 'sms'">{{ t('login.useSms') }}</button>
          <button type="button" :class="{ on: mode === 'pwd' }" @click="mode = 'pwd'">{{ t('login.usePwd') }}</button>
        </div>
        <label v-if="registering">
          {{ t('login.name') }}
          <input v-model="name" class="field" :placeholder="t('login.namePh')" autocomplete="name" />
        </label>
        <label>
          {{ t('login.phone') }}
          <div class="phone">
            <select v-model="zone" class="field zone">
              <option value="+86">+86</option>
              <option value="+7">+7</option>
            </select>
            <input v-model="phone" class="field" inputmode="tel" autocomplete="tel" :placeholder="t('login.phonePh')" />
          </div>
        </label>
        <label v-if="registering || mode === 'sms'">
          {{ t('login.code') }}
          <div class="code-row">
            <input v-model="code" class="field" inputmode="numeric" autocomplete="one-time-code" placeholder="000000" />
            <button class="btn btn-line" type="button" :disabled="sending || wait > 0" @click="sendCode">
              {{ wait > 0 ? `${wait}s` : t('login.send') }}
            </button>
          </div>
        </label>
        <label v-if="registering || mode === 'pwd'">
          {{ t('login.password') }}
          <input v-model="password" class="field" type="password" :autocomplete="registering ? 'new-password' : 'current-password'" />
          <small class="hint">{{ t('auth.pwdRule') }}</small>
        </label>
        <label v-if="registering">
          {{ t('login.confirm') }}
          <input v-model="confirm" class="field" type="password" autocomplete="new-password" />
        </label>
        <label v-if="registering" class="agree">
          <input v-model="agree" type="checkbox" />
          <span>{{ t('auth.agree') }}</span>
        </label>
        <button class="btn btn-green" type="submit" :disabled="loading">
          {{ loading ? t('auth.loggingIn') : (registering ? t('auth.register') : t('auth.login')) }}
        </button>
        <p class="switch">
          <button v-if="registering" type="button" @click="goMode('login')">{{ t('auth.toLogin') }}</button>
          <button v-else type="button" @click="goMode('register')">{{ t('auth.toRegister') }}</button>
        </p>
        <p v-if="hint" class="ok">{{ hint }}</p>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 12%, rgba(230, 244, 238, 0.9), transparent 32%),
    radial-gradient(circle at 88% 8%, rgba(234, 241, 254, 0.8), transparent 28%),
    #f5f7fa;
}
.split {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 56px;
  align-items: center;
  padding: 56px 0 88px;
}
.story h1 {
  margin: 0 0 16px;
  font-size: 44px;
  line-height: 1.15;
  letter-spacing: -0.04em;
  color: #1c2430;
}
.story p { margin: 0; color: #5c6b7a; max-width: 38ch; font-size: 16px; line-height: 1.75; }
.panel {
  width: 100%;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 20px;
  padding: 32px;
  display: grid;
  gap: 14px;
  box-shadow: 0 18px 40px rgba(16, 40, 63, 0.06);
}
.head h2 { margin: 0; font-size: 24px; color: #1c2430; }
.head p { margin: 6px 0 0; color: #5c6b7a; font-size: 13px; line-height: 1.5; }
.roles { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.roles button {
  height: 42px;
  border: 1px solid #e3e8ef;
  background: #f7f9fc;
  border-radius: 10px;
  font-weight: 650;
  color: #344054;
}
.roles button.on {
  background: linear-gradient(180deg, #eef6f1, #dceee4);
  color: #0e6a4c;
  border-color: #cde8d8;
}
label { display: grid; gap: 6px; font-size: 13px; color: var(--color-secondary); }
.phone, .code-row { display: grid; gap: 8px; }
.phone { grid-template-columns: 88px 1fr; }
.code-row { grid-template-columns: 1fr auto; }
.zone { padding: 0 8px; }
.agree { grid-template-columns: auto 1fr; align-items: start; gap: 8px; }
.agree input { margin-top: 3px; }
.ok { margin: 0; color: var(--color-success); font-size: 13px; }
.error { margin: 0; color: var(--color-danger); font-size: 13px; }
.hint { margin: 0; color: var(--color-secondary); font-size: 12px; }
.switch { margin: 0; text-align: center; }
.switch button { border: 0; background: none; color: #12805c; font-weight: 700; }
@media (max-width: 1100px) {
  .split { grid-template-columns: 1fr; padding-top: 28px; gap: 28px; }
  .story h1 { font-size: 32px; }
}
@media (max-width: 900px) {
  .split { padding-top: 20px; }
  .story h1 { font-size: 28px; }
}
</style>
