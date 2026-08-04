import { createRouter, createWebHashHistory } from 'vue-router'

// 管理端页面按路由拆包：首次登录只加载必要框架，进入功能页时再加载对应页面。
const Login = () => import('../views/Login.vue')
const Layout = () => import('../views/Layout.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const Classes = () => import('../views/Classes.vue')
const Users = () => import('../views/Users.vue')
const Import = () => import('../views/Import.vue')
const Subjects = () => import('../views/Subjects.vue')
const NotificationList = () => import('../views/notifications/list.vue')
const FeedbackList = () => import('../views/feedback/list.vue')
const AuditLogs = () => import('../views/audit/list.vue')
const SystemHealth = () => import('../views/system/health.vue')
const StorageUsage = () => import('../views/system/storage.vue')

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
      { path: 'subjects', component: Subjects, meta: { title: '选科管理' } },
      { path: 'import', component: Import, meta: { title: '批量导入' } },
      { path: 'notifications', component: NotificationList, meta: { title: '通知管理' } },
      { path: 'feedback', component: FeedbackList, meta: { title: '反馈诊断' } },
      { path: 'audit-logs', component: AuditLogs, meta: { title: '操作记录' } },
      { path: 'system-health', component: SystemHealth, meta: { title: '系统健康' } },
      { path: 'storage-usage', component: StorageUsage, meta: { title: '存储盘点' } },
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
