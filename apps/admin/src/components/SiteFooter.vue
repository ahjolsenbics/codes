<script setup lang="ts">
import { t } from '../i18n'
import BrandMark from './BrandMark.vue'
import PayMark from './PayMark.vue'

const modules = [
  'nav.market',
  'nav.estimate',
  'nav.portsLive',
  'nav.waybill',
  'nav.tracking',
  'nav.match',
  'nav.connect',
] as const

const pays = ['wechat', 'alipay', 'unionpay', 'kaspi'] as const
</script>

<template>
  <footer class="foot">
    <div class="wrap grid">
      <div>
        <div class="brand">
          <BrandMark :size="28" on-dark />
          <b>{{ t('brand.name') }}</b>
        </div>
        <p>{{ t('home.note') }}</p>
        <div class="pays">
          <span v-for="name in pays" :key="name"><PayMark :name="name" />{{ t('pay.' + name) }}</span>
        </div>
      </div>
      <div>
        <h4>{{ t('nav.ability') }}</h4>
        <span v-for="key in modules" :key="key">{{ t(key) }}</span>
      </div>
      <div>
        <h4>{{ t('foot.support') }}</h4>
        <span>{{ t('foot.phone') }}</span>
        <span>{{ t('foot.hours') }}</span>
      </div>
      <div>
        <h4>{{ t('ops.bench') }}</h4>
        <span>{{ t('foot.ops') }}</span>
      </div>
    </div>
    <div class="filing">{{ t('foot.filing') }} · 中文 / English / Русский</div>
  </footer>
</template>

<style scoped>
.foot { background: #10283f; color: #d5deea; padding: 36px 0 0; margin-top: 12px; }
.grid { display: grid; grid-template-columns: 1.4fr repeat(3, minmax(140px, 1fr)); gap: 28px; }
.brand { display: flex; align-items: center; gap: 10px; }
b { color: #fff; font-size: 16px; }
p, span { display: flex; align-items: center; gap: 8px; margin: 10px 0 0; color: #d5deea; font-size: 13px; }
h4 { margin: 0; color: #fff; font-size: 12px; letter-spacing: 0.06em; }
.pays { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.pays span { margin: 0; background: rgba(255,255,255,.08); border-radius: 8px; padding: 4px 8px; }
.filing {
  margin-top: 28px; text-align: center; font-size: 12px; padding: 14px 16px;
  border-top: 1px solid rgba(213, 222, 234, 0.18);
}
@media (max-width: 1040px) { .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; padding-bottom: 8px; } }
</style>
