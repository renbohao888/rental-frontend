<template>
  <div class="page-container" v-loading="loading">
    <el-card class="header-card">
      <h2>💬 消息管理</h2>
      <p>平台公告消息与投诉纠纷集中处理入口</p>
    </el-card>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="loadList">
        <el-tab-pane label="系统公告" name="notice">
          <el-table :data="list" stripe style="width: 100%; margin-top: 8px;">
            <el-table-column prop="title" label="公告标题" width="280" show-overflow-tooltip />
            <el-table-column prop="content" label="公告内容" min-width="260" show-overflow-tooltip />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.type || '平台公告' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="发布时间" width="170" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="投诉纠纷" name="dispute">
          <el-table :data="list" stripe style="width: 100%; margin-top: 8px;">
            <el-table-column prop="orderNo" label="订单号" width="170" show-overflow-tooltip />
            <el-table-column prop="roomTitle" label="房源" min-width="130" show-overflow-tooltip />
            <el-table-column prop="userNickname" label="投诉人" width="110" />
            <el-table-column prop="reason" label="类型" width="110" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="95">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)">{{ row.statusText || '未知' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="goDisputes">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-empty v-if="!loading && list.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('notice')
const list = ref([])

const getStatusTag = (status) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success', '3': 'info' }
  return map[String(status)] || 'info'
}

const loadList = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'notice') {
      const res = await request({ url: '/notice/list', method: 'get', params: { pageNum: 1, pageSize: 20 } })
      if (res.code === 200) {
        list.value = res.data?.records || (Array.isArray(res.data) ? res.data : [])
      } else {
        ElMessage.error(res.message || '加载失败')
      }
    } else {
      const res = await request({ url: '/dispute/admin/list', method: 'get', params: { pageNum: 1, pageSize: 20 } })
      if (res.code === 200) {
        list.value = res.data?.records || []
      } else {
        ElMessage.error(res.message || '加载失败')
      }
    }
  } catch (error) {
    console.error('加载消息失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const goDisputes = () => {
  router.push('/admin/disputes')
}

onMounted(loadList)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>


<style scoped>
.page-container {
  animation: slideUp 0.3s ease;
}

.header-card {
  margin-bottom: 20px;
}

.header-card h2 {
  margin: 0 0 8px;
}

.header-card p {
  margin: 0;
  color: #999;
  font-size: 13px;
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
