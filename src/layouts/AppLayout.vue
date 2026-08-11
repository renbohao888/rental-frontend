<template>
  <div class="app-layout">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="logo">🏠 房屋租赁</div>
      
      <div class="nav">
        <!-- 公共导航（未登录游客也可见） -->
        <el-menu v-if="!userInfo" mode="horizontal" :router="true">
          <el-menu-item index="/">🏠 首页</el-menu-item>
          <el-menu-item index="/rooms">🏘️ 找房源</el-menu-item>
          <el-menu-item index="/notices">📢 公告</el-menu-item>
        </el-menu>
        <el-menu mode="horizontal" :router="true" v-if="userInfo">
          <!-- 租客菜单（role=2） -->
          <template v-if="userInfo.role === 2">
            <el-menu-item index="/tenant/home">租客首页</el-menu-item>
            <el-menu-item index="/tenant/search">找房源</el-menu-item>
            <el-menu-item index="/tenant/my">个人中心</el-menu-item>
            <el-menu-item index="/notices">📢 公告</el-menu-item>
            <el-menu-item index="/chat">💬 聊天</el-menu-item>
          </template>
          
          <!-- 房东菜单（role=1） -->
          <template v-if="userInfo.role === 1">
            <el-menu-item index="/landlord/dashboard">📊 仪表盘</el-menu-item>
            <el-menu-item index="/landlord/rooms">🏠 房源管理</el-menu-item>
            <el-menu-item index="/landlord/orders">📋 订单管理</el-menu-item>
            <el-menu-item index="/landlord/bill">💰 账单对账</el-menu-item>
            <el-menu-item index="/landlord/repairs">🔧 报修管理</el-menu-item>
            <el-menu-item index="/notices">📢 公告</el-menu-item>
            <el-menu-item index="/chat">💬 聊天</el-menu-item>
            <!-- 房东也能像租客一样浏览房源、下单、收藏、评价、报修 -->
            <el-sub-menu index="landlord-tenant-side">
              <template #title>🧭 租客功能</template>
              <el-menu-item index="/rooms">🏘️ 找房源</el-menu-item>
              <el-menu-item index="/tenant/my/orders">📄 我的订单</el-menu-item>
              <el-menu-item index="/tenant/my/favorites">❤️ 我的收藏</el-menu-item>
              <el-menu-item index="/tenant/my/evaluations">⭐ 我的评价</el-menu-item>
              <el-menu-item index="/tenant/my/repairs">🔧 我的报修</el-menu-item>
            </el-sub-menu>
          </template>
          
          <!-- 管理员菜单（role=0） -->
          <template v-if="userInfo.role === 0">
            <el-menu-item index="/admin/dashboard">📈 运营大屏</el-menu-item>
            <el-sub-menu index="admin-users-group">
              <template #title>👤 用户账号</template>
              <el-menu-item index="/admin/users">用户账号管控</el-menu-item>
              <el-menu-item index="/admin/tenants">租客管理</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="admin-rooms-group">
              <template #title>🏘️ 房源管理</template>
              <el-menu-item index="/admin/rooms">房源管理</el-menu-item>
              <el-menu-item index="/admin/rooms/audit">房源审核</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/admin/landlords">💼 房东资质</el-menu-item>
            <el-sub-menu index="admin-order-group">
              <template #title>📦 订单与纠纷</template>
              <el-menu-item index="/admin/orders">订单管理</el-menu-item>
              <el-menu-item index="/admin/disputes">纠纷处理</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="admin-content-group">
              <template #title>📢 内容管理</template>
              <el-menu-item index="/admin/notices">公告管理</el-menu-item>
              <el-menu-item index="/admin/banners">轮播图管理</el-menu-item>
              <el-menu-item index="/notices">前台公告查看</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="admin-supervise-group">
              <template #title>🛡️ 监督与报表</template>
              <el-menu-item index="/admin/supervision">报修投诉督办</el-menu-item>
              <el-menu-item index="/admin/reports">数据报表</el-menu-item>
              <el-menu-item index="/admin/analytics">数据分析</el-menu-item>
              <el-menu-item index="/admin/messages">消息管理</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/admin/config">⚙️ 平台配置</el-menu-item>
            <el-menu-item index="/chat">💬 聊天</el-menu-item>
          </template>
        </el-menu>

        <!-- 游客/未登录菜单 -->
        <el-menu mode="horizontal" :router="true" v-else>
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/rooms">找房源</el-menu-item>
          <el-menu-item index="/notices">公告</el-menu-item>
        </el-menu>
      </div>
      
      <!-- 主题切换 -->
      <el-button link class="theme-toggle" :title="isDark ? '切换到浅色模式' : '切换到深色模式'" @click="toggleTheme">
        <span class="theme-icon">{{ isDark ? '🌙' : '☀️' }}</span>
      </el-button>

      <!-- 用户信息 + 个人中心 -->
      <div class="user-info">
        <span v-if="userInfo">{{ userInfo.nickname || '用户' }}</span>
        <span v-else>游客</span>
        
        <!-- 👇 新增：个人中心入口（仅登录用户显示） -->
        <el-button link type="primary" @click="goToProfile" v-if="userInfo">
          个人中心
        </el-button>
        
        <el-button link type="danger" @click="logout" v-if="userInfo">退出</el-button>
        <el-button link type="primary" @click="router.push('/login')" v-else>登录</el-button>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>© 2026 安居房屋租赁平台</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserInfo } from '@/api/user'

const router = useRouter()
const userInfo = ref(null)

// ===== 主题切换（浅色 / 夜晚深色） =====
const isDark = ref(document.documentElement.classList.contains('dark'))
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
      }
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  userInfo.value = null
  ElMessage.success('已退出')
  router.push('/login')
}

const goToProfile = () => {
  // 根据用户角色跳转到对应的个人中心
  if (userInfo.value?.role === 2) {
    router.push('/tenant/my')
  } else if (userInfo.value?.role === 1) {
    router.push('/landlord/dashboard')
  } else if (userInfo.value?.role === 0) {
    router.push('/admin/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 60px;
  background: var(--bg-card);
  color: var(--text-main);
  box-shadow: 0 2px 8px var(--shadow-color);
  border-bottom: 2px solid #ff6a00;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: background-color 0.3s ease, color 0.3s ease;
}
.logo {
  font-size: 20px;
  font-weight: bold;
  color: #ff6a00;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav {
  flex: 1;
  margin-left: 40px;
}
.theme-toggle {
  font-size: 20px;
  color: var(--text-main);
  padding: 4px;
}
.theme-icon {
  display: inline-block;
  line-height: 1;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-main);
}
.chat-entry {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.chat-badge {
  --el-badge-bg-color: #e8341e;
}
.main-content {
  flex: 1;
  padding: 20px;
  background: var(--bg-page);
  transition: background-color 0.3s ease;
}
.footer {
  text-align: center;
  padding: 20px;
  color: var(--text-sub);
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}
</style>