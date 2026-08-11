<template>
  <div class="page-container">
    <el-card class="header-card">
      <div class="page-header">
        <h2>🏘️ 房东管理</h2>
        <p>查看平台已认证房东，或处理房东入驻申请</p>
      </div>
    </el-card>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- ================= Tab1：已认证房东 ================= -->
        <el-tab-pane :label="`已认证房东 (${landlordTotal})`" name="landlords">
          <div class="toolbar">
            <el-input v-model="lKeyword" placeholder="搜索昵称 / 账号 / 手机号" style="width: 250px" clearable @change="pageNum = 1; loadLandlords()" />
            <el-button type="primary" @click="pageNum = 1; loadLandlords()" style="margin-left: 12px;">刷新</el-button>
          </div>

          <el-empty v-if="landlords.length === 0 && !loading" description="暂无已认证房东" />

          <el-table v-if="!loading" :data="filteredLandlords" border stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column label="昵称" min-width="130">
              <template #default="{ row }">
                <el-avatar :src="row.avatar" :size="30">{{ (row.nickname || 'U')[0] }}</el-avatar>
                <span style="margin-left: 8px;">{{ row.nickname || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="accountNo" label="账号" width="150" show-overflow-tooltip />
            <el-table-column prop="phone" label="手机号" width="130" />
            <el-table-column label="房源数" width="90" align="center">
              <template #default="{ row }">
                <el-link type="primary" :underline="false" @click="goToRooms(row)">{{ roomCountMap[row.id] ?? '…' }}</el-link>
              </template>
            </el-table-column>
            <el-table-column label="账号状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.auditStatus === 1 ? 'danger' : 'success'">{{ row.auditStatus === 1 ? '已禁用' : '正常' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="注册时间" width="165">
              <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="190" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="goToRooms(row)">查看房源</el-button>
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

          <div class="pagination" v-if="landlordTotal > 0">
            <el-pagination v-model:page-num="pageNum" v-model:page-size="pageSize" :total="landlordTotal" layout="total, prev, pager, next" @current-change="loadLandlords" />
          </div>
        </el-tab-pane>

        <!-- ================= Tab2：入驻申请 ================= -->
        <el-tab-pane :label="`入驻申请 (${total})`" name="applications">
          <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索昵称 / 手机号 / 姓名" style="width: 250px" clearable @change="loadApplications" />
            <el-select v-model="statusFilter" placeholder="筛选状态" style="width: 150px; margin-left: 12px;" clearable @change="loadApplications">
              <el-option label="待审核" :value="0" />
              <el-option label="已通过" :value="1" />
              <el-option label="已拒绝" :value="2" />
              <el-option label="已撤销" :value="3" />
            </el-select>
            <el-button type="primary" @click="loadApplications" style="margin-left: 12px;">刷新</el-button>
          </div>

          <el-empty v-if="list.length === 0 && !loading" description="暂无房东入驻申请" />

          <el-table v-if="!loading" :data="filteredList" border stripe style="width: 100%">
            <el-table-column prop="userNickname" label="用户昵称" width="120" />
            <el-table-column prop="userPhone" label="账号手机号" width="130" />
            <el-table-column prop="realName" label="真实姓名" width="110" />
            <el-table-column prop="idCard" label="身份证号" width="180" show-overflow-tooltip />
            <el-table-column label="提交时间" width="160">
              <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.statusText || statusName(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="auditRemark" label="审核备注" min-width="140" show-overflow-tooltip />
            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="openDetail(row)">详情</el-button>
                <el-button v-if="row.status === 0" size="small" type="success" @click="approve(row)">通过</el-button>
                <el-button v-if="row.status === 0" size="small" type="danger" plain @click="reject(row)">驳回</el-button>
                <el-button v-if="row.status === 1" size="small" type="warning" @click="revoke(row)">撤销认证</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination" v-if="total > 0">
            <el-pagination v-model:page-num="appPageNum" v-model:page-size="appPageSize" :total="total" layout="total, prev, pager, next" @current-change="loadApplications" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 申请详情 -->
    <el-dialog v-model="detailVisible" title="📄 入驻申请详情" width="720px">
      <el-descriptions v-if="current" :column="2" border>
        <el-descriptions-item label="用户昵称">{{ current.userNickname }}</el-descriptions-item>
        <el-descriptions-item label="账号手机号">{{ current.userPhone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ current.realName }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ current.phone }}</el-descriptions-item>
        <el-descriptions-item label="身份证号" :span="2">{{ current.idCard }}</el-descriptions-item>
        <el-descriptions-item label="申请备注" :span="2">{{ current.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(current.status)">{{ current.statusText || statusName(current.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核时间">{{ formatTime(current.auditTime) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核备注" :span="2">{{ current.auditRemark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">认证资料</el-divider>
      <div v-if="current" class="cert-images">
        <div v-if="current.idCardFront" class="cert-item">
          <div class="cert-label">身份证人像面</div>
          <el-image :src="current.idCardFront" class="cert-img" :preview-src-list="[current.idCardFront]" preview-teleported fit="cover" />
        </div>
        <div v-if="current.idCardBack" class="cert-item">
          <div class="cert-label">身份证国徽面</div>
          <el-image :src="current.idCardBack" class="cert-img" :preview-src-list="[current.idCardBack]" preview-teleported fit="cover" />
        </div>
        <div v-if="current.businessLicense" class="cert-item">
          <div class="cert-label">营业执照</div>
          <el-image :src="current.businessLicense" class="cert-img" :preview-src-list="[current.businessLicense]" preview-teleported fit="cover" />
        </div>
        <div v-if="!current.idCardFront && !current.idCardBack && !current.businessLicense" class="cert-none">未上传认证图片</div>
      </div>
    </el-dialog>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const activeTab = ref('landlords')
const loading = ref(false)

// ============ Tab1：已认证房东 ============
const landlords = ref([])
const landlordTotal = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const lKeyword = ref('')
const roomCountMap = ref({})

const filteredLandlords = computed(() => {
  const kw = lKeyword.value.trim().toLowerCase()
  if (!kw) return landlords.value
  return landlords.value.filter((u) =>
    (u.nickname || '').toLowerCase().includes(kw) ||
    (u.accountNo || '').toLowerCase().includes(kw) ||
    (u.phone || '').toLowerCase().includes(kw)
  )
})

const loadLandlords = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/user/admin/list',
      method: 'get',
      params: { pageNum: pageNum.value, pageSize: pageSize.value, role: 1 }
    })
    if (res.code === 200) {
      landlords.value = res.data?.records || []
      landlordTotal.value = res.data?.total || 0
      loadRoomCounts()
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载房东列表失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// 并行统计每个房东的房源数量
const loadRoomCounts = async () => {
  const ids = landlords.value.map((u) => u.id)
  const map = {}
  await Promise.all(
    ids.map(async (id) => {
      try {
        const res = await request({
          url: '/room/admin/list',
          method: 'get',
          params: { pageNum: 1, pageSize: 1, landlordId: id }
        })
        map[id] = res.code === 200 ? (res.data?.total || 0) : '-'
      } catch (e) {
        map[id] = '-'
      }
    })
  )
  roomCountMap.value = map
}

// 查看该房东名下房源
const goToRooms = (row) => {
  router.push({ path: '/admin/rooms', query: { landlordId: row.id } })
}

// 禁用 / 启用房东账号
const toggleStatus = (row) => {
  const action = row.auditStatus === 1 ? '启用' : '禁用'
  ElMessageBox.confirm(`确定要${action}房东「${row.nickname}」的账号吗？${action === '禁用' ? '禁用后该房东将无法登录平台。' : ''}`, '提示', {
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
        loadLandlords()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// ============ Tab2：入驻申请 ============
const list = ref([])
const total = ref(0)
const appPageNum = ref(1)
const appPageSize = ref(10)
const keyword = ref('')
const statusFilter = ref(null)

const detailVisible = ref(false)
const current = ref(null)

const statusName = (s) => {
  const map = { '0': '待审核', '1': '已通过', '2': '已拒绝', '3': '已撤销' }
  return map[String(s)] || '未知'
}

const getStatusType = (s) => {
  const map = { '0': 'warning', '1': 'success', '2': 'danger', '3': 'info' }
  return map[String(s)] || 'default'
}

const formatTime = (t) => {
  if (!t) return '-'
  const d = new Date(t)
  return isNaN(d.getTime()) ? '-' : d.toLocaleString()
}

const filteredList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return list.value
  return list.value.filter((r) =>
    (r.userNickname || '').toLowerCase().includes(kw) ||
    (r.userPhone || '').toLowerCase().includes(kw) ||
    (r.realName || '').toLowerCase().includes(kw)
  )
})

const loadApplications = async () => {
  loading.value = true
  try {
    const params = { pageNum: appPageNum.value, pageSize: appPageSize.value }
    if (statusFilter.value !== null && statusFilter.value !== '') params.status = statusFilter.value
    const res = await request({ url: '/landlord/applications', method: 'get', params })
    if (res.code === 200) {
      list.value = res.data?.records || []
      total.value = res.data?.total || 0
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载申请失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const openDetail = (row) => {
  current.value = row
  detailVisible.value = true
}

// 审核通过
const approve = (row) => {
  ElMessageBox.prompt(`确认通过「${row.realName}」的房东入驻申请？`, '审核通过', {
    confirmButtonText: '确认通过',
    cancelButtonText: '取消',
    inputPlaceholder: '审核备注（选填）',
    type: 'success'
  }).then(async ({ value }) => {
    try {
      const res = await request({
        url: `/landlord/audit/${row.id}`,
        method: 'post',
        params: { status: 1, auditRemark: value || '' }
      })
      if (res.code === 200) {
        ElMessage.success('已通过认证，该用户已成为房东')
        loadApplications()
        loadLandlords()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 审核驳回（必须填写原因）
const reject = (row) => {
  ElMessageBox.prompt(`请填写驳回「${row.realName}」申请的理由`, '驳回申请', {
    confirmButtonText: '确认驳回',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '驳回原因（必填）',
    inputValidator: (val) => (val && val.trim().length > 0 ? true : '驳回原因不能为空'),
    type: 'warning'
  }).then(async ({ value }) => {
    try {
      const res = await request({
        url: `/landlord/audit/${row.id}`,
        method: 'post',
        params: { status: 2, auditRemark: value.trim() }
      })
      if (res.code === 200) {
        ElMessage.success('已驳回该申请')
        loadApplications()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 撤销已认证的房东（必须填写原因，撤销后所有房源下架）
const revoke = (row) => {
  ElMessageBox.prompt(
    `撤销「${row.realName}」的房东认证后，该用户将降级为租客，且名下所有房源将立即下架！请填写撤销原因：`,
    '撤销房东认证',
    {
      confirmButtonText: '确认撤销',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputPlaceholder: '撤销原因（必填）',
      inputValidator: (val) => (val && val.trim().length > 0 ? true : '撤销原因不能为空'),
      type: 'error'
    }
  ).then(async ({ value }) => {
    try {
      const res = await request({
        url: `/landlord/revoke/${row.id}`,
        method: 'post',
        params: { reason: value.trim() }
      })
      if (res.code === 200) {
        ElMessage.success(res.message || '撤销成功，房源已下架')
        loadApplications()
        loadLandlords()
      } else {
        ElMessage.error(res.message || '撤销失败')
      }
    } catch (error) {
      ElMessage.error('撤销失败')
    }
  }).catch(() => {})
}

const onTabChange = (name) => {
  if (name === 'landlords') {
    loadLandlords()
  } else if (name === 'applications') {
    loadApplications()
  }
}

onMounted(loadLandlords)
</script>


<style scoped>
.page-container {
  animation: slideUp 0.3s ease;
}

.header-card {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px;
}

.page-header p {
  margin: 0;
  color: #999;
  font-size: 13px;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.cert-images {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.cert-item {
  width: 220px;
}

.cert-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.cert-img {
  width: 220px;
  height: 140px;
  border-radius: 6px;
  border: 1px solid #eee;
}

.cert-none {
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

}

