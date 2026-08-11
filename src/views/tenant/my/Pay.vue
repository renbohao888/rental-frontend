<template>
  <div class="pay-page">
    <el-card class="header-card">
      <h2>💳 订单支付</h2>
      <p>确认订单信息并完成支付（模拟支付，即时到账）</p>
    </el-card>

    <div v-loading="loading" class="pay-body">
      <el-empty v-if="!loading && !order" description="未找到该订单，可能已被取消或已支付">
        <el-button type="primary" @click="goOrders">返回我的订单</el-button>
      </el-empty>

      <template v-else-if="order">
        <!-- 订单信息 -->
        <el-card class="order-card">
          <template #header>
            <div class="card-header">
              <span>订单详情</span>
              <el-tag :type="getStatusType(order.status)">{{ getStatusName(order.status) }}</el-tag>
            </div>
          </template>

          <div class="order-row">
            <img :src="order.roomCoverSnapshot || ''" class="room-thumb" />
            <div class="order-meta">
              <div class="room-title">{{ order.roomTitleSnapshot }}</div>
              <div class="meta-line">订单号：{{ order.orderNo }}</div>
              <div class="meta-line">
                {{ formatDate(order.checkInDate) }} ~ {{ formatDate(order.checkOutDate) }}（{{ calcDays(order) }}晚）
              </div>
            </div>
          </div>

          <el-descriptions :column="1" border class="amount-desc">
            <el-descriptions-item label="租金">
              ¥{{ order.totalAmount }}
            </el-descriptions-item>
            <el-descriptions-item label="押金">
              ¥{{ order.deposit || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="合计应付">
              <span class="total-amount">¥{{ Number(order.totalAmount || 0) + Number(order.deposit || 0) }}</span>
            </el-descriptions-item>
          </el-descriptions>

          <div class="pay-actions">
            <el-button @click="goOrders">暂不支付</el-button>
            <el-button
              v-if="order.status === 0"
              type="primary"
              size="large"
              :loading="paying"
              @click="doPay"
            >
              确认支付（模拟）¥{{ order.totalAmount }}
            </el-button>
            <el-button v-else type="success" size="large" @click="goOrders">查看我的订单</el-button>
          </div>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const paying = ref(false)
const order = ref(null)

const getStatusName = (status) => {
  const map = { '0': '待支付', '1': '已支付待入住', '2': '已入住', '3': '退租核算中', '4': '已完成', '5': '已取消', '6': '已拒绝' }
  return map[String(status)] || '未知'
}

const getStatusType = (status) => {
  const map = { '0': 'danger', '1': 'success', '2': 'warning', '3': 'warning', '4': 'success', '5': 'info', '6': 'info' }
  return map[String(status)] || 'default'
}

const formatDate = (d) => {
  if (!d) return '-'
  return String(d).slice(0, 10)
}

const calcDays = (o) => {
  if (!o?.checkInDate || !o?.checkOutDate) return 0
  const diff = new Date(o.checkOutDate).getTime() - new Date(o.checkInDate).getTime()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

const loadOrder = async () => {
  const orderNo = route.query.orderNo
  if (!orderNo) {
    ElMessage.warning('缺少订单号参数')
    return
  }
  loading.value = true
  try {
    // 从我的订单中查找该订单
    const res = await request({ url: '/order/my', method: 'get' })
    if (res.code === 200 || res.code === 0) {
      const list = Array.isArray(res.data) ? res.data : (Array.isArray(res) ? res : [])
      order.value = list.find((o) => String(o.orderNo) === String(orderNo)) || null
      if (order.value && order.value.status !== 0) {
        // 订单已支付/取消等，无需再支付
      }
    } else {
      ElMessage.error(res.message || '加载订单失败')
    }
  } catch (error) {
    console.error('加载订单失败', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const doPay = async () => {
  paying.value = true
  try {
    const res = await request({
      url: '/pay/simulate',
      method: 'post',
      params: { orderNo: order.value.orderNo }
    })
    if (res.code === 200 || res.code === 0) {
      ElMessage.success('支付成功！（模拟）')
      order.value.status = 1
      setTimeout(() => {
        router.replace('/tenant/my/orders')
      }, 1200)
    } else {
      ElMessage.error(res.message || '支付失败')
    }
  } catch (error) {
    console.error('支付失败', error)
    ElMessage.error('支付失败，请稍后重试')
  } finally {
    paying.value = false
  }
}

const goOrders = () => {
  router.push('/tenant/my/orders')
}

onMounted(loadOrder)
</script>

<style scoped>
.pay-page { max-width: 720px; margin: 0 auto; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.pay-body { min-height: 260px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.order-row { display: flex; gap: 16px; margin-bottom: 16px; }
.room-thumb { width: 96px; height: 72px; border-radius: 6px; object-fit: cover; background: var(--bg-soft); }
.order-meta { flex: 1; }
.room-title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.meta-line { font-size: 12px; color: #666; margin-top: 4px; }
.amount-desc { margin-bottom: 16px; }
.total-amount { color: #ff6b6b; font-size: 18px; font-weight: 700; }
.pay-actions { display: flex; justify-content: flex-end; gap: 12px; }
</style>
