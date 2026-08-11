<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🔧 报修管理</h2>
      <p>查看租客提交的报修工单并处理</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 160px" @change="reload">
          <el-option label="待处理" :value="0" />
          <el-option label="处理中" :value="1" />
          <el-option label="已完成" :value="2" />
          <el-option label="已关闭" :value="3" />
        </el-select>
      </div>

      <el-empty v-if="repairs.length === 0 && !loading" description="暂无报修工单" />

      <el-table v-if="!loading" :data="repairs" border stripe style="width: 100%">
        <el-table-column prop="title" label="报修标题" min-width="160" />
        <el-table-column prop="description" label="问题描述" min-width="220" show-overflow-tooltip />
        <el-table-column prop="roomId" label="房源ID" width="90" />
        <el-table-column prop="userId" label="租客ID" width="90" />
        <el-table-column label="现场图片" width="120">
          <template #default="{ row }">
            <el-image v-if="row.images" :src="parseImages(row.images)[0]" class="repair-img" :preview-src-list="parseImages(row.images)" preview-teleported />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handlerRemark" label="处理备注" min-width="140" show-overflow-tooltip />
        <el-table-column prop="createTime" label="提交时间" min-width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0 || row.status === 1" type="primary" size="small" @click="openHandle(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadRepairs" />
      </div>
    </el-card>

    <el-dialog v-model="handleVisible" title="处理报修" width="480px">
      <el-form label-width="80px">
        <el-form-item label="处理状态">
          <el-select v-model="handleForm.status" placeholder="选择状态">
            <el-option label="处理中" :value="1" />
            <el-option label="已完成" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="handleForm.handlerRemark" type="textarea" :rows="3" placeholder="填写处理说明（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandle">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const repairs = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const statusFilter = ref(null)
const handleVisible = ref(false)
const handleForm = reactive({ repairId: null, status: 1, handlerRemark: '' })

const getStatusType = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success', '3': 'info' }
  return map[String(status)] || 'default'
}

const getStatusName = (status) => {
  const map = { '0': '待处理', '1': '处理中', '2': '已完成', '3': '已关闭' }
  return map[String(status)] || '未知'
}

const parseImages = (str) => {
  if (!str) return []
  try {
    const arr = JSON.parse(str)
    if (Array.isArray(arr)) return arr
  } catch (e) { /* 不是JSON，走逗号分隔 */ }
  return str.split(',').filter(Boolean)
}

const loadRepairs = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (statusFilter.value !== null && statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await request({ url: '/repair/landlord/list', method: 'get', params })
    if (res.code === 200) {
      repairs.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载报修失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadRepairs()
}

const openHandle = (row) => {
  handleForm.repairId = row.id
  handleForm.status = row.status === 0 ? 1 : row.status
  handleForm.handlerRemark = row.handlerRemark || ''
  handleVisible.value = true
}

const submitHandle = async () => {
  try {
    const res = await request({
      url: '/repair/handle',
      method: 'put',
      data: {
        repairId: handleForm.repairId,
        status: handleForm.status,
        handlerRemark: handleForm.handlerRemark
      }
    })
    if (res.code === 200) {
      ElMessage.success('处理成功')
      handleVisible.value = false
      loadRepairs()
    } else {
      ElMessage.error(res.message || '处理失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败')
  }
}

onMounted(loadRepairs)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { margin-bottom: 16px; }
.repair-img { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>