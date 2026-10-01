<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ name?: string }>()
const file = computed(() => {
  const name = props.name || 'wechat'
  if (name === 'wechat' || name === 'alipay' || name === 'unionpay' || name === 'kaspi') return name
  return 'wechat'
})
</script>

<template>
  <img class="mark" :src="`/media/pay/${file}.svg`" alt="" />
</template>

<style scoped>
.mark {
  height: 26px;
  width: auto;
  display: block;
  flex: none;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 0 0 1px rgba(28, 36, 48, 0.1);
}
</style>
