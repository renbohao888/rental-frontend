<template>
  <div class="page-container" v-loading="loading">
    <el-card class="header-card">
      <h2>📊 数据分析</h2>
      <p>平台各项关键数据分析和洞察</p>
    </el-card>

    <el-card>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="总用户数"><span class="clickable" @click="$router.push('/admin/users')">{{ stats.userStats?.totalUsers || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="租客数"><span class="clickable" @click="$router.push('/admin/tenants')">{{ stats.userStats?.tenantCount || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="房东数"><span class="clickable" @click="$router.push('/admin/landlords')">{{ stats.userStats?.landlordCount || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="管理员数"><span class="clickable" @click="$router.push('/admin/users')">{{ stats.userStats?.adminCount || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="房源总数"><span class="clickable" @click="$router.push('/admin/rooms')">{{ stats.roomStats?.totalRooms || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="已上架房源"><span class="clickable" @click="$router.push('/admin/rooms')">{{ stats.roomStats?.publishedRooms || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="已出租房源"><span class="clickable" @click="$router.push('/admin/rooms')">{{ stats.roomStats?.rentedRooms || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="待审核房源"><span class="clickable" @click="$router.push('/admin/rooms/audit')">{{ stats.roomStats?.pendingAuditRooms || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="订单总数"><span class="clickable" @click="$router.push('/admin/orders')">{{ stats.orderStats?.totalOrders || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="已完成订单"><span class="clickable" @click="$router.push('/admin/orders')">{{ stats.orderStats?.completedOrders || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="待处理订单"><span class="clickable" @click="$router.push('/admin/orders')">{{ stats.orderStats?.pendingOrders || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="本月订单"><span class="clickable" @click="$router.push('/admin/orders')">{{ stats.orderStats?.thisMonthOrders || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="总收益"><span class="clickable money" @click="$router.push('/admin/orders')">¥{{ stats.revenueStats?.totalRevenue || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="本月收入"><span class="clickable money" @click="$router.push('/admin/orders')">¥{{ stats.revenueStats?.thisMonthRevenue || 0 }} →</span></el-descriptions-item>
        <el-descriptions-item label="平均客单价"><span class="clickable money" @click="$router.push('/admin/orders')">¥{{ stats.revenueStats?.avgOrderAmount || 0 }} →</span></el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>📈 近7天订单与收入趋势</span>
          <el-button link type="primary" @click="$router.push('/admin/orders')">查看订单 →</el-button>
        </div>
      </template>
      <el-table :data="stats.recentTrend || []" border stripe size="small" class="clickable-table" @row-click="() => $router.push('/admin/orders')">
        <el-table-column prop="date" label="日期" />
        <el-table-column prop="orderCount" label="订单数" :align="'center'" />
        <el-table-column label="收入" :align="'right'">
          <template #default="{ row }">¥{{ row.revenue || 0 }}</template>
        </el-table-column>
      </el-table>
    </el-card>
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
    console.error('加载分析数据失败', error)
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
.clickable { color: #409eff; cursor: pointer; transition: all 0.2s; }
.clickable:hover { text-decoration: underline; }
.clickable.money { color: #e6a23c; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.clickable-table :deep(.el-table__row) { cursor: pointer; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>

