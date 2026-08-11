<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🏠 房源管理</h2>
      <p>平台所有房源监督和管理</p>
    </el-card>

    <el-card v-if="landlordFilter" class="filter-card">
      <el-tag type="info" closable @close="clearLandlordFilter">当前查看：房东 ID = {{ landlordFilter }} 的全部房源</el-tag>
      <el-button size="small" style="margin-left: 8px;" @click="clearLandlordFilter">清除筛选</el-button>
    </el-card>

    <el-card>
      <el-empty v-if="rooms.length === 0 && !loading" description="暂无房源" />

      <div v-if="loading">
        <el-skeleton :rows="5" animated />
      </div>

      <el-table v-if="!loading" :data="rooms" border stripe style="width: 100%">
        <el-table-column label="封面" width="110">
          <template #default="{ row }">
            <img :src="row.cover || fallbackCover(row)" class="room-cover" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="房源名称" min-width="160" />
        <el-table-column prop="address" label="地址" min-width="150" show-overflow-tooltip />
        <el-table-column label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}/晚</template>
        </el-table-column>
        <el-table-column label="押金" width="90">
          <template #default="{ row }">¥{{ row.deposit || 0 }}</template>
        </el-table-column>
        <el-table-column prop="landlordId" label="房东ID" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="350" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewRoom(row)">详情</el-button>
            <el-button type="info" size="small" @click="openCalendar(row)">房态日历</el-button>
            <el-button v-if="row.status === 1" type="warning" size="small" @click="doAudit(row, 3)">下架</el-button>
            <el-button v-else-if="row.status !== 2" type="success" size="small" @click="doAudit(row, 1)">上架</el-button>
            <el-button type="danger" size="small" plain @click="removeRoom(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 房态日历弹窗 -->
      <el-dialog v-model="calendarVisible" :title="`📅 ${calendarRoom?.title || ''} 房态日历`" width="880px" destroy-on-close>
        <RoomCalendar v-if="calendarRoom" :room-id="calendarRoom.id" />
      </el-dialog>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:page-num="pageNum"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadRooms"
          @current-change="loadRooms"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import RoomCalendar from '@/components/RoomCalendar.vue'
import request from '@/utils/request'
import { auditRoom, deleteRoom } from '@/api/room'

const router = useRouter()
const route = useRoute()
// 支持从房东管理页跳转过来按房东过滤（query 里的 landlordId）
const landlordFilter = ref(route.query.landlordId ? Number(route.query.landlordId) : null)
const loading = ref(false)
const rooms = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)

// 房态日历
const calendarVisible = ref(false)
const calendarRoom = ref(null)
const openCalendar = (row) => {
  calendarRoom.value = row
  calendarVisible.value = true
}

const getStatusType = (status) => {
  const map = { '0': 'warning', '1': 'success', '2': 'info', '3': 'info', '4': 'danger' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待审核', '1': '已上架', '2': '已租出', '3': '已下架', '4': '已驳回' }
  return map[String(status)] || '未知'
}

const fallbackCover = (row) => `https://loremflickr.com/300/200/house?random=${row.id}`

const loadRooms = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (landlordFilter.value) params.landlordId = landlordFilter.value
    const res = await request({
      url: '/room/admin/list',
      method: 'get',
      params
    })
    if (res.code === 200) {
      rooms.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载房源失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// 清除房东筛选，回到全部房源
const clearLandlordFilter = () => {
  landlordFilter.value = null
  router.replace({ path: '/admin/rooms' })
  pageNum.value = 1
  loadRooms()
}

const viewRoom = (row) => {
  router.push(`/room/${row.id}`)
}

const doAudit = (row, status) => {
  const action = status === 1 ? '上架' : '下架'
  ElMessageBox.confirm(`确定要${action}「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await auditRoom(row.id, status)
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else {
        ElMessage.success(message)
        loadRooms()
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 删除房源（软删除；存在进行中订单时后端会拒绝）
const removeRoom = (row) => {
  ElMessageBox.confirm(
    `确定要删除「${row.title}」吗？删除后房源将下架并从所有列表隐藏，该操作不可恢复。`,
    '删除房源',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(async () => {
    try {
      const res = await deleteRoom(row.id)
      const message = typeof res === 'string' ? res : (res?.message || '操作成功')
      if (typeof res === 'string' && res.includes('失败')) {
        ElMessage.error(message)
      } else if (res && res.code === 200) {
        ElMessage.success(message)
        loadRooms()
      } else {
        ElMessage.error(message)
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.page-container {
  animation: slideUp 0.3s ease;
}

.header-card {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.header-card h2 {
  margin: 0 0 8px;
}

.header-card p {
  margin: 0;
  color: #999;
  font-size: 13px;
}

.room-cover {
  width: 80px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

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