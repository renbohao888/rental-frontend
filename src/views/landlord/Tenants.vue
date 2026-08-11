<!-- 房东模块 - 租客管理页面 -->
<template>
  <div class="page-container">
    <el-card class="page-header-card">
      <div class="page-header">
        <h2>👥 租客管理</h2>
        <div class="header-actions">
          <el-input
            v-model="searchText"
            placeholder="搜索租客昵称/手机号"
            style="width: 250px"
            clearable
            @input="loadData"
          />
          <el-select v-model="filterStatus" placeholder="筛选状态" @change="loadData" style="width: 150px; margin-left: 12px;">
            <el-option label="全部" value="" />
            <el-option label="租住中" value="active" />
            <el-option label="已离开" value="left" />
          </el-select>
        </div>
      </div>
    </el-card>

    <el-card class="content-card">
      <el-table :data="tableData" stripe style="width: 100%;" :loading="loading">
        <el-table-column prop="nickname" label="租客昵称" width="150" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="roomTitle" label="租赁房源" width="150" />
        <el-table-column prop="checkInDate" label="入住日期" width="130" />
        <el-table-column prop="checkOutDate" label="退租日期" width="130" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '租住中' : '已离开' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewTenant(row.id)">详情</el-button>
            <el-button type="info" size="small" @click="sendMessage(row.id)">消息</el-button>
            <el-button type="warning" size="small" @click="viewRent(row.id)">查看租约</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:page-num="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const searchText = ref('')
const filterStatus = ref('')

const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据加载
    setTimeout(() => {
      tableData.value = [
        { id: 1, nickname: '张三', phone: '13800138000', roomTitle: '温馨大床房', checkInDate: '2026-08-01', checkOutDate: '', status: 'active' },
        { id: 2, nickname: '李四', phone: '13800138001', roomTitle: '豪华套房', checkInDate: '2026-07-15', checkOutDate: '2026-08-15', status: 'left' },
        { id: 3, nickname: '王五', phone: '13800138002', roomTitle: '温馨大床房', checkInDate: '2026-08-10', checkOutDate: '', status: 'active' },
      ]
      total.value = 30
      loading.value = false
    }, 500)
  } catch (error) {
    ElMessage.error('加载失败')
    loading.value = false
  }
}

const viewTenant = (id) => {
  ElMessage.info(`查看租客 ${id} 的详细信息`)
}

const sendMessage = (id) => {
  ElMessage.success('打开消息窗口')
}

const viewRent = (id) => {
  ElMessage.info(`查看租约`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container {
  animation: fadeIn 0.3s ease-in;
}

.page-header-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .header-actions > * {
    width: 100% !important;
  }
}
</style>
