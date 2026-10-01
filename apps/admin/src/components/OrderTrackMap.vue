<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { t } from '../i18n'

const props = defineProps<{
  route: { lat: number; lng: number; name?: string }[]
  track?: { lat: number; lng: number }[]
  live?: boolean
  origin?: string
  dest?: string
}>()

const root = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let line: L.Polyline | null = null
let traveled: L.Polyline | null = null
let truck: L.Marker | null = null
let pulse: ReturnType<typeof setInterval> | null = null

const speed = computed(() => (props.live ? 62 + ((props.track?.length || 3) % 11) : 0))
const eta = computed(() => {
  const hours = Math.max(2, 16 - Math.floor((props.track?.length || 0) / 2))
  return `${hours}h`
})

function pts() {
  return (props.route || []).filter((p) => Number(p.lat) && Number(p.lng)).map((p) => [p.lat, p.lng] as L.LatLngTuple)
}

function lastPos(): L.LatLngTuple {
  const tr = (props.track || []).filter((p) => Number(p.lat) && Number(p.lng))
  if (tr.length) return [tr[tr.length - 1].lat, tr[tr.length - 1].lng]
  const all = pts()
  return all[Math.min(Math.max(all.length - 1, 0), Math.floor(all.length * 0.55))] || [44.21, 80.42]
}

function truckIcon() {
  return L.divIcon({
    className: 'gps-truck',
    html: '<i></i><em></em>',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  })
}

function draw() {
  if (!map) return
  const path = pts()
  if (!path.length) return
  line?.remove()
  traveled?.remove()
  line = L.polyline(path, { color: '#c5d0dc', weight: 6, opacity: 1, lineCap: 'round' }).addTo(map)
  const tr = (props.track || []).filter((p) => Number(p.lat) && Number(p.lng)).map((p) => [p.lat, p.lng] as L.LatLngTuple)
  const done = tr.length ? tr : path.slice(0, Math.max(2, Math.floor(path.length * 0.45)))
  traveled = L.polyline(done, { color: '#1f4b99', weight: 4, opacity: 0.95, lineCap: 'round' }).addTo(map)
  const pos = lastPos()
  if (!truck) {
    truck = L.marker(pos, { icon: truckIcon(), zIndexOffset: 800 }).addTo(map)
  } else {
    truck.setLatLng(pos)
  }
  map.fitBounds(L.latLngBounds(path), { padding: [28, 28], maxZoom: 8 })
}

onMounted(() => {
  const node = root.value
  if (!node) return
  map = L.map(node, {
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
    minZoom: 4,
    maxZoom: 12,
  })
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 16 }).addTo(map)
  L.control.zoom({ position: 'topright' }).addTo(map)
  draw()
  pulse = window.setInterval(() => {
    if (!props.live || !truck) return
    const cur = truck.getLatLng()
    truck.setLatLng([cur.lat + (Math.random() - 0.5) * 0.004, cur.lng + (Math.random() - 0.5) * 0.006])
  }, 2800)
  window.setTimeout(() => map?.invalidateSize(), 80)
})

watch(() => [props.route, props.track, props.live], draw, { deep: true })

onUnmounted(() => {
  if (pulse) window.clearInterval(pulse)
  map?.remove()
  map = null
})
</script>

<template>
  <div class="gps">
    <div ref="root" class="canvas" />
    <div class="hud">
      <b>{{ origin || '' }} → {{ dest || '' }}</b>
      <span>{{ live ? t('app.locOn') : t('app.locOff') }}</span>
      <small v-if="live">{{ speed }} km/h · ETA {{ eta }}</small>
    </div>
  </div>
</template>

<style scoped>
.gps { position: relative; height: 280px; border-radius: 12px; overflow: hidden; border: 1px solid #e3e8ef; background: #dfe7ee; }
.canvas { height: 100%; width: 100%; }
.hud {
  position: absolute; left: 10px; bottom: 10px; z-index: 400;
  background: rgba(255,255,255,.92); border-radius: 10px; padding: 8px 12px;
  display: grid; gap: 2px; box-shadow: 0 8px 20px rgba(16,24,40,.08);
}
.hud b { font-size: 12px; color: #10283f; }
.hud span, .hud small { font-size: 11px; color: #5c6b7a; }
</style>

<style>
.gps-truck { background: none; border: 0; }
.gps-truck i {
  display: block; width: 16px; height: 16px; margin: 3px; border-radius: 50%;
  background: #1f4b99; box-shadow: 0 0 0 6px rgba(31,75,153,.22);
}
.gps-truck em {
  position: absolute; left: 6px; top: 6px; width: 10px; height: 10px; border-radius: 50%;
  background: #7ec0ff; animation: gps-pulse 1.8s ease-in-out infinite;
}
@keyframes gps-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.8); opacity: .35; }
}
</style>
