<script setup lang="ts">
import Flag from './Flag.vue'
import { isAppAuthed } from '../auth'
import { cargo, money, orderStatus, tone } from '../fmt'
import { place } from '../geo'
import { t } from '../i18n'
import { billCreated, billFill, type PublicBill } from '../siteData'

defineProps<{ bill: PublicBill; active?: boolean }>()
const emit = defineEmits<{ open: [] }>()
const authed = isAppAuthed
</script>

<template>
  <article class="card" :class="{ on: active }" @click="emit('open')">
    <div class="top">
      <div class="id">
        <b>{{ bill.id }}</b>
        <small>{{ billCreated(bill) }}</small>
      </div>
      <span class="pill" :class="tone(bill.status)">{{ orderStatus(bill.status) }}</span>
    </div>
    <div class="lane">
      <span class="end">
        <Flag :code="bill.originCountry" size="md" />
        <em>{{ place(bill.origin) }}</em>
      </span>
      <div class="rail">
        <i :style="{ width: billFill(bill.status) + '%' }" />
        <span class="dot a" />
        <span class="dot b" :class="{ on: billFill(bill.status) >= 50 }" />
        <span class="dot c" :class="{ on: billFill(bill.status) >= 90 }" />
      </div>
      <span class="end right">
        <Flag :code="bill.destCountry" size="md" />
        <em>{{ place(bill.dest) }}</em>
      </span>
    </div>
    <dl>
      <div>
        <dt>{{ t('trip.pre') }}</dt>
        <dd>{{ bill.preNo }}</dd>
      </div>
      <div>
        <dt>{{ t('col.freight') }}</dt>
        <dd>{{ authed() ? money(bill.freight) : t('auth.needLogin') }}</dd>
      </div>
    </dl>
    <div class="foot">
      <small>{{ cargo(bill.cargo) }} · {{ bill.weightT }} t</small>
      <button type="button" class="open" @click.stop="emit('open')">{{ t('trip.open') }}</button>
    </div>
  </article>
</template>

<style scoped>
.card {
  display: grid;
  gap: 12px;
  min-width: 0;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 16px 14px;
  text-align: left;
  box-shadow: var(--shadow-s);
  transition: border-color .15s, box-shadow .15s;
}
.card:hover, .card.on { border-color: var(--navy); box-shadow: var(--shadow); cursor: pointer; }
.top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.id { display: grid; gap: 2px; }
.id b { font-size: 15px; color: var(--navy-2); letter-spacing: -0.02em; }
.id small { color: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; }
.lane {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(48px, 1.4fr) minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.end { display: grid; justify-items: start; gap: 6px; min-width: 0; }
.end.right { justify-items: end; }
.end em { font-style: normal; font-size: 12px; font-weight: 650; color: var(--ink-soft); overflow-wrap: anywhere; }
.rail {
  position: relative;
  height: 4px;
  background: #e4eaf3;
  border-radius: 99px;
}
.rail i {
  position: absolute;
  inset: 0 auto 0 0;
  background: linear-gradient(90deg, #12805c, #3aa0ff);
  border-radius: 99px;
}
.dot {
  position: absolute;
  top: 50%;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #c5d0de;
  transform: translate(-50%, -50%);
}
.dot.a { left: 0; border-color: #12805c; background: #12805c; }
.dot.b { left: 50%; }
.dot.c { left: 100%; }
.dot.on { border-color: #3aa0ff; background: #3aa0ff; }
dl {
  display: grid;
  gap: 6px;
  margin: 0;
  padding-top: 4px;
  border-top: 1px solid var(--line-soft);
}
dl div { display: flex; justify-content: space-between; gap: 12px; }
dt { color: var(--muted); font-size: 12px; }
dd { margin: 0; font-size: 13px; font-weight: 650; color: var(--ink); font-variant-numeric: tabular-nums; }
.foot { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.foot small { color: var(--muted); }
.open {
  height: 32px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid #9ad0b8;
  background: #fff;
  color: var(--signal-ink);
  font-size: 13px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}
.card:hover .open { background: var(--signal-soft); }
</style>
