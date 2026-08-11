<template>
  <div class="room-list-page">
    <!-- 搜索筛选栏（58同城风格） -->
    <div class="filter-bar rc-card" v-reveal>
      <el-input v-model="searchForm.title" placeholder="输入小区 / 房源名称" clearable class="f-input f-title">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-input v-model="searchForm.address" placeholder="区域 / 地址" clearable class="f-input f-addr" />
      <div class="f-price">
        <el-input v-model="searchForm.minPrice" placeholder="最低价" type="number" />
        <span class="price-sep">—</span>
        <el-input v-model="searchForm.maxPrice" placeholder="最高价" type="number" />
        <span class="price-unit">元/晚</span>
      </div>
      <el-button type="primary" @click="handleSearch" class="f-search-btn">搜索</el-button>
      <el-button @click="resetSearch" class="f-reset-btn">重置</el-button>
    </div>

    <!-- 房源信息流列表 -->
    <div class="room-feed">
      <div
        class="rc-card room-item"
        v-for="(room, idx) in roomList"
        :key="room.id"
        v-reveal="{ delay: (idx % 3) * 100 }"
        @click="goDetail(room.id)"
      >
        <img :src="room.cover || `https://loremflickr.com/300/200/house?random=${room.id}`" class="room-cover" />
        <div class="room-info">
          <div class="room-title">{{ room.title }}</div>
          <div class="room-address">
            <el-icon><Location /></el-icon> {{ room.address }}
          </div>
          <div class="room-tags">
            <span class="rc-tag" v-for="tag in getTags(room)" :key="tag">{{ tag }}</span>
            <span class="room-status-tag" :class="room.status === 1 ? 'on' : 'off'">
              {{ room.status === 1 ? '在租' : '待审核' }}
            </span>
          </div>
          <div class="room-bottom">
            <div class="room-price">
              <span class="currency">¥</span>{{ room.price }}<span class="unit">/晚</span>
            </div>
            <el-button size="small" type="primary" plain @click.stop="goDetail(room.id)">查看详情</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="roomList.length === 0 && !loading" description="暂无房源，换个条件试试吧" />

    <!-- 分页 -->
    <div class="pagination" v-reveal>
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
import { Search, Location } from '@element-plus/icons-vue'
import { getRoomList } from '@/api/room'

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
    // 兼容 code === 0 或 200
    if (res.code === 200 || res.code === 0) {
      const list = res.data?.records || res.data?.list || []
      roomList.value = list
      total.value = res.data?.total || list.length || 0
    } else {
      ElMessage.error(res.message || '加载失败，请检查网络')
    }
  } catch (error) {
    console.error('加载房源列表失败', error)
    // 不弹出错误，避免影响用户体验
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

const getTags = (room) => {
  if (!room.tags) return []
  return String(room.tags).split(',').map(t => t.trim()).filter(Boolean).slice(0, 3)
}

onMounted(loadRooms)
</script>

<style scoped>
.room-list-page {
  max-width: 1100px;
  margin: 0 auto;
}

/* ===== 58同城风格筛选栏 ===== */
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 20px;
  margin-bottom: 18px;
}
.f-title {
  width: 220px;
}
.f-addr {
  width: 160px;
}
.f-price {
  display: flex;
  align-items: center;
  gap: 6px;
}
.f-price .el-input {
  width: 96px;
}
.price-sep {
  color: #999;
}
.price-unit {
  color: #999;
  font-size: 12px;
  white-space: nowrap;
}
.f-search-btn {
  padding: 0 26px;
}

/* ===== 房源信息流卡片 ===== */
.room-feed {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.room-item {
  display: flex;
  padding: 14px;
  cursor: pointer;
}
.room-cover {
  width: 220px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
  background: var(--bg-hover);
}
.room-info {
  flex: 1;
  min-width: 0;
  margin-left: 16px;
  display: flex;
  flex-direction: column;
}
.room-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.room-title:hover {
  color: #ff6a00;
}
.room-address {
  display: flex;
  align-items: center;
  gap: 2px;
  color: var(--text-sub);
  font-size: 13px;
  margin-top: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.room-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.room-status-tag {
  font-size: 12px;
  border-radius: 4px;
  padding: 0 6px;
  line-height: 20px;
}
.room-status-tag.on {
  background: rgba(255, 106, 0, 0.15);
  color: #ff6a00;
  border: 1px solid rgba(255, 106, 0, 0.4);
}
html.dark .room-status-tag.on {
  background: rgba(255, 106, 0, 0.15);
  border-color: rgba(255, 106, 0, 0.4);
}
.room-status-tag.off {
  background: var(--bg-soft);
  color: var(--text-sub);
  border: 1px solid var(--border-color);
}
.room-bottom {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.room-price {
  color: #ff6a00;
  font-weight: 700;
  font-size: 20px;
}
.room-price .currency {
  font-size: 15px;
}
.room-price .unit {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-sub);
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .filter-bar {
    padding: 12px;
  }
  .f-title, .f-addr {
    width: 100%;
  }
  .f-price {
    width: 100%;
    flex-wrap: wrap;
  }
  .f-price .el-input {
    width: 40%;
  }
  .f-search-btn, .f-reset-btn {
    width: 100%;
  }
  .room-item {
    flex-direction: column;
  }
  .room-cover {
    width: 100%;
    height: 180px;
  }
  .room-info {
    margin-left: 0;
    margin-top: 10px;
  }
  .pagination :deep(.el-pagination) {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .room-cover { height: 150px; }
  .room-title { font-size: 14px; }
  .room-price { font-size: 17px; }
  .room-bottom { flex-direction: column; gap: 8px; align-items: flex-start; }
}
</style>