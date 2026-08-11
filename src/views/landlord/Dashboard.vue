<template>
  <div class="dashboard-page" v-loading="loading">
    <el-alert v-if="loadError" type="error" :closable="false" show-icon :title="loadError" style="margin-bottom: 16px" />
    <!-- 第一排：核心指标 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/rooms')">
          <div class="stat-item">
            <div class="stat-icon">🏠</div>
            <div class="stat-value">{{ stats.totalRooms || 0 }}</div>
            <div class="stat-label">房源总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/orders?status=active')">
          <div class="stat-item">
            <div class="stat-icon">📋</div>
            <div class="stat-value">{{ stats.activeOrders || 0 }}</div>
            <div class="stat-label">进行中订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/bill')">
          <div class="stat-item">
            <div class="stat-icon">💰</div>
            <div class="stat-value">¥{{ formatMoney(stats.thisMonthRevenue) }}</div>
            <div class="stat-label">本月收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stat-card clickable" @click="$router.push('/landlord/evaluations')">
          <div class="stat-item">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">{{ stats.avgRating || '0.0' }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二排：待办提醒 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card warn clickable" @click="$router.push('/landlord/rooms')">
          <div class="stat-item">
            <div class="stat-icon">⏳</div>
            <div class="stat-value">{{ stats.pendingAuditRooms || 0 }}</div>
            <div class="stat-label">待审核房源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card danger clickable" @click="$router.push('/landlord/repairs')">
          <div class="stat-item">
            <div class="stat-icon">🔧</div>
            <div class="stat-value">{{ stats.pendingRepairs || 0 }}</div>
            <div class="stat-label">待处理报修</div>
            <el-badge v-if="(stats.pendingRepairs || 0) > 0" class="urgent-badge" :value="stats.pendingRepairs" type="danger" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card blue clickable" @click="$router.push('/landlord/repairs')">
          <div class="stat-item">
            <div class="stat-icon">🛠️</div>
            <div class="stat-value">{{ stats.processingRepairs || 0 }}</div>
            <div class="stat-label">处理中报修</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card green clickable" @click="$router.push('/landlord/rooms')">
          <div class="stat-item">
            <div class="stat-icon">📈</div>
            <div class="stat-value">{{ stats.publishedRooms || 0 }}</div>
            <div class="stat-label">已上架房源</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <!-- 最近订单 -->
      <el-col :xs="24" :md="14">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>📅 最近订单</span>
              <el-button link type="primary" @click="$router.push('/landlord/orders')">查看全部订单 →</el-button>
            </div>
          </template>
          <el-table :data="stats.recentOrders || []" style="width: 100%;" size="small" class="clickable-table" @row-click="openOrderDetail">
            <el-table-column prop="roomTitle" label="房源" min-width="110" show-overflow-tooltip />
            <el-table-column prop="tenantName" label="租客" width="90" />
            <el-table-column label="入住日期" width="105">
              <template #default="{ row }">{{ row.checkInDate || '-' }}</template>
            </el-table-column>
            <el-table-column label="金额" width="90" :align="'right'">
              <template #default="{ row }">¥{{ row.totalAmount || 0 }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderTagType(row.status)">{{ row.statusText || '未知' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!(stats.recentOrders || []).length" description="暂无订单" :image-size="60" />
        </el-card>
      </el-col>

      <!-- 待处理报修提醒 -->
      <el-col :xs="24" :md="10">
        <el-card class="chart-card repair-card">
          <template #header>
            <div class="card-header">
              <span>🔧 待处理报修</span>
              <el-badge v-if="(stats.pendingRepairs || 0) > 0" :value="stats.pendingRepairs" type="danger" />
              <el-button v-if="(stats.pendingRepairs || 0) > 0" link type="danger" @click="$router.push('/landlord/repairs')">去处理 →</el-button>
            </div>
          </template>

          <el-alert v-if="(stats.pendingRepairs || 0) > 0" type="error" :closable="false" show-icon
            :title="`有 ${stats.pendingRepairs} 个报修工单等待处理，请尽快处理以免影响租客体验！`" style="margin-bottom: 12px;" />

          <el-timeline v-if="(stats.pendingRepairList || []).length">
            <el-timeline-item v-for="item in stats.pendingRepairList" :key="item.id"
              :timestamp="formatTime(item.createTime)" placement="top"
              :type="item.status === 0 ? 'danger' : 'warning'">
              <div class="repair-item clickable" @click="$router.push('/landlord/repairs')">
                <div class="repair-title">{{ item.title }}</div>
                <div class="repair-desc">{{ item.description }}</div>
                <el-tag size="small" :type="item.status === 0 ? 'danger' : 'warning'">
                  {{ item.status === 0 ? '待处理' : '处理中' }}
                </el-tag>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无待处理报修，太棒了！" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单详情弹窗 -->
    <OrderDetailDialog v-model="detailVisible" :order="detailOrder" title="订单详情" show-user />
  </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import OrderDetailDialog from '@/components/OrderDetailDialog.vue'

const loading = ref(false)
const loadError = ref('')
const stats = ref({})

// 订单详情弹窗（最近订单行点击下钻）
const detailVisible = ref(false)
const detailOrder = ref(null)
const openOrderDetail = (row) => {
  detailOrder.value = row
  detailVisible.value = true
}

const formatMoney = (val) => {
  if (val === null || val === undefined) return '0'
  const num = Number(val)
  if (isNaN(num)) return '0'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const formatTime = (time) => {
  if (!time) return ''
  const d = new Date(time)
  return isNaN(d.getTime()) ? '' : d.toLocaleString()
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
      loadError.value = ''
    } else {
      loadError.value = res.message || '加载失败'
    }
  } catch (error) {
    console.error('加载数据失败', error)
    loadError.value = '网络请求失败，请检查后端服务是否启动'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
.dashboard-page {
  animation: fadeIn 0.3s ease-in;
}

.mb-20 {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  margin-bottom: 4px;
}

.stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-item {
  text-align: center;
  padding: 12px 0;
  position: relative;
}

.stat-icon {
  font-size: 26px;
  margin-bottom: 6px;
  opacity: 0.35;
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #999;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.warn .stat-value { color: #e6a23c; }
.stat-card.danger .stat-value { color: #f56c6c; }
.stat-card.blue .stat-value { color: #409eff; }
.stat-card.green .stat-value { color: #67c23a; }

.urgent-badge {
  position: absolute;
  top: 6px;
  right: 10px;
}

.chart-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-height: 340px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header .el-button {
  margin-left: auto;
}

.repair-item {
  border: 1px solid var(--border-color);
  background: var(--bg-soft);
  border-radius: 8px;
  padding: 10px 12px;
}
.repair-item.clickable { cursor: pointer; transition: all 0.2s; }
.repair-item.clickable:hover { background: var(--bg-hover); border-color: rgba(245, 108, 108, 0.5); }
.clickable-table :deep(.el-table__row) { cursor: pointer; }

.repair-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.repair-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 20px;
  }
  .stat-icon {
    font-size: 22px;
  }
}
</style>
