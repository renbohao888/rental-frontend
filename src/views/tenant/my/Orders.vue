<template>
  <div class="orders-page">
    <div class="page-header">
      <h2>📋 我的订单</h2>
      <div class="header-actions">
        <el-button
          type="danger"
          plain
          size="small"
          :disabled="selectedIds.length === 0"
          @click="batchDelete"
        >
          批量删除{{ selectedIds.length ? `（${selectedIds.length}）` : '' }}
        </el-button>
        <el-select v-model="statusFilter" @change="loadOrders" size="small" style="width: 160px;">
          <el-option label="全部订单" value="" />
          <el-option label="待支付" value="0" />
          <el-option label="已支付待入住" value="1" />
          <el-option label="已入住" value="2" />
          <el-option label="退租核算中" value="3" />
          <el-option label="已完成" value="4" />
          <el-option label="已取消" value="5" />
          <el-option label="已拒绝" value="6" />
        </el-select>
      </div>
    </div>

    <el-empty v-if="orders.length === 0 && !loading" description="暂无订单" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-for="order in orders" :key="order.id" class="order-card" :class="{ checked: selectedIds.includes(order.id) }" @click="openDetail(order)">
      <div class="order-header">
        <div class="order-info">
          <el-checkbox v-model="selectedIds" :value="order.id" @click.stop />
          <div class="order-id">订单号：{{ order.orderNo }}</div>
          <el-tag :type="getStatusType(order.status)">{{ getStatusName(order.status) }}</el-tag>
        </div>
        <div class="order-time">{{ formatDate(order.createTime) }}</div>
      </div>

      <div class="order-body">
        <img :src="order.roomCoverSnapshot" class="room-thumb" />
        <div class="room-details">
          <div class="room-title">{{ order.roomTitleSnapshot }}</div>
          <div class="order-dates">
            {{ formatDate(order.checkInDate) }} ~ {{ formatDate(order.checkOutDate) }}
          </div>
          <div class="order-deposit">押金 ¥{{ order.deposit || 0 }}</div>
        </div>
        <div class="order-amount">
          <div class="price">¥{{ order.totalAmount }}</div>
          <div class="days">{{ calcDays(order) }} 晚</div>
        </div>
      </div>

      <div class="order-actions" @click.stop>
        <el-button size="small" @click="openDetail(order)">查看详情</el-button>
        <el-button v-if="order.status === 0" type="primary" size="small" @click="goPay(order)">去支付</el-button>
        <el-button v-if="order.status === 0" size="small" @click="cancelOrder(order.id)">取消订单</el-button>
        <el-button v-if="order.status === 4" type="success" size="small" @click="goEvaluate(order)">去评价</el-button>
        <el-button v-if="order.status === 4 || order.status === 5 || order.status === 6" size="small" type="danger" plain @click="deleteOrder(order.id)">删除订单</el-button>
      </div>
    </div>

    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadOrders"
        @current-change="loadOrders"
      />
    </div>

    <!-- 订单详情弹窗 -->
    <OrderDetailDialog v-model="detailVisible" :order="detailOrder" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import OrderDetailDialog from '@/components/OrderDetailDialog.vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const statusFilter = ref('')
const selectedIds = ref([])

// 订单详情弹窗
const detailVisible = ref(false)
const detailOrder = ref(null)
const openDetail = (order) => {
  detailOrder.value = order
  detailVisible.value = true
}

const getStatusType = (status) => {
  const map = { '0': 'warning', '1': 'primary', '2': 'success', '3': 'info', '4': 'success', '5': 'info', '6': 'danger' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待支付', '1': '已支付待入住', '2': '已入住', '3': '退租核算中', '4': '已完成', '5': '已取消', '6': '已拒绝' }
  return map[String(status)] || '未知'
}

const calcDays = (order) => {
  if (!order.checkInDate || !order.checkOutDate) return 0
  const start = new Date(order.checkInDate)
  const end = new Date(order.checkOutDate)
  return Math.max(0, Math.round((end - start) / (1000 * 60 * 60 * 24)))
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/order/tenant/list',
      method: 'get',
      params: {
        pageNum: pageNum.value,
        pageSize: pageSize.value,
        status: statusFilter.value || undefined
      }
    })

    if (res.code === 200) {
      orders.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载订单失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const goPay = (order) => {
  router.push({ path: '/tenant/my/pay', query: { orderNo: order.orderNo, orderId: order.id } })
}

const goEvaluate = (order) => {
  router.push({ path: '/tenant/my/evaluations', query: { orderId: order.id, roomTitle: order.roomTitleSnapshot } })
}

const cancelOrder = (orderId) => {
  ElMessageBox.confirm('确定要取消此订单吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: `/order/${orderId}/cancel`,
        method: 'post'
      })

      if (res.code === 200) {
        ElMessage.success('已取消订单')
        loadOrders()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const deleteOrder = (orderId) => {
  ElMessageBox.confirm('确定要删除此订单吗？删除后可在回收站保留30天。', '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: `/order/${orderId}`,
        method: 'delete'
      })
      if (res.code === 200 || res === '删除成功' || res.data === '删除成功') {
        ElMessage.success('订单已删除')
        loadOrders()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const batchDelete = () => {
  if (!selectedIds.value.length) return
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条订单吗？删除后可在回收站保留30天。`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: '/order/batch',
        method: 'delete',
        data: selectedIds.value
      })
      if (res.code === 200) {
        ElMessage.success(res.message || '批量删除成功')
        selectedIds.value = []
        loadOrders()
      } else {
        ElMessage.error(res.message || '批量删除失败')
      }
    } catch (error) {
      ElMessage.error('批量删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadOrders()
})
</script>
<style scoped>
.orders-page {
  background: var(--bg-card);
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-header h2 {
  margin: 0;
}

.order-card {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  &.checked {
    border-color: #409eff;
    background: #f0f9ff;
  }
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.order-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.order-id {
  font-size: 13px;
  color: #666;
}

.order-time {
  font-size: 12px;
  color: #999;
}

.order-body {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.room-thumb {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  object-fit: cover;
}

.room-details {
  flex: 1;
}

.room-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.room-address {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.order-dates {
  font-size: 12px;
  color: #666;
}

.order-amount {
  text-align: right;
}

.price {
  font-size: 16px;
  font-weight: 600;
  color: #ff6b6b;
}

.days {
  font-size: 12px;
  color: #999;
}

.order-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 768px) {
  .orders-page {
    padding: 12px;
  }

  .order-body {
    flex-direction: column;
  }

  .room-thumb {
    width: 100%;
    height: 150px;
  }
}
</style>
