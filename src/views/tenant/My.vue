<template>
  <div class="my-center">
    <!-- 侧边栏导航（PC） -->
    <div v-if="!isMobile" class="my-sidebar">
      <nav class="my-nav">
        <router-link 
          v-for="item in myNavItems"
          :key="item.path"
          :to="item.path"
          class="my-nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
        </router-link>
      </nav>
    </div>

    <!-- 顶部标签页导航（Mobile） -->
    <div v-if="isMobile" class="my-tabs">
      <div class="tabs-scroll">
        <router-link 
          v-for="item in myNavItems"
          :key="item.path"
          :to="item.path"
          class="my-tab-item"
          :class="{ active: isActive(item.path) }"
        >
          {{ item.label }}
        </router-link>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="my-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMobile = ref(false)

const myNavItems = [
  { label: '个人资料', path: '/tenant/my/profile', icon: '👤' },
  { label: '修改密码', path: '/tenant/my/password', icon: '🔐' },
  { label: '我的订单', path: '/tenant/my/orders', icon: '📋' },
  { label: '我的预约', path: '/tenant/my/appointments', icon: '🗓️' },
  { label: '我的收藏', path: '/tenant/my/favorites', icon: '❤️' },
  { label: '报修管理', path: '/tenant/my/repairs', icon: '🔧' },
  { label: '我的评价', path: '/tenant/my/evaluations', icon: '⭐' },
  { label: '纠纷管理', path: '/tenant/my/disputes', icon: '⚖️' },
  { label: '房东入驻', path: '/tenant/my/landlord-apply', icon: '🏘️' },
]

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.my-center {
  display: flex;
  gap: 20px;
  background: var(--bg-card);
  border-radius: 8px;
  overflow: hidden;
}

.my-sidebar {
  width: 200px;
  border-right: 1px solid var(--border-color);
  background: var(--bg-soft);
}

.my-nav {
  padding: 16px 0;
}

.my-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: #666;
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;

  &:hover {
    background-color: #f0f0f0;
    color: #409eff;
  }

  &.active {
    background-color: #f0f9ff;
    color: #409eff;
    border-left-color: #409eff;
  }
}

.my-nav-item .icon {
  font-size: 18px;
  min-width: 24px;
}

.my-nav-item .label {
  font-size: 14px;
  font-weight: 500;
}

.my-content {
  flex: 1;
  padding: 20px;
  min-height: 500px;
}

/* Mobile 样式 */
.my-tabs {
  width: 100%;
  border-bottom: 1px solid #f0f0f0;
  overflow-x: auto;
}

.tabs-scroll {
  display: flex;
  gap: 0;
  padding: 0;
  white-space: nowrap;
}

.my-tab-item {
  flex: 1;
  min-width: 100px;
  padding: 12px 16px;
  text-align: center;
  color: #666;
  text-decoration: none;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;

  &:hover {
    color: #409eff;
  }

  &.active {
    color: #409eff;
    border-bottom-color: #409eff;
  }
}

@media (max-width: 768px) {
  .my-center {
    flex-direction: column;
    gap: 0;
  }

  .my-sidebar {
    display: none;
  }

  .my-content {
    padding: 12px;
  }

  .my-tabs {
    display: flex;
  }
}
</style>
