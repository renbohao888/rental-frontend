<template>
  <div class="tenant-layout" :class="{ 'mobile-view': isMobile }">
    <!-- 左侧导航（PC：永久显示，Mobile：隐藏） -->
    <aside v-if="!isMobile" class="sidebar">
      <div class="sidebar-header">
        <div class="user-card">
          <img :src="userInfo?.avatar || 'https://ui-avatars.com/api/?name=User'" class="avatar" />
          <div class="user-name">{{ userInfo?.nickname || '用户' }}</div>
          <div class="user-role">租客</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: activeTab === item.id }"
          @click="activeTab = item.id"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
          <span v-if="item.path === '/chat' && unreadCount > 0" class="nav-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <el-button link type="danger" @click="logout" style="width: 100%;">
          <el-icon><SwitchButton /></el-icon> 退出登录
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main :class="{ 'with-sidebar': !isMobile, 'full-width': isMobile }">
      <router-view />
    </main>

    <!-- 底部导航（Mobile：显示，PC：隐藏） -->
    <nav v-if="isMobile" class="mobile-tabs">
      <router-link 
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="tab-item"
        :class="{ active: activeTab === item.id }"
        @click="activeTab = item.id"
      >
        <div class="icon">
          {{ item.icon }}
          <span v-if="item.path === '/chat' && unreadCount > 0" class="tab-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </div>
        <div class="label">{{ item.label }}</div>
      </router-link>
    </nav>

    <!-- 退出登录按钮（Mobile 专用，显示在底部Tab上方） -->
    <div v-if="isMobile" class="mobile-logout">
      <el-button type="danger" size="small" @click="logout">
        <el-icon><SwitchButton /></el-icon> 退出
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { SwitchButton } from '@element-plus/icons-vue'
import { getUserInfo } from '@/api/user'
import { getChatUnreadCount } from '@/api/chat'

const router = useRouter()
const route = useRoute()
const userInfo = ref(null)
const isMobile = ref(false)
const activeTab = ref('home')
const unreadCount = ref(0)
let unreadTimer = null

const loadUnread = async () => {
  try {
    const res = await getChatUnreadCount()
    if (res.code === 200) {
      unreadCount.value = res.data || 0
    }
  } catch (error) {
    console.error('获取未读消息数失败', error)
  }
}

const menuItems = [
  { id: 'home', label: '首页', path: '/tenant/home', icon: '🏠' },
  { id: 'search', label: '找房源', path: '/tenant/search', icon: '🔍' },
  { id: 'chat', label: '聊天', path: '/chat', icon: '💬' },
  { id: 'my', label: '我的', path: '/tenant/my', icon: '👤' }
]

// 根据当前路由设置 activeTab
const updateActiveTab = () => {
  const path = route.path
  const item = menuItems.find(m => m.path === path)
  if (item) {
    activeTab.value = item.id
  }
}

// 监听窗口大小变化
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(async () => {
  // 获取用户信息
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
    router.push('/login')
  }

  // 初始化响应式
  handleResize()
  window.addEventListener('resize', handleResize)
  updateActiveTab()

  // 启动聊天未读红点轮询（每 5 秒）
  loadUnread()
  unreadTimer = setInterval(loadUnread, 5000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (unreadTimer) {
    clearInterval(unreadTimer)
    unreadTimer = null
  }
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.tenant-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* ===== PC 布局（左侧导航） ===== */
.sidebar {
  width: 260px;
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

.user-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #409eff;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.user-role {
  font-size: 12px;
  color: #999;
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
    background-color: #f5f7fa;
    color: #409eff;
  }

  &.active {
    background-color: #f0f9ff;
    color: #409eff;
    border-left-color: #409eff;
  }
}

.nav-item .icon {
  font-size: 18px;
  min-width: 24px;
}

.nav-item .label {
  font-size: 14px;
  font-weight: 500;
}

/* 聊天未读红点（PC 侧边栏） */
.nav-badge {
  margin-left: auto;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  background: #e8341e;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  padding: 0 5px;
}

/* 聊天未读红点（移动端底部 Tab） */
.tab-badge {
  position: absolute;
  top: -4px;
  right: -10px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  background: #e8341e;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  padding: 0 4px;
}
.tab-item .icon {
  position: relative;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.with-sidebar {
  margin-left: 260px;
  flex: 1;
  padding: 20px;
}

/* ===== Mobile 布局（底部Tab） ===== */
.mobile-view {
  display: flex;
  flex-direction: column;
}

.mobile-view main {
  flex: 1;
  padding: 16px 12px;
  padding-bottom: 120px;
  overflow-y: auto;
}

.mobile-logout {
  padding: 12px;
  text-align: center;
  border-top: 1px solid #e0e0e0;
  background: white;
}

.mobile-tabs {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  padding-top: 8px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  color: #999;
  text-decoration: none;
  font-size: 12px;
  flex: 1;
  transition: all 0.3s;

  &:hover {
    color: #409eff;
  }

  &.active {
    color: #409eff;
  }
}

.tab-item .icon {
  font-size: 24px;
}

.tab-item .label {
  font-size: 11px;
  font-weight: 500;
}

.full-width {
  width: 100%;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .with-sidebar {
    margin-left: 0;
    padding: 12px;
  }
}
</style>
