<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { place } from '../geo'
import { locale, t } from '../i18n'

const root = ref<HTMLElement | null>(null)
let map: L.Map | null = null

type Label = 'left' | 'right' | 'top' | 'bottom'
type City = { lat: number; lng: number; label?: Label; gate?: boolean }

/** 霍尔果斯只作口岸入口；走廊主要铺在哈萨克斯坦内部，再接到莫斯科 */
const CITIES: Record<string, City> = {
  圣彼得堡: { lat: 59.93, lng: 30.32, label: 'right' },
  莫斯科: { lat: 55.75, lng: 37.62, label: 'top' },
  乌拉尔斯克: { lat: 51.23, lng: 51.37 },
  阿特劳: { lat: 47.12, lng: 51.88, label: 'bottom' },
  阿克托别: { lat: 50.28, lng: 57.21, label: 'top' },
  科斯塔奈: { lat: 53.21, lng: 63.62 },
  彼得罗巴甫尔: { lat: 54.87, lng: 69.14 },
  阿斯塔纳: { lat: 51.17, lng: 71.43, label: 'bottom' },
  巴甫洛达尔: { lat: 52.29, lng: 76.95 },
  卡拉干达: { lat: 49.80, lng: 73.10 },
  克孜勒奥尔达: { lat: 44.85, lng: 65.51 },
  奇姆肯特: { lat: 42.32, lng: 69.60, label: 'left' },
  塔拉兹: { lat: 42.90, lng: 71.37 },
  阿拉木图: { lat: 43.24, lng: 76.95, label: 'bottom' },
  塔尔迪库尔干: { lat: 45.02, lng: 78.37 },
  塞梅伊: { lat: 50.41, lng: 80.23, label: 'top' },
  比什凯克: { lat: 42.87, lng: 74.59 },
  霍尔果斯: { lat: 44.21, lng: 80.42, gate: true, label: 'right' },
}

const LINES: { route: (keyof typeof CITIES)[]; gate?: boolean; beat: string }[] = [
  { route: ['霍尔果斯', '阿拉木图'], gate: true, beat: 'a' },
  { route: ['阿拉木图', '塔尔迪库尔干'], beat: 'b' },
  { route: ['阿拉木图', '比什凯克'], beat: 'c' },
  { route: ['阿拉木图', '塔拉兹'], beat: 'd' },
  { route: ['塔拉兹', '奇姆肯特'], beat: 'a' },
  { route: ['阿拉木图', '卡拉干达'], beat: 'b' },
  { route: ['阿拉木图', '阿斯塔纳'], beat: 'c' },
  { route: ['奇姆肯特', '阿斯塔纳'], beat: 'd' },
  { route: ['塔尔迪库尔干', '卡拉干达'], beat: 'a' },
  { route: ['阿斯塔纳', '卡拉干达'], beat: 'b' },
  { route: ['卡拉干达', '巴甫洛达尔'], beat: 'c' },
  { route: ['阿斯塔纳', '巴甫洛达尔'], beat: 'd' },
  { route: ['阿斯塔纳', '彼得罗巴甫尔'], beat: 'a' },
  { route: ['阿斯塔纳', '科斯塔奈'], beat: 'b' },
  { route: ['科斯塔奈', '彼得罗巴甫尔'], beat: 'c' },
  { route: ['阿斯塔纳', '阿克托别'], beat: 'd' },
  { route: ['科斯塔奈', '阿克托别'], beat: 'a' },
  { route: ['阿克托别', '乌拉尔斯克'], beat: 'b' },
  { route: ['乌拉尔斯克', '阿特劳'], beat: 'c' },
  { route: ['阿克托别', '阿特劳'], beat: 'd' },
  { route: ['奇姆肯特', '克孜勒奥尔达'], beat: 'a' },
  { route: ['克孜勒奥尔达', '阿克托别'], beat: 'b' },
  { route: ['克孜勒奥尔达', '阿斯塔纳'], beat: 'c' },
  { route: ['巴甫洛达尔', '塞梅伊'], beat: 'd' },
  { route: ['卡拉干达', '塞梅伊'], beat: 'a' },
  { route: ['塞梅伊', '塔尔迪库尔干'], beat: 'b' },
  { route: ['乌拉尔斯克', '莫斯科'], beat: 'c' },
  { route: ['阿克托别', '莫斯科'], beat: 'd' },
  { route: ['彼得罗巴甫尔', '莫斯科'], beat: 'a' },
  { route: ['莫斯科', '圣彼得堡'], beat: 'b' },
]

const pins: { key: string; city: City; marker: L.Marker }[] = []
const copy = computed(() => {
  locale.value
  return {
    reset: t('map.reset'),
    road: t('map.road'),
    gate: t('map.gate'),
  }
})

function pts(route: (keyof typeof CITIES)[]): L.LatLngExpression[] {
  return route.map((key) => {
    const city = CITIES[key]
    return [city.lat, city.lng]
  })
}

function pinBox(side: Label | '', name: string) {
  const w = Math.max(86, Math.min(170, Math.round(name.length * 8.4 + 28)))
  if (side === 'left') return { size: [w, 18] as L.PointTuple, anchor: [w - 6, 9] as L.PointTuple }
  if (side === 'right') return { size: [w, 18] as L.PointTuple, anchor: [6, 9] as L.PointTuple }
  if (side === 'top' || side === 'bottom') return { size: [w, 28] as L.PointTuple, anchor: [w / 2, 20] as L.PointTuple }
  return { size: [14, 14] as L.PointTuple, anchor: [7, 7] as L.PointTuple }
}

function cityIcon(key: string, city: City) {
  const name = place(key)
  const side = city.label || ''
  const box = pinBox(side, name)
  return L.divIcon({
    className: `city-pin ${city.gate ? 'is-gate' : ''} ${side ? `lab-${side}` : ''}`,
    html: side
      ? `<i class="${city.gate ? 'gate' : ''}"></i><b>${name}</b>`
      : `<i class="${city.gate ? 'gate' : ''}"></i>`,
    iconSize: box.size,
    iconAnchor: box.anchor,
  })
}

function applyCityNames() {
  pins.forEach(({ key, city, marker }) => {
    const name = place(key)
    marker.setIcon(cityIcon(key, city))
    if (city.label) return
    if (marker.getTooltip()) marker.setTooltipContent(name)
    else marker.bindTooltip(name, { direction: 'top', offset: [0, -8], className: 'city-name' })
  })
}

function fitCorridor() {
  if (!map) return
  map.invalidateSize()
  map.fitBounds(L.latLngBounds([41.8, 29.2], [60.7, 82.6]), {
    paddingTopLeft: [22, 40],
    paddingBottomRight: [22, 80],
    maxZoom: 5.25,
  })
}

function onResize() {
  map?.invalidateSize()
}

onMounted(() => {
  const node = root.value
  if (!node) return
  map = L.map(node, {
    zoomControl: false,
    scrollWheelZoom: true,
    doubleClickZoom: true,
    touchZoom: true,
    boxZoom: true,
    keyboard: true,
    attributionControl: false,
    dragging: true,
    minZoom: 3,
    maxZoom: 12,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
  })
  L.control.zoom({ position: 'topright' }).addTo(map)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
  }).addTo(map)

  LINES.forEach((line) => {
    const path = pts(line.route)
    const color = line.gate ? '#ff8a1e' : '#5aa4ff'
    L.polyline(path, {
      color,
      weight: line.gate ? 1.35 : 1.15,
      opacity: line.gate ? 0.62 : 0.48,
      lineCap: 'round',
      lineJoin: 'round',
      className: 'lane-base',
      interactive: false,
    }).addTo(map!)
    L.polyline(path, {
      color,
      weight: line.gate ? 1.8 : 1.45,
      opacity: 0.92,
      lineCap: 'round',
      lineJoin: 'round',
      className: `${line.gate ? 'lane-gate-flow' : 'lane-flow'} beat-${line.beat}`,
      interactive: false,
    }).addTo(map!)
  })

  Object.entries(CITIES).forEach(([key, city]) => {
    const marker = L.marker([city.lat, city.lng], { icon: cityIcon(key, city), interactive: true }).addTo(map!)
    pins.push({ key, city, marker })
  })
  applyCityNames()

  fitCorridor()
  window.setTimeout(fitCorridor, 80)
  window.setTimeout(fitCorridor, 280)
  window.addEventListener('resize', onResize)
})

watch(locale, applyCityNames)

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  pins.length = 0
  map?.remove()
  map = null
})
</script>

<template>
  <div class="shell">
    <div ref="root" class="canvas" />
    <button type="button" class="fit" @click.stop="fitCorridor">{{ copy.reset }}</button>
    <div class="legend">
      <span><i class="road" />{{ copy.road }}</span>
      <span><i class="gate" />{{ copy.gate }}</span>
    </div>
  </div>
</template>

<style scoped>
.shell { position: relative; z-index: 0; isolation: isolate; height: 100%; min-height: 220px; background: #0b1c33; border-radius: 18px; overflow: hidden; }
.canvas { height: 100%; width: 100%; background: #0b1c33; }
.fit {
  position: absolute; top: 76px; right: 10px; z-index: 500;
  height: 28px; padding: 0 10px; border: 0; border-radius: 4px;
  background: rgba(8, 18, 36, 0.78); color: #e8eef6;
  font-size: 12px; font-weight: 650; letter-spacing: 0.02em;
}
.fit:hover { background: rgba(16, 40, 63, 0.95); }
.legend {
  position: absolute; left: 12px; bottom: 10px; z-index: 500;
  display: flex; gap: 12px;
  background: rgba(8, 18, 36, 0.72);
  color: #e8eef6;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
}
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.legend i { width: 16px; height: 2px; border-radius: 99px; display: block; }
.legend .road { background: #5aa4ff; }
.legend .gate { background: #ff8a1e; }
</style>

<style>
.leaflet-container img { max-width: none; }
.leaflet-control-zoom {
  border: 0 !important;
  box-shadow: 0 8px 18px rgba(8, 18, 36, 0.28);
}
.leaflet-control-zoom a {
  width: 28px !important; height: 28px !important; line-height: 28px !important;
  background: rgba(8, 18, 36, 0.78) !important; color: #e8eef6 !important;
  border: 0 !important;
}
.leaflet-control-zoom a:hover { background: rgba(16, 40, 63, 0.95) !important; }
.city-pin { background: none; border: 0; }
.city-pin i {
  display: block; width: 8px; height: 8px; border-radius: 50%;
  background: #7ec0ff; box-shadow: 0 0 0 2px rgba(94, 176, 255, 0.28);
}
.city-pin i.gate {
  width: 11px; height: 11px; background: #ff8a1e;
  box-shadow: 0 0 0 4px rgba(255, 138, 30, 0.35);
  animation: gate-pulse 2.2s ease-in-out infinite;
}
.city-pin b {
  position: absolute;
  color: #f4f7fb;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.75);
  pointer-events: none;
}
.city-pin.lab-left, .city-pin.lab-right { height: 18px; }
.city-pin.lab-left i { position: absolute; right: 0; top: 3px; }
.city-pin.lab-left b { right: 18px; top: 0; color: #ffd7a8; }
.city-pin.lab-right i { position: absolute; left: 0; top: 3px; }
.city-pin.lab-right b { left: 18px; top: 0; }
.city-pin.lab-right.is-gate b { color: #ffd7a8; }
.city-pin.lab-top, .city-pin.lab-bottom { height: 28px; }
.city-pin.lab-top i { position: absolute; left: 50%; bottom: 0; margin-left: -4px; }
.city-pin.lab-top b { left: 50%; bottom: 12px; transform: translateX(-50%); }
.city-pin.lab-bottom i { position: absolute; left: 50%; top: 0; margin-left: -4px; }
.city-pin.lab-bottom b { left: 50%; top: 12px; transform: translateX(-50%); }
.city-name {
  background: transparent; border: 0; box-shadow: none;
  color: #f4f7fb; font-size: 11px; font-weight: 650;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.65);
}
.city-name::before { display: none; }
.lane-base { stroke-linecap: round; }
.lane-flow, .lane-gate-flow {
  stroke-dasharray: 11 78 !important;
  stroke-linecap: round;
  animation: lane-run 7.2s linear infinite;
}
.lane-gate-flow {
  stroke-dasharray: 12 64 !important;
  animation-duration: 5.6s;
}
.lane-flow.beat-b, .lane-gate-flow.beat-b { animation-delay: -1.6s; }
.lane-flow.beat-c, .lane-gate-flow.beat-c { animation-delay: -3.1s; }
.lane-flow.beat-d { animation-delay: -4.4s; animation-duration: 8.4s; }
@keyframes lane-run { to { stroke-dashoffset: -520; } }
@keyframes gate-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25); }
}
</style>
