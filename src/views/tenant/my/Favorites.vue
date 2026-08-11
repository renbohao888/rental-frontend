<template>
  <div class="favorites-page">
    <div class="page-header">
      <h2>❤️ 我的收藏</h2>
      <el-select v-model="sortBy" @change="loadFavorites" size="small" style="width: 150px;">
        <el-option label="最新收藏" value="newest" />
        <el-option label="价格低到高" value="price-asc" />
        <el-option label="价格高到低" value="price-desc" />
        <el-option label="评分最高" value="rating" />
      </el-select>
    </div>

    <el-empty v-if="favorites.length === 0 && !loading" description="暂无收藏" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <el-row :gutter="20">
      <el-col :span="6" v-for="room in favorites" :key="room.id">
        <el-card :body-style="{ padding: '12px' }" class="room-card" @click="viewRoom(room.id)">
          <img :src="room.cover || `https://loremflickr.com/300/200/house?random=${room.id}`" class="room-cover" />
          <div class="room-title">{{ room.title }}</div>
          <div class="room-address">{{ room.address }}</div>
          <div class="room-price">¥{{ room.price }}<span class="unit">/晚</span></div>
          <div class="room-rating">⭐ {{ room.rating || '暂无' }}</div>
          <div class="room-actions">
            <el-button type="primary" size="small" @click.stop="viewRoom(room.id)">查看详情</el-button>
            <el-button type="danger" size="small" @click.stop="removeFavorite(room.id)">取消收藏</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[8, 16, 24]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadFavorites"
        @current-change="loadFavorites"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const favorites = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(8)
const sortBy = ref('newest')

const loadFavorites = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/favorite/list',
      method: 'get',
      params: {
        pageNum: pageNum.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value
      }
    })

    if (res.code === 200) {
      favorites.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.warning('后端接口开发中...')
      favorites.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载收藏失败', error)
    // 后端接口不可用时显示提示
    if (error.response?.status === 404 || error.message?.includes('404')) {
      ElMessage.info('功能开发中，敬请期待')
    } else {
      ElMessage.error('网络请求失败')
    }
    favorites.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const viewRoom = (roomId) => {
  router.push(`/room/${roomId}`)
}

const removeFavorite = async (roomId) => {
  try {
    const res = await request({
      url: '/favorite/cancel',
      method: 'post',
      data: { roomId }
    })

    if (res.code === 200) {
      ElMessage.success('已取消收藏')
      loadFavorites()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-page {
  background: var(--bg-card);
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
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
  margin-bottom: 4px;
}

.unit {
  font-size: 12px;
  font-weight: normal;
  color: #666;
}

.room-rating {
  font-size: 12px;
  color: #ffa726;
  margin-bottom: 8px;
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
  .favorites-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  :deep(.el-col) {
    width: 100% !important;
  }
}
</style>
