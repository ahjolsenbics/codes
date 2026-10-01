import { createRouter, createWebHistory } from 'vue-router'
import { getOpsToken } from './api'
import { appRoleFromToken, clearInvalidAppToken, isAppAuthed } from './auth'
import About from './views/About.vue'
import ApiPage from './views/ApiPage.vue'
import Board from './views/Board.vue'
import Connect from './views/Connect.vue'
import Estimate from './views/Estimate.vue'
import Landing from './views/Landing.vue'
import Login from './views/Login.vue'
import Match from './views/Match.vue'
import OpsLogin from './views/OpsLogin.vue'
import PortsLive from './views/PortsLive.vue'
import Tracking from './views/Tracking.vue'
import Waybill from './views/Waybill.vue'
import Shell from './views/Shell.vue'
import Workspace from './views/Workspace.vue'
import AppShell from './views/AppShell.vue'

const consoleChildren = [
  '',
  'users',
  'kyc',
  'loads',
  'orders',
  'deposits',
  'disputes',
  'blacklist',
  'ports',
  'config',
  'i18n',
  'announcements',
  'audit',
].map((path) => ({ path, component: Workspace }))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Landing },
    { path: '/about', component: About },
    { path: '/board', component: Board },
    { path: '/board/:id', redirect: (to) => ({ path: '/board', query: { id: String(to.params.id) } }) },
    { path: '/estimate', component: Estimate },
    { path: '/ports', component: PortsLive },
    { path: '/waybill', component: Waybill },
    { path: '/waybill/:id', redirect: (to) => ({ path: '/waybill', query: { id: String(to.params.id) } }) },
    { path: '/tracking', component: Tracking },
    { path: '/tracking/:id', redirect: (to) => ({ path: '/tracking', query: { id: String(to.params.id) } }) },
    { path: '/match', component: Match },
    { path: '/connect', component: Connect },
    { path: '/login', component: Login },
    { path: '/apps', redirect: '/' },
    { path: '/developers', component: ApiPage },
    { path: '/help', redirect: '/' },
    { path: '/ops/login', component: OpsLogin },
    { path: '/app/shipper', component: AppShell, props: { role: 'shipper' }, meta: { app: true } },
    { path: '/app/driver', component: AppShell, props: { role: 'driver' }, meta: { app: true } },
    { path: '/console', component: Shell, meta: { ops: true }, children: consoleChildren },
    { path: '/users', redirect: '/console/users' },
    { path: '/kyc', redirect: '/console/kyc' },
    { path: '/loads', redirect: '/console/loads' },
    { path: '/orders', redirect: '/console/orders' },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  clearInvalidAppToken()
  if (to.meta.ops && !getOpsToken()) return '/ops/login'
  if (to.meta.app) {
    const need = to.path.includes('driver') ? 'driver' : 'shipper'
    if (!isAppAuthed() || appRoleFromToken() !== need) {
      return { path: '/login', query: { role: need, next: to.fullPath } }
    }
  }
  return true
})

export default router
