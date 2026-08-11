<template>
  <div class="page-container" v-loading="loading">
    <el-card class="header-card">
      <h2>📊 数据报表</h2>
      <p>平台运营数据实时统计（数据来源：平台运营大屏）</p>
    </el-card>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/admin/users')"><div class="stat-label">平台总用户</div><div class="stat-value">{{ stats.userStats?.totalUsers || 0 }}</div></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/admin/rooms')"><div class="stat-label">房源总数</div><div class="stat-value">{{ stats.roomStats?.totalRooms || 0 }}</div></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/admin/orders')"><div class="stat-label">订单总数</div><div class="stat-value">{{ stats.orderStats?.totalOrders || 0 }}</div></el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card money clickable" @click="$router.push('/admin/orders')"><div class="stat-label">平台总收益</div><div class="stat-value">¥{{ stats.revenueStats?.totalRevenue || 0 }}</div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :md="14">
        <el-card>
          <template #header>📈 近7天订单 / 收入趋势</template>
          <el-table :data="stats.recentTrend || []" size="small" border stripe class="clickable-table" @row-click="() => $router.push('/admin/orders')">
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="orderCount" label="订单数" :align="'center'" />
            <el-table-column label="收入" :align="'right'">
              <template #default="{ row }">¥{{ row.revenue || 0 }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card>
          <template #header>🔥 热门房源 Top5</template>
          <div v-for="(r, i) in stats.hotRooms || []" :key="i" class="hot-item clickable" @click="$router.push('/admin/orders')">
            <span class="hot-rank">{{ i + 1 }}</span>
            <img :src="r.roomCover || 'https://loremflickr.com/50/36/house'" class="hot-cover" />
            <div class="hot-info">
              <div class="hot-title">{{ r.roomTitle }}</div>
              <div class="hot-sub">{{ r.orderCount }}单 · ¥{{ r.totalRevenue || 0 }}</div>
            </div>
          </div>
          <el-empty v-if="!(stats.hotRooms || []).length" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const stats = ref({})

const loadStats = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/dashboard/admin/stats', method: 'get' })
    if (res.code === 200) {
      stats.value = res.data || {}
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载报表失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-card.clickable { cursor: pointer; transition: all 0.3s; }
.stat-card.clickable:hover { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); transform: translateY(-2px); }
.stat-label { color: #999; font-size: 13px; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: 700; color: #409eff; }
.stat-card.money .stat-value { color: #e6a23c; }
.hot-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px dashed #eee; }
.hot-item:last-child { border-bottom: none; }
.hot-item.clickable { cursor: pointer; transition: all 0.2s; border-radius: 6px; }
.hot-item.clickable:hover { background: var(--bg-hover); }
.clickable-table :deep(.el-table__row) { cursor: pointer; }
.hot-rank { width: 22px; height: 22px; border-radius: 50%; background: #409eff; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.hot-cover { width: 48px; height: 36px; object-fit: cover; border-radius: 4px; }
.hot-info { flex: 1; }
.hot-title { font-size: 13px; color: #333; }
.hot-sub { font-size: 12px; color: #999; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>

