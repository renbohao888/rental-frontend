<template>
  <div class="appointments-page">
    <div class="page-header">
      <h2>🗓️ 我的看房预约</h2>
      <div class="header-actions">
        <el-radio-group v-model="statusFilter" size="small" @change="reload">
          <el-radio-button :value="null">全部</el-radio-button>
          <el-radio-button :value="0">待确认</el-radio-button>
          <el-radio-button :value="1">已确认</el-radio-button>
          <el-radio-button :value="2">已拒绝</el-radio-button>
          <el-radio-button :value="3">已看房</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-empty v-if="list.length === 0 && !loading" description="暂无看房预约，快去房源详情页预约看房吧～" />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-for="item in list" :key="item.id" class="appointment-card" :class="'st-' + item.status">
      <div class="appointment-body">
        <img :src="item.roomCover || 'https://loremflickr.com/100/80/house'" class="room-thumb" @click="goRoom(item)" />
        <div class="room-details">
          <div class="room-title" @click="goRoom(item)">{{ item.roomTitle || '房源#' + item.roomId }}</div>
          <div class="room-address" v-if="item.roomAddress">{{ item.roomAddress }}</div>
          <div class="appointment-time">🕐 {{ item.appointmentDate }} {{ item.appointmentTime }}</div>
          <div class="remark" v-if="item.remark">备注：{{ item.remark }}</div>
          <div class="landlord-remark" v-if="item.landlordRemark">房东回复：{{ item.landlordRemark }}</div>
        </div>
        <div class="appointment-status">
          <el-tag :type="getStatusType(item.status)">{{ item.statusText || getStatusName(item.status) }}</el-tag>
        </div>
      </div>

      <div class="appointment-footer">
        <span class="create-time">提交于 {{ formatTime(item.createTime) }}</span>
        <div class="actions">
          <el-button v-if="item.status === 0" size="small" type="danger" plain @click="cancel(item)">取消预约</el-button>
          <el-button v-if="item.status === 1" size="small" type="success" @click="viewed(item)">标记已看房</el-button>
          <el-button v-if="item.status === 1" size="small" @click="goChat(item)">💬 联系房东</el-button>
          <el-button size="small" @click="goRoom(item)">查看房源</el-button>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyAppointments, cancelAppointment, markAsViewed } from '@/api/appointment'

const router = useRouter()
const loading = ref(false)
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const statusFilter = ref(null)

const getStatusType = (s) => {
  const map = { '0': 'warning', '1': 'success', '2': 'danger', '3': 'info' }
  return map[String(s)] || 'default'
}
const getStatusName = (s) => {
  const map = { '0': '待确认', '1': '已确认', '2': '已拒绝', '3': '已看房' }
  return map[String(s)] || '未知'
}
const formatTime = (t) => (t ? String(t).replace('T', ' ').slice(0, 19) : '')

const loadList = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (statusFilter.value !== null && statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await getMyAppointments(params)
    if (res.code === 200) {
      list.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (e) {
    console.error('加载预约失败', e)
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadList()
}

const goRoom = (item) => {
  if (item.roomId) router.push(`/room/${item.roomId}`)
}

const goChat = () => {
  router.push('/chat')
}

const cancel = (item) => {
  ElMessageBox.confirm(`确定要取消「${item.roomTitle}」的看房预约吗？`, '提示', {
    confirmButtonText: '取消预约',
    cancelButtonText: '再想想',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await cancelAppointment(item.id)
      if (res.code === 200) {
        ElMessage.success(res.message || '预约已取消')
        loadList()
      } else {
        ElMessage.error(res.message || '取消失败')
      }
    } catch (e) {
      ElMessage.error('取消失败')
    }
  }).catch(() => {})
}

const viewed = (item) => {
  ElMessageBox.confirm(`确认已完成看房（${item.appointmentDate} ${item.appointmentTime}）吗？`, '提示', {
    confirmButtonText: '已完成看房',
    cancelButtonText: '取消',
    type: 'success'
  }).then(async () => {
    try {
      const res = await markAsViewed(item.id)
      if (res.code === 200) {
        ElMessage.success('已标记看房完成')
        loadList()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped>
.appointments-page { background: var(--bg-card); padding: 20px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}
.page-header h2 { margin: 0; }
.loading { padding: 20px; }
.appointment-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 12px;
  transition: all 0.3s;
}
.appointment-card:hover { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); }
.appointment-card.st-1 { border-left: 3px solid #67c23a; }
.appointment-card.st-2 { border-left: 3px solid #f56c6c; }
.appointment-body { display: flex; gap: 14px; }
.room-thumb {
  width: 90px;
  height: 70px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  flex-shrink: 0;
}
.room-details { flex: 1; }
.room-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; cursor: pointer; }
.room-title:hover { color: #409eff; }
.room-address { font-size: 12px; color: #999; margin-bottom: 6px; }
.appointment-time { font-size: 13px; color: #409eff; margin-bottom: 6px; }
.remark { font-size: 12px; color: #666; margin-bottom: 4px; }
.landlord-remark {
  font-size: 12px;
  color: #c96f2b;
  background: rgba(255, 106, 0, 0.12);
  border: 1px solid rgba(255, 106, 0, 0.35);
  border-radius: 4px;
  padding: 4px 8px;
  display: inline-block;
}
.appointment-status { text-align: right; flex-shrink: 0; }
.appointment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #f0f0f0;
}
.create-time { font-size: 12px; color: #999; }
.actions { display: flex; gap: 8px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@media (max-width: 768px) {
  .appointments-page { padding: 12px; }
  .appointment-body { flex-direction: column; }
  .appointment-status { text-align: left; }
}
</style>
