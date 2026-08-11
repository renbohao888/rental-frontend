<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>📋 全平台订单</h2>
      <p>平台所有订单监控，支持强制退款/强制退房</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 160px" @change="reload">
          <el-option label="待支付" :value="0" />
          <el-option label="待入住" :value="1" />
          <el-option label="已入住" :value="2" />
          <el-option label="退租核算中" :value="3" />
          <el-option label="已完成" :value="4" />
          <el-option label="已取消" :value="5" />
          <el-option label="已拒绝" :value="6" />
        </el-select>
        <el-button
          type="danger"
          plain
          size="small"
          class="batch-btn"
          :disabled="selectedRows.length === 0"
          @click="batchForceDelete"
        >
          批量删除{{ selectedRows.length ? `（${selectedRows.length}）` : '' }}
        </el-button>
      </div>

      <el-empty v-if="orders.length === 0 && !loading" description="暂无订单" />

      <el-table v-if="!loading" :data="orders" border stripe style="width: 100%" @selection-change="onSelectionChange" @row-click="openDetail" class="orders-table">
        <el-table-column type="selection" width="45" @click.stop />
        <el-table-column label="房源" min-width="180">
          <template #default="{ row }">
            <div class="room-cell">
              <img :src="row.roomCoverSnapshot || 'https://loremflickr.com/100/70/house'" class="room-cover" />
              <span>{{ row.roomTitleSnapshot }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="orderNo" label="订单号" min-width="170" show-overflow-tooltip />
        <el-table-column prop="userId" label="租客ID" width="90" />
        <el-table-column prop="roomId" label="房源ID" width="90" />
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
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="openDetail(row)">详情</el-button>
            <el-button v-if="row.status === 1" type="danger" size="small" @click.stop="forceRefund(row)">强制退款</el-button>
            <el-button v-if="row.status === 2 || row.status === 3" type="warning" size="small" @click.stop="forceCheckout(row)">强制退房</el-button>
            <el-button v-if="row.status === 4 || row.status === 5 || row.status === 6" type="danger" size="small" plain @click.stop="forceDelete(row)">物理删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 订单详情弹窗 -->
      <OrderDetailDialog v-model="detailVisible" :order="detailOrder" title="订单详情" show-user>
        <template #actions>
          <el-button v-if="detailOrder?.status === 1" type="danger" size="small" @click="forceRefund(detailOrder)">强制退款</el-button>
          <el-button v-if="detailOrder?.status === 2 || detailOrder?.status === 3" type="warning" size="small" @click="forceCheckout(detailOrder)">强制退房</el-button>
          <el-button v-if="detailOrder?.status === 4 || detailOrder?.status === 5 || detailOrder?.status === 6" type="danger" size="small" plain @click="forceDelete(detailOrder)">物理删除</el-button>
        </template>
      </OrderDetailDialog>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, sizes, prev, pager, next" :page-sizes="[10, 20, 50]" @size-change="reload" @current-change="loadOrders" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import OrderDetailDialog from '@/components/OrderDetailDialog.vue'
import request from '@/utils/request'

const loading = ref(false)
const orders = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const statusFilter = ref(null)

// 订单详情弹窗
const detailVisible = ref(false)
const detailOrder = ref(null)
const openDetail = (row) => {
  detailOrder.value = row
  detailVisible.value = true
}
const selectedRows = ref([])

const getStatusType = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'primary', '3': 'warning', '4': 'success', '5': 'info', '6': 'info' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待支付', '1': '待入住', '2': '已入住', '3': '退租核算中', '4': '已完成', '5': '已取消', '6': '已拒绝' }
  return map[String(status)] || '未知'
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (statusFilter.value !== null && statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await request({ url: '/order/admin/all', method: 'get', params })
    orders.value = res?.records || []
    total.value = res?.total || 0
  } catch (error) {
    console.error('加载订单失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadOrders()
}

const onSelectionChange = (rows) => {
  selectedRows.value = rows
}

const forceRefund = (row) => {
  ElMessageBox.prompt('请输入强制退款原因：', '强制退款', {
    confirmButtonText: '确认退款',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async ({ value }) => {
    const res = await request({
      url: `/order/admin/force-refund/${row.id}`,
      method: 'post',
      params: { reason: value }
    })
    if (res.code === 200) {
      ElMessage.success(res.data || '退款成功')
      loadOrders()
    } else {
      ElMessage.error(res.message || '退款失败')
    }
  }).catch(() => {})
}

const forceCheckout = (row) => {
  ElMessageBox.prompt('请输入强制退房原因：', '强制退房', {
    confirmButtonText: '确认退房',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async ({ value }) => {
    const res = await request({
      url: `/order/admin/force-checkout/${row.id}`,
      method: 'post',
      params: { reason: value }
    })
    if (res.code === 200) {
      ElMessage.success(res.data || '退房成功')
      loadOrders()
    } else {
      ElMessage.error(res.message || '退房失败')
    }
  }).catch(() => {})
}

const forceDelete = (row) => {
  ElMessageBox.confirm(
    `确定要物理删除订单「${row.orderNo}」吗？此操作不可恢复！`,
    '物理删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(async () => {
    const res = await request({
      url: `/order/admin/force-delete/${row.id}`,
      method: 'delete'
    })
    if (res.code === 200 || res === '删除成功' || res.data === '删除成功') {
      ElMessage.success('订单已物理删除')
      loadOrders()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  }).catch(() => {})
}

const batchForceDelete = () => {
  const ids = selectedRows.value.map((r) => r.id)
  if (!ids.length) return
  ElMessageBox.confirm(
    `确定要物理删除选中的 ${ids.length} 条订单吗？此操作不可恢复！`,
    '批量物理删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(async () => {
    try {
      const res = await request({
        url: '/order/admin/force-delete/batch',
        method: 'delete',
        data: ids
      })
      if (res.code === 200) {
        ElMessage.success(res.message || '批量删除成功')
        selectedRows.value = []
        loadOrders()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(loadOrders)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.batch-btn { margin-left: auto; }
.room-cell { display: flex; align-items: center; gap: 10px; }
.room-cover { width: 70px; height: 46px; object-fit: cover; border-radius: 4px; }
.orders-table :deep(.el-table__row) { cursor: pointer; }
.deposit { font-size: 12px; color: #999; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>