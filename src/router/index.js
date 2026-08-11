import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/tenant/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/tenant/Register.vue') },
  { path: '/forgot-password', name: 'ForgotPassword', component: () => import('@/views/tenant/ForgotPassword.vue') },

  // ---------- 主布局 AppLayout（统一顶部导航，不再跳动） ----------
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'Home', component: () => import('@/views/tenant/Home.vue') },
      { path: 'rooms', name: 'Rooms', component: () => import('@/views/tenant/RoomList.vue') },
      { path: 'room/:id', name: 'RoomDetail', component: () => import('@/views/tenant/RoomDetail.vue') },
      { path: 'notices', name: 'Notices', component: () => import('@/views/tenant/NoticeList.vue') },
      { path: 'notice/:id', name: 'NoticeDetail', component: () => import('@/views/tenant/NoticeDetail.vue') },

      // 聊天（统一消息中心：好友聊天 + 系统消息）
      { path: 'chat', name: 'Chat', component: () => import('@/views/chat/Chat.vue'), meta: { requiresAuth: true, roles: [0, 1, 2] } },

      // 租客专区
      { path: 'tenant/home', name: 'TenantHome', component: () => import('@/views/tenant/TenantHome.vue'), meta: { requiresAuth: true, roles: [1, 2] } },
      { path: 'tenant/search', name: 'TenantSearch', component: () => import('@/views/tenant/TenantSearch.vue'), meta: { requiresAuth: true, roles: [1, 2] } },
      {
        path: 'tenant/my', name: 'TenantMy',
        component: () => import('@/views/tenant/My.vue'),
        redirect: '/tenant/my/profile',
        meta: { requiresAuth: true, roles: [1, 2] },
        children: [
          { path: 'profile', name: 'MyProfile', component: () => import('@/views/tenant/my/Profile.vue') },
          { path: 'password', name: 'MyPassword', component: () => import('@/views/tenant/my/ChangePassword.vue') },
          { path: 'favorites', name: 'MyFavorites', component: () => import('@/views/tenant/my/Favorites.vue') },
          { path: 'orders', name: 'MyOrders', component: () => import('@/views/tenant/my/Orders.vue') },
          { path: 'appointments', name: 'MyAppointments', component: () => import('@/views/tenant/my/Appointments.vue') },
          { path: 'pay', name: 'MyPay', component: () => import('@/views/tenant/my/Pay.vue') },
          { path: 'repairs', name: 'MyRepairs', component: () => import('@/views/tenant/my/Repairs.vue') },
          { path: 'evaluations', name: 'MyEvaluations', component: () => import('@/views/tenant/my/Evaluations.vue') },
          { path: 'disputes', name: 'MyDisputes', component: () => import('@/views/tenant/my/Disputes.vue') },
          { path: 'landlord-apply', name: 'MyLandlordApply', component: () => import('@/views/tenant/my/LandlordApply.vue') },
        ]
      },

      // 房东后台
      { path: 'landlord/dashboard', name: 'LandlordDashboard', component: () => import('@/views/landlord/Dashboard.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/rooms', name: 'LandlordRooms', component: () => import('@/views/landlord/Rooms.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/orders', name: 'LandlordOrders', component: () => import('@/views/landlord/Orders.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/tenants', name: 'LandlordTenants', component: () => import('@/views/landlord/Tenants.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/bill', name: 'LandlordBill', component: () => import('@/views/landlord/Bill.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/repairs', name: 'LandlordRepairs', component: () => import('@/views/landlord/Repairs.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/appointments', name: 'LandlordAppointments', component: () => import('@/views/landlord/Appointments.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/evaluations', name: 'LandlordEvaluations', component: () => import('@/views/landlord/Evaluations.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/contracts', name: 'LandlordContracts', component: () => import('@/views/landlord/Contracts.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/analytics', name: 'LandlordAnalytics', component: () => import('@/views/landlord/Analytics.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/marketing', name: 'LandlordMarketing', component: () => import('@/views/landlord/Marketing.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/profile', name: 'LandlordProfile', component: () => import('@/views/landlord/Profile.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/settings', name: 'LandlordSettings', component: () => import('@/views/landlord/Settings.vue'), meta: { requiresAuth: true, roles: [1] } },
      { path: 'landlord/apply', name: 'LandlordApply', component: () => import('@/views/landlord/Apply.vue'), meta: { requiresAuth: true, roles: [1] } },

      // 管理员后台
      { path: 'admin/dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/landlords', name: 'AdminLandlords', component: () => import('@/views/admin/Landlords.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/tenants', name: 'AdminTenants', component: () => import('@/views/admin/AdminTenants.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/rooms', name: 'AdminRooms', component: () => import('@/views/admin/AdminRooms.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/rooms/audit', name: 'AdminRoomAudit', component: () => import('@/views/admin/RoomAudit.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/orders', name: 'AdminOrders', component: () => import('@/views/admin/Orders.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/disputes', name: 'AdminDisputes', component: () => import('@/views/admin/Disputes.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/notices', name: 'AdminNotices', component: () => import('@/views/admin/Notices.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/banners', name: 'AdminBanners', component: () => import('@/views/admin/Banners.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/messages', name: 'AdminMessages', component: () => import('@/views/admin/Messages.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/reports', name: 'AdminReports', component: () => import('@/views/admin/Reports.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/analytics', name: 'AdminAnalytics', component: () => import('@/views/admin/Analytics.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/config', name: 'AdminConfig', component: () => import('@/views/admin/Config.vue'), meta: { requiresAuth: true, roles: [0] } },
      { path: 'admin/supervision', name: 'AdminSupervision', component: () => import('@/views/admin/Supervision.vue'), meta: { requiresAuth: true, roles: [0] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const role = userInfo?.role

  // 如果去登录/注册/找回密码，直接放行
  if (to.path === '/login' || to.path === '/register' || to.path === '/forgot-password') {
    next()
    return
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!token) {
      next('/login')
      return
    }
    // 检查角色权限（如果设置了 roles）
    if (to.meta.roles && !to.meta.roles.includes(role)) {
      // 角色不符，跳转首页或提示
      next('/')
      return
    }
  }

  // 非私有页面直接放行
  next()
})

export default router