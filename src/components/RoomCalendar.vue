<template>
  <div class="room-calendar" v-loading="loading">
    <el-calendar v-model="current" @update:date="onDateChange">
      <template #header>
        <div class="cal-header">
          <div class="cal-nav">
            <el-button size="small" plain @click="prevMonth">◀ 上个月</el-button>
            <span class="cal-month">{{ monthStr }}</span>
            <el-button size="small" plain @click="nextMonth">下个月 ▶</el-button>
          </div>
          <div class="legend">
            <span class="legend-item free">空闲</span>
            <span class="legend-item booked">已预订</span>
            <span class="legend-item in">已入住</span>
            <span class="legend-item settle">核算中</span>
          </div>
        </div>
      </template>
      <template #date-cell="{ data }">
        <div class="cell" :class="cellClass(data.day)">
          <span class="day-num">{{ Number(data.day.slice(8, 10)) }}</span>
          <div v-if="infoOf(data.day)" class="status-tag" :class="cellClass(data.day)">
            <span v-if="infoOf(data.day).orderNo" class="order-no" :title="'订单号：' + infoOf(data.day).orderNo">#{{ infoOf(data.day).orderNo.slice(-6) }}</span>
            <span v-else>{{ statusLabel(infoOf(data.day).status) }}</span>
          </div>
        </div>
      </template>
    </el-calendar>
    <div v-if="errorMsg" class="cal-error">{{ errorMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getRoomCalendar } from '@/api/room'

const props = defineProps({
  roomId: { type: [String, Number], required: true },
  // 初始月份 yyyy-MM，缺省为当前月
  month: { type: String, default: '' }
})

const current = ref(new Date())
const loading = ref(false)
const errorMsg = ref('')
const dayMap = ref({}) // { 'YYYY-MM-DD': { status, orderNo, orderId } }

const monthStr = computed(() => {
  const d = current.value
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${d.getFullYear()}-${m}`
})

const load = async () => {
  if (!props.roomId) return
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await getRoomCalendar(props.roomId, monthStr.value)
    if (res.code === 200 && res.data?.days) {
      const map = {}
      res.data.days.forEach((d) => { map[d.date] = d })
      dayMap.value = map
    } else {
      errorMsg.value = res.message || '加载房态失败'
    }
  } catch (e) {
    errorMsg.value = '加载房态失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const onDateChange = () => {
  load()
}

// 切换月份：上一月 / 下一月（el-calendar 头部按钮被自定义 header 覆盖，这里手动实现）
const prevMonth = () => {
  current.value = new Date(current.value.getFullYear(), current.value.getMonth() - 1, 1)
  load()
}

const nextMonth = () => {
  current.value = new Date(current.value.getFullYear(), current.value.getMonth() + 1, 1)
  load()
}

const infoOf = (day) => {
  if (!dayMap.value[day]) return null
  const info = dayMap.value[day]
  if (info.status === 0) return null
  return info
}

const statusLabel = (s) => {
  switch (s) {
    case 1: return '已预订'
    case 2: return '已入住'
    case 3: return '核算中'
    default: return ''
  }
}

const cellClass = (day) => {
  const info = dayMap.value[day]
  if (!info || info.status === 0) return 'free'
  switch (info.status) {
    case 1: return 'booked'
    case 2: return 'in'
    case 3: return 'settle'
    default: return 'free'
  }
}

onMounted(() => {
  if (props.month) {
    const parts = props.month.split('-').map(Number)
    if (parts.length === 2) {
      current.value = new Date(parts[0], parts[1] - 1, 1)
    }
  }
  load()
})

watch(() => props.roomId, () => { load() })
</script>

<style scoped>
.room-calendar { min-height: 200px; }
.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.cal-nav { display: flex; align-items: center; gap: 8px; }
.cal-month { font-size: 15px; font-weight: 600; min-width: 84px; text-align: center; }
.legend { display: flex; gap: 12px; font-size: 12px; color: #555; }
.legend-item::before {
  content: '';
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}
.legend-item.free::before { background: #e8f5e9; }
.legend-item.booked::before { background: #fff3e0; }
.legend-item.in::before { background: #ffebee; }
.legend-item.settle::before { background: #fff7e6; }
.cell {
  height: 100%;
  min-height: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
}
.cell .day-num { font-size: 13px; font-weight: 500; color: #666; }
.cell.free { background: #e8f5e9; }
.cell.booked { background: #fff3e0; }
.cell.in { background: #ffebee; }
.cell.settle { background: #fff7e6; }
.status-tag {
  margin-top: 3px;
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 92%;
}
.status-tag.booked { color: #b76e00; }
.status-tag.in { color: #d32f2f; }
.status-tag.settle { color: #8a5a00; }
.order-no { font-family: monospace; }
.cal-error { color: #f56c6c; text-align: center; padding: 10px; font-size: 13px; }
:deep(.el-calendar-table .el-calendar-day) {
  padding: 0;
  height: auto;
}
:deep(.el-calendar-table td.is-selected) {
  background: #fff;
}
</style>
