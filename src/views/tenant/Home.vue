<template>
  <div class="home-page">
    <!-- 轮播图 -->
    <el-carousel height="400px" v-if="banners.length">
      <el-carousel-item v-for="item in banners" :key="item.id">
        <div class="banner-slide" :class="{ clickable: item.linkUrl }" @click="bannerClick(item)">
          <img :src="item.imageUrl || 'https://loremflickr.com/1200/400/house?random=1'" class="banner-img" />
          <div class="banner-title">{{ item.title }}</div>
        </div>
      </el-carousel-item>
    </el-carousel>
    <el-carousel v-else height="400px">
      <el-carousel-item v-for="(fallback, idx) in defaultBanners" :key="idx">
        <img :src="fallback.img" class="banner-img" />
        <div class="banner-title">{{ fallback.title }}</div>
      </el-carousel-item>
    </el-carousel>

    <!-- 搜索框 -->
    <div class="search-box" v-reveal="{ delay: 100 }">
      <el-input v-model="searchForm.title" placeholder="搜索房源标题" style="width:200px" />
      <el-input v-model="searchForm.address" placeholder="地址" style="width:200px" />
      <el-input v-model="searchForm.minPrice" placeholder="最低价" style="width:120px" />
      <el-input v-model="searchForm.maxPrice" placeholder="最高价" style="width:120px" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 热门房源 -->
    <div class="section" v-reveal>
      <h2>🔥 热门房源</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="(room, idx) in hotRooms" :key="room.id" v-reveal="{ delay: (idx % 4) * 80 }">
          <el-card :body-style="{ padding: '10px' }" class="room-card">
            <img :src="room.cover || `https://loremflickr.com/300/200/house?random=${room.id}`" class="room-cover" />
            <div class="room-title">{{ room.title }}</div>
            <div class="room-price">¥{{ room.price }}/晚</div>
            <div class="room-tags">
              <el-tag v-for="tag in room.tags?.split(',')" :key="tag" size="small">{{ tag }}</el-tag>
            </div>
            <div style="display:flex; gap:8px; margin-top:10px;">
              <el-button type="primary" size="small" @click="goDetail(room.id)">查看详情</el-button>
              <el-button 
                :type="room.isFavorited ? 'danger' : 'default'" 
                size="small" 
                @click.stop="toggleFavorite(room)"
              >
                {{ room.isFavorited ? '❤️ 已收藏' : '🤍 收藏' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 公告 -->
    <div class="section" v-reveal="{ delay: 150 }">
      <h2>📢 最新公告</h2>
      <ul class="notice-list">
        <li v-for="item in notices" :key="item.id">
          <router-link :to="'/notice/'+item.id">{{ item.title }}</router-link>
          <span class="notice-time">{{ item.publishTime?.slice(0,10) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'  // 🔥 新增：导入 ElMessage
import { getBannerList } from '@/api/banner'
import { getHotRooms } from '@/api/room'
import { getNoticeList } from '@/api/notice'
import request from '@/utils/request'

const router = useRouter()
const banners = ref([])
const hotRooms = ref([])
const notices = ref([])

// 轮播图兜底（后端无数据时也保证首页有轮播展示）
const defaultBanners = [
  { title: '安居房屋租赁平台', img: 'https://loremflickr.com/1200/400/house?random=1' },
  { title: '海量优质房源', img: 'https://loremflickr.com/1200/400/house?random=2' },
  { title: '安心租房 · 诚信服务', img: 'https://loremflickr.com/1200/400/house?random=3' }
]

// 点击轮播图跳转到配置的链接
const bannerClick = (item) => {
  if (item?.linkUrl) {
    router.push(item.linkUrl)
  }
}

const searchForm = reactive({
  title: '',
  address: '',
  minPrice: '',
  maxPrice: ''
})

// 🔥 统一的 loadData 函数（只定义一次）
const loadData = async () => {
  try {
    const [bannerRes, hotRes, noticeRes] = await Promise.all([
      getBannerList(),
      getHotRooms(8),
      getNoticeList({ pageNum: 1, pageSize: 5 })
    ])
    if (bannerRes.code === 200) banners.value = bannerRes.data
    
    // 处理热门房源 + 收藏状态
    if (hotRes.code === 200) {
      const token = localStorage.getItem('token')
      if (token) {
        // 有登录：查询每个房源的收藏状态
        const favoriteStatus = await Promise.all(
          hotRes.data.map(async (room) => {
            try {
              const res = await request({
                url: '/favorite/check',
                method: 'get',
                params: { roomId: room.id }
              })
              return { ...room, isFavorited: res.data === true }
            } catch {
              return { ...room, isFavorited: false }
            }
          })
        )
        hotRooms.value = favoriteStatus
      } else {
        // 未登录（游客）：全部标记为未收藏
        hotRooms.value = hotRes.data.map(room => ({ ...room, isFavorited: false }))
      }
    }
    
    if (noticeRes.code === 200) notices.value = noticeRes.data?.records || []
  } catch (error) {
    console.error('加载首页数据失败', error)
  }
}

const handleSearch = () => {
  router.push({ path: '/rooms', query: searchForm })
}

const goDetail = (id) => {
  router.push(`/room/${id}`)
}

const toggleFavorite = async (room) => {
  // 未登录（游客）不能收藏
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再收藏房源')
    return
  }
  
  try {
    if (room.isFavorited) {
      // 取消收藏
      const res = await request({
        url: '/favorite/cancel',
        method: 'post',
        data: { roomId: room.id }
      })
      if (res.code === 200) {
        room.isFavorited = false
        ElMessage.success('已取消收藏')
      } else {
        ElMessage.error(res.message || '取消收藏失败')
      }
    } else {
      // 添加收藏
      const res = await request({
        url: '/favorite/add',
        method: 'post',
        data: { roomId: room.id }
      })
      if (res.code === 200) {
        room.isFavorited = true
        ElMessage.success('收藏成功')
      } else {
        ElMessage.error(res.message || '收藏失败')
      }
    }
  } catch (error) {
    console.error('收藏操作失败', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

onMounted(loadData)
</script>

<style scoped>
.banner-slide { position: relative; height: 100%; cursor: default; }
.banner-slide.clickable { cursor: pointer; }
.banner-img { width: 100%; height: 100%; object-fit: cover; }
.banner-title {
  position: absolute;
  left: 40px;
  bottom: 30px;
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  background: rgba(0, 0, 0, 0.35);
  padding: 8px 16px;
  border-radius: 6px;
}
/* 样式保持不变 */
</style>