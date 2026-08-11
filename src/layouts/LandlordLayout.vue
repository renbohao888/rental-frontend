<template>
  <div class="landlord-layout">
    <!-- 左侧导航 -->
    <aside v-if="!isMobile" class="sidebar">
      <div class="sidebar-header">
        <h3>🏘️ 房东中心</h3>
      </div>
      <nav class="sidebar-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <el-button link type="danger" @click="logout" style="width: 100%;">
          <el-icon><SwitchButton /></el-icon> 退出登录
        </el-button>
      </div>
    </aside>

    <!-- 顶部导航 + 主内容 -->
    <div class="main-wrapper">
      <header class="top-navbar">
        <div class="navbar-left">
          <el-button 
            v-if="isMobile" 
            link 
            @click="sidebarVisible = !sidebarVisible"
          >
            ☰ 菜单
          </el-button>
          <h2>{{ currentPageTitle }}</h2>
        </div>
        <div class="navbar-right">
          <el-badge :value="messageCount" :hidden="messageCount === 0">
            <el-icon><Bell /></el-icon>
          </el-badge>
          <el-dropdown>
            <span class="user-name">{{ userInfo?.nickname }}</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToProfile">👤 个人资料</el-dropdown-item>
                <el-dropdown-item @click="goToSettings">⚙️ 设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">🚪 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- 移动端侧边栏 -->
    <el-drawer
      v-model="sidebarVisible"
      title="菜单"
      direction="ltr"
      v-if="isMobile"
    >
      <nav class="mobile-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item"
          @click="sidebarVisible = false"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
        </router-link>
      </nav>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { SwitchButton, Bell } from '@element-plus/icons-vue'
import { getUserInfo } from '@/api/user'

const router = useRouter()
const route = useRoute()
const userInfo = ref(null)
const isMobile = ref(false)
const sidebarVisible = ref(false)
const messageCount = ref(3) // 示例数据

const menuItems = [
  { icon: '📊', label: '仪表盘', path: '/landlord/dashboard' },
  { icon: '🏠', label: '房源管理', path: '/landlord/rooms' },
  { icon: '📋', label: '订单管理', path: '/landlord/orders' },
  { icon: '👥', label: '租客管理', path: '/landlord/tenants' },
  { icon: '💰', label: '账单对账', path: '/landlord/bill' },
  { icon: '🔧', label: '报修管理', path: '/landlord/repairs' },
  { icon: '⭐', label: '评价管理', path: '/landlord/evaluations' },
  { icon: '📅', label: '看房预约', path: '/landlord/appointments' },
  { icon: '📝', label: '合同管理', path: '/landlord/contracts' },
  { icon: '📊', label: '数据统计', path: '/landlord/analytics' },
  { icon: '🎯', label: '营销推广', path: '/landlord/marketing' },
]

const currentPageTitle = computed(() => {
  const item = menuItems.find(m => m.path === route.path)
  return item?.label || '房东中心'
})

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    sidebarVisible.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goToProfile = () => {
  router.push('/landlord/profile')
}

const goToSettings = () => {
  router.push('/landlord/settings')
}

onMounted(async () => {
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
  }

  handleResize()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.landlord-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
  text-align: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #666;
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
  cursor: pointer;

  &:hover {
    background-color: #f5f5f5;
    color: #333;
  }

  &.active {
    background-color: #e6f7ff;
    color: #409eff;
    border-left-color: #409eff;
    font-weight: 600;
  }
}

.icon {
  font-size: 18px;
}

.label {
  font-size: 14px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.main-wrapper {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
}

.top-navbar {
  background: white;
  padding: 12px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 50;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.navbar-left h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-name {
  cursor: pointer;
  color: #666;
  font-size: 14px;

  &:hover {
    color: #333;
  }
}

.main-content {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #666;
  text-decoration: none;
  border-bottom: 1px solid #f0f0f0;

  &:hover {
    background-color: #f5f5f5;
    color: #333;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .main-wrapper {
    margin-left: 0;
  }

  .top-navbar {
    padding: 12px 16px;
  }

  .main-content {
    padding: 12px 16px;
  }

  .navbar-right {
    gap: 12px;
  }
}
</style>
