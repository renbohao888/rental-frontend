<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>⚖️ 纠纷管理</h2>
      <p>处理租客与房东之间的交易纠纷</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 150px" @change="reload">
          <el-option label="待受理" :value="0" />
          <el-option label="处理中" :value="1" />
          <el-option label="已解决" :value="2" />
          <el-option label="已驳回" :value="3" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
      </div>

      <el-table v-loading="loading" :data="disputes" border stripe style="width: 100%">
        <el-table-column prop="orderNo" label="订单号" width="150" show-overflow-tooltip />
        <el-table-column prop="roomTitle" label="房源" min-width="130" show-overflow-tooltip />
        <el-table-column prop="userNickname" label="投诉用户" width="100" />
        <el-table-column prop="reason" label="纠纷类型" width="110" />
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="95">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="165">
          <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openDetail(row)">查看详情</el-button>
            <el-button v-if="row.status === 0 || row.status === 1" size="small" type="success" @click="openHandle(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:page-num="pageNum"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadDisputes"
        />
      </div>
    </el-card>

    <!-- 纠纷详情 -->
    <el-dialog v-model="detailVisible" title="⚖️ 纠纷详情" width="680px">
      <el-descriptions v-if="current" :column="2" border>
        <el-descriptions-item label="订单号">{{ current.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="房源">{{ current.roomTitle }}</el-descriptions-item>
        <el-descriptions-item label="投诉用户">{{ current.userNickname }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ current.userPhone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="纠纷类型">{{ current.reason }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(current.status)">{{ current.statusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间" :span="2">{{ formatTime(current.createTime) }}</el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="2">
          <div class="desc-text">{{ current.description }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="证据图片" :span="2">
          <div v-if="evidenceImages.length" class="evidence-list">
            <el-image v-for="(img, i) in evidenceImages" :key="i" :src="img" class="evidence-img"
              :preview-src-list="evidenceImages" preview-teleported fit="cover" />
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="current.adminRemark" label="处理备注" :span="2">{{ current.adminRemark }}</el-descriptions-item>
        <el-descriptions-item v-if="current.resolution" label="解决方案" :span="2">{{ current.resolution }}</el-descriptions-item>
        <el-descriptions-item v-if="current.handleTime" label="处理时间" :span="2">{{ formatTime(current.handleTime) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button v-if="current && (current.status === 0 || current.status === 1)" type="success" @click="openHandle(current)">处理该纠纷</el-button>
      </template>
    </el-dialog>

    <!-- 处理纠纷 -->
    <el-dialog v-model="handleVisible" title="处理纠纷" width="520px">
      <el-form label-width="90px">
        <el-form-item label="处理状态">
          <el-select v-model="handleForm.status" placeholder="选择状态">
            <el-option label="处理中" :value="1" />
            <el-option label="已解决" :value="2" />
            <el-option label="已驳回" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="handleForm.adminRemark" type="textarea" :rows="2" placeholder="处理备注（可选）" />
        </el-form-item>
        <el-form-item label="解决方案">
          <el-input v-model="handleForm.resolution" type="textarea" :rows="3" placeholder="解决方案（已解决时必填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitHandle">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const submitting = ref(false)
const disputes = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const query = reactive({ status: null })

const detailVisible = ref(false)
const current = ref(null)
const evidenceImages = ref([])
const handleVisible = ref(false)
const handleForm = reactive({ disputeId: null, status: 1, adminRemark: '', resolution: '' })

const getStatusTag = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success', '3': 'info' }
  return map[String(status)] || 'info'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

const parseImages = (str) => {
  if (!str) return []
  return String(str).split(',').map(s => s.trim()).filter(Boolean)
}

const loadDisputes = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (query.status !== null && query.status !== '') params.status = query.status
    const res = await request({ url: '/dispute/admin/list', method: 'get', params })
    if (res.code === 200) {
      disputes.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载纠纷失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadDisputes()
}

const openDetail = (row) => {
  current.value = row
  evidenceImages.value = parseImages(row.evidenceImages)
  detailVisible.value = true
}

const openHandle = (row) => {
  handleForm.disputeId = row.id
  handleForm.status = row.status === 1 ? 1 : 1
  handleForm.adminRemark = row.adminRemark || ''
  handleForm.resolution = row.resolution || ''
  handleVisible.value = true
}

const submitHandle = async () => {
  if (handleForm.status === 2 && !handleForm.resolution.trim()) {
    ElMessage.warning('已解决时请填写解决方案')
    return
  }
  submitting.value = true
  try {
    const res = await request({
      url: '/dispute/handle',
      method: 'put',
      data: {
        disputeId: handleForm.disputeId,
        status: handleForm.status,
        adminRemark: handleForm.adminRemark,
        resolution: handleForm.resolution
      }
    })
    if (res.code === 200) {
      ElMessage.success(res.message || '处理成功')
      handleVisible.value = false
      detailVisible.value = false
      loadDisputes()
    } else {
      ElMessage.error(res.message || '处理失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadDisputes)
</script>



<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 16px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
.desc-text { white-space: pre-wrap; line-height: 1.6; color: #555; }
.evidence-list { display: flex; gap: 8px; flex-wrap: wrap; }
.evidence-img { width: 90px; height: 70px; border-radius: 6px; cursor: pointer; border: 1px solid #eee; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>