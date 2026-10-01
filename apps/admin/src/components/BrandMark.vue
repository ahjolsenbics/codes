<script setup lang="ts">
withDefaults(defineProps<{
  size?: number
  onDark?: boolean
}>(), { size: 32, onDark: false })
</script>

<template>
  <svg
    class="mark"
    :width="size"
    :height="size"
    viewBox="0 0 48 48"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    focusable="false"
  >
    <!-- 运满满：海军蓝方标 + 口岸门廊 -->
    <rect
      x="1"
      y="1"
      width="46"
      height="46"
      rx="11"
      fill="#0B2540"
      :stroke="onDark ? 'rgba(255,255,255,0.22)' : 'none'"
      stroke-width="1.2"
    />
    <path
      fill="#fff"
      d="M14 37.5V17.2C14 11.8 18.2 8.2 24 8.2s10 3.6 10 9V37.5h-5.8V18.4c0-2.6-1.9-4.1-4.2-4.1s-4.2 1.5-4.2 4.1v19.1H14z"
    />
    <rect x="17.6" y="22.8" width="12.8" height="5" rx="2.5" fill="#fff" />
  </svg>
</template>

<style scoped>
.mark { display: block; flex: none; }
</style>
