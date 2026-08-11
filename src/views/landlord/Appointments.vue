<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🗓️ 看房预约管理</h2>
      <p>查看租客的看房预约并确认或拒绝</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-radio-group v-model="statusFilter" @change="reload">
          <el-radio-button :value="null">全部</el-radio-button>
          <el-radio-button :value="0">待确认</el-radio-button>
          <el-radio-button :value="1">已确认</el-radio-button>
          <el-radio-button :value="2">已拒绝</el-radio-button>
          <el-radio-button :value="3">已完成看房</el-radio-button>
        </el-radio-group>
      </div>

      <el-empty v-if="list.length === 0 && !loading" description="暂无看房预约" />

      <el-table v-if="!loading" :data="list" border stripe style="width: 100%">
        <el-table-column prop="roomTitle" label="房源" min-width="160" />
        <el-table-column prop="userNickname" label="租客" width="120">
          <template #default="{ row }">{{ row.userNickname || `用户#${row.userId}` }}<div class="sub" v-if="row.userPhone">{{ row.userPhone }}</div></template>
        </el-table-column>
        <el-table-column label="预约时间" min-width="180">
          <template #default="{ row }">{{ row.appointmentDate }} {{ row.appointmentTime }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column prop="landlordRemark" label="处理备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.statusText || getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="提交时间" min-width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0" type="success" size="small" @click="handle(row, 1)">确认</el-button>
            <el-button v-if="row.status === 0" type="danger" size="small" plain @click="handle(row, 2)">拒绝</el-button>
            <el-button v-else size="small" disabled>已处理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadList" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const statusFilter = ref(null)

const getStatusType = (status) => {
  const map = { '0': 'warning', '1': 'success', '2': 'danger', '3': 'info' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待确认', '1': '已确认', '2': '已拒绝', '3': '已完成看房' }
  return map[String(status)] || '未知'
}

const loadList = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (statusFilter.value !== null && statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await request({ url: '/appointment/landlord/list', method: 'get', params })
    if (res.code === 200) {
      list.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载预约失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadList()
}

const handle = (row, status) => {
  const label = status === 1 ? '确认' : '拒绝'
  ElMessageBox.confirm(`确定要${label}「${row.roomTitle}」的看房预约吗？`, '提示', {
    confirmButtonText: label,
    cancelButtonText: '取消',
    type: status === 1 ? 'success' : 'warning'
  }).then(async () => {
    try {
      const res = await request({
        url: '/appointment/handle',
        method: 'put',
        data: { appointmentId: row.id, status, landlordRemark: `${label}预约` }
      })
      if (res.code === 200) {
        ElMessage.success('操作成功')
        loadList()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('网络请求失败')
    }
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { margin-bottom: 16px; }
.sub { font-size: 12px; color: #999; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>