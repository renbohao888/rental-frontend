<template>
  <div class="page" v-loading="loading">
    <el-card class="header">
      <h2>📊 数据统计分析</h2>
      <p style="color: #999; margin: 8px 0 0;">房源、订单、收入、报修等关键指标统计（点击卡片可进入详情）</p>
    </el-card>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/rooms')">
          <el-statistic title="房源总数" :value="stats.totalRooms || 0" />
          <div class="stat-go">房源管理 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/orders')">
          <el-statistic title="进行中订单" :value="stats.activeOrders || 0" />
          <div class="stat-go">订单管理 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/bill')">
          <el-statistic title="本月收入" :value="Number(stats.thisMonthRevenue || 0)" prefix="¥" />
          <div class="stat-go">账单明细 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/evaluations')">
          <el-statistic title="平均评分" :value="Number(stats.avgRating || 0)" :precision="1" suffix="⭐" />
          <div class="stat-go">查看评价 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/rooms')">
          <el-statistic title="已上架房源" :value="stats.publishedRooms || 0" />
          <div class="stat-go">房源管理 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/rooms')">
          <el-statistic title="待审核房源" :value="stats.pendingAuditRooms || 0" />
          <div class="stat-go">房源管理 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/repairs')">
          <el-statistic title="待处理报修" :value="stats.pendingRepairs || 0" />
          <div class="stat-go">报修管理 →</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/orders')">
          <el-statistic title="累计订单" :value="stats.totalOrders || 0" />
          <div class="stat-go">订单管理 →</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>📅 最近订单</span>
          <el-button link type="primary" @click="$router.push('/landlord/orders')">查看全部订单 →</el-button>
        </div>
      </template>
      <el-table :data="stats.recentOrders || []" border stripe size="small" class="clickable-table" @row-click="openOrderDetail">
        <el-table-column prop="roomTitle" label="房源" min-width="120" show-overflow-tooltip />
        <el-table-column prop="tenantName" label="租客" width="100" />
        <el-table-column label="入住日期" width="110">
          <template #default="{ row }">{{ row.checkInDate || '-' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ row.totalAmount || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getOrderTagType(row.status)">{{ row.statusText || '未知' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!(stats.recentOrders || []).length" description="暂无订单" :image-size="60" />
    </el-card>

    <!-- 订单详情弹窗 -->
    <OrderDetailDialog v-model="detailVisible" :order="detailOrder" title="订单详情" show-user />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import OrderDetailDialog from '@/components/OrderDetailDialog.vue'

const loading = ref(false)
const stats = ref({})

// 订单详情弹窗
const detailVisible = ref(false)
const detailOrder = ref(null)
const openOrderDetail = (row) => {
  detailOrder.value = row
  detailVisible.value = true
}

const getOrderTagType = (status) => {
  const map = { '0': 'warning', '1': 'primary', '2': 'success', '3': 'warning', '4': 'success', '5': 'info', '6': 'danger' }
  return map[String(status)] || 'info'
}

const loadStats = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/dashboard/landlord/stats', method: 'get' })
    if (res.code === 200) {
      stats.value = res.data || {}
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载统计失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.page {
  animation: slideUp 0.3s ease;
}

.header {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header h2 {
  margin: 0;
  font-size: 20px;
}

.stat-card { margin-bottom: 16px; text-align: center; transition: all 0.3s; }
.stat-card.clickable { cursor: pointer; }
.stat-card.clickable:hover {
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.2);
  transform: translateY(-3px);
}
.stat-go { font-size: 12px; color: #409eff; margin-top: 8px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.clickable-table :deep(.el-table__row) { cursor: pointer; }

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

