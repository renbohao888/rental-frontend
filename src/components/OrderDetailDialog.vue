<template>
  <el-dialog :model-value="modelValue" :title="title || '订单详情'" width="620px" @update:model-value="$emit('update:modelValue', $event)" destroy-on-close>
    <div v-if="order" class="order-detail">
      <!-- 房源信息（可点击下钻） -->
      <div class="room-card" @click="goRoomDetail">
        <img :src="order.roomCoverSnapshot || 'https://loremflickr.com/120/80/house'" class="room-cover" />
        <div class="room-info">
          <div class="room-title">{{ order.roomTitleSnapshot }}</div>
          <div class="room-sub">房源ID：{{ order.roomId }}</div>
        </div>
        <el-tag :type="statusType" size="small">{{ statusName }}</el-tag>
      </div>

      <!-- 基本信息 -->
      <el-descriptions :column="2" border size="small" class="desc">
        <el-descriptions-item label="订单号">{{ order.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(order.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="入住日期">{{ order.checkInDate }}</el-descriptions-item>
        <el-descriptions-item label="退租日期">{{ order.checkOutDate }}</el-descriptions-item>
        <el-descriptions-item label="入住晚数">{{ stayNights }} 晚</el-descriptions-item>
        <el-descriptions-item label="支付流水">
          <span v-if="order.alipayTradeNo">{{ order.alipayTradeNo }}</span>
          <span v-else class="muted">—</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="showUser" label="租客">
          <span>{{ order.userNickname || ('用户#' + order.userId) }}</span>
          <span class="muted" v-if="order.userPhone">（{{ order.userPhone }}）</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 押金 / 租金明细 -->
      <div class="money-block">
        <div class="money-title">💰 费用明细</div>
        <div class="money-row">
          <span>租金单价</span>
          <span>¥{{ fmt(unitPrice) }} / 晚</span>
        </div>
        <div class="money-row">
          <span>入住晚数</span>
          <span>{{ stayNights }} 晚</span>
        </div>
        <div class="money-row">
          <span>租金小计（{{ stayNights }} 晚）</span>
          <span>¥{{ fmt(order.totalAmount) }}</span>
        </div>
        <div class="money-row">
          <span>押金</span>
          <span>¥{{ fmt(order.deposit) }}</span>
        </div>
        <div class="money-row total">
          <span>应付合计（租金 + 押金）</span>
          <span>¥{{ fmt((Number(order.totalAmount) || 0) + (Number(order.deposit) || 0)) }}</span>
        </div>
        <el-alert v-if="order.status === 3" type="info" :closable="false" show-icon
          title="该订单处于退租核算中，结算时将从押金中扣除违约/损坏费用，剩余部分退还租客。" style="margin-top:10px" />
      </div>

      <!-- 管理员备注 -->
      <div v-if="order.adminRemark" class="remark">
        <span class="remark-label">备注：</span>{{ order.adminRemark }}
      </div>

      <!-- 操作按钮插槽（由父组件根据角色/状态渲染） -->
      <div v-if="$slots.actions" class="actions">
        <slot name="actions" />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: null },
  title: { type: String, default: '订单详情' },
  // 是否展示租客信息列（管理端/房东端传 true）
  showUser: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const STATUS_MAP = {
  0: { name: '待支付', type: 'warning' },
  1: { name: '已支付待入住', type: 'primary' },
  2: { name: '已入住', type: 'success' },
  3: { name: '退租核算中', type: 'warning' },
  4: { name: '已完成', type: 'success' },
  5: { name: '已取消', type: 'info' },
  6: { name: '已拒绝', type: 'danger' }
}
const statusName = computed(() => STATUS_MAP[props.order?.status]?.name || '未知')
const statusType = computed(() => STATUS_MAP[props.order?.status]?.type || 'info')
const stayNights = computed(() => {
  if (!props.order?.checkInDate || !props.order?.checkOutDate) return 0
  const diff = new Date(props.order.checkOutDate).getTime() - new Date(props.order.checkInDate).getTime()
  return Math.round(diff / 86400000)
})
// 租金单价：优先取快照字段，缺失时按总额/晚数推算
const unitPrice = computed(() => {
  const o = props.order
  if (o?.unitPrice != null && Number(o.unitPrice) > 0) return o.unitPrice
  if (o?.roomPrice != null && Number(o.roomPrice) > 0) return o.roomPrice
  if (o?.totalAmount && stayNights.value > 0) {
    return Number(o.totalAmount) / stayNights.value
  }
  return 0
})

const fmt = (v) => {
  const n = Number(v || 0)
  return isNaN(n) ? '0.00' : n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
const formatTime = (t) => (t ? String(t).replace('T', ' ').slice(0, 19) : '')

const goRoomDetail = () => {
  if (props.order?.roomId) {
    router.push(`/room/${props.order.roomId}`)
  }
}
</script>

<style scoped>
.order-detail .room-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.order-detail .room-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.room-cover {
  width: 90px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
}
.room-info { flex: 1; }
.room-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.room-sub { font-size: 12px; color: #999; }
.desc { margin-bottom: 14px; }
.muted { color: #999; font-size: 12px; }
.money-block {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
}
.money-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; }
.money-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 13px;
  color: #555;
}
.money-row.total {
  font-weight: 700;
  font-size: 15px;
  color: #f56c6c;
  border-top: 1px dashed #ddd;
  margin-top: 6px;
  padding-top: 10px;
}
.remark {
  background: #fff7e6;
  border: 1px solid #ffd591;
  color: #874d00;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
  margin-bottom: 14px;
}
.remark-label { font-weight: 600; }
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
</style>
