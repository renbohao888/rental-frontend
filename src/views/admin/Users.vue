<template>
  <div class="page-container">
    <el-card class="header-card">
      <h2>👥 用户管理</h2>
      <p>查看平台注册用户</p>
    </el-card>

    <el-card>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索昵称 / 账号 / 手机号" clearable style="width: 240px" />
        <el-radio-group v-model="roleFilter" @change="reload">
          <el-radio-button :value="null">全部</el-radio-button>
          <el-radio-button :value="0">管理员</el-radio-button>
          <el-radio-button :value="1">房东</el-radio-button>
          <el-radio-button :value="2">租客</el-radio-button>
        </el-radio-group>
      </div>

      <el-empty v-if="users.length === 0 && !loading" description="暂无用户" />

      <el-table v-if="!loading" :data="filteredUsers" border stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column label="头像" width="70">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :size="36">{{ (row.nickname || 'U')[0] }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="accountNo" label="账号" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleName(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="账号状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.auditStatus === 1 ? 'danger' : 'success'">{{ row.auditStatus === 1 ? '已禁用' : '正常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="注册时间" min-width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.role !== 0"
              size="small"
              :type="row.auditStatus === 1 ? 'success' : 'danger'"
              plain
              @click="toggleStatus(row)"
            >
              {{ row.auditStatus === 1 ? '启用' : '禁用' }}
            </el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadUsers" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const roleFilter = ref(null)
const keyword = ref('')

const getRoleName = (role) => {
  const map = { '0': '管理员', '1': '房东', '2': '租客' }
  return map[String(role)] || '未知'
}

const getRoleType = (role) => {
  const map = { '0': 'danger', '1': 'warning', '2': 'success' }
  return map[String(role)] || 'default'
}

const filteredUsers = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return users.value
  return users.value.filter((u) =>
    (u.nickname || '').toLowerCase().includes(kw) ||
    (u.accountNo || '').toLowerCase().includes(kw) ||
    (u.phone || '').toLowerCase().includes(kw)
  )
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = { pageNum: pageNum.value, pageSize: pageSize.value }
    if (roleFilter.value !== null) {
      params.role = roleFilter.value
    }
    const res = await request({ url: '/user/admin/list', method: 'get', params })
    users.value = res?.records || []
    total.value = res?.total || 0
  } catch (error) {
    console.error('加载用户失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const reload = () => {
  pageNum.value = 1
  loadUsers()
}

// 禁用 / 启用账号
const toggleStatus = (row) => {
  const action = row.auditStatus === 1 ? '启用' : '禁用'
  ElMessageBox.confirm(`确定要${action}用户「${row.nickname}」的账号吗？${action === '禁用' ? '禁用后该用户将无法登录平台。' : ''}`, '提示', {
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
        loadUsers()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(loadUsers)
</script>

<style scoped>
.page-container { animation: slideUp 0.3s ease; }
.header-card { margin-bottom: 20px; }
.header-card h2 { margin: 0 0 8px; }
.header-card p { margin: 0; color: #999; font-size: 13px; }
.toolbar { margin-bottom: 16px; }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>