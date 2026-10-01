<script setup lang="ts">
import PayMark from '../components/PayMark.vue'
import SiteBack from '../components/SiteBack.vue'
import SiteFooter from '../components/SiteFooter.vue'
import SiteNav from '../components/SiteNav.vue'
import { t } from '../i18n'

const modes = [
  { title: 'mode.bid', line: 'site.rule.bid.d', extra: 'site.rule.bid.x', n: '24h' },
  { title: 'mode.grab', line: 'site.rule.grab.d', extra: 'site.rule.grab.x', n: '30m' },
  { title: 'mode.assign', line: 'site.rule.assign.d', extra: 'site.rule.assign.x', n: '5' },
] as const

const who = [
  { title: 'site.who.trade.t', line: 'site.who.trade.d', to: '/board', act: 'site.who.trade.a' },
  { title: 'site.who.fleet.t', line: 'site.who.fleet.d', to: '/board?kind=trucks', act: 'site.who.fleet.a' },
  { title: 'site.who.ops.t', line: 'site.who.ops.d', to: '/ops/login', act: 'site.who.ops.a' },
] as const

const pays = ['wechat', 'alipay', 'unionpay', 'kaspi'] as const
</script>

<template>
  <div>
    <SiteNav />
    <section class="hero">
      <div class="wrap">
        <SiteBack to="/" />
        <p>{{ t('about.lead') }}</p>
        <h1>{{ t('about.title') }}</h1>
      </div>
    </section>
    <section class="wrap modes">
      <article v-for="item in modes" :key="item.title">
        <b>{{ item.n }}</b>
        <h2>{{ t(item.title) }}</h2>
        <span>{{ t(item.line) }}</span>
        <p>{{ t(item.extra) }}</p>
      </article>
    </section>
    <section class="wrap who">
      <h2>{{ t('site.whoTitle') }}</h2>
      <div class="grid">
        <article v-for="item in who" :key="item.title">
          <h3>{{ t(item.title) }}</h3>
          <p>{{ t(item.line) }}</p>
          <router-link :to="item.to">{{ t(item.act) }}</router-link>
        </article>
      </div>
    </section>
    <section class="wrap pay">
      <h2>{{ t('about.deposit') }}</h2>
      <p>{{ t('site.rule.deposit.d') }}</p>
      <p class="extra">{{ t('site.rule.deposit.x') }}</p>
      <div class="marks">
        <span v-for="name in pays" :key="name">
          <PayMark :name="name" />
          {{ t('pay.' + name) }}
        </span>
      </div>
    </section>
    <SiteFooter />
  </div>
</template>

<style scoped>
.hero { padding: 48px 0 8px; }
.hero p { margin: 0; color: #5c6b7a; font-size: 14px; }
h1 { margin: 8px 0 0; font-size: 40px; color: #10283f; }
.modes { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; padding: 28px 0 8px; }
.modes article {
  background: #fff; border: 1px solid #e3e8ef; border-radius: 18px; padding: 22px;
  display: grid; gap: 6px; color: #5c6b7a;
}
.modes article b { font-size: 36px; color: #10283f; letter-spacing: -0.03em; }
.modes article h2 { margin: 0; font-size: 18px; color: #1c2430; }
.modes article p { margin: 8px 0 0; font-size: 13px; line-height: 1.55; }
.who { padding: 36px 0 8px; }
.who > h2, .pay h2 { margin: 0 0 14px; font-size: 22px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.who article { background: #fff; border: 1px solid #e3e8ef; border-radius: 16px; padding: 18px; }
.who h3 { margin: 0 0 8px; font-size: 16px; }
.who p { margin: 0 0 12px; color: #5c6b7a; font-size: 14px; }
.who a { color: #157a40; font-weight: 700; font-size: 14px; }
.pay { padding: 36px 0 88px; }
.pay p { margin: 0 0 10px; color: #5c6b7a; }
.extra { max-width: 72ch; font-size: 14px; }
.marks { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }
.marks span {
  display: inline-flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid #e3e8ef; border-radius: 12px; padding: 8px 12px; font-size: 14px;
}
@media (max-width: 720px) {
  .modes, .grid { grid-template-columns: 1fr; }
  h1 { font-size: 32px; }
}
</style>
