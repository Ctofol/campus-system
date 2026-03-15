import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Classes from '../views/Classes.vue'
import Users from '../views/Users.vue'
import Import from '../views/Import.vue'
import SunshineDashboard from '../views/SunshineDashboard.vue'
import Layout from '../views/Layout.vue'

const routes = [
  { path: '/login', component: Login },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: Dashboard, meta: { title: '控制台' } },
      { path: 'classes', component: Classes, meta: { title: '班级管理' } },
      { path: 'users', component: Users, meta: { title: '账号管理' } },
      { path: 'import', component: Import, meta: { title: '批量导入' } },
      { path: 'sunshine', component: SunshineDashboard, meta: { title: '阳光跑全校看板' } },
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) return '/login'
})

export default router
