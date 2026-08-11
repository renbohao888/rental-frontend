<template>
  <div class="tenant-search">
    <!-- 搜索筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="searchForm.title" placeholder="搜索房源标题" style="width:200px" clearable />
      <el-input v-model="searchForm.address" placeholder="地址" style="width:180px" clearable />
      <el-input v-model="searchForm.minPrice" placeholder="最低价" style="width:120px" type="number" />
      <span style="color:#999;">-</span>
      <el-input v-model="searchForm.maxPrice" placeholder="最高价" style="width:120px" type="number" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 房源列表 -->
    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <el-empty v-if="roomList.length === 0 && !loading" description="暂无房源" />

    <el-row :gutter="20">
      <el-col :xs="12" :sm="6" :md="6" :lg="6" v-for="room in roomList" :key="room.id">
        <el-card :body-style="{ padding: '12px' }" class="room-card" @click="goDetail(room.id)">
          <img :src="room.cover || `https://loremflickr.com/300/200/house?random=${room.id}`" class="room-cover" />
          <div class="room-title">{{ room.title }}</div>
          <div class="room-address">{{ room.address }}</div>
          <div class="room-price">¥{{ room.price }}<span class="unit">/晚</span></div>
          <div class="room-tags">
            <template v-for="tag in (room.tags || '').split(',')" :key="tag">
              <el-tag size="small" v-if="tag">
                {{ tag }}
              </el-tag>
            </template>
          </div>
          <div class="room-actions">
            <el-button type="primary" size="small" @click.stop="goDetail(room.id)">查看详情</el-button>
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

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[8, 16, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadRooms"
        @current-change="loadRooms"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRoomList } from '@/api/room'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const roomList = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(8)

const searchForm = reactive({
  title: '',
  address: '',
  minPrice: '',
  maxPrice: ''
})

const loadRooms = async () => {
  loading.value = true
  try {
    const params = {
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      title: searchForm.title || undefined,
      address: searchForm.address || undefined,
      minPrice: searchForm.minPrice ? Number(searchForm.minPrice) : undefined,
      maxPrice: searchForm.maxPrice ? Number(searchForm.maxPrice) : undefined
    }
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === null) {
        delete params[key]
      }
    })
    const res = await getRoomList(params)
    if (res.code === 200 || res.code === 0) {
      const list = res.data?.records || res.data?.list || []
      
      // 检查收藏状态
      const token = localStorage.getItem('token')
      if (token) {
        roomList.value = await Promise.all(list.map(async (room) => {
          try {
            const favRes = await request({
              url: '/favorite/check',
              method: 'get',
              params: { roomId: room.id }
            })
            return { ...room, isFavorited: favRes.data === true }
          } catch {
            return { ...room, isFavorited: false }
          }
        }))
      } else {
        roomList.value = list.map(room => ({ ...room, isFavorited: false }))
      }
      
      total.value = res.data?.total || list.length || 0
    } else {
      ElMessage.error(res.message || '加载失败，请检查网络')
    }
  } catch (error) {
    console.error('加载房源列表失败', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pageNum.value = 1
  loadRooms()
}

const resetSearch = () => {
  searchForm.title = ''
  searchForm.address = ''
  searchForm.minPrice = ''
  searchForm.maxPrice = ''
  pageNum.value = 1
  loadRooms()
}

const goDetail = (id) => {
  router.push(`/room/${id}`)
}

const toggleFavorite = async (room) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    if (room.isFavorited) {
      const res = await request({
        url: '/favorite/cancel',
        method: 'post',
        data: { roomId: room.id }
      })
      if (res.code === 200) {
        room.isFavorited = false
        ElMessage.success('已取消收藏')
      }
    } else {
      const res = await request({
        url: '/favorite/add',
        method: 'post',
        data: { roomId: room.id }
      })
      if (res.code === 200) {
        room.isFavorited = true
        ElMessage.success('收藏成功')
      }
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.tenant-search {
  background: var(--bg-card);
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
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
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 8px;
}

.room-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-address {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.room-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff6b6b;
  margin-bottom: 8px;
}

.unit {
  font-size: 12px;
  font-weight: normal;
  color: #666;
}

.room-tags {
  margin-bottom: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.room-actions {
  display: flex;
  gap: 6px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 1200px) {
  :deep(.el-col) {
    width: 50% !important;
  }
}

@media (max-width: 768px) {
  .tenant-search {
    padding: 12px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-bar :deep(.el-input) {
    width: 100% !important;
  }

  .filter-bar :deep(.el-button) {
    width: 100%;
  }
  
  .room-actions { flex-wrap: wrap; }
}

@media (max-width: 480px) {
  .room-cover { height: 180px; }
  .pagination :deep(.el-pagination) { justify-content: center; flex-wrap: wrap; }
}
</style>
