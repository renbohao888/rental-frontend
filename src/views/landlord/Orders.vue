<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>📋 订单管理</h2>
      <p>处理租客的租房申请、办理入住与退租结算</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-radio-group v-model="statusFilter" @change="applyFilter">
          <el-radio-button value="active">进行中</el-radio-button>
          <el-radio-button value="0">待支付</el-radio-button>
          <el-radio-button value="1">待入住</el-radio-button>
          <el-radio-button value="2">已入住</el-radio-button>
          <el-radio-button value="3">退租核算中</el-radio-button>
          <el-radio-button value="4">已完成</el-radio-button>
          <el-radio-button value="5">已取消</el-radio-button>
          <el-radio-button value="6">已拒绝</el-radio-button>
          <el-radio-button value="all">全部</el-radio-button>
        </el-radio-group>
        <el-button
          type="danger"
          plain
          size="small"
          :disabled="selectedRows.length === 0"
          @click="batchDelete"
          class="batch-btn"
        >
          批量删除{{ selectedRows.length ? `（${selectedRows.length}）` : '' }}
        </el-button>
      </div>

      <el-empty v-if="filteredOrders.length === 0 && !loading" description="暂无订单" />

      <el-table v-if="!loading" :data="filteredOrders" border stripe style="width: 100%" @selection-change="onSelectionChange" @row-click="openDetail" class="orders-table">
        <el-table-column type="selection" width="45" @click.stop />
        <el-table-column label="房源" min-width="200">
          <template #default="{ row }">
            <div class="room-cell">
              <img :src="row.roomCoverSnapshot || 'https://loremflickr.com/100/70/house'" class="room-cover" />
              <span>{{ row.roomTitleSnapshot }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="orderNo" label="订单号" min-width="170" show-overflow-tooltip />
        <el-table-column prop="userId" label="租客ID" width="90" />
        <el-table-column label="日期" min-width="180">
          <template #default="{ row }">{{ row.checkInDate }} ~ {{ row.checkOutDate }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">¥{{ row.totalAmount }}<div class="deposit">押金 ¥{{ row.deposit || 0 }}</div></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="下单时间" min-width="160" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="openDetail(row)">详情</el-button>
            <el-button v-if="row.status === 1" type="warning" size="small" @click.stop="rejectOrder(row)">拒绝</el-button>
            <el-button v-if="row.status === 1" type="success" size="small" @click.stop="checkIn(row)">办理入住</el-button>
            <el-button v-if="row.status === 3" type="primary" size="small" @click.stop="openSettle(row)">结算完成</el-button>
            <el-button type="danger" size="small" plain @click.stop="deleteOrder(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 订单详情弹窗 -->
      <OrderDetailDialog v-model="detailVisible" :order="detailOrder" title="订单详情" show-user>
        <template #actions>
          <el-button v-if="detailOrder?.status === 1" type="warning" size="small" @click="rejectOrder(detailOrder)">拒绝订单</el-button>
          <el-button v-if="detailOrder?.status === 1" type="success" size="small" @click="checkIn(detailOrder)">办理入住</el-button>
          <el-button v-if="detailOrder?.status === 3" type="primary" size="small" @click="openSettle(detailOrder)">结算完成</el-button>
        </template>
      </OrderDetailDialog>

      <!-- 退租结算弹窗（押金 / 扣款 / 应退押金实时计算） -->
      <el-dialog v-model="settleVisible" title="💰 退租结算" width="460px" destroy-on-close>
        <div v-if="settleOrder" class="settle-block">
          <el-alert type="warning" :closable="false" show-icon
            title="结算将从押金中扣除违约/损坏等费用，剩余押金退还给租客。" style="margin-bottom: 16px" />
          <div class="settle-row">
            <span>房源</span>
            <span>{{ settleOrder.roomTitleSnapshot }}</span>
          </div>
          <div class="settle-row">
            <span>订单号</span>
            <span>{{ settleOrder.orderNo }}</span>
          </div>
          <div class="settle-row">
            <span>实付租金</span>
            <span>¥{{ fmt(settleOrder.totalAmount) }}</span>
          </div>
          <div class="settle-row">
            <span>押金</span>
            <span>¥{{ fmt(settleOrder.deposit) }}</span>
          </div>
          <div class="settle-row">
            <span>扣款金额</span>
            <el-input-number v-model="settleForm.deductAmount" :min="0" :max="Number(settleOrder.deposit) || 0" :precision="2" style="width: 180px" />
          </div>
          <div class="settle-row refund">
            <span>应退押金</span>
            <span class="refund-amount">¥{{ fmt(Number(settleOrder.deposit || 0) - Number(settleForm.deductAmount || 0)) }}</span>
          </div>
        </div>
        <template #footer>
          <el-button @click="settleVisible = false">取消</el-button>
          <el-button type="primary" :loading="settleSubmitting" @click="settleSubmit">确认结算</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import OrderDetailDialog from '@/components/OrderDetailDialog.vue'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(false)
const orders = ref([])
const selectedRows = ref([])
const statusFilter = ref('active')

// 订单详情弹窗
const detailVisible = ref(false)
const detailOrder = ref(null)
const openDetail = (row) => {
  detailOrder.value = row
  detailVisible.value = true
}

// 退租结算弹窗
const settleVisible = ref(false)
const settleOrder = ref(null)
const settleSubmitting = ref(false)
const settleForm = ref({ deductAmount: 0 })
const openSettle = (row) => {
  settleOrder.value = row
  settleForm.value = { deductAmount: 0 }
  settleVisible.value = true
}
const fmt = (v) => {
  const n = Number(v || 0)
  return isNaN(n) ? '0.00' : n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const filteredOrders = computed(() => {
  const f = statusFilter.value
  if (f === 'all') return orders.value
  if (f === 'active') return orders.value.filter((o) => o.status === 1 || o.status === 2 || o.status === 3)
  return orders.value.filter((o) => o.status === Number(f))
})

const getStatusType = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'primary', '3': 'warning', '4': 'success', '5': 'info', '6': 'info' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待支付', '1': '待入住', '2': '已入住', '3': '退租核算中', '4': '已完成', '5': '已取消', '6': '已拒绝' }
  return map[String(status)] || '未知'
}

const applyFilter = () => {}

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/order/landlord/my', method: 'get' })
    orders.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('加载订单失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const onSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleRaw = (res) => {
  if (typeof res === 'string') {
    if (res.includes('失败')) {
      ElMessage.error(res)
      return false
    }
    ElMessage.success(res)
    return true
  }
  if (res.code !== undefined && res.code !== 200) {
    ElMessage.error(res.message || '操作失败')
    return false
  }
  ElMessage.success(res.message || '操作成功')
  return true
}

const checkIn = (row) => {
  ElMessageBox.confirm(`确认入住「${row.roomTitleSnapshot}」？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const res = await request({ url: `/order/checkin/${row.id}`, method: 'post' })
    if (handleRaw(res)) loadOrders()
  }).catch(() => {})
}

const rejectOrder = (row) => {
  ElMessageBox.confirm(`拒绝订单「${row.orderNo}」？`, '提示', {
    confirmButtonText: '拒绝',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    const res = await request({ url: `/order/reject/${row.id}`, method: 'post' })
    if (handleRaw(res)) loadOrders()
  }).catch(() => {})
}

const settleSubmit = async () => {
  if (!settleOrder.value) return
  settleSubmitting.value = true
  try {
    const res = await request({
      url: `/order/complete/${settleOrder.value.id}`,
      method: 'post',
      params: { deductAmount: settleForm.value.deductAmount ?? 0 }
    })
    if (handleRaw(res)) {
      ElMessage.success(`结算成功，应退押金 ¥${fmt(Number(settleOrder.value.deposit || 0) - Number(settleForm.value.deductAmount || 0))}`)
      settleVisible.value = false
      detailVisible.value = false
      loadOrders()
    }
  } catch (error) {
    ElMessage.error('结算失败')
  } finally {
    settleSubmitting.value = false
  }
}

const deleteOrder = (row) => {
  ElMessageBox.confirm(`确定要删除订单「${row.orderNo}」吗？删除后不可恢复。`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({ url: `/order/landlord/${row.id}`, method: 'delete' })
      if (res.code === 200) { ElMessage.success('删除成功'); loadOrders() }
      else { ElMessage.error(res.message || '删除失败') }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const batchDelete = () => {
  const ids = selectedRows.value.map((r) => r.id)
  if (!ids.length) return
  ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 条订单吗？删除后不可恢复。`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await request({ url: '/order/landlord/batch', method: 'delete', data: ids })
      if (res.code === 200) { ElMessage.success(res.message || '批量删除成功'); selectedRows.value = []; loadOrders() }
      else { ElMessage.error(res.message || '删除失败') }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  const q = route.query.status
  if (q && ['active', 'all', '0', '1', '2', '3', '4', '5', '6'].includes(q)) {
    statusFilter.value = q
  }
  loadOrders()
})
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.batch-btn { margin-left: auto; }
.room-cell { display: flex; align-items: center; gap: 10px; }
.room-cover { width: 70px; height: 46px; object-fit: cover; border-radius: 4px; }
.deposit { font-size: 12px; color: #999; }
.orders-table :deep(.el-table__row) { cursor: pointer; }
.settle-block { padding: 4px 0; }
.settle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  color: #555;
  border-bottom: 1px dashed #f0f0f0;
}
.settle-row.refund {
  font-weight: 700;
  border-bottom: none;
  font-size: 15px;
}
.refund-amount { color: #67c23a; font-size: 18px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>