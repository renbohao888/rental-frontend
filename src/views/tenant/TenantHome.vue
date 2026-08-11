<template>
  <div class="tenant-home">
    <!-- 欢迎区 -->
    <div class="welcome-banner" v-reveal>
      <h1>欢迎回来，{{ userInfo?.nickname || '租客' }}</h1>
      <p>探索您喜欢的房源，享受舒适生活</p>
    </div>

    <!-- 轮播图 -->
    <el-carousel v-if="banners.length" height="260px" class="banner-carousel">
      <el-carousel-item v-for="item in banners" :key="item.id">
        <div class="banner-slide" :class="{ clickable: item.linkUrl }" @click="bannerClick(item)">
          <img :src="item.imageUrl || 'https://loremflickr.com/1200/400/house?random=1'" class="banner-img" />
          <div class="banner-title">{{ item.title }}</div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 快速导航 -->
    <div class="quick-links" v-reveal="{ delay: 100 }">
      <router-link to="/tenant/search" class="quick-link-card">
        <div class="icon">🔍</div>
        <div class="label">找房源</div>
        <div class="desc">浏览租赁房源</div>
      </router-link>
      <router-link to="/tenant/my/orders" class="quick-link-card">
        <div class="icon">📋</div>
        <div class="label">我的订单</div>
        <div class="desc">查看订单详情</div>
      </router-link>
      <router-link to="/tenant/my/favorites" class="quick-link-card">
        <div class="icon">❤️</div>
        <div class="label">我的收藏</div>
        <div class="desc">{{ favoriteCount }}个房源</div>
      </router-link>
      <router-link to="/tenant/my/repairs" class="quick-link-card">
        <div class="icon">🔧</div>
        <div class="label">报修管理</div>
        <div class="desc">{{ repairCount }}条待处理</div>
      </router-link>
      <router-link to="/chat" class="quick-link-card">
        <div class="icon">💬</div>
        <div class="label">消息中心</div>
        <div class="desc">{{ messageCount }}条未读</div>
      </router-link>
      <router-link to="/tenant/my/profile" class="quick-link-card">
        <div class="icon">👤</div>
        <div class="label">个人中心</div>
        <div class="desc">修改个人信息</div>
      </router-link>
    </div>

    <!-- 热门推荐 -->
    <div class="section" v-reveal>
      <h2>🔥 热门房源推荐</h2>
      <div v-if="loading" class="loading">
        <el-skeleton :rows="2" animated />
      </div>
      <el-empty v-if="hotRooms.length === 0 && !loading" description="暂无房源" />
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" :md="6" v-for="(room, idx) in hotRooms" :key="room.id" v-reveal="{ delay: (idx % 4) * 80 }">
          <el-card :body-style="{ padding: '10px' }" class="room-card" @click="goDetail(room.id)">
            <img :src="room.cover || `https://loremflickr.com/300/200/house?random=${room.id}`" class="room-cover" />
            <div class="room-title">{{ room.title }}</div>
            <div class="room-price">¥{{ room.price }}/晚</div>
            <el-button type="primary" size="small" style="width: 100%; margin-top: 8px;" @click.stop="goDetail(room.id)">
              查看详情
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 个人统计 -->
    <div class="stats-section" v-reveal="{ delay: 120 }">
      <div class="stat-card clickable" @click="router.push('/tenant/my/orders')">
        <div class="stat-title">活跃订单</div>
        <div class="stat-value">{{ activeOrderCount }}</div>
        <div class="stat-go">查看订单 →</div>
      </div>
      <div class="stat-card clickable" @click="router.push('/tenant/my/favorites')">
        <div class="stat-title">我的收藏</div>
        <div class="stat-value">{{ favoriteCount }}</div>
        <div class="stat-go">查看收藏 →</div>
      </div>
      <div class="stat-card clickable" @click="router.push('/tenant/my/orders')">
        <div class="stat-title">完成订单</div>
        <div class="stat-value">{{ completedOrderCount }}</div>
        <div class="stat-go">查看订单 →</div>
      </div>
      <div class="stat-card clickable" @click="router.push('/tenant/my/repairs')">
        <div class="stat-title">待处理报修</div>
        <div class="stat-value">{{ repairCount }}</div>
        <div class="stat-go">查看报修 →</div>
      </div>
    </div>

    <!-- 平台公告 -->
    <div class="section" v-reveal="{ delay: 150 }">
      <h2>📢 平台公告</h2>
      <ul v-if="notices.length" class="notice-list">
        <li v-for="item in notices" :key="item.id">
          <router-link :to="'/notice/'+item.id">{{ item.title }}</router-link>
          <span class="notice-time">{{ item.publishTime?.slice(0,10) }}</span>
        </li>
      </ul>
      <el-empty v-else-if="!loading" description="暂无公告" :image-size="60" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserInfo } from '@/api/user'
import { getHotRooms } from '@/api/room'
import { getBannerList } from '@/api/banner'
import { getNoticeList } from '@/api/notice'
import request from '@/utils/request'

const router = useRouter()
const userInfo = ref(null)
const hotRooms = ref([])
const loading = ref(false)
const banners = ref([])
const notices = ref([])

// 统计数据
const favoriteCount = ref(0)
const repairCount = ref(0)
const messageCount = ref(0)
const activeOrderCount = ref(0)
const completedOrderCount = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    // 获取用户信息
    const userRes = await getUserInfo()
    if (userRes.code === 200) {
      userInfo.value = userRes.data
    }

    // 获取轮播图
    const bannerRes = await getBannerList().catch(() => null)
    if (bannerRes?.code === 200) {
      banners.value = bannerRes.data || []
    }

    // 获取热门房源
    const hotRes = await getHotRooms(8)
    if (hotRes.code === 200) {
      hotRooms.value = hotRes.data || []
    }

    // 获取平台公告
    const noticeRes = await getNoticeList({ pageNum: 1, pageSize: 5 }).catch(() => null)
    if (noticeRes?.code === 200) {
      notices.value = noticeRes.data?.records || []
    }

    // 获取统计数据
    const statsRes = await request({
      url: '/tenant/stats',
      method: 'get'
    }).catch(() => null) // 统计接口失败不阻塞页面

    if (statsRes?.code === 200) {
      favoriteCount.value = statsRes.data?.favoriteCount || 0
      repairCount.value = statsRes.data?.repairCount || 0
      messageCount.value = statsRes.data?.messageCount || 0
      activeOrderCount.value = statsRes.data?.activeOrderCount || 0
      completedOrderCount.value = statsRes.data?.completedOrderCount || 0
    }
  } catch (error) {
    console.error('加载数据失败', error)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => {
  router.push(`/room/${id}`)
}

const bannerClick = (item) => {
  if (item?.linkUrl) {
    router.push(item.linkUrl)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.tenant-home {
  background: var(--bg-card);
  padding: 20px;
  border-radius: 12px;
  transition: background-color 0.3s ease;
}

.banner-carousel { margin-bottom: 24px; border-radius: 10px; overflow: hidden; }
.banner-slide { position: relative; height: 100%; cursor: default; }
.banner-slide.clickable { cursor: pointer; }
.banner-img { width: 100%; height: 100%; object-fit: cover; }
.banner-title {
  position: absolute;
  left: 30px;
  bottom: 20px;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  background: rgba(0, 0, 0, 0.35);
  padding: 6px 14px;
  border-radius: 6px;
}

.welcome-banner {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 32px;
}

.welcome-banner h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.welcome-banner p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.quick-link-card {
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }
}

.quick-link-card .icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.quick-link-card .label {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 4px;
}

.quick-link-card .desc {
  font-size: 12px;
  color: var(--text-sub);
}

.section {
  margin-bottom: 32px;
}

.section h2 {
  margin-bottom: 16px;
  font-size: 18px;
}

.loading {
  padding: 20px;
}

.room-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
}

.room-cover {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 8px;
}

.room-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-price {
  font-size: 14px;
  color: #ff6b6b;
  font-weight: 600;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 20px;
  background: var(--bg-soft);
  border-radius: 8px;
}

.stat-card {
  background: var(--bg-card);
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  border-left: 3px solid #409eff;
}

.stat-card.clickable { cursor: pointer; transition: all 0.3s; }
.stat-card.clickable:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.25);
  transform: translateY(-2px);
}
.stat-go { font-size: 12px; color: #409eff; margin-top: 4px; opacity: 0.8; }

.stat-title {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
}

.notice-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notice-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 8px;
  border-bottom: 1px dashed var(--border-color);
}

.notice-list li:last-child {
  border-bottom: none;
}

.notice-list a {
  color: var(--text-main);
  text-decoration: none;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
}

.notice-list a:hover {
  color: #409eff;
}

.notice-time {
  color: var(--text-sub);
  font-size: 12px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .tenant-home {
    padding: 12px;
  }

  .welcome-banner {
    padding: 20px;
  }

  .welcome-banner h1 {
    font-size: 18px;
  }

  .quick-links {
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .quick-link-card {
    padding: 12px;
  }

  .quick-link-card .icon {
    font-size: 24px;
  }

  .quick-link-card .label {
    font-size: 12px;
  }

  .quick-link-card .desc {
    display: none;
  }

  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
