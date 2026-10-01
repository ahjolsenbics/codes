<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, setOpsToken } from '../api'
import { t } from '../i18n'
import BrandMark from '../components/BrandMark.vue'
import LangSwitch from '../components/LangSwitch.vue'

const router = useRouter()
const account = ref('13800001000')
const password = ref('Yunmm@2026')
const loading = ref(false)
const error = ref('')

async function enter() {
  loading.value = true
  error.value = ''
  const acc = account.value.replace(/\s/g, '')
  const okAcc = acc.includes('13800001000') || account.value.includes('王敏')
  if (!okAcc || password.value !== 'Yunmm@2026') {
    error.value = '账号或密码不正确'
    loading.value = false
    return
  }
  try {
    const data = await api.demoLogin('admin')
    setOpsToken(data.token)
    await router.push('/console')
  } catch (e) {
    setOpsToken('demo-admin')
    console.error('运营接口不可用，进入演示后台', e)
    await router.push('/console')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="ops">
    <header>
      <router-link to="/" class="brand">
        <BrandMark :size="28" />
        <span>{{ t('brand.name') }}</span>
      </router-link>
      <LangSwitch />
    </header>
    <main>
      <p class="kicker">{{ t('ops.bench') }}</p>
      <h1>{{ t('ops.hero') }}</h1>
      <form @submit.prevent="enter">
        <label>
          {{ t('ops.account') }}
          <input v-model="account" autocomplete="username" />
        </label>
        <label>
          {{ t('ops.password') }}
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <button class="btn btn-green" type="submit" :disabled="loading">
          {{ loading ? t('auth.loggingIn') : t('auth.login') }}
        </button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <small>13800001000 · Yunmm@2026</small>
    </main>
  </div>
</template>

<style scoped>
.ops {
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 0%, rgba(230, 244, 238, 0.8), transparent 34%),
    radial-gradient(circle at 90% 8%, rgba(253, 243, 224, 0.7), transparent 30%),
    #f5f7fa;
  display: grid;
  grid-template-rows: 64px 1fr;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(255,255,255,.92);
  border-bottom: 1px solid #e3e8ef;
}
header a.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; color: #1c2430; }
main {
  width: min(420px, calc(100% - 32px));
  margin: auto;
  padding: 32px;
  background: #fff;
  border: 1px solid #e3e8ef;
  border-radius: 20px;
  box-shadow: 0 18px 40px rgba(16, 40, 63, 0.06);
}
.kicker { margin: 0 0 8px; color: #12805c; font-size: 13px; font-weight: 700; letter-spacing: .06em; }
h1 { font-size: 26px; font-weight: 650; margin: 0 0 24px; color: #1c2430; }
form { display: grid; gap: 14px; }
label { display: grid; gap: 6px; font-size: 13px; color: #5c6b7a; }
input {
  height: 44px;
  border: 1px solid #e3e8ef;
  border-radius: 10px;
  background: #f7f9fc;
  color: #1c2430;
  padding: 0 12px;
}
input:focus { outline: 3px solid rgba(18, 128, 92, 0.14); border-color: #12805c; background: #fff; }
.btn { margin-top: 8px; width: 100%; }
.error { color: #b42318; }
small { display: block; margin-top: 14px; color: #98a2b3; font-size: 12px; }
</style>
