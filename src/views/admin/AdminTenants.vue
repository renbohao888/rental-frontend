<template>
  <div class="page-container">
    <el-card class="header-card">
      <div class="page-header">
        <h2>👥 租客管理</h2>
        <div class="actions">
          <el-input v-model="keyword" placeholder="搜索昵称 / 账号 / 手机号" style="width: 250px" clearable />
          <el-button type="primary" @click="loadTenants">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-empty v-if="tenants.length === 0 && !loading" description="暂无租客" />

      <el-table v-if="!loading" :data="filteredTenants" border stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column label="头像" width="70">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :size="36">{{ (row.nickname || 'U')[0] }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="租客昵称" width="140" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="accountNo" label="账号" width="180" show-overflow-tooltip />
        <el-table-column label="账号状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.auditStatus === 1 ? 'danger' : 'success'">{{ row.auditStatus === 1 ? '已禁用' : '正常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="注册时间" min-width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.auditStatus === 1 ? 'success' : 'danger'"
              plain
              @click="toggleStatus(row)"
            >
              {{ row.auditStatus === 1 ? '启用' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadTenants" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const tenants = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const keyword = ref('')

const filteredTenants = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return tenants.value
  return tenants.value.filter((u) =>
    (u.nickname || '').toLowerCase().includes(kw) ||
    (u.accountNo || '').toLowerCase().includes(kw) ||
    (u.phone || '').toLowerCase().includes(kw)
  )
})

const loadTenants = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/user/admin/list',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value, role: 2 }
    })
    tenants.value = res?.records || []
    total.value = res?.total || 0
  } catch (error) {
    console.error('加载租客失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const toggleStatus = (row) => {
  const action = row.auditStatus === 1 ? '启用' : '禁用'
  ElMessageBox.confirm(`确定要${action}租客「${row.nickname}」的账号吗？${action === '禁用' ? '禁用后该租客将无法登录平台。' : ''}`, '提示', {
    confirmButtonText: `确定${action}`,
    cancelButtonText: '取消',
    type: action === '禁用' ? 'warning' : 'info'
  }).then(async () => {
    try {
      const res = await request({
        url: `/user/admin/toggle-status/${row.id}`,
        method: 'post',
        params: { status: row.auditStatus === 1 ? 0 : 1 }
      })
      if (res.code === 200) {
        ElMessage.success(res.message || `${action}成功`)
        loadTenants()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(loadTenants)
</script>

<style scoped>
.page-container {
  animation: slideUp 0.3s ease;
}

.header-card {
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
}

.actions {
  display: flex;
  gap: 12px;
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
