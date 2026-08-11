<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>🛡️ 报修纠纷督办</h2>
      <p>监督平台报修与纠纷处理</p>
    </el-card>

    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :xs="12" :sm="6"><el-card class="mini"><div class="mini-label">待处理报修</div><div class="mini-value">{{ stats.pendingRepairs || 0 }}</div></el-card></el-col>
      <el-col :xs="12" :sm="6"><el-card class="mini"><div class="mini-label">处理中报修</div><div class="mini-value">{{ stats.processingRepairs || 0 }}</div></el-card></el-col>
      <el-col :xs="12" :sm="6"><el-card class="mini"><div class="mini-label">已完成报修</div><div class="mini-value">{{ stats.completedRepairs || 0 }}</div></el-card></el-col>
      <el-col :xs="12" :sm="6"><el-card class="mini"><div class="mini-label">纠纷总数</div><div class="mini-value">{{ stats.totalDisputes || 0 }}</div></el-card></el-col>
    </el-row>

    <el-card>
      <el-tabs v-model="type" @tab-change="reload">
        <el-tab-pane label="报修工单" name="repair">
          <el-table :data="list" border stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="title" label="标题" min-width="160" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="roomId" label="房源ID" width="90" />
            <el-table-column prop="userId" label="租客ID" width="90" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="repairStatusType(row.status)">{{ repairStatusName(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handlerRemark" label="处理备注" min-width="140" show-overflow-tooltip />
            <el-table-column prop="createTime" label="提交时间" min-width="160" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="用户纠纷" name="dispute">
          <el-table :data="list" border stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="title" label="标题" min-width="180" />
            <el-table-column prop="content" label="内容" min-width="240" show-overflow-tooltip />
            <el-table-column prop="userId" label="用户ID" width="90" />
            <el-table-column prop="createTime" label="提交时间" min-width="160" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadList" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const type = ref('repair')
const list = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const stats = ref({})

const repairStatusType = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success', '3': 'info' }
  return map[String(status)] || 'default'
}

const repairStatusName = (status) => {
  const map = { '0': '待处理', '1': '处理中', '2': '已完成', '3': '已关闭' }
  return map[String(status)] || '未知'
}

const loadStats = async () => {
  try {
    const res = await request({ url: '/repair/admin/supervision/stats', method: 'get' })
    if (res.code === 200) stats.value = res.data || {}
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/repair/admin/supervision/list',
      method: 'get',
      params: { type: type.value, pageNum: pageNum.value, pageSize: pageSize.value }
    })
    if (res.code === 200) {
      const page = res.data?.list || {}
      list.value = page?.records || []
      total.value = page?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadList()
}

onMounted(() => {
  loadStats()
  loadList()
})
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.mini { text-align: center; }
.mini-label { color: #999; font-size: 12px; }
.mini-value { font-size: 24px; font-weight: 700; color: #409eff; margin-top: 6px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* 手机端适配 */
@media (max-width: 768px) {
  .mini-value { font-size: 20px; }
  :deep(.el-table) { overflow-x: auto; display: block; }
  :deep(.el-tabs__nav-wrap) { overflow-x: auto; }
}
</style>