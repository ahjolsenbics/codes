<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { locale, setLocale, type Locale } from '../i18n'
import Flag from './Flag.vue'

const open = ref(false)
const emit = defineEmits<{ open: [] }>()

const langs: { id: Locale; flag: string; label: string }[] = [
  { id: 'zh-CN', flag: 'cn', label: '中文' },
  { id: 'en-US', flag: 'us', label: 'English' },
  { id: 'ru-RU', flag: 'ru', label: 'Русский' },
]

const current = computed(() => langs.find((x) => x.id === locale.value) || langs[0])

function toggle(event: MouseEvent) {
  event.stopPropagation()
  open.value = !open.value
  if (open.value) emit('open')
}

function pick(next: Locale) {
  setLocale(next)
  open.value = false
}

function close() {
  open.value = false
}

onMounted(() => document.addEventListener('click', close))
onUnmounted(() => document.removeEventListener('click', close))

defineExpose({ close })
</script>

<template>
  <div class="lang" @click.stop>
    <button type="button" :class="{ on: open }" :aria-expanded="open" aria-haspopup="listbox" @click="toggle">
      <Flag :code="current.flag" />
      {{ current.label }}
    </button>
    <div v-show="open" class="lang-menu" role="listbox">
      <button
        v-for="item in langs"
        :key="item.id"
        type="button"
        :class="{ on: locale === item.id }"
        @click="pick(item.id)"
      >
        <Flag :code="item.flag" />
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.lang { position: relative; }
.lang > button, .lang-menu button {
  border: 0; background: #f4f7fb; color: #1c2430; border-radius: 8px;
  height: 34px; padding: 0 10px; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 650;
}
.lang > button.on { background: #f4f1ea; }
.lang-menu {
  position: absolute; top: calc(100% + 6px); right: 0; left: auto; z-index: 30;
  width: 148px; display: grid; gap: 2px;
  background: #fff; border: 1px solid #e3e8ef; border-radius: 14px; padding: 6px;
  box-shadow: 0 16px 36px rgba(16, 40, 63, 0.12);
}
.lang-menu button { width: 100%; background: transparent; justify-content: flex-start; }
.lang-menu button.on, .lang-menu button:hover { background: #f4f1ea; }
</style>
