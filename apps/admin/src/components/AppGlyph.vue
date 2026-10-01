<script setup lang="ts">
defineProps<{ name: string }>()
</script>

<template>
  <svg class="g" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-if="name === 'home'" d="M4 10.5 12 4l8 6.5V20H15v-6H9v6H4z" />
    <g v-else-if="name === 'loads'">
      <rect x="3" y="8" width="11" height="8" rx="1.2" />
      <path d="M14 10h4l3 3v3h-7" />
      <circle cx="7.5" cy="17.5" r="1.4" />
      <circle cx="17.5" cy="17.5" r="1.4" />
    </g>
    <g v-else-if="name === 'orders'">
      <path d="M7 4h10v16H7z" />
      <path d="M10 8h4M10 12h4M10 16h2" />
    </g>
    <path v-else-if="name === 'chat'" d="M6 5h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H10l-4 3v-3H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z" />
    <g v-else-if="name === 'me'">
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5 19c1.4-3.2 3.4-5 7-5s5.6 1.8 7 5" />
    </g>
    <path v-else-if="name === 'plus'" d="M12 6v12M6 12h12" />
    <path v-else-if="name === 'calc'" d="M6 4h12v16H6zM9 8h6M9 12h2M13 12h2M9 16h2M13 16h2" />
    <path v-else-if="name === 'flag'" d="M5 21V4m0 1h10l-2.4 3.4L15 12H5" />
    <g v-else-if="name === 'wallet'">
      <rect x="4" y="7" width="16" height="11" rx="2" />
      <path d="M4 10h16M16 13.5h2" />
    </g>
    <path v-else-if="name === 'shield'" d="M12 3 19 6v6c0 4-3 7-7 9-4-2-7-5-7-9V6z" />
    <path v-else-if="name === 'star'" d="M12 4 14.2 9.2 20 10l-4 3.8.9 5.2L12 16.8 7.1 19l.9-5.2L4 10l5.8-.8z" />
    <g v-else-if="name === 'gear'">
      <path d="M12.2 3h-.4a2 2 0 0 0-2 2v.2a2 2 0 0 1-1 1.7l-.4.2a2 2 0 0 1-2 0l-.2-.1a2 2 0 0 0-2.7.7l-.2.4a2 2 0 0 0 .7 2.7l.2.1a2 2 0 0 1 1 1.7v.5a2 2 0 0 1-1 1.7l-.2.1a2 2 0 0 0-.7 2.7l.2.4a2 2 0 0 0 2.7.7l.2-.1a2 2 0 0 1 2 0l.4.3a2 2 0 0 1 1 1.7V19a2 2 0 0 0 2 2h.4a2 2 0 0 0 2-2v-.2a2 2 0 0 1 1-1.7l.4-.3a2 2 0 0 1 2 0l.2.1a2 2 0 0 0 2.7-.7l.2-.4a2 2 0 0 0-.7-2.7l-.2-.1a2 2 0 0 1-1-1.7v-.5a2 2 0 0 1 1-1.7l.2-.1a2 2 0 0 0 .7-2.7l-.2-.4a2 2 0 0 0-2.7-.7l-.2.1a2 2 0 0 1-2 0l-.4-.2a2 2 0 0 1-1-1.7V5a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="2.6" />
    </g>
    <path v-else-if="name === 'ban'" d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM7 17 17 7" />
    <g v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="8" />
      <path d="M4 12h16M12 4c2.2 2.2 3.3 5 3.3 8s-1.1 5.8-3.3 8c-2.2-2.2-3.3-5-3.3-8S9.8 6.2 12 4z" />
    </g>
    <path v-else-if="name === 'bell'" d="M6 16h12l-1.2-2.2V11a4.8 4.8 0 0 0-9.6 0v2.8L6 16zM10 16a2 2 0 0 0 4 0" />
    <path v-else-if="name === 'route'" d="M6 16c2.5-6 4-6 6-2s3.5 6 6-2" />
    <g v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4.5l3 2" />
    </g>
    <path v-else="true" d="M5 12h14" />
  </svg>
</template>

<style scoped>
.g { width: 1.15em; height: 1.15em; display: block; flex: none; }
</style>
